import datamuse as dm
import conceptnet as cn
import wordnet_helpers as wh
wh = reload(wh)
import random

def extract_cn(cn_result):
    return [res[1] for res in cn_result]

def filter(list_in):
    filtered = set()
    for inc in list_in:
        words = inc.split()
        if len(words) == 1:
            filtered.add(inc)
        else:
            for w in words:
                if wh.is_noun(w):
                    filtered.add(w)

    return list(filtered)

def pickSome(l, n, topic, parents):
    ret = []
    dontMatch = {wh.baseWord(topic)}
    for p in parents:
        dontMatch.add(wh.baseWord(p))
        dontMatch.add(wh.baseWord(wh.toNoun(p)))

	while len(ret) < n:
		c = random.choice(l)
		if wh.baseWord(c) in dontMatch:
			continue
		ret.append(wh.toNoun(c))
		dontMatch.add(wh.baseWord(c))

	return ret

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

def get_bg(topic = "", parents = [], word_count = 1, juxtapose = False, w2v = None):
    if not topic:
        print("Please provide a topic.")
        return []

    if not parents:
        print("Please supply at least one parent term.")
        return []

    if not w2v:
        print("Please supply w2v parameter.")
        return []

    if topic not in w2v:
        print 'Warning: topic not in w2v. Filtering won\'t work'

    incoming = []
    for p in parents:
        incoming.extend(cn.getIncoming(p, "HasSubevent"))
        incoming.extend(cn.getIncoming(p, "Causes"))
        incoming.extend(cn.getIncoming(p, "HasPrerequisite"))
        incoming.extend(cn.getIncoming(p, "UsedFor"))

    picked_bg = extract_cn(incoming)
    picked_bg = filter(picked_bg)
    picked_bg = augment(picked_bg, topic, w2v)
    picked_bg = filter(picked_bg)
    picked_bg = sorted(picked_bg, key=lambda w:w2v.similarity(topic, w) if w in w2v else 0, reverse=True) # make sure word is actually in w2v
    picked_bg = picked_bg[:-len(picked_bg)/2]
    return pickSome(picked_bg, word_count, topic, parents)

def get_result(topic = '', parents = [], word_count = 1, juxtapose = False, w2v = None):
    if not topic:
        print("Please provide a topic.")
        return []

    if not parents:
        print("Please supply at least one parent term.")
        return []

    if not w2v:
        print("Please supply w2v parameter.")
        return []

    if topic not in w2v:
        print 'Warning: topic not in w2v. Filtering won\'t work'

    outgoing = []
    for p in parents:
        outgoing.extend(cn.getOutgoing(p, "HasSubevent"))
        outgoing.extend(cn.getOutgoing(p, "Causes"))
        outgoing.extend(cn.getOutgoing(p, "HasPrerequisite"))

    print outgoing
    picked_results = extract_cn(outgoing)
    picked_results = filter(picked_results)
    picked_results = augment(picked_results, topic, w2v)
    picked_results = filter(picked_results)
    picked_results = sorted(picked_results, key=lambda w:w2v.similarity(topic, w) if w in w2v else 0, reverse=True)

    return pickSome(picked_results, word_count, topic, parents)
