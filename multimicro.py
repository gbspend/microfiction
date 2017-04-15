import sys
import random

topic = sys.argv[1]
if '_' not in topic:
	print "Make sure to tag topic"
	exit()
#noun = sys.argv[2]
num = int(sys.argv[2])
ns=[
"cowboy",
"astronaut",
"clown",
"dinosaur",
"doctor",
"king",
"queen",
"child",
"spy",
"magician",
"dog",
"professor",
"mechanic",
"knight",
"wizard",
"pilot",
"solider",
"policeman",
"woman",
"man",
"cat",
"plumber",
"coach",
"reporter",
"robber",
"judge",
"artist",
"politician",
"hobo",
"gangster",
"trainer",
"librarian",
"student",
"computer",
"band",
"writer",
"actor",
"manager",
"prince",
"princess",
"officer",
"singer",
"secretary",
"bishop",
"horse",
"fish",
"guard",
"teacher",
"poet",
"driver",
"baby",
"lawyer",
"architect",
"senator",
"musician",
"hunter",
"bachelor",
"tourist",
"hero",
"pioneer",
"citizen",
"scientist",
"reporter",
"patient",
"monster",
"pirate",
"ninja",
"detective",
"activist",
"farmer",
"philosopher",
"celebrity",
"referee",
"widow",
"quarterback",
"witch",
"dancer",
"baby",
"wrestler",
"nurse",
"surgeon",
"villain",
"team",
"sailor",
"undergraduate",
"samurai"
]

import word2vec
from penseur import penseur
import micro
w2v = word2vec.load('data/tagged.bin')
print "Word2Vec Loaded"
pens = penseur.Penseur()
print "Penseur Loaded"


import micro
r = []
for i in xrange(num):
	noun = random.choice(ns)
	r.append(micro.doit(topic,noun,w2v,pens))

print "RESULTS"
for s in r:
	print s
