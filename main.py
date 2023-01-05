import pandas as pd
import itertools
import evaluator as eval
from multiprocessing.dummy import Pool as ThreadPool
results = []
intercon_range = [0,0.15,0.25,0.35]
sample_range = [0.001,0.005,0.01,0.02,0.03,0.05,0.1]
num_ot_range = [2,3,4]
num_act_range = [2,3,4,5,6,7]
# intercon_range = [0]
# sample_range = [0.001]
# num_ot_range = [2,3]
# num_act_range = [2]
parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range))




pool = ThreadPool(16)
results = pool.starmap(eval.eval_params,parameter_space)
#for params in parameter_space:
#    res_dict = eval.eval_params(params)
#    results.append(res_dict)
print(results)
pd.DataFrame(results).to_csv("results.csv", index = False)