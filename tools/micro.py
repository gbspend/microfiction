import gensim
import conceptnet as cn
from nltk.corpus import wordnet as wn
import random
import sys

#w2v = gensim.models.Word2Vec.load_word2vec_format('gn.bin',binary=True)
#w2v.init_sims(replace=True)
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

def synName(s):
	return s.name().split('.')[0]

def dist(s1, s2):
	if len(s1) > len(s2):
		s1, s2 = s2, s1

	distances = range(len(s1) + 1)
	for i2, c2 in enumerate(s2):
		distances_ = [i2+1]
		for i1, c1 in enumerate(s1):
			if c1 == c2:
				distances_.append(distances[i1])
			else:
				distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
		distances = distances_
	return distances[-1]

def nounify(verb_word):
	set_of_related_nouns = set()

	for lemma in wn.lemmas(wn.morphy(verb_word, wn.VERB), pos="v"):
		for related_form in lemma.derivationally_related_forms():
			for synset in wn.synsets(related_form.name(), pos=wn.NOUN):
				set_of_related_nouns.add(synset)

	return set_of_related_nouns

def toNoun(w):
	for ss in wn.synsets(w):
		if ss.pos() == 'n':
			return w
	related = nounify(w)
	best = w
	mindist = 100000
	for r in related:
		s = synName(r)
		d = dist(s,w)
		if d < mindist:
			mindist = d
			best = s
	return best

def pickSome(l, n, noun, verb):
	ret = []
	dontMatch = [baseWord(noun),baseWord(verb)]
	while len(ret) < n:
		c = random.choice(l)
		if baseWord(c) in dontMatch:
			continue
		ret.append(toNoun(c))
		dontMatch.append(baseWord(c))
		
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