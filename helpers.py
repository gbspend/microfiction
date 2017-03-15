from nltk.corpus import wordnet as wn
import string
import numpy as np
import datamuse as dm
import random

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
def w2vsort(l,word,w2v):
	return sorted(l,reverse=True,key=lambda x: w2v.similarity(word,x))

def w2vweights(l,word,w2v):
	return [(x,w2v.similarity(word,x)) for x in l]

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
# [('dog', 'bark'), ('bird', 'chirp'), ('pig', 'oink'), ('cow', 'moo'), ('chicken', 'cluck')]
def relation(start, relations, w2v):
	if start not in w2v:
		print start, ' not in w2v. Can\'t use if for relations.'
		return []
	filtered = [x for x in relations if x[0] in w2v and x[1] in w2v]
	froms, tos = zip(*filtered)
	from_p = sum((w2v[x] for x in froms)) /  len(relations)
	to_p = sum((w2v[x] for x in tos)) / len(relations)
	rel = to_p - from_p

	return sorted([x[0] for x in w2v.similar_by_vector(w2v[start] + rel)], key=lambda x : w2v.similarity(start, x), reverse = True)

#Ideas:
#wn.synsets(word) -> lemmas -> names (to "cast a wider net")

#use w2v to make our own "relations": give it [(nail,hammer),(horse,ride)] and pass in king
#see nancy's notes in Slack
