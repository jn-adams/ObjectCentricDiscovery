import pandas as pd
import itertools
import evaluator as eval
from multiprocessing.dummy import Pool as ThreadPool
import tqdm
import warnings
warnings.filterwarnings("ignore")
results = []
import pickle
#for experiments
intercon_range = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
sample_range = [0.001,0.005,0.01,0.02,0.03,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
num_ot_range = [2]
num_act_range = [2,2,2,3,3,3,3,4,4,4,5,6,2,2,2,3,3,3,3,4,4,4,5,6]
chance_and = [0.0,0.2,0.5,0.8,0.95]
chance_xor = [0.0,0.3,0.6,0.8,0.95]
# intercon_range = [0.1,0.3,0.5]
# sample_range = [0.001,0.01]
# num_ot_range = [2,3]
# num_act_range = [2,3,4]
parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))

#TODO: add total number of traces to skip model- DONE
#Todo: interconnectedness range higher - DONE
#todo: more high completeness mocels - Probably Done
#todo: equalize ranges
#NEW
#TODO: Only one size of activities!!!
#TODO: Change the added and to attach directly to the previous transition and the next transition instead of adding splits

#this is for experiments
pool = ThreadPool(16)
results = list(tqdm.tqdm(pool.imap(eval.eval_params,parameter_space),total = len(parameter_space)))
pd.DataFrame(results).to_csv("results.csv", index = False)








# intercon_range = [0,0.1,0.3,0.5,0.8,1.0]
# sample_range = [1]
# num_ot_range = [2]
# num_act_range = [2,2,2,3,3,3,3,4,4,4,5,6,2,2,2,3,3,3,3,4,4,4,5,6]
# chance_and = [0.0,0.2,0.5,0.8,0.95]
# chance_xor = [0.0,0.3,0.6,0.8,0.95]
# # intercon_range = [0]
# # num_act_range = [2,3,4]
# # sample_range = [1]
# # num_ot_range = [2]
# # chance_and = [0.95]
# # chance_xor = [0.3]
# parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))
#
# #TODO: add total number of traces to skip model- DONE
# #Todo: interconnectedness range higher - DONE
# #todo: more high completeness mocels - Probably Done
# #todo: equalize ranges
# #NEW
# #TODO: Only one size of activities!!!
# #TODO: Change the added and to attach directly to the previous transition and the next transition instead of adding splits
#
# #this is for experiments
# # pool = ThreadPool(16)
# # results = list(tqdm.tqdm(pool.imap(eval.eval_params,parameter_space),total = len(parameter_space)))
# # pd.DataFrame(results).to_csv("results.csv", index = False)
#
# results_dict = eval.generate_example_models(parameter_space,interc_vals = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],con_vals = [0.01*i for i in range(0,100)],epsilon_i=0.05,epsilon_c = 0.005)
# print(results_dict)
# with open('model_dict.pkl', 'wb') as file:
#     pickle.dump(results_dict, file)



