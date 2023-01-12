import pickle
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
results_dict = {}
with open('model_dict.pkl', 'rb') as file:
    results_dict = pickle.load(file)
for key in results_dict.keys():
    gviz = ocpn_vis_factory.apply(results_dict[key], parameters={'format': 'png'})
    ocpn_vis_factory.save(gviz,"models/i_"+str(key[0])+"__seq"+str(key[1])+".png")