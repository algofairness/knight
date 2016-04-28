#!/usr/bin/python

# Tony Tuttle
# March 2016
# tuttle.tony@gmail.com

import os.path
import time
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka.filters import Filter
from weka.classifiers import Classifier
import weka.plot.graph as graph
import sys

def write_file(d, path):
    with open(path, 'w') as f:
        f.write(",".join(k for k in d.keys()) + "\n")
        f.write(",".join(str(v) for v in d.values()) + "\n")

def run_classifier(path, prot, sel, cols, prot_vals, beta):
        
    DIs = dict()
    jvm.start()

    for i in range(len(cols)-1):
        loader = Loader(classname="weka.core.converters.CSVLoader")
        data = loader.load_file(path)
    
        # remove selected attribute from the data
        # NOTE: options are ONE indexed, not ZERO indexed
        remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", \
                        options=["-R", str(sel[2]+1)])
        remove.inputformat(data)
        data = remove.filter(data)

        # if running for only one attribue, remove all others (except protected)
        if i > 0:
            for j in range(1, prot[2]+1):
                if i != j:
                    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", \
                                    options=["-R", ("1" if i>j else "2")])
                    remove.inputformat(data)
                    data = remove.filter(data)

        # set prot attribute as Class attribute
        data.class_is_last()
        
        # run classifier
        cls = Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        cls.build_classifier(data)
    
        # count the number of each combination
        pos_and_pred = float(0.0)
        pos_and_not_pred = float(0.0)
        neg_and_pred = float(0.0)
        neg_and_not_pred = float(0.0)
        for ind, inst in enumerate(data):
            if cls.classify_instance(inst):
                if prot_vals[ind] == prot[1]:
                    pos_and_pred += 1
                else:
                    neg_and_pred += 1
            else:
                if prot_vals[ind] == prot[1]:
                    pos_and_not_pred += 1
                else:
                    neg_and_not_pred += 1

        # calculate DI
        BER = ((pos_and_not_pred / (pos_and_pred + pos_and_not_pred)) + \
               (neg_and_pred / (neg_and_pred + neg_and_not_pred))) * 0.5
        if BER > 0.5:
            BER = 1 - BER
        DI = 1 - ((1 - 2 * BER) / (beta + 1 - 2 * BER))

        if i == 0: # consider changing this to a 'code word' instead of 'all'
            DIs["all"] = DI
        else:
            DIs[cols[i-1]] = DI

    jvm.stop()

    return DIs
    #write_file(DIs, out)


def read_file(path, prot, sel):

    # **********************************************************************
    # ******************************** TODO ********************************
    # ** change this so it rearranges the columns of the csv to ensure *****
    # ** that the protected column is penultimate and the selected column **
    # ** is last ***********************************************************
    # **********************************************************************

    # open the file and look for match for protected and selected attributes
    imc = 0
    saimc = 0
    protected_vals = []
    with open(path, 'r') as f:
        col_names = f.readline().rstrip().split(',')
        
        if not prot[0] in col_names:
            raise ValueError("Protected attribute " + prot[0] + " not found.")
        prot.append(col_names.index(prot[0]))
        if not sel[0] in col_names:
            raise ValueError("Selected attribute " + sel[0] + " not found.")
        sel.append(col_names.index(sel[0]))
        
        # calculate:
        # > imc = |minority_attr|
        # > saimc = |minority_attr ^ selected_attr|
        # > beta = saimc / imc
        # > BERt = 0.5 - beta/8
        for l in f:
            l_lst = l.rstrip().split(',')
            protected_vals.append(l_lst[prot[2]])
            if l_lst[prot[2]] == prot[1]:
                imc += 1
                if l_lst[sel[2]] == sel[1]:
                    saimc += 1

    beta = 0 if imc == 0 else float(saimc) / float(imc)

    return col_names, beta, protected_vals


# args to the script are:
# 1) path to input csv file
# 2) name of protected attribute (pulled directly from user input csv file)
# 3) 'positive' value of the protected attribute we are interested in
# 4) name of selected attribute (pulled directly from user input csv file)
# 5) 'positive' value of the selected attribute we are interested in
# 6) (?)OPTIONAL: path to write output csv file to 

if len(sys.argv) < 6:
    raise ValueError("Missing arguments")

in_path = sys.argv[1]
protected = [sys.argv[2], sys.argv[3]]
selected = [sys.argv[4], sys.argv[5]]
out_path = "out_files/out.csv"

if len(sys.argv) >=6:
    out_path = sys.argv[6]

# verify path is good
if not os.path.isfile(in_path):
    raise IOError("File not found: " + in_path + " " + sys.path[0])

col_names, beta, protected_vals = read_file(in_path, protected, selected)

#return run_classifier(in_path, protected, selected, col_names, protected_vals, beta)
DIs = run_classifier(in_path, protected, selected, col_names, protected_vals, beta)

write_file(DIs, out_path)
