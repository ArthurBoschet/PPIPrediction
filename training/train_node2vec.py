from linkpred.node2vec_link_pred import Node2VecLinkPredModel
from training.train import train

#Pytorch
import torch

#ray
import ray
from ray.air import session
from ray.tune.integration.wandb import (
    wandb_mixin,
)

@wandb_mixin
def train_node2vec(config):

  #print which device is being used to the terminal
  device = config["device"]
  print(f"\nThe device is {device}\n")

  datasets = ray.get(config['datasets_id'][config["seed"]])

  #GAT link prediction model
  model = Node2VecLinkPredModel( 
    datasets['train'][0],
    config["seed"],
    int(config["input_size"]),
    int(config["walk_length"]),
    config["p"],
    config["q"], 
    int(config["num_layers"]), 
    int(config["hidden_size"]),
    config["device"],
    dropout=config["dropout"],
    batch_size=config["batch_size"],
    directory=config["directory"],
    species=config["species"],
  ).to(config["device"])

  #print the model architecture
  print(model)

  #optimizer setup
  optimizer = torch.optim.SGD(model.parameters(), lr=config['lr'], momentum=config['momentum'], weight_decay=config['weight_decay'])

  #training
  score_val = train(model, config['dataloaders_id'][config["seed"]], optimizer, config, verbose=True)
  session.report({"auroc_validation": score_val})
  print(score_val)
  return