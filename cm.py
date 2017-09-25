import requests
from myTools import csvLib
import numpy as np
import os
import argparse
from scipy import stats
import json

topic_URL = "http://130.209.249.32:9804/topic"
word_URL = "http://130.209.249.32:9804/words"
mix_URL = "http://130.209.249.32:9804/mix"

csvlib = csvLib()

def getWordSimilarity(w1, w2):
    words = {'w1':w1, 'w2':w2}
    resp = requests.post(word_URL,json=words)
    return float(resp.json()['Similairty'])

def getTopicSimilarity(topic_s):
    topic ={'topic':topic_s}
    resp = requests.post(topic_URL, json=topic)
    return float(resp.json()['Similairty'])

def printEvaPerModel(filename, corherenceN=[3,5,10]):
    topics = csvlib.readFileLineByLine(filename)
    scores = {i: getTopicSimilarity(topics[i]) for i in range(len(topics))}
    sorted_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    res = {'C@'+str(n): np.array([t[1] for t in sorted_score[:n]]).mean() for n in corherenceN}
    res['aver'] = np.mean(scores.values())
    return res

def getMixureLeve(topics):
    topics = {'topics':','.join(topics)}
    resp = requests.post(mix_URL, json=topics)
    return float(resp.json()['Mixure'])

def printMixPerModel(filename):
    topics = csvlib.readFileLineByLine(filename)
    return {'mixLeve': getMixureLeve(topics)}

def evaFoler(folder, corherenceN=[3,5,10]):
    files = [file for file in os.listdir(folder)]
    print 'File num: ' + str(len(files))
    res = {}
    res_all = {}
    for file in files:
        tmp_res = printEvaPerModel(folder + '/' + file, corherenceN=corherenceN)
        tmp_res.update(printMixPerModel(folder + '/' + file))
        for k in tmp_res:
            if k in res:
                res[k] += tmp_res[k]
                res_all[k].append(tmp_res[k])
            else:
                res[k] = tmp_res[k]
                res_all[k] = [tmp_res[k]]
    for k in res:
        res[k] = res[k] / float(len(files))
    return res, res_all

def evaFile(filename, corherenceN=[3,5,10]):
    res = printEvaPerModel(filename, corherenceN=corherenceN)
    res.update(printMixPerModel(filename))
    return res

def eva():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='inputfile', required=True)
    parser.add_argument('-c', type=str, dest='coherenceN', default='2,5,7')
    parser.add_argument('-models', default=False, dest='isModels', action='store_true')
    parser.add_argument('-file', default=False, dest='isFile', action='store_true')
    a = parser.parse_args()

    title = ['aver']
    title.extend(['C@' + n for n in a.coherenceN.split(',')])
    title.append('sim')
    cnList = [int(i) for i in a.coherenceN.split(',')]

    if a.isModels:
        res, _ = evaFoler(a.inputfile, corherenceN=cnList)
        print '******************RESULTS******************'
        print ',' + ','.join(title)
        print ' ,' + ','.join([str(res[t]) for t in title  if t in res])
        print '*******************************************'
    if a.isFile:
        res = evaFile(a.inputfile, corherenceN=cnList)
        print '******************RESULTS******************'
        print ','.join(title)
        print ','.join([str(res[t]) for t in title if t in res])
        print '*******************************************'

if __name__ == '__main__':
    eva()