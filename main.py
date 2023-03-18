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
intercon_range = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
sample_range = [0.01,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
num_ot_range = [2]
num_act_range = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]
chance_and = [0.0,0.3,0.5,0.8,0.95]
chance_xor = [0.0,0.2,0.5,0.8,0.95]
# intercon_range = [0,0.2]
# sample_range = [0.001]
# num_ot_range = [2]
# num_act_range = [2,3,4,5,6,7,8,9,10,11,12,9,10,11,12,9,10,11,12,9,10,11,12]
# chance_and = [0.2]
# chance_xor = [0.3]
parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))


#this is for experiments
pool = ThreadPool(4)
results = list(tqdm.tqdm(pool.imap(eval.eval_params,parameter_space),total = len(parameter_space)))
pd.DataFrame(results).to_csv("results.csv", index = False)




# #this is to generate some models
# intercon_range = [0,0.1,0.2,0.7,1.0]
# sample_range = [1]
# num_ot_range = [2]
# num_act_range = [1,2,3,4,5,6,7,8]
# chance_and = [0.0,0.3,0.5,0.8,0.95]
# chance_xor = [0.0,0.2,0.5,0.7]
# # intercon_range = [0]
# # num_act_range = [2,3,4]
# # sample_range = [1]
# # num_ot_range = [2]
# # chance_and = [0.95]
# # chance_xor = [0.3]
# parameter_space = list(itertools.product(intercon_range,sample_range,num_ot_range,num_act_range,chance_and,chance_xor))
#
#
# results_dict = eval.generate_example_models(parameter_space,interc_vals = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],con_vals = [0.01*i for i in range(0,101)],epsilon_i=0.05,epsilon_c = 0.005)
# print(results_dict)
# with open('model_dict.pkl', 'wb') as file:
#     pickle.dump(results_dict, file)



