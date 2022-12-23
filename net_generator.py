#for now does not allow silent activities
#also no replacement of activtiies by constructs yet
#The chance_overlap x now means we assgn an activty label to one object and then there is an chance x
#for each other object to also be assigned to that one

#Notes Jari
# The number of activities does NOT include the common start and end transition now, I think thats fine

import string

from enum import Enum

import itertools

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



def create_places_activity(label_act, objects_act, timespots):
    #place is here tuple (Name, object_type, timespot of transition it follows)
    #name: Place_ + ObjTypeNumber + ActTypeNumber (activity that comes after it)
    return [("Place_"+get_digit(obj)+"_"+get_digit(label_act), obj, timespots[label_act]) for obj in objects_act]

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
    #Edited By Jari
    relevant_activities = get_all_activities_for_object(obj_type, object_types_for_all_activties)
    transitions = [("Source_"+get_digit(obj_type), relevant_activities[0])] 
    transitions = transitions + [("Place_"+get_digit(obj_type)+"_"+get_digit(act), act) for act in relevant_activities[1:]]
    transitions = transitions + [(relevant_activities[i], "Place_"+get_digit(obj_type)+"_"+get_digit(relevant_activities[i+1])) for i in range(0, len(relevant_activities)-1)]
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



def generate_net(num_act, num_ot, interconnectedness):
    random.seed(1)
    (transitions, places, arcs) = get_simple_net(num_act, num_ot, interconnectedness)
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


