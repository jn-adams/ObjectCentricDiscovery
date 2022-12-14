from copy import deepcopy


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
            if p.name not in state[0].keys():
                enabled = False
        if enabled:
            enabled_activities.append(t.name)

    return enabled_activities

def get_next_state(ocpn, state, activity):
    new_state = deepcopy(state)
    for t in ocpn.transitions:
        if t.name == activity:
            #store whihc tokens of which type in in places
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
    return new_state

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
    return tuple(stored_trace)

def enumerate_ocpn(ocpn):
    initial_state = initialize_search(ocpn)
    trace_set = set()
    state_hashes = set()
    #could be extended with acheck for already added
    state_queue = []
    state_queue.append(initial_state)
    dfs = 0
    while dfs < len(state_queue):
        state=state_queue[dfs]
        en_act= get_enabled_activities(ocpn, state)
        #print(en_act)
        for act in en_act:
            #check here
            next_state = get_next_state(ocpn, state, act)
            #if a loop is detected do not follow that
            trace_seq = [s[0] for s in next_state[1]]
            if any([v>1 for v in {i:trace_seq.count(i) for i in trace_seq}.values()]):
                continue
            next_state_string = state_to_string(next_state)
            if next_state_string not in state_hashes:
                state_hashes.add(next_state_string)
                state_queue.append(next_state)
        #print(state_queue)

        if len(en_act) == 0:
            trace_set.add(store_trace(state, len(trace_set)))#tuple(state[1]))
        dfs+=1
        if dfs % 1000 == 0:
            print(dfs)

    return trace_set