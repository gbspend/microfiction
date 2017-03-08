import gensim
import conceptnet as cn
from nltk.corpus import wordnet as wn
import random
import sys
import helpers as h
import punchy as p
import nounverb as nv

#=FORMATS===========================================
#formats take 1 string "topic" and a list of either None or string that will be "locked in" (from eval.)
# it's up to each function to intelligently handle "locks" in their respective hierarchies
# (for example, in 123action if the noun is unlocked, then ignore other locks because everything needs to change

nones = [None,None,None,None,None,None]

def threeaction(topic,w2v,lock=nones):
	useLock = True
	if lock[4] is not None:
		noun = lock[4]
	else:
		noun = nv.makeNoun(topic)
		useLock = False

	if lock[5] is not None and useLock:
		verb = lock[5]
	else:
		verb = nv.makeVerb(topic,[noun],1,False)[0] #how to decide jux?
		useLock = False

	bgs = ['', '', '']
	for i in range(3):
		if lock[i] is not None and useLock:
			bgs[i] = lock[i]
		else:
			bgs[i] = p.get_bg(topic,[verb],w2v)

	return ". ".join([h.firstCharUp(x) for x in bgs])+". "+random.choice(["A","The"])+" "+noun+" "+verb+"."

formats = [
	threeaction
]

#===================================================
temp = False
#if eval likes everything, return None (not a list)
def eval(s):
	global temp

	if temp:
		return None
	s = h.strip(s)
	words = s.split()
	i = random.randint(0,5)
	ret = words
	ret[i] = None
	temp = True
	return ret

def doit(topic,w2v):
	form = random.choice(formats)
	s = form(topic,w2v)
	while True:
		print "GEN:",s
		lock = eval(s)
		if lock is None:
			break
		s = form(topic,w2v,lock)
	print s

if __name__ == "__main__":
	w2v = gensim.models.Word2Vec.load_word2vec_format('gn.bin',binary=True)
	w2v.init_sims(replace=True)
	print "Word2Vec Loaded"
	topic = sys.argv[1]
	
