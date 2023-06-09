import string

from enum import Enum

import itertools

import copy

import random
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet as OCPN
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
def get_digit(label): #function to extract the number, not necessary but easier to match places and transitions
    return ''.join(c for c in label if c.isdigit())

def get_labels_activties(num_act):
    return ["Activity_"+str(i+1) for i in range(0, num_act)]

def get_timespot_activities(labels_act):
    return dict([(labels_act[i], i) for i in range(0, len(labels_act))])


def get_labels_objecttypes(num_obj):
    return ["Object_"+str(i) for i in range(1, num_obj+1)]

def get_object_types_for_activity(labels_obj, chance_overlap):
    #choose an object type
    prim_obj = random.choice(labels_obj)
    obj_list=[prim_obj]
    #go over all other object types
    for obj in labels_obj:
        #chance of overlap add an extra object type
        if (random.random() < chance_overlap) == True:
            obj_list.append(obj)
    #we return the set because primary object might be added twice
    return set(obj_list)

def get_object_types_for_all_activties(labels_act, labels_obj, chance_overlap):
    types_act = dict([(labels_act[i], get_object_types_for_activity(labels_obj, chance_overlap)) for i in range(0, len(labels_act))])
    types_act["start"] = set(labels_obj)
    types_act["end"] = set(labels_obj)
    return types_act

def get_digit_withexception(label, integer): #function to extract the number, not necessary but easier to match places and transitions
    digit = ''.join(c for c in label if c.isdigit())
    if digit == '':
        return str(integer)
    else:
        return digit

def create_places_activity(label_act, objects_act, timespots):
    #place is here tuple (Name, object_type, timespot of transition it follows)
    #name: Place_ + ObjTypeNumber + ActTypeNumber (activity that comes after it)
    return [("Place_"+get_digit(obj)+"_"+get_digit_withexception(label_act, (len(timespots)-1)), obj, timespots[label_act]) for obj in objects_act]

def create_all_places(object_types_for_all_activties, timespots, object_types):
    sources =  [("Source_"+get_digit(obj_type), obj_type, 0) for obj_type in object_types]
    new_object_types_for_all_activties = {k: object_types_for_all_activties[k] for k in set(list(object_types_for_all_activties.keys())) - set(["start"])}
    places = [create_places_activity(key, object_types_for_all_activties[key], timespots) for key in new_object_types_for_all_activties]
    sinks = [("Sink_"+get_digit(obj_type), obj_type, len(timespots)) for obj_type in object_types]
    return sources + [item for sublist in places for item in sublist] + sinks

def get_all_activities_for_object(obj_type, object_types_for_all_activties):
    return [key for key in object_types_for_all_activties if obj_type in object_types_for_all_activties[key]]

def get_all_arcs_for_object(obj_type, object_types_for_all_activties):

    relevant_activities = get_all_activities_for_object(obj_type, object_types_for_all_activties)
    transitions = [("Source_"+get_digit(obj_type), relevant_activities[0])] 
    transitions = transitions + [("Place_"+get_digit(obj_type)+"_"+get_digit_withexception(act, (len(object_types_for_all_activties)-1)), act) for act in relevant_activities[1:]]
    transitions = transitions + [(relevant_activities[i], "Place_"+get_digit(obj_type)+"_"+get_digit_withexception(relevant_activities[i+1], (len(object_types_for_all_activties)-1))) for i in range(0, len(relevant_activities)-1)]
    transitions = transitions + [(relevant_activities[-1], "Sink_"+get_digit(obj_type))]
    return transitions

def get_all_arcs(labels_obj, object_types_for_all_activties):
    arcs = [get_all_arcs_for_object(obj_type, object_types_for_all_activties) for obj_type in labels_obj]
    return [item for sublist in arcs for item in sublist]


def get_simple_net(num_act, num_obj, chance_overlap):
    transitions = []
    places = []
    arcs = []

    labels_act = get_labels_activties(num_act)
    labels_obj = get_labels_objecttypes(num_obj)
    

    labels_act.insert(0, "start")
    labels_act.append("end")
    
    object_types_for_all_activties = get_object_types_for_all_activties(labels_act, labels_obj, chance_overlap)
    transitions = [(act, obj) for act, obj in object_types_for_all_activties.items()]
    places = create_all_places(object_types_for_all_activties, get_timespot_activities(labels_act), labels_obj)
    arcs = get_all_arcs(labels_obj, object_types_for_all_activties)
    return (transitions, places, arcs)


def get_full_digit(label):
    return ''.join(c for c in label if (c.isdigit() or c=='-'))

def get_previous_and_next_places(tr, places, arcs):
    labels_in = [a[0] for a in arcs if a[1] == tr[0]]
    labels_out = [a[1] for a in arcs if a[0] == tr[0]]
    pl_in = [p for p in places if p[0] in labels_in]
    pl_out = [p for p in places if p[0] in labels_out]
    return pl_in, pl_out
    

def get_matching_places_arcs(curr_tr, places, arcs):
    places_in, places_out = get_previous_and_next_places(curr_tr, places, arcs)
    arcs_in = [a for a in arcs if a[1] == curr_tr[0]]
    arcs_out = [a for a in arcs if a[0] == curr_tr[0]]
    return places_in, places_out, arcs_in, arcs_out
    

def add_XOR(transitions, places, arcs, chance_add_split, transition, reduce_chance):
    places_in, places_out, arcs_in, arcs_out = get_matching_places_arcs(transition, places, arcs)
    
    tr1 = (transition[0]+'-1', transition[1])
    tr2 = (transition[0]+'-2', transition[1])
    transitions.append(tr1)
    transitions.append(tr2)
    transitions.remove(transition)
        
    #XOR so no need to replace the places
    
    for pl_in in places_in:
        arc_in1 = (pl_in[0], tr1[0])
        arc_in2 = (pl_in[0], tr2[0])
        curr_arc_in = [a for a in arcs_in if a[0] == pl_in[0]][0]
        arcs.remove(curr_arc_in)
        arcs.append(arc_in1)
        arcs.append(arc_in2)

    for pl_out in places_out:
        arc_out1 = (tr1[0], pl_out[0])
        arc_out2 = (tr2[0], pl_out[0])
        curr_arc_out = [a for a in arcs_out if a[1] == pl_out[0]][0]
        arcs.remove(curr_arc_out)
        arcs.append(arc_out1)
        arcs.append(arc_out2)

    #recursivily so another chance to add a split
    if reduce_chance == True:
        chance_add_split = chance_add_split/2
    a1 = random.random()
    a2 = random.random()
    if a1 < chance_add_split:
        #print("adding recursive XOR")
        (transitions, places, arcs) = add_XOR(transitions, places, arcs, chance_add_split, tr1, reduce_chance)
    if a2 < chance_add_split:
        #print("adding recursive XOR")
        (transitions, places, arcs) = add_XOR(transitions, places, arcs, chance_add_split, tr2, reduce_chance)
    return (transitions, places, arcs)

    
def add_XORs(transitions, places, arcs, chance_add_split, reduce_chance=True):
    original_transitions = copy.deepcopy(transitions)
    for tr in original_transitions:
        if ('start' not in tr[0]) and ('end' not in tr[0]) and ('split' not in tr[0]) and ('join' not in tr[0]):
            a = random.random()
            if a < chance_add_split:
                #print("adding XOR")
                (transitions, places, arcs) = add_XOR(transitions, places, arcs, chance_add_split, tr, reduce_chance)
    return (transitions, places, arcs)



def get_matching_places_arcs_and(curr_tr,transitions, places, arcs):
    places_in, places_out = get_previous_and_next_places(curr_tr, places, arcs)
    arcs_in = [a for a in arcs if a[1] == curr_tr[0]]
    arcs_out = [a for a in arcs if a[0] == curr_tr[0]]
    arcs_inin = []
    for pl_in in places_in:
        arcs_inin += [a for a in arcs if a[1] == pl_in[0]]
    arcs_outout = []
    for pl_out in places_out:
        arcs_outout += [a for a in arcs if a[1] == pl_out[0]]
    prev_transitions = []
    for arc in arcs_inin:
        prev_transitions += [t for t in transitions if t[0] == arc[0]]
    next_transitions = []
    for arc in arcs_outout:
        next_transitions += [t for t in transitions if t[0] == arc[1]]
    return places_in, places_out, arcs_in, arcs_out, arcs_inin, arcs_outout, prev_transitions, next_transitions

def get_arcs_in(pl_in, arcs):
    arcs_in = [a for a in arcs if a[0] == pl_in[0]]
    arcs_inin = [a for a in arcs if a[1] == pl_in[0]]
    #print(len(arcs_in), len(arcs_inin))

    return arcs_inin[0], arcs_in[0]

def get_arcs_out(pl_out, arcs):
    arcs_out = [a for a in arcs if a[1] == pl_out[0]]
    arcs_outout = [a for a in arcs if a[0] == pl_out[0]]
    #print(len(arcs_out), len(arcs_outout))

    return arcs_outout[0], arcs_out[0]

def add_AND(transitions, places, arcs, chance_add_split, transition, reduce_chance):
    places_in, places_out = get_previous_and_next_places(transition, places, arcs)
    
    tr_split = (transition[0]+'-split', transition[1])
    tr1 = (transition[0]+'-1', transition[1])
    tr2 = (transition[0]+'-2', transition[1])
    tr_join = (transition[0]+'-join', transition[1])
    
    transitions.remove(transition)
    transitions.append(tr_split)
    transitions.append(tr1)
    transitions.append(tr2)
    transitions.append(tr_join)
                
    for pl_in in places_in:
        pl_in1 = (pl_in[0]+'-split-1', pl_in[1], pl_in[2])
        pl_in2 = (pl_in[0]+'-split-2', pl_in[1], pl_in[2])
        places.append(pl_in1)
        places.append(pl_in2)
        arc_inin, arc_in = get_arcs_in(pl_in, arcs)
        arc_split_out = (pl_in[0], tr_split[0])
        arc_inin1 = (tr_split[0], pl_in1[0])
        arc_inin2 = (tr_split[0], pl_in2[0])
        arc_in1 = (pl_in1[0], tr1[0])
        arc_in2 = (pl_in2[0], tr2[0])
        arcs.append(arc_split_out)
        arcs.append(arc_inin1)
        arcs.append(arc_inin2)
        arcs.append(arc_in1)
        arcs.append(arc_in2)
        arcs.remove(arc_in)
        

    for pl_out in places_out:
        pl_out1 = (pl_out[0]+'-join-1', pl_out[1], pl_out[2])
        pl_out2 = (pl_out[0]+'-join-2', pl_out[1], pl_out[2])
        places.append(pl_out1)
        places.append(pl_out2)
        arc_outout, arc_out = get_arcs_out(pl_out, arcs)
        arc_out1 = (tr1[0], pl_out1[0])
        arc_out2 = (tr2[0], pl_out2[0])
        arc_outout1 = (pl_out1[0], tr_join[0])
        arc_outout2 = (pl_out2[0], tr_join[0])
        arc_join_in = (tr_join[0], pl_out[0])
        arcs.remove(arc_out)
        arcs.append(arc_out1)
        arcs.append(arc_out2)     
        arcs.append(arc_outout1)
        arcs.append(arc_outout2)
        arcs.append(arc_join_in)


    #recursivily so another chance to add a split

    if reduce_chance == True:
        chance_add_split = chance_add_split/2
    a1 = random.random()
    a2 = random.random()
    if a1 < chance_add_split:
        #print("adding recursive and")
        (transitions, places, arcs) = add_AND(transitions, places, arcs, chance_add_split, tr1, reduce_chance)
    if a2 < chance_add_split:
        #print("adding recursive and")
        (transitions, places, arcs) = add_AND(transitions, places, arcs, chance_add_split, tr2, reduce_chance)
    return (transitions, places, arcs)
    
def add_ANDs(transitions, places, arcs, chance_add_split, reduce_chance=True):
    original_transitions = copy.deepcopy(transitions)
    for tr in original_transitions:
        if ('start' not in tr[0]) and ('end' not in tr[0]) and ('split' not in tr[0]) and ('join' not in tr[0]):
            a = random.random()
            if a < chance_add_split:
                #print("add and")
                (transitions, places, arcs) = add_AND(transitions, places, arcs, chance_add_split, tr, reduce_chance)
    return (transitions, places, arcs)

def generate_net(num_act, num_ot, interconnectedness, chance_add_AND, chance_add_XOR):
    #random.seed(2)
    (transitions, places, arcs) = get_simple_net(num_act, num_ot, interconnectedness)
    (transitions, places, arcs) = add_ANDs(transitions, places, arcs, chance_add_AND, reduce_chance=True)
    (transitions, places, arcs) = add_XORs(transitions, places, arcs, chance_add_XOR, reduce_chance=True)
    transition_dict = {t[0]: OCPN.Transition(t[0]) for t in transitions}
    place_dict = {p[0]:OCPN.Place(p[0],p[1]) for p in places}
    arc_dict = {(source,target):OCPN.Arc(transition_dict[source] if source in transition_dict.keys() else place_dict[source], transition_dict[target] if target in transition_dict.keys() else place_dict[target]) for (source,target) in arcs}
    transition_dict = {t[0]: OCPN.Transition(t[0], in_arcs = [arc_dict[(source, target)] for (source,target) in arc_dict.keys() if target == t[0]], out_arcs = [arc_dict[(source, target)] for (source,target) in arc_dict.keys() if source == t[0]]) for t in transitions}
    #update arc dict
    for (source,target) in arc_dict.keys():
        if source in transition_dict.keys():
            arc_dict[(source,target)].source = transition_dict[source]
        else:
            arc_dict[(source, target)].source = place_dict[source]

        if target in transition_dict.keys():
            arc_dict[(source, target)].target = transition_dict[target]
        else:
            arc_dict[(source, target)].target = place_dict[target]

    places_ocpn = list(place_dict.values())
    for p in places_ocpn:
        p.in_arcs = [arc_dict[(source, target)] for (source,target) in arc_dict.keys() if target == p.name]
        p.out_arcs = [arc_dict[(source, target)] for (source, target) in arc_dict.keys() if source == p.name]
    arcs_ocpn = list(arc_dict.values())
    transitions_ocpn = list(transition_dict.values())
    model = OCPN(name="Test",places = places_ocpn, transitions=transitions_ocpn,arcs=arcs_ocpn )
    for t in model.transitions:
        if "split" in t.name or "join" in t.name:
            t.silent = True
    #gviz = ocpn_vis_factory.apply(model, parameters={'format': 'svg'})
    #ocpn_vis_factory.view(gviz)
    return model

