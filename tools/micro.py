import gensim
import conceptnet as cn
from nltk.corpus import wordnet as wn
import random
import sys

#w2v = gensim.models.Word2Vec.load_word2vec_format('gn.bin',binary=True)
c = cn.ConceptNet()

def baseWord(word):
	while True:
		last = word
		word = wn.morphy(word)
		if last == word:
			return word

def comesBefore(word):
	return c.getIncoming(word,"Causes") + c.getIncoming(word,"HasSubevent") + c.getOutgoing(word,"HasPrerequisite")

def comesBeforeId(id):
	return c.getIdIncoming(id,"Causes") + c.getIdIncoming(id,"HasSubevent") + c.getIdOutgoing(id,"HasPrerequisite")

def pickSome(l, n, noun, verb):
	ret = []
	dontMatch = [noun,verb]
	while len(ret) < n:
		c = random.choice(l)
		for i in dontMatch:
			if baseWord(i) == baseWord(c):
				continue
		ret.append(c)
		dontMatch.append(c)
		
	return ret

def firstCharUp(s):
	return s[0].upper() + s[1:]

def doIt(noun,verbi):
	verb = baseWord(verbi)

	before = comesBefore(verb)
	choices = []
	for x in before:
		for y in comesBeforeId(x[0]):
			if len(y[1].split()) == 1:
				choices.append(y[1])
	print ". ".join([firstCharUp(x) for x in pickSome(choices, 3, noun, verb)])+". "+random.choice(["A","The"])+" "+noun+" "+verbi+"."

noun = sys.argv[1]
verbi = sys.argv[2]

doIt(noun, verbi)