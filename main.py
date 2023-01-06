import pandas as pd
import itertools
import evaluator as eval
from multiprocessing.dummy import Pool as ThreadPool
import tqdm
import warnings
warnings.filterwarnings("ignore")
results = []
intercon_range = [0,0.075,0.1,0.15,0.2,0.25,0.35]
sample_range = [0.001,0.005,0.01,0.02,0.03,0.05,0.1,0.15,0.2,0.25,0.3]
num_ot_range = [2]
num_act_range = [2,3,3,4,4,5,5,6]
chance_and = [0.1,0.3,0.5]
chance_xor = [0.2,0.4,0.6]
# intercon_range = [0.1,0.3,0.5]
# sample_range = [0.001,0.01]
# num_ot_range = [2,3]
# num_act_range = [2,3,4]
parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))




pool = ThreadPool(16)
results = list(tqdm.tqdm(pool.imap(eval.eval_params,parameter_space),total = len(parameter_space)))
#for params in parameter_space:
#    res_dict = eval.eval_params(params)
#    results.append(res_dict)
#print(results)
pd.DataFrame(results).to_csv("results.csv", index = False)