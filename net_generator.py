#for now does not allow silent activities
#also no replacement of activtiies by constructs yet
#The chance_overlap x now means we assgn an activty label to one object and then there is an chance x
#for each other object to also be assigned to that one

#Notes Jari
# The number of activities does NOT include the common start and end transition now, I think thats fine

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
    #Edited By Jari with a plus one t not be confusing
    return ["Activity_"+str(i+1) for i in range(0, num_act)]

def get_timespot_activities(labels_act):
    #Edited By Jari
    #dictionary with the original spot activities have on "the timeline"
    #Changed with a plus one because of start activity
    return dict([(labels_act[i], i+1) for i in range(0, len(labels_act))])



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
    #Edited By Jari
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
    #Edited By Jari
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

    #Edited By Jari
    labels_act.insert(0, "start")
    labels_act.append("end")

    object_types_for_all_activties = get_object_types_for_all_activties(labels_act, labels_obj, chance_overlap)

    transitions = [(act, obj) for act, obj in object_types_for_all_activties.items()]
    places = create_all_places(object_types_for_all_activties, get_timespot_activities(labels_act), labels_obj)
    arcs = get_all_arcs(labels_obj, object_types_for_all_activties)

    return (transitions, places, arcs)

#I used - in stead of _ for deeper levels so its easy to split on either one
def get_full_digit(label):
    return ''.join(c for c in label if (c.isdigit() or c=='-'))


def get_previous_and_next_place(tr, places, arcs):
    label_in = [a for a in arcs if a[1] == tr[0]][0][0]
    label_out = [a for a in arcs if a[0] == tr[0]][0][1]
    pl_in = [p for p in places if p[0] == label_in][0]
    pl_out = [p for p in places if p[0] == label_out][0]
    return pl_in, pl_out


def get_matching_places_arcs(curr_tr, places, arcs):
    place_in, place_out = get_previous_and_next_place(curr_tr, places, arcs)
    arcs_in = [a for a in arcs if a[1] == curr_tr[0]]
    arcs_out = [a for a in arcs if a[0] == curr_tr[0]]
    return place_in, place_out, arcs_in[0], arcs_out[0]


def add_XOR(transitions, places, arcs, chance_add_split, transition, reduce_chance):
    pl_in, pl_out, arc_in, arc_out = get_matching_places_arcs(transition, places, arcs)
    tr1 = (transition[0]+'-1', transition[1])
    tr2 = (transition[0]+'-2', transition[1])
    for i in range(0, len(transitions)):
        if transitions[i] == transition:
            transitions[i] = tr1
            transitions.insert(i+1, tr2)
    #XOR so no need to replace the places
    arc_in1 = (pl_in[0], tr1[0])
    arc_in2 = (pl_in[0], tr2[0])
    arc_out1 = (tr1[0], pl_out[0])
    arc_out2 = (tr2[0], pl_out[0])
    for i in range(0, len(arcs)):
        if arcs[i] == arc_in:
            arcs[i] = arc_in1
            arcs.insert(i+1, arc_in2)
        if arcs[i] == arc_out:
            arcs[i] = arc_out1
            arcs.insert(i+1, arc_out2)
    #recursivily so another chance to add a split
    if reduce_chance == True:
        chance_add_split = chance_add_split/2
    a1 = random.random()
    a2 = random.random()
    if a1 < chance_add_split:
        add_XOR(transitions, places, arcs, chance_add_split, tr1, reduce_chance)
    if a2 < chance_add_split:
        add_XOR(transitions, places, arcs, chance_add_split, tr2, reduce_chance)


def add_XORs(transitions, places, arcs, chance_add_split, reduce_chance=True):
    original_transitions = copy.deepcopy(transitions)
    for tr in original_transitions:
        if len(tr[1])==1:
            a = random.random()
            if a < chance_add_split:
                add_XOR(transitions, places, arcs, chance_add_split, tr, reduce_chance)
    return (transitions, places, arcs)




def get_matching_places_arcs_and(curr_tr,transitions, places, arcs):
    place_in, place_out = get_previous_and_next_place(curr_tr, places, arcs)
    arc_in = [a for a in arcs if a[1] == curr_tr[0]][0]
    arc_out = [a for a in arcs if a[0] == curr_tr[0]][0]
    arc_inin = [a for a in arcs if a[1] == place_in[0]][0]
    arc_outout = [a for a in arcs if a[0] == place_out[0]][0]
    prev_tr = [t for t in transitions if t[0] == arc_inin[0]][0]
    next_tr = [t for t in transitions if t[0] == arc_outout[1]][0]
    return place_in, place_out, arc_in, arc_out, arc_inin, arc_outout, prev_tr, next_tr


def add_AND(transitions, places, arcs, chance_add_split, transition, reduce_chance):
    pl_in, pl_out, arc_in, arc_out, arc_inin, arc_outout, prev_tr, next_tr = get_matching_places_arcs_and(transition,transitions, places, arcs)
    tr1 = (transition[0]+'-1', transition[1])
    tr2 = (transition[0]+'-2', transition[1])
    for i in range(0, len(transitions)):
        if transitions[i] == transition:
            transitions[i] = tr1
            transitions.insert(i+1, tr2)
    #AND so we need to replace the places
    pl_in1 = (pl_in[0]+'-1', pl_in[1], pl_in[2])
    pl_in2 = (pl_in[0]+'-2', pl_in[1], pl_in[2])
    pl_out1 = (pl_out[0]+'-1', pl_out[1], pl_out[2])
    pl_out2 = (pl_out[0]+'-2', pl_out[1], pl_out[2])

    for i in range(0, len(places)):
        if places[i] == pl_in:
            places[i] = pl_in1
            places.insert(i+1, pl_in2)
            for j in range(i+1, len(places)):
                places[j] = (places[j][0],places[j][1],places[j][2]+1)
    for i in range(0, len(places)):
        if places[i] == pl_out:
            places[i] = pl_out1
            places.insert(i+1, pl_out2)
            for j in range(i+1, len(places)):
                places[j] = (places[j][0],places[j][1],places[j][2]+1)
    print(places)
    arc_inin1 = (prev_tr[0], pl_in1[0])
    arc_inin2 = (prev_tr[0], pl_in2[0])
    arc_in1 = (pl_in1[0], tr1[0])
    arc_in2 = (pl_in2[0], tr2[0])
    arc_out1 = (tr1[0], pl_out1[0])
    arc_out2 = (tr2[0], pl_out2[0])
    arc_outout1 = (pl_out1[0], next_tr[0])
    arc_outout2 = (pl_out2[0], next_tr[0])
    for i in range(0, len(arcs)):
        if arcs[i] == arc_inin:
            arcs[i] = arc_inin1
            arcs.insert(i+1, arc_inin2)
    for i in range(0, len(arcs)):
        if arcs[i] == arc_in:
            arcs[i] = arc_in1
            arcs.insert(i+1, arc_in2)
    for i in range(0, len(arcs)):
        if arcs[i] == arc_out:
            arcs[i] = arc_out1
            arcs.insert(i+1, arc_out2)
    for i in range(0, len(arcs)):
        if arcs[i] == arc_outout:
            arcs[i] = arc_outout1
            arcs.insert(i+1, arc_outout2)
    #recursivily so another chance to add a split
    if reduce_chance == True:
        chance_add_split = chance_add_split/2
    a1 = random.random()
    a2 = random.random()
    if a1 < chance_add_split:
        add_AND(transitions, places, arcs, chance_add_split, tr1, reduce_chance)
    if a2 < chance_add_split:
        add_AND(transitions, places, arcs, chance_add_split, tr2, reduce_chance)


def add_ANDs(transitions, places, arcs, chance_add_split, reduce_chance=True):
    original_transitions = copy.deepcopy(transitions)
    for tr in original_transitions:
        if len(tr[1])==1:
            a = random.random()
            if a < chance_add_split:
                add_AND(transitions, places, arcs, chance_add_split, tr, reduce_chance)
    return (transitions, places, arcs)

def generate_net(num_act, num_ot, interconnectedness, chance_add_AND, chance_add_XOR):
    #random.seed(2)
    (transitions, places, arcs) = get_simple_net(num_act, num_ot, interconnectedness)
    #print('adding ANDs')
    #(transitions, places, arcs) = add_ANDs(transitions, places, arcs, chance_add_AND, reduce_chance=True)
    print('adding XORs')
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
    gviz = ocpn_vis_factory.apply(model, parameters={'format': 'svg'})
    ocpn_vis_factory.view(gviz)
    return model