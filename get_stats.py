#recale interconnectivity
import math

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


def get_ot_elements(ocpn, ot):
    places = [(p.name,ot) for p in ocpn.places if p.object_type == ot]
    transitions = [(t.name,) for t in ocpn.transitions if any([p.object_type == ot for p in t.preset])]
    place_list = [x[0] for x in places]
    t_list = [x[0] for x in transitions]
    arcs = [(a.source.name, a.target.name) for a in ocpn.arcs if a.source.name in place_list and a.target.name in t_list or  a.source.name in t_list and a.target.name in place_list]

    return (transitions,places,arcs)



def get_model_per_object_fixed(ocpn):
    obj_types = ocpn.object_types
    nets = {}
    for obj in obj_types:
        (transitions, places, arcs) = get_ot_elements(ocpn, obj)

        transition_dict = {t[0]: OCPN.Transition(t[0]) for t in transitions}
        place_dict = {p[0]: OCPN.Place(p[0], p[1]) for p in places}
        arc_dict = {(source, target): OCPN.Arc(
            transition_dict[source] if source in transition_dict.keys() else place_dict[source],
            transition_dict[target] if target in transition_dict.keys() else place_dict[target]) for (source, target) in
                    arcs}
        transition_dict = {t[0]: OCPN.Transition(t[0], in_arcs=[arc_dict[(source, target)] for (source, target) in
                                                                arc_dict.keys() if target == t[0]],
                                                 out_arcs=[arc_dict[(source, target)] for (source, target) in
                                                           arc_dict.keys() if source == t[0]]) for t in transitions}
        # update arc dict
        for (source, target) in arc_dict.keys():
            if source in transition_dict.keys():
                arc_dict[(source, target)].source = transition_dict[source]
            else:
                arc_dict[(source, target)].source = place_dict[source]

            if target in transition_dict.keys():
                arc_dict[(source, target)].target = transition_dict[target]
            else:
                arc_dict[(source, target)].target = place_dict[target]

        places_ocpn = list(place_dict.values())
        for p in places_ocpn:
            p.in_arcs = [arc_dict[(source, target)] for (source, target) in arc_dict.keys() if target == p.name]
            p.out_arcs = [arc_dict[(source, target)] for (source, target) in arc_dict.keys() if source == p.name]
        arcs_ocpn = list(arc_dict.values())
        transitions_ocpn = list(transition_dict.values())
        model = OCPN(name="Test", places=places_ocpn, transitions=transitions_ocpn, arcs=arcs_ocpn)
        #gviz = ocpn_vis_factory.apply(model, parameters={'format': 'svg'})
        #ocpn_vis_factory.view(gviz)
        nets[obj]=model
    return nets

def get_complexity_per_object(ocpn):
    models = get_model_per_object_fixed(ocpn)
    trace_share = {}
    for ot in models.keys():
        model = models[ot]
        #this is where it goes wrong: as far as I can see the models per object are nicely defined. 
        #The only problem is that the enumration always gives an empty set
        amount_traces = len(en.enumerate_ocpn(model))
        max_possible_traces = math.factorial(len(model.transitions)-2)
        trace_share[ot] = amount_traces/max_possible_traces
        trace_share[ot+"_act"] =  len([t for t in model.transitions if not t.silent])
    return trace_share


