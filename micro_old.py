import gensim
import conceptnet as cn
from nltk.corpus import wordnet as wn
import random
import sys
import helpers as h

#w2v = gensim.models.Word2Vec.load_word2vec_format('gn.bin',binary=True)
#w2v.init_sims(replace=True)
#print "Word2Vec Loaded"

def comesBefore(word):
	return cn.getIncoming(word,"Causes") + cn.getIncoming(word,"HasSubevent") + cn.getOutgoing(word,"HasPrerequisite")

def comesBeforeId(id):
	return cn.getIdIncoming(id,"Causes") + cn.getIdIncoming(id,"HasSubevent") + cn.getIdOutgoing(id,"HasPrerequisite")



def pickSome(l, n, noun, verb):
	ret = []
	dontMatch = [h.baseWord(noun),h.baseWord(verb),h.baseWord(h.toNoun(verb))]
	while len(ret) < n:
		c = random.choice(l)
		if h.baseWord(c) in dontMatch:
			continue
		ret.append(h.toNoun(c))
		dontMatch.append(h.baseWord(c))
		
	return ret

def w2vDist(x,y):
	if x not in w2v or y not in w2v:
		return 0
	return w2v.similarity(x,y)

def nvCompare(word, noun, verb):
	return w2vDist(word, noun) + w2vDist(word, verb)

def doIt(noun,verbi,n):
	verb = h.baseWord(verbi)

	print "building choices"
	before = comesBefore(verb)
	choices = [] #fill choices with "before" initially?
	for x in before:
		for y in comesBeforeId(x[0]):
			curr = y[1]
			if len(curr.split()) == 1:
				ss = wn.synsets(curr)
				found = False
				for s in ss:
					if h.synName(s) == verb:
						found = True
				if not found:
					choices.append(curr)
	choices = list(set(choices)) #removes duplicates
	print "done"
	#the idea here was to sort them by how they're related to the noun/verb and then... chop off the bottom 1/4?
#	ordered = sorted(choices, key=lambda x: nvCompare(x, noun, verb), reverse=True)
#	print ordered[:10]
	while n > 0:
		print ". ".join([h.firstCharUp(x) for x in pickSome(choices, 3, noun, verb)])+". "+random.choice(["A","The"])+" "+noun+" "+verbi+"."
		n-=1

if __name__ == "__main__":
	noun = sys.argv[1]
	verbi = sys.argv[2]

	doIt(noun, verbi,3)
