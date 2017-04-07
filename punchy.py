import conceptnet as cn
import datamuse as dm
import helpers as h
import stanford as stan
import random

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
			filtered.add(inc)
		else:
			for w in h.pos(words,'n'):
				filtered.add(w)
	return list(filtered)

def removeMatch(l, topic, parents):
	dontMatch = {h.baseWord(topic)}
	for p in parents:
		dontMatch.add(h.baseWord(p))
		dontMatch.add(h.baseWord(h.toNoun(p)))

	temp = []
	for w in l:
		if h.baseWord(w) not in dontMatch:
			temp.append(w)
	l[:] = temp

#assumes l is a list of (word,weight) tuples
def pickOne(l):
	i = h.weighted_choice(l)
	return l[i][0]

def get_words(topic, parents, cn_relations, isIncoming=True):
	res = []
	for p in parents:
		for rel in cn_relations:
			if isIncoming:
				res += (x[1] for x in cn.getIncoming(p, rel))
			else:
				res += (x[1] for x in cn.getOutgoing(p, rel))

		# TODO: find good datamuse relationships for outgoing edges.
		if isIncoming:
			res += (x[0] for x in dm.query(dm.related('trg',p),dm.topics(topic), dm.metadata('p'))
					 if ('tags' in x[1] and x[1]['tags'][0] == 'n')) # get only nouns

	#res = filterNoun(res)
	res = oldFilterNoun(res)
	removeMatch(res, topic, parents)
	return res

def get_bg(topic, parents, w2v, juxtapose = False):
	global bg_cache

	k = topic + "".join(parents)
	if k not in bg_cache:
		cn_relations = ["HasSubevent", "Causes", "HasPrerequisite", "UsedFor"]

		picked_bg = get_words(topic, parents, cn_relations)

		relations = parents + [topic]
		picked_bg = sorted(picked_bg, key=lambda w:h.total_similarity(w, relations, w2v), reverse=True) # make sure word is actually in w2v
		if len(picked_bg) > 20:
			picked_bg = picked_bg[:-len(picked_bg)/5]

		bg_key = topic + "".join(parents)
		bg_list = picked_bg
		bg_list = h.w2vweightslist(bg_list,relations,w2v)
		#print parents,'CACHE:',[x[0] for x in bg_list]
		if not bg_list:
			print "bg_list empty"
			return None
		bg_cache[k] = bg_list
	else:
		bg_list = bg_cache[k]
	#print(bg_list)
	return pickOne(bg_list)

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
