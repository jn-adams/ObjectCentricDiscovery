import net_generator as gen
import net_enumerator as en
import misc as misc
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
import get_stats as stats

def eval_params(params):
    (intercon, sample_rate, num_ot, num_act,chance_and,chance_xor) = params
    # generate a model
    # net = gen.generate_net(num_act=20,num_ot=5, interconnectedness=0.2)
    # things missing: Replacement of activities by choice or parallel constructs and making sure that the net is conencted(can also be  covered by high enough interconnectedness)
    net = gen.generate_net(num_act=num_act, num_ot=num_ot, interconnectedness=intercon, chance_add_AND=chance_and,
                           chance_add_XOR=chance_xor)
    if len([t for t in net.transitions if not t.silent]) > 12:
        return {}
    complexity = stats.get_complexity_per_object(net)
    for ot in net.object_types:
        if complexity[ot + "_act"] < 6:
            return {}
    interconnectedness = stats.get_interconnectivity(net, False)
    # enumerate system behavior
    full_log = en.enumerate_ocpn(net)
    #if there is only one trace in the model dont use it
    #####if len(full_log) <= 1:
    #####    return {}
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
        return {}
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
        return {}
    fitness_flat, precision_flat = misc.compare_languages(full_log, full_flat_log)
    #print(fitness_flat)
    #print(precision_flat)
    res_dict = {
        "interconnectedness": interconnectedness,
        "number object types": num_ot,
        "number activities": len(net.transitions),
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
        if len([t for t in net.transitions if not t.silent]) > 12:
            continue
        interconnectedness = stats.get_interconnectivity(net, False)
        for i_val in interc_vals:
            if i_val - epsilon_i < interconnectedness and i_val + epsilon_i > interconnectedness:
                sum_complexity= []
                complexity_d = stats.get_complexity_per_object(net)
                model_too_small = False
                for ot in net.object_types:
                    sum_complexity.append(complexity_d[ot])
                    if complexity_d[ot+"_act"] < 6:
                        model_too_small = True
                if model_too_small:
                    continue
                complexity = sum(sum_complexity) / len(sum_complexity)


                for c_val in con_vals:
                    if c_val - epsilon_c < complexity and c_val + epsilon_c > complexity:
                        return_dict[(i_val,c_val)] = net
                        print(complexity_d)
                        print((i_val,c_val))


    return return_dict