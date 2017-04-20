import random
import conceptnet as cn
from nltk.corpus import wordnet as wn
import datamuse as dm
import sys
import helpers as h
import oxdict as od
import pattern.en as pen

def pickOne(l):
	i = h.weighted_choice(l)
	return l.pop(i)[0]

#=============================================

cache = {}

#adds every element of list a to set s
def addAll(s,a):
	for i in a:
		s.add(i)

#"parents" in a list of strings (assumed to be nouns)
#returns list of strings with [0-num] elements (in case it can't find that many)
def makeVerb(topic, parents, num, w2v, jux=False):
	key = topic + "".join(parents)
	if key in cache:
		final = cache[key]
	else:
		choices = set()
		stripped_topic = h.strip_tag(topic)
		for p in parents:
			for r in ['trg']: #bga is terrible
				addAll(choices,h.pos([x[0] for x in dm.query(dm.related(r,p),dm.topics(stripped_topic))],'v'))
			for r in ['CapableOf','UsedFor','Desires']:
				for phrase in [x[1] for x in cn.getOutgoing(p,r)]:
					addAll(choices,h.pos(phrase.split(),'v'))
		final = list(choices)

		if jux:
			temp = set()
			for w in final:
				addAll(temp,h.pos([x[0] for x in dm.query(dm.related('ant',w),dm.topics(stripped_topic))],'v'))
				for phrase in [x[1] for x in cn.getOutgoing(w,'Antonym')]:
					addAll(choices,h.pos(phrase.split(),'v'))

			final = list(temp)

		#word2vec sort
		parents = [x+'_NN' for x in parents]
		relations = parents + [topic]

		#word2vec threshold

		final = [pen.conjugate(x)+'_VB' for x in final]
		final = h.w2vWeightsListNew(final,relations,w2v)
		if len(final) > 20:
			final = final[:-len(final)/5]
			
		cache[key] = final

	if len(final) < 1:
		print "VERB FINAL IS EMPTY:",topic,parents,num,list(choices)
	#just in case
	if len(final) <= num:
		return [x[0] for x in final]
	return [pickOne(final) for x in range(num)]


if __name__ == "__main__":
	noun = sys.argv[1]
	print [str(wn.morphy(x)) for x in makeVerb('',noun,5)]
	print [str(wn.morphy(x)) for x in makeVerb('',noun,5,True)]
