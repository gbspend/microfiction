import word2vec
import random
import sys
import helpers as h
import punchy as p
import nounverb as nv
from penseur import penseur
import priority
from pattern.en import conjugate,INFINITIVE,article,DEFINITE,INDEFINITE
import oxdict as od

priority = reload(priority)
p = reload(p)
h = reload(h)
nv = reload(nv)

#=FORMATS===========================================
#formats take 1 string "topic" and a list of either None or string that will be "locked in" (from eval.)
# it's up to each function to intelligently handle "locks" in their respective hierarchies
# (for example, in 123action if the noun is unlocked, then ignore other locks because everything needs to change

nones = [None,None,None,None,None,None]

threeactaxis = ('plunger volcano paper the mug switches',['bridge standoff gunshot the revolution begins','eternity loneliness homecoming the tail wags'])
threeactregen = [0,1,2,5] #TODO add 4 [[],[],[],None,None,[]]
def threeaction(topic,noun,w2v,lock=nones):
	useLock = True
	#if lock[4] is not None:
	#	noun = lock[4]
	#else:
	#	noun = nv.makeNoun(topic)
	#	if noun is None:
	#		print "ABORT! NO NOUN FOR:",topic
	#		exit()
	#	useLock = False

	if lock[5] is not None and useLock:
		verb = conjugate(lock[5],INFINITIVE) + '_VB'
	else:
		verbs = nv.makeVerb(topic,[noun],1,w2v,False) #how to decide jux?
		if not verbs:
			print "NO VERB FOR:",noun
			return None
		verb = verbs[0]
		useLock = False

	# print "VERB:",verb

	bgs = ['', '', '']
	for i in range(3):
		if lock[i] is not None and useLock:
			bgs[i] = lock[i]
		else:
			b = p.get_bg(topic,[verb, noun+'_NN'],w2v) # add tag for w2v
			if b is None:
				print "NO BG WORDS FOR:",noun,verb
				return None
			bgs[i] = b
	art = h.firstCharUp(article(noun.lower(), function=random.choice([INDEFINITE,DEFINITE])))
	return ". ".join([h.firstCharUp(x) for x in bgs])+". "+art+" "+noun+" "+h.toPresent(h.strip_tag(verb))+"."

formats = [
	(threeaction, threeactaxis, threeactregen)
]

#===================================================
temp = False
#if eval likes everything, return None (not a list)
def oldeval(s):
	global temp

	if temp:
		return None
	s = h.strip(s)
	words = s.split()
	i = random.choice([0,1,2,5]) #TODO add 4
	ret = words
	print "EVAL REPLACE:",i,ret[i]
	ret[i] = None
	temp = True
	return ret

def olddoit(topic,noun,w2v,dum):
	global temp
	temp = False
	f = random.choice(formats)
	form = f[0]
	s = form(topic,noun,w2v)
	if s is None:
		print "RETRYING"
		olddoit(topic,noun,w2v,dum)
	else:
		while True:
			print "GEN:",s
			lock = oldeval(s)
			if lock is None:
				break
			s = form(topic,noun,w2v,lock)
		print s

#def score(s,axes,pens):
#	scores = [h.getSkipScore(a[0],a[1],s,pens) for a in axes]
#	return sum(scores)/len(scores)

def isBad(v):
	if not od.checkVerb(v):
		return True
	return False

def doit(topic,noun,w2v,pens,retries=0):
	#if not stanford.check():
	#	print "START THE SERVER"
	#	raw_input('Press Enter...')
	f = random.choice(formats)
	form = f[0]
	axis = f[1]
	canRegen = f[2]
	s = form(topic,noun,w2v)
	regenf = lambda lock: form(topic,noun,w2v,lock)
	scoref = lambda x: h.getSkipScores(axis[0],axis[1][0],axis[1][1],x,pens)
	if s is None or isBad(h.getV(s)):
		if retries > 20:
			return None
		print "RETRYING"
		return doit(topic,noun,w2v,pens,retries+1)
	else:
		#instead of just randomly genning one story, randomly gen one for each verb (species) to get started?
		best = priority.best(s,regenf,canRegen,scoref)[0]
		raw = h.strip(best).split()[:3]
		notraw = best.split()
		best = ". ".join([h.firstCharUp(h.makePlural(r)) for r in raw])+". "+" ".join(notraw[3:])
		print best,"\n"
		return best

if __name__ == "__main__":
	topic = sys.argv[1]
	if '_' not in topic:
		print "Make sure to tag topic"
		exit()
	noun = sys.argv[2]
	w2v = word2vec.load('data/tagged.bin')
	#w2v = gensim.models.Word2Vec.load_word2vec_format('../gn.bin',binary=True)
	#w2v.init_sims(replace=True)
	print "Word2Vec Loaded"
	pens = penseur.Penseur()
	print "Penseur Loaded"

	doit(topic,noun,w2v,pens)
