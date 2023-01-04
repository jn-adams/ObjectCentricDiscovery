#recale interconnectivity

from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet as OCPN

import net_enumerator as en

from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory


def get_interconnectivity(ocpn, count_start_and_end = True):
    amount_extra = []
    if count_start_and_end == False:
        transitions_used = [t for t in ocpn.transitions if (t.name != 'start' and t.name != 'end')]
    else:
        transitions_used = ocpn.transitions
    for t in transitions_used:
        out_arcs = t.out_arcs
        if len(out_arcs) == 1:
            amount_extra.append(0)
        else:
            obj_types = []
            for arc in out_arcs:
                obj_types.append(arc.target.object_type)
            amount_extra.append(len(set(obj_types)) - 1)
    #normailzation by the amount of obj types. If not max value is always equal to #obj_types - 1 
    return (sum(amount_extra)/len(amount_extra))/(len(ocpn.object_types)-1)

def get_model_per_object(ocpn):
    obj_types = ocpn.object_types
    nets_list = []
    for obj in obj_types:
        places_obj = []
        arcs_obj = []
        transitions_obj = []
        for pl in ocpn.places:
            if pl.object_type == obj:
                places_obj.append(pl)
        for arc in ocpn.arcs:
            if arc.target in places_obj:
                arcs_obj.append(arc)
                transitions_obj.append(arc.source)
            elif arc.source in places_obj: 
                arcs_obj.append(arc)
                transitions_obj.append(arc.target)         
        objnet = OCPN(name="Test"+obj, transitions = list(set(transitions_obj)), places = places_obj, arcs=arcs_obj)
        nets_list.append(objnet)
    return nets_list

def get_complexity_per_object(ocpn):
    models = get_model_per_object(ocpn)
    amount_traces = []
    for model in models:
        
        #this is where it goes wrong: as far as I can see the models per object are nicely defined. 
        #The only problem is that the enumration always gives an empty set

        amount_traces.append(len(en.enumerate_ocpn(model)))
    return sum(amount_traces)/len(amount_traces)


