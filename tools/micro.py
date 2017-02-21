import gensim
import conceptnet as cn
from nltk.corpus import wordnet as wn
import random
import sys

#w2v = gensim.models.Word2Vec.load_word2vec_format('gn.bin',binary=True)
#w2v.init_sims(replace=True)
#print "Word2Vec Loaded"
c = cn.ConceptNet()

def baseWord(word):
	while True:
		last = word
		word = wn.morphy(word)
		if word is None:
			return last
		if last == word:
			return word

def comesBefore(word):
	return c.getIncoming(word,"Causes") + c.getIncoming(word,"HasSubevent") + c.getOutgoing(word,"HasPrerequisite")

def comesBeforeId(id):
	return c.getIdIncoming(id,"Causes") + c.getIdIncoming(id,"HasSubevent") + c.getIdOutgoing(id,"HasPrerequisite")

def synName(s):
	return s.lemma_names()[0]

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
	
	m = wn.morphy(verb_word, wn.VERB)
	if m is not None:
		for lemma in wn.lemmas(m, pos="v"):
			for related_form in lemma.derivationally_related_forms():
				for synset in wn.synsets(related_form.name(), pos=wn.NOUN):
					if not synName(synset)[0].isupper(): #filters out proper nouns
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
	dontMatch = [baseWord(noun),baseWord(verb),baseWord(toNoun(verb))]
	while len(ret) < n:
		c = random.choice(l)
		if baseWord(c) in dontMatch:
			continue
		ret.append(toNoun(c))
		dontMatch.append(baseWord(c))
		
	return ret

def firstCharUp(s):
	return s[0].upper() + s[1:]

def w2vDist(x,y):
	if x not in w2v or y not in w2v:
		return 0
	return w2v.similarity(x,y)

def nvCompare(word, noun, verb):
	return w2vDist(word, noun) + w2vDist(word, verb)

def doIt(noun,verbi):
	verb = baseWord(verbi)

	before = comesBefore(verb)
	choices = []
	for x in before:
		for y in comesBeforeId(x[0]):
			curr = y[1]
			if len(curr.split()) == 1:
				ss = wn.synsets(curr)
				found = False
				for s in ss:
					if synName(s) == verb:
						found = True
				if not found:
					choices.append(curr)
	choices = list(set(choices)) #removes duplicates

#	ordered = sorted(choices, key=lambda x: nvCompare(x, noun, verb), reverse=True)
#	print ordered[:10]
	print ". ".join([firstCharUp(x) for x in pickSome(choices, 3, noun, verb)])+". "+random.choice(["A","The"])+" "+noun+" "+verbi+"."

if __name__ == "__main__":
	noun = sys.argv[1]
	verbi = sys.argv[2]

	doIt(noun, verbi)
