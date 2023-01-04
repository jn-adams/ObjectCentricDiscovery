import net_generator as gen
import net_enumerator as en
import misc as misc
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
results = []
# for intercon in [0.3,0.4,0.5]:
#     for sample_rate in [0.01,0.02,0.05,0.1,0.2]:
#         for num_ot in [2,3,4]:
#             for num_act in [10,15,20]:
for intercon in [0.25]:
    for sample_rate in [0.02]:
        for num_ot in [2]:
            for num_act in [5]:
                #generate a model
                #net = gen.generate_net(num_act=20,num_ot=5, interconnectedness=0.2)
                #things missing: Replacement of activities by choice or parallel constructs and making sure that the net is conencted(can also be  covered by high enough interconnectedness)
                net = gen.generate_net(num_act=num_act,num_ot=num_ot, interconnectedness=intercon, chance_add_AND=0.1, chance_add_XOR=0.3)

                #enumerate system behavior
                full_log = en.enumerate_ocpn(net)
                print(len(full_log))

                #generate an event log from the model
                log = misc.sample_log(full_log,ratio=sample_rate)
                ocel = misc.to_OCEL(log)

                print(len(ocel.process_executions))
                #discover ocpn
                ocpn = ocpn_discovery_factory.apply(ocel, parameters={"debug": False})
                gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
                ocpn_vis_factory.view(gviz)



                #discover flat pn
                #fitness of ocpn to model
                full_model_log = en.enumerate_ocpn(ocpn)
                fitness, precision = misc.compare_languages(full_log, full_model_log)
                print(fitness)
                print(precision)


                #fitness of pn to model
                flat_ocel = misc.flatten_ocel(ocel)
                print(len(flat_ocel.process_executions))
                ocpn = ocpn_discovery_factory.apply(flat_ocel, parameters={"debug": False})
                gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
                ocpn_vis_factory.view(gviz)
                full_flat_log = en.enumerate_ocpn(ocpn)
                fitness_flat, precision_flat = misc.compare_languages(full_log, full_flat_log)
                print(fitness_flat)
                print(precision_flat)
                results.append(
                    {
                     "interconnectedness":intercon,
                     "number object types":num_ot,
                     "number activities": num_act,
                     "sample_rate" :sample_rate,
                     "fitness_ocpn":fitness,
                     "precision_ocpn": precision,
                     "fitness_flat":fitness_flat,
                     "precision_flat": precision_flat}
                )
print(results)