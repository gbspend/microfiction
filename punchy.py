import conceptnet as cn
import datamuse as dm
import helpers as h
h = reload(h)
import stanford as stan
import random
from nltk.corpus import wordnet as wn

bg_cache = {}

res_key = ""
res_cache = [] #TODO change to dict

# TODO see how get_nouns affects single words
#doesnt help much, but slows down a lot
def filterNoun(list_in):
	filtered = set()
	for inc in list_in:
		nounified = stan.get_nouns(inc)
		for n in nounified:
			filtered.add(n)

	return list(filtered)

def oldFilterNoun(list_in):
	filtered = set()
	for inc in list_in:
		words = inc.split()
		if len(words) == 1:
			if wn.morphy(inc) is not None:
				filtered.add(wn.morphy(inc))
			else:
				filtered.add(inc)
		else:
			for w in h.pos(words,'n'):
				if wn.morphy(w) is not None:
					filtered.add(wn.morphy(w))
				else:
					filtered.add(w)
	return list(filtered)

def removeMatch(l, topic, parents):
	dontMatch = {h.strip_tag(topic)}
	for p in parents:
		dontMatch.add(h.strip_tag(p))
		#dontMatch.add(h.baseWord(h.toNoun(p)))

	temp = []
	for w in l:
		if w not in dontMatch:
			temp.append(w)
			dontMatch.add(w)
	l[:] = temp

#assumes l is a list of (word,weight) tuples
def pickOne(l):
	i = h.weighted_choice(l)
	return l[i][0]

def get_words(topic, parents, cn_relations, w2v_relations, w2v, isIncoming=True):
	res = []
	stripped_topic = h.strip_tag(topic)
	for p in parents:
		stripped_parent = h.strip_tag(p)
		for rel in cn_relations:
			if isIncoming:
				res += (x[1] for x in cn.getIncoming(stripped_parent, rel))
			else:
				res += (x[1] for x in cn.getOutgoing(stripped_parent, rel))

		# TODO: find good datamuse relationships for outgoing edges.
		if isIncoming:
			res += (x[0] for x in dm.query(dm.related('trg',stripped_parent),dm.topics(stripped_topic), dm.metadata('p'))
					 if ('tags' in x[1] and x[1]['tags'][0] == 'n')) # get only nouns

		w2v_words = h.get_nouns_from_verb(stripped_parent, w2v_relations, w2v)
		res += w2v_words

	#res = filterNoun(res)
	res = oldFilterNoun(res)
	removeMatch(res, topic, parents)
	res = [x+'_NN' for x in res] # should hopefully all be nouns at this point...
	return res

def get_bg(topic, parents, w2v, juxtapose = False):
	global bg_cache

	k = topic + "".join(parents)
	if k not in bg_cache:
		cn_relations = ["HasSubevent", "Causes", "HasPrerequisite", "UsedFor"]
		w2v_relations = [('eat', 'hunger'), ('drink', 'thirst'), ('shoot', 'hatred'), ('laugh', 'happiness'), ('sleep', 'fatigue'), ('scream', 'fear')]
		picked_bg = get_words(topic, parents, cn_relations, w2v_relations, w2v)
		relations = parents + [topic]
		if len(picked_bg) > 20:
			picked_bg = picked_bg[:-len(picked_bg)/5]

		picked_bg = h.w2vWeightsListNew(picked_bg, relations, w2v)
		bg_key = topic + "".join(parents)
		bg_list = picked_bg
		if not bg_list:
			print "bg_list empty"
			return None
		bg_cache[k] = bg_list
	else:
		bg_list = bg_cache[k]
	#print(bg_list)
	return h.strip_tag(pickOne(bg_list))

def get_result(topic, parents, w2v, juxtapose = False):
	global res_key, res_cache

	if res_key != topic + "".join(parents) or len(res_cache) == 0:
		cn_relations = ["HasSubevent", "Causes", "HasPrerequisite", "UsedFor"]

		picked_results = get_words(topic, parents, cn_relations, False)

		relations = parents + [topic]
		picked_results = sorted(picked_results, key=lambda w:h.total_similarity(w, relations, w2v), reverse=True)
		if len(picked_results) > 20:
			picked_results = picked_results[:-len(picked_results)/5]

		res_key = topic + "".join(parents)
		res_cache = picked_results
		res_cache = h.w2vweightslist(res_cache,relations,w2v)
		if not res_cache:
			return None

	return pickOne(res_cache)
