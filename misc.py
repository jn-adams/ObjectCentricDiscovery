import random
import pandas as pd
from ocpa.objects.log.ocel import OCEL
from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
import ocpa.objects.log.converter.versions.df_to_ocel as obj_converter
import ocpa.objects.log.importer.csv.versions.to_df as df_importer
import ocpa.objects.log.variants.util.table as table_utils
def sample_log(log, ratio):
    return random.sample(log,int(ratio*len(log)))

def to_OCEL(log):
    dict_list= []
    counter = 0
    ots = []
    for trace in log:
        for event in trace:
            event_dict = {}
            event_dict["event_activity"] = event[0]
            event_dict["event_timestamp"] = counter
            event_dict["event_id"] = counter
            counter+=1
            for (ot,o) in event[1]:
                event_dict[ot] = set(o)
                if ot not in ots:
                    ots.append(ot)
            dict_list.append(event_dict)
    df = pd.DataFrame(dict_list)
    df = df.applymap(lambda d: set() if pd.isnull(d) else d)
    print(df)
    parameters = {"obj_names": ots,
                  "val_names": [],
                  "act_name": "event_activity",
                  "time_name": "event_timestamp"}
    log = Table(df, parameters=parameters, object_attributes=None)
    obj = obj_converter.apply(df)
    graph = EventGraph(table_utils.eog_from_log(log))
    ocel = OCEL(log, obj, graph, parameters)
    return ocel

def compare_languages(system_log, model_log):
    system_traces = set()
    for t in system_log:
        system_traces.add(tuple([e[0] for e in t]))

    model_traces = set()
    for t in model_log:
        model_traces.add(tuple([e[0] for e in t]))

    common_traces = system_traces.intersection(model_traces)
    recall = len(common_traces)/len(system_traces)
    precision = len(common_traces)/len(model_traces)
    return recall, precision

def flatten_ocel(ocel):
    dict_list = []
    counter = 0
    for p in ocel.process_executions:
        for event in p:
            event_dict = {}
            event_dict["event_activity"] = ocel.get_value(event,"event_activity")
            event_dict["event_timestamp"] = event
            event_dict["event_id"] = event
            event_dict["pexec"] = set(["p"+str(counter)])

            dict_list.append(event_dict)
        counter += 1
    df = pd.DataFrame(dict_list)
    df = df.applymap(lambda d: set() if pd.isnull(d) else d)
    print(df)
    parameters = {"obj_names": ["pexec"],
                  "val_names": [],
                  "act_name": "event_activity",
                  "time_name": "event_timestamp"}
    log = Table(df, parameters=parameters, object_attributes=None)
    obj = obj_converter.apply(df)
    graph = EventGraph(table_utils.eog_from_log(log))
    ocel = OCEL(log, obj, graph, parameters)
    return ocel
