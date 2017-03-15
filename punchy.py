import conceptnet as cn
import helpers as h
import random


bg_key = ""
bg_cache = []

res_key = ""
res_cache = []

def extract_cn(cn_result):
	return [res[1] for res in cn_result]

def filterNoun(list_in):
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
	return l.pop(i)[0]

def get_bg(topic, parents, w2v, juxtapose = False):
	global bg_key, bg_cache

	if bg_key != topic + "".join(parents) or len(bg_cache) == 0:
		incoming = []
		for p in parents:
			incoming.extend(cn.getIncoming(p, "HasSubevent"))
			incoming.extend(cn.getIncoming(p, "Causes"))
			incoming.extend(cn.getIncoming(p, "HasPrerequisite"))
			incoming.extend(cn.getIncoming(p, "UsedFor"))

		picked_bg = extract_cn(incoming)
		picked_bg = filterNoun(picked_bg)
		#picked_bg = h.augment(picked_bg, topic, 'n')
		picked_bg = filterNoun(picked_bg)
		relations = parents + [topic]
		picked_bg = sorted(picked_bg, key=lambda w:h.total_similarity(w, relations, w2v), reverse=True) # make sure word is actually in w2v
#		picked_bg = picked_bg[:-len(picked_bg)/4]

		bg_key = topic + "".join(parents)
		bg_cache = picked_bg
		removeMatch(bg_cache,topic,parents)
		bg_cache = h.w2vweightslist(bg_cache,relations,w2v)
		#print 'CACHE:',[x[0] for x in bg_cache]
		if not bg_cache:
			print "bg_cache empty"
			return None

	return pickOne(bg_cache)

def get_result(topic, parents, w2v, juxtapose = False):
	global res_key, res_cache

	if res_key != topic + "".join(parents) or len(res_cache) == 0:
		outgoing = []
		for p in parents:
			outgoing.extend(cn.getOutgoing(p, "HasSubevent"))
			outgoing.extend(cn.getOutgoing(p, "Causes"))
			outgoing.extend(cn.getOutgoing(p, "HasPrerequisite"))

		print outgoing
		picked_results = extract_cn(outgoing)
		picked_results = filterNoun(picked_results)
		#picked_results = h.augment(picked_results, topic, 'n')
		picked_results = filterNoun(picked_results)
		relations = parents + [topic]
		picked_results = sorted(picked_results, key=lambda w:h.total_similarity(w, relations, w2v), reverse=True)
		picked_results = picked_results[:-len(picked_results)/4]

		res_key = topic + "".join(parents)
		res_cache = picked_results
		removeMatch(res_cache,topic,parents)
		res_cache = h.w2vweightslist(res_cache,relations,w2v)
		if not res_cache:
			return None

	return pickOne(res_cache)

















