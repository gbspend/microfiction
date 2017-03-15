import requests

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

#returns array of id/label tuples
def doQuery(u, retStart):
	obj = requests.get(u).json()
	ret = []
	for edge in obj['edges']:
		node = edge['start']
		if not retStart:
			node = edge['end']
		if node['language'] == 'en':
			ret.append((node['@id'],node['label']))
	return ret

#returns array of id/label tuples
def doQueryEither(u, id):
	obj = requests.get(u).json()
	ret = []
	for edge in obj['edges']:
		if edge['start']['@id'] == id:
			node = edge['end'] #choose the other
		else:
			node = edge['start']
		if node['language'] == 'en':
			ret.append((node['@id'],node['label']))
	return ret
