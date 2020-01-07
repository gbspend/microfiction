from collections import defaultdict
from nltk.corpus import wordnet as wn
import string
import numpy as np
import datamuse as dm
import random
from pattern.en import parse, pluralize, comparative, superlative, conjugate, PRESENT, PAST, PARTICIPLE, INFINITIVE
import oxdict as od
from operator import itemgetter
import os, csv

#maps number n, which is in rage oldmin--oldmax to newmin--newmax
def rangify(n,oldmin,oldmax,newmin,newmax):
	R = float(newmax - newmin) / (oldmax - oldmin)
	return (n - oldmin) * R + newmin

def synName(s):
	return s.lemma_names()[0]

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

def baseWord(word):
	base = wn.morphy(word)
	if base is None:
		return word
	return base

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

def strip(s):
	return str(s).translate(None, string.punctuation).lower().strip()

def firstCharUp(s):
	return s[0].upper() + s[1:]

#takes in a list of words and returns the ones that match part of speech p ('n' or 'v' for example) (unmorphied)
def pos(a,p):
	ret = set()
	for i in a:
		m = wn.morphy(i)
		if m is None:
			continue
		for ss in wn.synsets(m):
			if ss.pos() == p:
				ret.add(i)
	return list(ret)

# Grab words with similar meaning from datamuse.
#word_list is list of strings, topic is string, pos is string like 'n' or 'v'
def augment(word_list, topic, pos):
	extended = []
	for w in word_list:
		means_like = dm.query(dm.meansLike(w), dm.metadata('p'), dm.topics(topic))
		for result in means_like:
			meta = result[1]
			if 'tags' in meta:
				if pos in meta['tags'] and len(result[0].split()) == 1:# and result[0] in w2v and w2v.similarity(topic, result[0]) > 0.3:
					extended.append(result[0])

	word_list.extend(extended)
	return list(set(word_list))

def total_similarity(word, relations, w2v):
	if word not in w2v:
		return 0.0
	return sum((w2v.similarity(word, x) for x in relations if x in w2v), 0.0)

def new_total_similarity(word, relations, w2v):
	if word not in w2v:
		return 0.0
	return sum((max(0.0,get_cosine_similarity(word, x, w2v)) for x in relations if x in w2v), 0.0)

def get_cosine_similarity(word1, word2, w2v):
	vec1 = w2v.get_vector(word1)
	vec2 = w2v.get_vector(word2)
	dividend = np.dot(vec1, vec2)
	divisor = np.linalg.norm(vec1) * np.linalg.norm(vec2)
	result = dividend / divisor
	return result

#l is a list of words, word is the word that the w2v similarity will be measured against
#returns the list sorted by similarity
def w2vsort(l,word,w2v):
	return sorted(l,reverse=True,key=lambda x: w2v.similarity(word,x))

#l is a list of words, words is the LIST OF words that the w2v total_similarity will be measured against
#returns the list sorted by similarity
def w2vsortlist(l,words,w2v):
	return sorted(l,reverse=True,key=lambda x: total_similarity(x,words,w2v))

def w2vsortlistNew(l,words,w2v):
	return sorted(l,reverse=True,key=lambda x: new_total_similarity(x,words,w2v))

#l is a list of words, word is the word that the w2v similarity will be measured against
#returns a list of (w, similarty) tuples
def w2vweights(l,word,w2v):
	return [(x,w2v.similarity(word,x)) for x in l]

#l is a list of words, words is the LIST OF words that the w2v total_similarity will be measured against
#returns a list of (w, similarty) tuples
def w2vweightslist(l,words,w2v):
	return [(x,total_similarity(x,words,w2v)) for x in l]

def strip_tag(w):
	loc = w.find('_')
	if loc == -1:
		return w
	return w[:-(len(w)-loc)]

def w2vWeightsListNew(l, words, w2v):
	tuple_list = [(x, new_total_similarity(x, words, w2v)) for x in l]
	return sorted(tuple_list, key=itemgetter(1), reverse=True)

#choices is a list of (choice,weight) tuples
#Doesn't need to be sorted! :D
#returns index
def weighted_choice(choices,offset=0):
	total = sum(w+offset for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for i,t in enumerate(choices):
		w = t[1]+offset
		if upto + w >= r:
			return i
		upto += w
	assert False, "Shouldn't get here"

# [('dog', 'bark'), ('bird', 'chirp'), ('pig', 'oink'), ('cow', 'moo'), ('chicken', 'cluck')]
def relation(start, relations, w2v):
	'''
	Parameters
	----------
	start : str
		The word that the calculated vector should be added to.
	relations : list of tuple of str
		A list of tuples of the form (from, to) for creating the relationship vector

	Returns
	--------
	ret : list of str
	'''
	if start not in w2v:
		print start, ' not in w2v. Can\'t use if for relations.'
		return []
	filtered = [x for x in relations if x[0] in w2v and x[1] in w2v]
	froms, tos = zip(*filtered)
	from_p = sum((w2v[x] for x in froms)) /  len(relations)
	to_p = sum((w2v[x] for x in tos)) / len(relations)
	rel = to_p - from_p

	return sorted([x[0] for x in w2v.similar_by_vector(w2v[start] + rel)], key=lambda x : w2v.similarity(start, x), reverse = True)

# relations should be [(noun, verb)...]
def get_verbs_from_noun(start, relations, w2v):
	if '_' not in start:
		start += '_NN'
	return get_scholar_rels(start, relations, w2v, '_NN', '_VB')

# relations should be [(verb, noun)...]
def get_nouns_from_verb(start, relations, w2v):
	if '_' not in start:
		start += '_VB'
	return get_scholar_rels(start, relations, w2v, '_VB', '_NN')

#start: POS tagged word like "dog_NN"
#relations: list of tuples/lists of len 2, untagged [(cat, meow), (cow, moo)]
#tag1: POS tag of left hand of relations (t[0]) and start
#tag2: POS tag of right hand of relations (t[1])
# Scholar by Daniel Ricks: https://github.com/danielricks/scholar
def get_scholar_rels(start, relations, w2v, tag1, tag2,num=10):
	counts = defaultdict(float)
	ret = []
	for rel in relations:
		positives = [rel[1] + tag2, start]
		negatives = [rel[0] + tag1]
		flag = False
		for w in positives+negatives:
			if w not in w2v:
				flag = True
				break
		if flag:
			continue

		idxs, metrics = w2v.analogy(pos=positives, neg=negatives, n=num)
		res = w2v.generate_response(idxs, metrics).tolist()
		ret += res
		for x in res:
			counts[x[0]] += x[1]

	ret = [x[0] for x in ret]
	ret = sorted(ret, key=counts.get, reverse=True)
	ret = [x[:-(len(x)-x.find('_'))] for x in ret]
	ret = list(set(ret)) # remove duplicates (and undoes sort!)

	return ret

#Ideas:
#wn.synsets(word) -> lemmas -> names (to "cast a wider net")

#for collecting survey data on how well the scorer is doing
def writeCsv(csvname, row):
	csvPath = "score_data/"
	fname = csvPath+csvname+'.csv'
	if os.path.exists(fname):
		o = 'a' # append if already exists
	else:
		o = 'w' # make a new file if not
	with open(fname,o+'b') as f:
		writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE)
		try:
			writer.writerow(row)
		except Exception:
			pass

#good/bad are axis ends
#l is list of sentences to score
#p is Penseur instance
#returns score, higher is better
#len(l) > 1
def getSkipScores(bad,good1,good2,sts,p):
	story_list = sts[:]
	story_list += ['asdf'] #need to add/remove dummy story in case len(story_list) ==1
	p.encode([strip(s) for s in story_list])
	scores = p.get_axis_scores(bad,good1,good2)
	#story_list = story_list[:-1]
	scores = scores[:-1]
	#for i,story in enumerate(story_list):
	#	writeCsv("basic1D",[story,scores[i]])
	return scores

def toPresent(verb):
	return conjugate(verb,PRESENT)

#only takes single words!
def makePlural(w):
	if od.isMassOrProper(w) or getPOS(w) == 'NNS':
		return w
	return pluralize(w)

def getV(s,i=5):
	v = strip(s).split()[i]
	m = wn.morphy(v)
	if m is None:
		return v
	return m

def addToDictList(d,k,v):
	if k not in d:
		d[k] = []
	d[k].append(v)

def getPOS(w):
	return parse(w).split('/')[1].split('-')[0]

def numMatch(parentWords,childWords):
	ret = 0
	for i in range(len(parentWords)):
		if parentWords[i] == childWords[i] or wn.morphy(parentWords[i]) == wn.morphy(childWords[i]):
			ret += 1
	return ret

'''
* is pattern.en
^ is custom
= is leave it
# is can't
JJR <- JJ comparative
JJS <- JJ superlative
NNS <- NN pluralize
NNP <- NN=
NNPS <- NN, NNP pluralize (both)
PDT <- DT#
PRP <- RP#
PRP$ <- PRP^ RP#
RBR <- RB comparative
RBS <- RB superlative
VBD <- VB conjugate
VBG <- VB conjugate?
VBN <- VB conjugate?
VBP <- VB conjugate
VBZ <- VB conjugate
WDT <- DT#
WP$ <- WP^
WRB <- RB#
'''

PRPD = {'me':'mine','you':'yours','he':'his','she':'hers','it':'its','us':'ours','them':'theirs'}
WPD = {'who':'whose'}

#try to conjugate the word from POS p to POS target
#See "p in target" cases above
def tryPOS(word,p,target):
	if target in p and target not in ['RB','DT','RP']:
		if target == 'PRP' or target == 'WP':
			d = WPD
			if target == 'PRP':
				d = PRPD
			for k in d:
				if d[k] == word:
					return k
			return None
		return wn.morphy(word)

	#else
	if target == 'PRP$' and p == 'PRP':
		return PRPD.get(word)
	if target == 'WP$':
		return WPD.get(word)
	if p == 'NN':
		if target == 'NNP':
			return word
		else:
			return pluralize(word)
	if p == 'NNP':
		return pluralize(word)
	if 'VB' in p:
		t = ''
		if target == 'VBD':
			t = PAST
		if target == 'VBP':
			t = INFINITIVE
		if target == 'VBZ':
			t = PRESENT
		if target == 'VBN':
			t = PAST+PARTICIPLE
		if target == 'VBG':
			t = PARTICIPLE
		if t:
			return conjugate(word,tense=t)
	
	ret = ''
	if target == 'JJR' or target == 'RBR':
		ret = comparative(word)
	if target == 'JJS' or target == 'RBS':
		ret = superlative(word)
	if not ret or ' ' in ret:
		return None #default
	else:
		return ret

