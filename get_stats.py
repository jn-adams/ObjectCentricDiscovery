from copy import deepcopy

from ocpa.objects.log.ocel import OCEL
import ocpa

import net_generator as gen
import net_enumerator as en

def get_interconnectivity(ocpn, count_start_and_end = False):
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
    return sum(amount_extra)/len(amount_extra)

