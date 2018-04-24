from config import *

os.system("java -Xmx"+max_memory+"g -Xms"+min_memory+"g -jar "+data_path+"/training/RankLib.jar -train "+dataset_path+"train.txt -validate "+dataset_path+"val.txt -test "+dataset_path+"test.txt -ranker 6 -metric2t "+optimization+" -sparse -save "+dataset_path+"model.m")
