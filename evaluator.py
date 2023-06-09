import net_generator as gen
import net_enumerator as en
import misc as misc
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
import get_stats as stats

def eval_params(params):
    (intercon, sample_rate, num_ot, num_act,chance_and,chance_xor) = params
    # generate a model
    net = gen.generate_net(num_act=num_act, num_ot=num_ot, interconnectedness=intercon, chance_add_AND=chance_and,
                           chance_add_XOR=chance_xor)
    if len([t for t in net.transitions if not t.silent]) > 8:
        return {}
    complexity = stats.get_complexity_per_object(net)
    #print(complexity)
    for ot in net.object_types:
        if complexity[ot + "_act"] < 4:
            return {}
    interconnectedness = stats.get_interconnectivity(net, False)
    # enumerate system behavior
    full_log = en.enumerate_ocpn(net)
    #if there is an error in generating the log return empty
    if len(full_log) < 1:
        return {"number activities": -1}
    #print(len(full_log))
    # generate an event log from the model
    log = misc.sample_log(full_log, ratio=sample_rate)
    ocel = misc.to_OCEL(log)

    #print(len(ocel.process_executions))
    # discover ocpn
    ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
    #gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
    #ocpn_vis_factory.view(gviz)

    # fitness of ocpn to model
    full_model_log = en.enumerate_ocpn(ocpn)
    if len(full_model_log) == 0:
        return {"number activities": -1}
    fitness, precision = misc.compare_languages(full_log, full_model_log)
    #print(fitness)
    #print(precision)

    # fitness of pn to model
    flat_ocel = misc.flatten_ocel(ocel)
    #print(len(flat_ocel.process_executions))
    ocpn = ocpn_discovery_factory.apply(flat_ocel, parameters={"debug": False})
    #gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
    #ocpn_vis_factory.view(gviz)
    full_flat_log = en.enumerate_ocpn(ocpn)
    if len(full_flat_log) == 0:
        return {"number activities": -1}
    fitness_flat, precision_flat = misc.compare_languages(full_log, full_flat_log)
    #print(fitness_flat)
    #print(precision_flat)
    res_dict = {
        "interconnectedness": interconnectedness,
        "number object types": num_ot,
        "number activities": len([t for t in net.transitions if not t.silent]),
        "sample_rate": len(ocel.process_executions) / len(full_log),
        "fitness_ocpn": fitness,
        "precision_ocpn": precision,
        "fitness_flat": fitness_flat,
        "precision_flat": precision_flat}

    sum_complexity = []
    for ot in net.object_types:
        res_dict["completeness_" + ot] = complexity[ot]
        sum_complexity.append(complexity[ot])
    res_dict["completeness"] = sum(sum_complexity) / len(sum_complexity)
    return res_dict


def generate_example_models(params_list,interc_vals,con_vals,epsilon_i,epsilon_c):
    return_dict = {}
    for params in params_list:
        (intercon, sample_rate, num_ot, num_act, chance_and, chance_xor) = params
        net = gen.generate_net(num_act=num_act, num_ot=num_ot, interconnectedness=intercon, chance_add_AND=chance_and,
                               chance_add_XOR=chance_xor)
        if len([t for t in net.transitions if not t.silent]) < 8 or len([t for t in net.transitions if not t.silent]) > 8 :
            continue
        interconnectedness = stats.get_interconnectivity(net, False)
        for i_val in interc_vals:
            if i_val - epsilon_i < interconnectedness and i_val + epsilon_i > interconnectedness:
                sum_complexity= []
                complexity_d = stats.get_complexity_per_object(net)
                print(complexity_d)
                model_too_small = False
                for ot in net.object_types:
                    sum_complexity.append(complexity_d[ot])
                    if complexity_d[ot+"_act"] < 4:
                        model_too_small = True
                if model_too_small:
                    continue
                complexity = sum(sum_complexity) / len(sum_complexity)

                print(complexity)
                for c_val in con_vals:
                    if c_val - epsilon_c < complexity and c_val + epsilon_c > complexity:
                        return_dict[(i_val,c_val)] = net
                        print(complexity_d)
                        print((i_val,c_val))


    return return_dict