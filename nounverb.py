import random
import conceptnet as cn
from nltk.corpus import wordnet as wn
import datamuse as dm
import sys
import helpers as h

#TODO
#ignores parents, num and juxtaposition for now
def makeNoun(topic):
	return "cowboy"

#=============================================

#adds every element of list a to set s
def addAll(s,a):
	for i in a:
		s.add(i)

#TODO: doesn't take topic into account
#"parents" in a list of strings (assumed to be nouns)
#returns list of strings with [0-num] elements (in case it can't find that many)
def makeVerb(topic, parents, num, jux=False):
	choices = set()
	for p in parents:
		for r in ['trg']: #bga is terrible
			addAll(choices,h.pos([x[0] for x in dm.query(dm.related(r,p),dm.topics(topic))],'v'))
		for r in ['CapableOf','UsedFor','Desires']:
			for phrase in [x[1] for x in cn.getOutgoing(p,r)]:
				addAll(choices,h.pos(phrase.split(),'v'))
	final = list(choices)

	if jux:
		temp = set()
		for w in final:
			addAll(temp,h.pos([x[0] for x in dm.query(dm.related('ant',w),dm.topics(topic))],'v'))
			for phrase in [x[1] for x in cn.getOutgoing(w,'Antonym')]:
				addAll(choices,h.pos(phrase.split(),'v'))

		final = list(temp)

	#word2vec threshold?

	#just in case
	if len(final) <= num:
		return final

	ret = []
	while True:
		next = random.choice(final)
		if next not in ret:
			ret.append(next)
		if len(ret) >= num:
			return ret


if __name__ == "__main__":
	noun = sys.argv[1]
	print [str(wn.morphy(x)) for x in makeVerb('',noun,5)]
	print [str(wn.morphy(x)) for x in makeVerb('',noun,5,True)]
	

























