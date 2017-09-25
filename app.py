from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import numpy as np
import sys
from nltk.stem.porter import PorterStemmer
from scipy.spatial import distance

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('w2')
parser.add_argument('w1')
parser.add_argument('topic')
parser.add_argument('topics')
parser.add_argument('w')
parser.add_argument('n')
parser.add_argument('miniD')
parser.add_argument('m')

print 'Reading ...'
indices = {}
words = []
vector = []
ps = PorterStemmer()

f = open(sys.argv[1])
for w in f:
    words.append(w.strip())
f.close()

f = open(sys.argv[2])
for line in f:
    vector.append(np.array(line.split(' ')).astype(np.float))
f.close()


for i in range(len(words)):
    indices[words[i]] = i

print 'Reading finishes!'

def isExist(w):
    if w in indices:
        return True
    else:
        return False

def cosine(v1, v2):
    return np.dot(v1, v2) / (np.sqrt(np.sum(v1 ** 2)) * np.sqrt(np.sum(v2 ** 2)))

def cosine_distances(v1,v2):
    return 1 - cosine(v1, v2)

def getDistance_cosine(w1, w2, isStem=True):
    if w1 == w2:
        return 0.0
    if isStem:
        w1 = str(ps.stem(w1)).lower().strip()
        w2 = str(ps.stem(w2)).lower().strip()
    if w1 not in indices or w2 not in indices:
        return 1.0
    v1 = vector[indices[w1]]
    v2 = vector[indices[w2]]
    return cosine_distances(v1, v2)


def getDistance_euclidean(w1, w2, isStem=True):
    if w1 == w2:
        return 0.0
    if isStem:
        w1 = str(ps.stem(w1)).lower().strip()
        w2 = str(ps.stem(w2)).lower().strip()
    if w1 not in indices or w2 not in indices:
        return 1.0
    v1 = vector[indices[w1]]
    v2 = vector[indices[w2]]
    return distance.euclidean(v1, v2)

def getTopicsDis_vec_sum_eucliean(topic1, topic2):
    if topic1 == topic2:
        return 0.0
    topic1 = topic1.split(' ')
    topic2 = topic2.split(' ')
    topic1 = [str(ps.stem(w)).lower().strip() for w in topic1]
    topic2 = [str(ps.stem(w)).lower().strip() for w in topic2]
    topic1 = [w for w in topic1 if w in indices]
    topic2 = [w for w in topic2 if w in indices]
    if len(topic1) == 0 or len(topic2) == 0:
        return 1.0
    vec1 = np.array([vector[indices[w]] for w in topic1])
    vec1 = np.sum(vec1, axis=0)
    vec2 = np.array([vector[indices[w]] for w in topic2])
    vec2 = np.sum(vec2, axis=0)
    return distance.euclidean(vec1, vec2)

def getTopicsDis_miniPath(topic1, topic2, topN=5, disType='eucliean'):

    if topic1 == topic2:
        return 0.0
    topic1 = topic1.split(' ')
    topic2 = topic2.split(' ')
    topic1 = [str(ps.stem(w)).lower().strip() for w in topic1]
    topic2 = [str(ps.stem(w)).lower().strip() for w in topic2]
    topic1 = [w for w in topic1 if w in indices]
    topic2 = [w for w in topic2 if w in indices]

    if len(topic1) == 0 or len(topic2) == 0:
        return 1.0

    res = []
    minPath = []
    for i in range(len(topic1)):
        disT = np.zeros(len(topic2))
        for j in range(len(topic2)):
            if disType == 'eucliean':
                disT[j] = getDistance_euclidean(topic1[i], topic2[j], isStem=False)
            else:
                disT[j] = getDistance_cosine(topic1[i], topic2[j], isStem=False)
        minPath.append(np.min(disT))
    res.extend(sorted(minPath)[:topN])

    minPath = []
    for i in range(len(topic2)):
        disT = np.zeros(len(topic1))
        for j in range(len(topic1)):
            if disType == 'eucliean':
                disT[j] = getDistance_euclidean(topic1[j], topic2[i], isStem=False)
            else:
                disT[j] = getDistance_cosine(topic1[j], topic2[i], isStem=False)
        minPath.append(np.min(disT))
    res.extend(sorted(minPath)[:topN])

    res = np.array(res)
    return res.mean()


def getTopicsDis_count(topic1, topic2, disT='eucliean', miniD=0.6):
    if topic1 == topic2:
        return 0.0
    topic1 = topic1.split(' ')
    topic2 = topic2.split(' ')
    topic1 = [str(ps.stem(w)).lower().strip() for w in topic1]
    topic2 = [str(ps.stem(w)).lower().strip() for w in topic2]
    topic1 = [w for w in topic1 if w in indices]
    topic2 = [w for w in topic2 if w in indices]
    if len(topic1) == 0 or len(topic2) == 0:
        return 1.0
    count = 0.0
    for i in range(len(topic1)):
        for j in range(len(topic2)):
            dis = None
            if disT == 'eucliean':
                dis = getDistance_euclidean(topic1[i], topic2[j], isStem=False)
            else:
                dis = getDistance_cosine(topic1[i], topic2[j], isStem=False)
            if dis <= miniD:
                count += 1
    if count == 0:
        return 1.0
    return 1.0 / count

# def getSimilarity(w1, w2):
#     if w1 == w2:
#         return 1.0
#     w1 = str(ps.stem(w1)).lower().strip()
#     w2 = str(ps.stem(w2)).lower().strip()
#     if w1 not in indices or w2 not in indices:
#         return -1.0
#     v1 = vector[indices[w1]]
#     v2 = vector[indices[w2]]
#     return cosine(v1, v2)


def getSimilarity(w1, w2):
    w1 = str(ps.stem(w1)).lower().strip()
    w2 = str(ps.stem(w2)).lower().strip()
    if w1 not in indices or w2 not in indices:
        return 0.0
    v1 = vector[indices[w1]]
    v2 = vector[indices[w2]]
    return np.dot(v1,v2)/(np.sqrt(np.sum(v1**2)) * np.sqrt(np.sum(v2**2)))


def getTopicSimilarity(topic):
    topic = topic.split(' ')
    words = [w for w in topic if w in indices]
    if len(words) == 0:
        return  0.0
    sumS = 0.0
    count = 0.0
    for i in range(len(words)):
        for j in range(len(words)):
            sumS += getSimilarity(topic[i], topic[j])
            count += 1
    return sumS / count

def getMixureLeve(topic1, topic2):
    topic1 = topic1.split(' ')
    topic2 = topic2.split(' ')
    topic1 = [w for w in topic1 if w in indices]
    topic2 = [w for w in topic2 if w in indices]
    sum_s = 0.0
    count = 0.0
    for i in range(len(topic1)):
        for j in range(len(topic2)):
            sum_s += getSimilarity(topic1[i], topic2[j])
            count += 1
    if count == 0:
    	return 0.0
    return sum_s/count


# checked
class getWordDistance(Resource):
    def post(self):
        args = parser.parse_args()
        dis = 'eucliean'
        if args['m'] is not None: dis = args['m']
        if dis == 'cosine':
            return {'Distance': getDistance_cosine(args['w1'], args['w2'])}
        else:
            return {'Distance': getDistance_euclidean(args['w1'], args['w2'])}

class getTopicsDistance_minipath(Resource):
    def post(self):
        args = parser.parse_args()
        topics = args['topics']
        topN = 5
        if args['n'] is not None: topN = int(args['n'])
        dis = 'eucliean'
        if args['m'] is not None: dis = args['m']
        topics = topics.split(',')
        res = {}
        for i in range(len(topics)):
            for j in range(i, len(topics)):
                res[str(i)+','+str(j)] = getTopicsDis_miniPath(topics[i], topics[j], topN=topN, disType = dis)
        return res

class getTopicsDistance_count(Resource):
    def post(self):
        args = parser.parse_args()
        topics = args['topics']
        topics = topics.split(',')
        miniD = 0.6
        if args['miniD'] is not None: miniD = float(args['miniD'])
        dis = 'cosine'
        if args['m'] is not None: dis = args['m']
        res = {}
        for i in range(len(topics)):
            for j in range(i, len(topics)):
                res[str(i)+','+str(j)] = getTopicsDis_count(topics[i], topics[j], disT=dis, miniD=miniD)
        return res


class getTopicsDistance_vecsum(Resource):
    def post(self):
        args = parser.parse_args()
        topics = args['topics']
        topics = topics.split(',')
        res = {}
        for i in range(len(topics)):
            for j in range(i, len(topics)):
                res[str(i)+','+str(j)] = getTopicsDis_vec_sum_eucliean(topics[i], topics[j])
        return res

class getWordsSimilarity(Resource):
    def post(self):
        args = parser.parse_args()
        return {'Similairty': getSimilarity(args['w1'], args['w2'])}

class getTopicSimilary(Resource):
    def post(self):
        args = parser.parse_args()
        return {'Similairty': getTopicSimilarity(args['topic'])}

class getMixTopics(Resource):
    def post(self):
        args = parser.parse_args()
        topics = args['topics']
        topics = topics.split(',')
        sum_s = 0.0
        count = 0.0
        for i in range(len(topics)):
            for j in range(len(topics)):
                if i != j:
                    mixure = getMixureLeve(topics[i], topics[j])
                    if mixure != 0:
                    	sum_s += mixure
                    	count += 1
        return {'Mixure': sum_s / count}

class checkExist(Resource):
    def post(self):
        args = parser.parse_args()
        w = args['w']
        return {'Exist': isExist(w)}

api.add_resource(getWordsSimilarity, '/words')
api.add_resource(getTopicSimilary, '/topic')
api.add_resource(getMixTopics, '/mix')
api.add_resource(getWordDistance, '/dis')
api.add_resource(getTopicsDistance_minipath, '/tdis_minipath')
api.add_resource(getTopicsDistance_count, '/tdis_count')
api.add_resource(getTopicsDistance_vecsum, '/tdis_vec_sum')
api.add_resource(checkExist, '/exist')

if __name__ == '__main__':
    # app.debug = True
    app.run(port=int(sys.argv[3]), host='0.0.0.0')