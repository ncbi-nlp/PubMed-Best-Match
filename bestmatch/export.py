from config import *
from xml.etree import ElementTree
import json

featurenb = 179

def xmltojson(xml):
    featureList = range(1,featurenb+1)
    jsonModel = {"class":"org.apache.solr.ltr.model.MultipleAdditiveTreesModel","name":"model","store": "_DEFAULT_","features":[],"params":{"trees": []}}
    for feature in featureList:
        jsonModel["features"].append({"name":str(feature)})
    trees = ElementTree.fromstring(xml)
    for tree in trees:
        split = tree.find("split")
        tObject = {"weight":str(tree.get("weight"))}
        tObject["root"] = recursiveTraversal(split)
        jsonModel["params"]["trees"].append(tObject)
    return jsonModel

def recursiveTraversal(node):
    thisNode = {}
    featureNode = node.find("feature")
    if featureNode == None:
        thisNode["value"] = str(node.find("output").text.strip())
    else:
        thisNode["feature"] = featureNode.text.strip()
        thisNode["threshold"] = str(node.find("threshold").text.strip())
        leftNode = node.find("split[@pos='left']")
        rightNode = node.find("split[@pos='right']")
        if leftNode:
            thisNode["left"] = recursiveTraversal(leftNode)
        if rightNode:
            thisNode["right"] = recursiveTraversal(rightNode)
    return thisNode

xmlModelPath = dataset_path+"model.m"
with open(xmlModelPath) as f:
    xmlModel = ""
    for line in f:
        if not line.startswith("#"):
            xmlModel += line

pyModel = xmltojson(xmlModel)
print("The model contains "+str(len(pyModel["params"]["trees"]))+" trees.")
with open(xmlModelPath.replace(".m", ".json"), 'w') as f:
    json.dump(pyModel, f, indent=4)
print("Model saved in JSON format.")
