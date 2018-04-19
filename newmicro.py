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
import formats

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

axes = ('plunger volcano paper the mug switches',['bridge standoff gunshot the revolution begins','eternity loneliness homecoming the tail wags'])

#word, start, and end are untagged
def w2vChoices(word,start,startTag,end,endTag,w2v):
	return h.get_scholar_rels(word+startTag,[(start,end)],w2v,startTag,endTag)

#node is current node
#parent is parent node
#prev is previously generated word (remember parent -> child words are just a _relation_; prev is the word that rel will be applied to)
#force is boolean to force regen (ignore lock)
#w2v is w2v
#fillin is out var; starts as lock, fill in other words (replace if forced)
def genrec(node,parent,prev,force,w2v,fillin):
	i = node['index']
	if not force and fillin[i]:
		if parent:
			force = True #only force regen if its not the root (i.e. it has a parent)
	else:
		startTag = '_'+parent['pos']
		endTag = '_'+node['pos']
		choices = w2vChoices(prev,parent['word'],startTag,node['word'],endTag,w2v)
		cnRels = cn.getRels(parent['word'],node['word'])
		for rel in cnRels:
			choices += cn.getOutgoing(prev, rel):

		#PLEASE MAKE THIS SMARTER
		word = random.choice(choices)
		#^^^

		fillin[i]=word
	if len(node['children']):
		for child in node['children']:
			genrec(child,node,word,force,w2v,fillin)

#MUST LOCK ROOT!
def gen(fraw,w2v,lock):
	#traverse tree; if parent locked, regen all children (set a force flag)
	root = fraw['root']
	if not lock[root['index']]:
		print "ROOT NOT LOCKED!"
		return None
	genrec(node,None,None,False,w2v,lock) #lock is out var
	for i in fraw['cap']:
		lock[i] = h.firstCharUp(lock[i])
	
def makeFormats(w2v):
	ret = []
	for fraw in formats.makeAllForms():
		addRels(fraw)
		genf = lambda w2v, lock=[None,None,None,None,None,None]: gen(fraw,w2v,lock)
		regen = range(6)
		del regen[fraw['root']['index']]
		ret.append((genf,axes,regen))
	return ret

#===================================================

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
		return s
#		best = priority.best(s,regenf,canRegen,scoref)[0]
#		raw = h.strip(best).split()[:3]
#		notraw = best.split()
#		best = ". ".join([h.firstCharUp(h.makePlural(r)) for r in raw])+". "+" ".join(notraw[3:])
#		print best,"\n"
#		return best

if __name__ == "__main__":
	topic = sys.argv[1]
	if '_' not in topic:
		print "Make sure to tag topic"
		exit()
	noun = sys.argv[2]
	w2v = word2vec.load('data/tagged.bin')
	print "Word2Vec Loaded"
	pens = penseur.Penseur()
	print "Penseur Loaded"

	formats = makeFormats(w2v)
	doit(topic,noun,w2v,pens)
