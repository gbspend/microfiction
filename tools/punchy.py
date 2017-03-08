import datamuse as dm
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

def pickOne(l, topic, parents):
	i = random.randint(0,len(l)-1)
	return l.pop(i)

# Grab words with similar meaning from datamuse.
def augment(word_list, topic, w2v):
	extended = []
	for w in word_list:
		means_like = dm.query(dm.meansLike(w), dm.metadata('p'), dm.topics(topic))
		for result in means_like:
			meta = result[1]
			if 'tags' in meta:
				if 'n' in meta['tags'] and len(result[0].split()) == 1 and result[0] in w2v and w2v.similarity(topic, result[0]) > 0.3:
					extended.append(result[0])

	word_list.extend(extended)
	return list(set(word_list))


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
		picked_bg = augment(picked_bg, topic, w2v)
		picked_bg = filterNoun(picked_bg)
		picked_bg = sorted(picked_bg, key=lambda w:w2v.similarity(topic, w) if w in w2v else 0, reverse=True) # make sure word is actually in w2v
		picked_bg = picked_bg[:-len(picked_bg)/4]

		bg_key = topic + "".join(parents)
		bg_cache = picked_bg
		removeMatch(bg_cache,topic,parents)
		if not bg_cache:
			return None

	return pickOne(bg_cache, topic, parents)

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
		picked_results = augment(picked_results, topic, w2v)
		picked_results = filterNoun(picked_results)
		picked_results = sorted(picked_results, key=lambda w:w2v.similarity(topic, w) if w in w2v else 0, reverse=True)
		picked_results = picked_results[:-len(picked_results)/4]

		res_key = topic + "".join(parents)
		res_cache = picked_results
		removeMatch(res_cache,topic,parents)
		if not res_cache:
			return None

	return pickOne(res_cache, topic, parents)
