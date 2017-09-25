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
    scores = {}
    for i in range(len(topics)):
        scores[i] = getTopicSimilarity(topics[i])
    sorted_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    res = {}
    res['aver'] = np.mean(scores.values())
    for n in corherenceN:
        res['C@' + str(n)] = np.array([t[1] for t in sorted_score[:n]]).mean()
    # print ','.join(res.keys())
    # print ','.join([str(i) for i in res.values()])
    return res

def getMixureLeve(topics):
    topics = {'topics':','.join(topics)}
    resp = requests.post(mix_URL, json=topics)
    return float(resp.json()['Mixure'])

def printMixPerModel(filename):
    topics = csvlib.readFileLineByLine(filename)
    return {'mixLeve': getMixureLeve(topics)}


def evaFoler(folder, keys, corherenceN=[3,5,10]):
    files = []
    for file in os.listdir(folder):
        if all([key in file for key in keys]):
            files.append(file)
            print file
    print 'File num: ' + str(len(files))
    res = {}
    res_all = {}
    for file in files:
        tmp_res = printEvaPerModel(folder + '/' + file, corherenceN=corherenceN)
        tmp_res.update(printMixPerModel(folder + '/' + file))
        josn_file = '.'.join(file.split('.')[:-2]) + '.log.json'
        josn_res = json.load(open(folder + '/' + josn_file))
        if 'bound' in josn_res: del josn_res['bound']
        if 'ro' in josn_res: del josn_res['ro']
        if 'NoTime' in file or 'beta' in file or 'gauss' in file:
            josn_res['time'] /= 10.0
        else:
            josn_res['time'] /= 50.0
        tmp_res.update(josn_res)
        for k in tmp_res.keys():
            if k in res:
                res[k] += tmp_res[k]
                res_all[k].append(tmp_res[k])
            else:
                res[k] = tmp_res[k]
                res_all[k] = [tmp_res[k]]
    for k in res.keys():
        res[k] = res[k] / float(len(files))
    return (res, res_all)

def evaFile(filename, corherenceN=[3,5,10]):
    res = printEvaPerModel(filename, corherenceN=corherenceN)
    res.update(printMixPerModel(filename))
    return res

def eva():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='inputfile', required=True)
    parser.add_argument('-c', type=str, dest='coherenceN', default='2,5,7')
    parser.add_argument('-models', default=False, dest='isModels', action='store_true')
    parser.add_argument('-keys', type=str, dest='keys')
    parser.add_argument('-file', default=False, dest='isFile', action='store_true')
    parser.add_argument('-p', default=True, dest='isPrint', action='store_true')
    parser.add_argument('-w', default=False, dest='isWords', action='store_true')
    parser.add_argument('-test', default=False, dest='isTTest', action='store_true')
    a = parser.parse_args()

    title = ['aver']
    title.extend(['C@' + n for n in a.coherenceN.split(',')])
    # title.append('mixLeve')
    title.append('sim')
    # title.append('acc')
    # title.append('precision')
    # title.append('recall')
    # title.append('f1')
    # title.append('mi')
    # title.append('time')
    if a.keys:
        if 'beta' in a.keys or 'gauss' in a.keys or 'tot' in a.keys or 'pttm' in a.keys:
            title.append('time_err')

    cnList = [int(i) for i in a.coherenceN.split(',')]

    res = None
    if a.isModels:
        res, _ = evaFoler(a.inputfile, keys=a.keys.split(','), corherenceN=cnList)
        if a.isPrint:
            print '******************RESULTS******************'
            print ',' + ','.join(title)
            print a.keys.replace(',','+') + ',' + ','.join([str(res[t]) for t in title  if t in res])
            print '*******************************************'
    if a.isFile:
        res = evaFile(a.inputfile, corherenceN=cnList)
        if a.isPrint:
            print '******************RESULTS******************'
            print ','.join(title)
            print ','.join([str(res[t]) for t in title if t in res])
            print '*******************************************'
    if a.isWords:
        print '******************RESULTS******************'
        print 'Words: ' + str(a.inputfile)
        words = a.inputfile.split(',')
        print 'Similarity: ' + str(getWordSimilarity(words[0], words[1]))
        print '*******************************************'
    if a.isTTest:
        keys1 = a.keys.split('&')[0].split(',')
        keys2 = a.keys.split('&')[1].split(',')
        _, res1 = evaFoler(a.inputfile, keys=keys1, corherenceN=cnList)
        _, res2 = evaFoler(a.inputfile, keys=keys2, corherenceN=cnList)
        ps = []
        tl = []
        for t in title:
            if t in res1 and t in res2:
                ps.append(stats.ttest_ind(res1[t],res2[t])[1])
                tl.append(t)
        print '******************RESULTS******************'
        print ',' + ','.join(tl)
        print a.keys.replace(',','+') + ',' + ','.join([str(t) for t in ps])
        print '*******************************************'

if __name__ == '__main__':
    eva()