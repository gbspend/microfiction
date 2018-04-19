import requests, string
import helpers as h

url = 'http://api.conceptnet.io'

#ex: http://api.conceptnet.io/query?end=/c/en/scream&rel=/r/HasSubevent
# that gets all words that have the "[word] has subevent: scream" relation (edge)
#make functions that query for a word in start or end position and a relation. return words from edges by breaking out the while True part of getWord

#gets all "Start" words that end with "End" given the relation
def getIncoming(word, rel):
	u = url+'/query?end=/c/en/'+word+'&rel=/r/'+rel
	return doQuery(u, True)

def getOutgoing(word, rel):
	u = url+'/query?start=/c/en/'+word+'&rel=/r/'+rel
	return doQuery(u, False)

def getIdIncoming(id, rel):
	u = url+'/query?end='+id+'&rel=/r/'+rel
	return doQuery(u, True)

def getIdOutgoing(id, rel):
	u = url+'/query?start='+id+'&rel=/r/'+rel
	return doQuery(u, False)

def getEither(word, rel):
	id = '/c/en/'+word
	return getIdEither(id,rel)

def getIdEither(id, rel):
	u = url+'/query?node='+id+'&rel=/r/'+rel
	return doQueryEither(u, True)

eng = '&other=/c/en'
#returns array of id/label tuples
def doQuery(u, retStart):
	u+=eng
	obj = requests.get(u).json()
	ret = []
	for edge in obj['edges']:
		node = edge['start']
		if not retStart:
			node = edge['end']
		ret.append((node['@id'],node['label']))
	return ret

#returns array of id/label tuples
def doQueryEither(u, id):
	u+=eng
	obj = requests.get(u).json()
	ret = []
	for edge in obj['edges']:
		if edge['start']['@id'] == id:
			node = edge['end'] #choose the other
		else:
			node = edge['start']
		ret.append((node['@id'],node['label']))
	return ret

#'/c/en/scream' -> 'scream'
#'/c/en/scream/n' -> 'scream'
def stripPre(s):
	parts = s.split('/')
	if len(parts[-1])<3:
		return parts[-2]
	return parts[-1]

#gets relationship(s) between words
def getRels(start, end):
	rels = superGet(start, end, True)
	subs = ['HasFirstSubevent','HasLastSubevent','HasSubevent'] #these are indistinguishable for our purposes, so add them
	if any(r in subs for r in rels):
		rels.update(subs)
	return list(rels)


#Un-needed currently...
#takes a start word and an end word and returns all words related to start by any relation by which end is related to it
def superGet(start, end, justRels=False):
	u = url+'/query?start=/c/en/'+start+eng
	obj = requests.get(u).json() #results are paginated, but let's just stick with one for now
	allrels = {}
	endBase = h.baseWord(end)
	good = set()
	for edge in obj['edges']:
		node = edge['end']
		rel = stripPre(edge['rel']['@id'])
		word = string.replace(stripPre(node['@id']),'_',' ')
		h.addToDictList(allrels, rel, word)
		if h.baseWord(word) == endBase:
			good.add(rel)
	if justRels:
		return good

	ret = set()
	for g in good:
		for w in allrels[g]:
			if h.baseWord(w) != endBase:
				ret.add(w)
	return list(ret)

