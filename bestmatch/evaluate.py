from config import *

def evaluate(afterTraining):
    load = ""
    if afterTraining:
        load = "-load "+dataset_path+"model.m "
    os.system("java -Xmx"+max_memory+"g -Xms"+min_memory+"g -jar "+data_path+"/training/RankLib.jar "+load+"-test "+dataset_path+"test.txt -metric2t "+optimization+" -sparse")
