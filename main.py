import pandas as pd
import itertools
import evaluator as eval
from multiprocessing.dummy import Pool as ThreadPool
import tqdm
import warnings
warnings.filterwarnings("ignore")
results = []
intercon_range = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
sample_range = [0.001,0.005,0.01,0.02,0.03,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
num_ot_range = [2]
#num_act_range = [2,3,3,4,4,5,5,6]
num_act_range = [3,4,5,6]
#chance_and = [0.1,0.3,0.5]
#chance_xor = [0.2,0.4,0.6]
chance_and = [0.2,0.5]
chance_xor = [0.3,0.6]
# intercon_range = [0.1,0.3,0.5]
# sample_range = [0.001,0.01]
# num_ot_range = [2,3]
# num_act_range = [2,3,4]
parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))

#TODO: add total number of traces to skip model- DONE
#Todo: interconnectedness range higher - DONE
#todo: more high completeness mocels - Probably Done
#todo: equalize ranges



pool = ThreadPool(16)
results = list(tqdm.tqdm(pool.imap(eval.eval_params,parameter_space),total = len(parameter_space)))
#for params in parameter_space:
#    res_dict = eval.eval_params(params)
#    results.append(res_dict)
#print(results)
pd.DataFrame(results).to_csv("results.csv", index = False)