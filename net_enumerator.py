from copy import deepcopy
import time
from sys import getsizeof

def initialize_search(ocpn):
    #A state consists of the current tokens in the different places and the sequence of previously executed activities
    #for different objects
    marking = dict()
    #generate a token for each starting place
    for p in ocpn.places:
        if len(p.in_arcs) == 0:
            marking[p.name]= [p.object_type]


    #initialize an empty prefix
    prefix = []
    return (marking, prefix)

def get_enabled_activities(ocpn, state):
    enabled_activities = []
    for t in ocpn.transitions:
        enabled = True
        for a in t.in_arcs:
            p = a.source
            if p.name not in state[0]:
                enabled = False
        if enabled:
            enabled_activities.append(t.name)

    return enabled_activities

def copy_state(state):
    marking = state[0].copy()
    prefix = state[1].copy()
    new_state = (marking, prefix)
    return new_state

def get_next_state(ocpn, state, activity):
    time_cp = 0
    time_dcp = 0
    ti = time.time()
    #new_state = deepcopy(state)
    time_dcp += time.time() - ti
    ti = time.time()
    new_state = copy_state(state)
    time_cp += time.time() - ti
    for t in ocpn.transitions:
        if t.name == activity:
            #store which tokens of which type in in places
            token_dict = {}
            for a in t.in_arcs:
                p = a.source
                ot = p.object_type
                if ot not in token_dict.keys():
                    token_dict[ot] = []
                token_dict[ot]+= state[0][p.name]
                # remove tokens from outplaces
                new_state[0].pop(p.name,None)
            #add tokens to out places
            for a in t.out_arcs:
                p = a.target
                ot = p.object_type
                if ot in token_dict.keys():
                    new_state[0][p.name] = token_dict[ot]



            #add activity to prefix
            if not t.silent:
                objects = [list(i) for i in sorted(token_dict.items())]
                for i in range(0,len(objects)):
                    objects[i][1] = tuple(objects[i][1])
                objects = tuple([tuple(o) for o in objects])
                new_state[1].append((activity,objects))
            break
    return new_state, time_cp, time_dcp

def state_to_string(state):
    state_string = ""
    for k in sorted(state[0].keys()):
        state_string+=k+".".join(sorted(state[0][k]))
    state_string+=".".join([x[0] for x in state[1]])
    return state_string

def store_trace(state, num_of_traces):
    stored_trace = []
    for event in state[1]:
        stored_trace.append( (event[0] , tuple([(ot, tuple([o_x+str(num_of_traces) for o_x in o])) for (ot, o) in event[1]]) ) )
    #print(stored_trace)
    return tuple(stored_trace)

def store_trace_trace_aware(state):
    stored_trace = []
    for event in state[1]:
        stored_trace.append( (event[0] , tuple([(ot, tuple([o_x for o_x in o])) for (ot, o) in event[1]]) ) )
    #print(stored_trace)
    return tuple(stored_trace)

def enumerate_ocpn(ocpn):
    time_en = 0
    time_next = 0
    time_string = 0
    initial_state = initialize_search(ocpn)
    trace_set = set()
    trace_set_only_traces = set()
    state_hashes = set()
    state_queue = []
    state_queue.append(initial_state)
    dfs = 0
    while dfs < len(state_queue):
        if dfs >=1000000:
            return set()
        state=state_queue[dfs]
        # ti = time.time()
        en_act= get_enabled_activities(ocpn, state)
        # time_en += time.time()-ti
        #print(en_act)
        for act in en_act:
            #check here
            # ti = time.time()
            next_state, time_cp, time_dcp = get_next_state(ocpn, state, act)
            # time_next += time.time() - ti

            #if a loop is detected do not follow that
            trace_seq = [s[0] for s in next_state[1]]
            if len(set(trace_seq))< len(trace_seq):
                continue
            #if any([v>1 for v in {i:trace_seq.count(i) for i in trace_seq}.values()]):
            #    continue
            # ti = time.time()
            # next_state_string = state_to_string(next_state)
            # time_string += time.time() - ti
            # if next_state_string not in state_hashes:
            #     state_hashes.add(next_state_string)
            #     state_queue.append(next_state)
            state_queue.append(next_state)

        #print(state_queue)

        if len(en_act) == 0:
            trace_object_agnostic = store_trace_trace_aware(state)
            if trace_object_agnostic not in trace_set_only_traces:
                trace_set_only_traces.add(trace_object_agnostic)
                trace_set.add(store_trace(state, len(trace_set)))#tuple(state[1]))
        dfs+=1
        #if dfs % 1000 == 0:
        #    print(dfs)
    #print("enabled time "+str(time_en))
    #print("state time " + str(time_next))
    #print("string time " + str(time_string))
    #print(len(trace_set))
    if dfs >40000:
        print(dfs)
        print(getsizeof(state_queue))
        print(getsizeof(trace_set))
        print(getsizeof(trace_set_only_traces))
    return trace_set