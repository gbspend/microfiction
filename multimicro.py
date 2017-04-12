import sys

topic = sys.argv[1]
if '_' not in topic:
	print "Make sure to tag topic"
	exit()
noun = sys.argv[2]
num = int(sys.argv[3])

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
	r.append(micro.doit(topic,noun,w2v,pens))

print "RESULTS"
for s in r:
	print s
