from collections import defaultdict
from nltk.corpus import wordnet as wn
import string
import numpy as np
import datamuse as dm
import random
from pattern.en import conjugate, PRESENT, parse, pluralize
import oxdict as od
od = reload(od)

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
	return str(s).translate(None, string.punctuation).lower()

def firstCharUp(s):
	return s[0].upper() + s[1:]

#takes in a list of words and returns the ones that match part of speech p ('n' or 'v' for example) (unmorphied)
#if "extra" is True: add all synset names that are related (example: 'chair' (verb) would return 'chair' and 'moderate')
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

#l is a list of words, word is the word that the w2v similarity will be measured against
#returns the list sorted by similarity
def w2vsort(l,word,w2v):
	return sorted(l,reverse=True,key=lambda x: w2v.similarity(word,x))

#l is a list of words, words is the LIST OF words that the w2v total_similarity will be measured against
#returns the list sorted by similarity
def w2vsortlist(l,words,w2v):
	return sorted(l,reverse=True,key=lambda x: total_similarity(x,words,w2v))

#l is a list of words, word is the word that the w2v similarity will be measured against
#returns a list of (w, similarty) tuples
def w2vweights(l,word,w2v):
	return [(x,w2v.similarity(word,x)) for x in l]

#l is a list of words, words is the LIST OF words that the w2v total_similarity will be measured against
#returns a list of (w, similarty) tuples
def w2vweightslist(l,words,w2v):
	return [(x,total_similarity(x,words,w2v)) for x in l]

#choices is a list of (choice,weight) tuples
#Doesn't need to be sorted! :D
#returns index
def weighted_choice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for i,t in enumerate(choices):
		w = t[1]
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
def get_verbs_from_noun(start, relations, w2v_alt):
	start += '_NN'
	return get_scholar_rels(start, relations, w2v_alt, '_NN', '_VB')

# relations should be [(verb, noun)...]
def get_nouns_from_verb(start, relations, w2v_alt):
	start += '_VB'
	return get_scholar_rels(start, relations, w2v_alt, '_VB', '_NN')

# Scholar by Daniel Ricks: https://github.com/danielricks/scholar
def get_scholar_rels(start, relations, w2v_alt, tag1, tag2):
	positives = []
	negatives = []
	counts = defaultdict(int)
	total_res = []
	for rel in relations:
		positives += [rel[1] + tag2, start]
		negatives += [rel[0] + tag1]

		idxs, metrics = w2v_alt.analogy(pos=positives, neg=negatives, n=10)
		res = w2v_alt.generate_response(idxs, metrics).tolist()
		total_res += res
		for x in res:
			counts [x[0]] += 1

	total_res = [x[0] for x in total_res]
	total_res = list(set(total_res)) # remove duplicates
	total_res = sorted(total_res, key=counts.get, reverse=True)
	total_res = [x[:-(len(x)-x.find('_'))] for x in total_res]

	return total_res

#Ideas:
#wn.synsets(word) -> lemmas -> names (to "cast a wider net")

#use w2v to make our own "relations": give it [(nail,hammer),(horse,ride)] and pass in king
#see nancy's notes in Slack


#good/bad are axis ends
#s is sentence to score
#p is Penseur instance
#returns score, higher is better
def getSkipScore(bad,good,s,p):
	p.encode([s,'gun mask note the teller screams'])
	return p.get_axis_scores(bad,good)[0]

#len(l) > 1
def getSkipScores(bad,good,l,p):
	#return [random.random() for x in l]
	if len (l) == 1:
		return [getSkipScore(bad,good,l[0],p)]
	p.encode(l)
	return p.get_axis_scores(bad,good)

def toPresent(verb):
	return conjugate(verb,PRESENT)

#only takes single words!
def makePlural(w):
	if od.isMassOrProper(w) or parse(w).split('/')[1] == 'NNS':
		return w
	return pluralize(w)
















