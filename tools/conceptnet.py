import requests

class Word:
	def __init__(self, i, l, g, t):
		self.id = i
		self.label = l
		self.lang = g
		self.term = t
		self.rels = { #arrays of id/label tuples that can be looked up in ConceptNet
			'RelatedTo':set(),
			#'ExternalURL':set(),
			'FormOf':set(),
			'IsA':set(),
			'PartOf':set(),
			'HasA':set(),
			'UsedFor':set(),
			'CapableOf':set(),
			'AtLocation':set(),
			'Causes':set(),
			'HasSubevent':set(),
			'HasFirstSubevent':set(),
			'HasLastSubevent':set(),
			'HasPrerequisite':set(),
			'HasProperty':set(),
			'MotivatedByGoal':set(),
			'ObstructedBy':set(),
			'Desires':set(),
			'CreatedBy':set(),
			'Synonym':set(),
			'Antonym':set(),
			'DerivedFrom':set(),
			'SymbolOf':set(),
			'DefinedAs':set(),
			'Entails':set(),
			'MannerOf':set(),
			'LocatedNear':set(),
			'Other':set() #this will always be empty
		}
	
	#returns names of non-empty relations
	def nonEmpty(self):
		ret = []
		for k in self.rels.keys():
			if len(self.rels[k]) > 0:
				ret.append(k)
		return ret

	def addRel(self, rel, label):
		if rel not in self.rels:
			rel = 'Other'
		self.rels[rel].add(label)
	
	#convenience function to say whether a relation is "Other" or not
	def isOther(self, rel):
		return rel not in self.rels

	def relatedTo (self):
		return self.rels['RelatedTo']
	#def externalURL (self):
	#	return self.rels['ExternalURL']
	def formOf (self):
		return self.rels['FormOf']
	def isA (self):
		return self.rels['IsA']
	def partOf (self):
		return self.rels['PartOf']
	def hasA (self):
		return self.rels['HasA']
	def usedFor (self):
		return self.rels['UsedFor']
	def capableOf (self):
		return self.rels['CapableOf']
	def atLocation (self):
		return self.rels['AtLocation']
	def causes (self):
		return self.rels['Causes']
	def hasSubevent (self):
		return self.rels['HasSubevent']
	def hasFirstSubevent (self):
		return self.rels['HasFirstSubevent']
	def hasLastSubevent (self):
		return self.rels['HasLastSubevent']
	def hasPrerequisite (self):
		return self.rels['HasPrerequisite']
	def hasProperty (self):
		return self.rels['HasProperty']
	def motivatedByGoal (self):
		return self.rels['MotivatedByGoal']
	def obstructedBy (self):
		return self.rels['ObstructedBy']
	def desires (self):
		return self.rels['Desires']
	def createdBy (self):
		return self.rels['CreatedBy']
	def synonym (self):
		return self.rels['Synonym']
	def antonym (self):
		return self.rels['Antonym']
	def derivedFrom (self):
		return self.rels['DerivedFrom']
	def symbolOf (self):
		return self.rels['SymbolOf']
	def definedAs (self):
		return self.rels['DefinedAs']
	def entails (self):
		return self.rels['Entails']
	def mannerOf (self):
		return self.rels['MannerOf']
	def locatedNear (self):
		return self.rels['LocatedNear']
	def other (self):
		return self.rels['Other']


#instance ConceptNet first
class ConceptNet:

	def __init__(self):
		#dict that maps strings to "Word" 
		self.data = {}
		self.url = 'http://api.conceptnet.io'

	#ex: http://api.conceptnet.io/query?end=/c/en/scream&rel=/r/HasSubevent
	# that gets all words that have the "[word] has subevent: scream" relation (edge)
	#make functions that query for a word in start or end position and a relation. return words from edges by breaking out the while True part of getWord

	#gets all "Start" words that end with "End" given the relation
	def getIncoming(self, word, rel):
		u = 'http://api.conceptnet.io/query?end=/c/en/'+word+'&rel=/r/'+rel
		return self.doQuery(u, True)

	def getOutgoing(self, word, rel):
		u = 'http://api.conceptnet.io/query?start=/c/en/'+word+'&rel=/r/'+rel
		return self.doQuery(u, False)

	def getIdIncoming(self, id, rel):
		u = 'http://api.conceptnet.io/query?end='+id+'&rel=/r/'+rel
		return self.doQuery(u, True)

	def getIdOutgoing(self, id, rel):
		u = 'http://api.conceptnet.io/query?start='+id+'&rel=/r/'+rel
		return self.doQuery(u, False)

	def doQuery(self, u, retStart):
		obj = requests.get(u).json()
		ret = []
		for edge in obj['edges']:
			node = edge['start']
			if not retStart:
				node = edge['end']
			if node['language'] == 'en':
				ret.append((node['@id'],node['label']))
		return ret		

	#get a word (request if necessary)
	#ex. "dog" (use "label" from an edge)
	def getWord(self, word):
		if word in self.data:
			return self.data[word]
		return self.getId('/c/en/' + word)

	def getId(self, id):
		#TODO re-design so that it caches ids too (fetch first page, then look up caching?)
		obj = requests.get(self.url + id).json()
		if 'view' not in obj:
			return None
		#note: can't do self.data[word]=... here because we don't have "start"
		#load edges
		while True:
			for edge in obj['edges']:
				word = edge['start']['label']
				if word not in self.data:
					s = edge['start']
					self.data[word] = Word(s['@id'],s['label'],s['language'],s['term'])
				rel = edge['rel']['label']
				#check whether the relation is "Other", if it is, skip it
				if not self.data[word].isOther(rel):
					end = edge['end']
					if end['language'] == 'en':
						self.data[word].addRel(rel, (end['@id'], end['label']))
				#doesn't include "surfaceText" or "weight"
			if 'nextPage' not in obj['view']:
				self.data[word].loaded = True
				break
			obj = requests.get(self.url+obj['view']['nextPage']).json()
		return self.data[word]

if __name__ == "__main__":
	cc = ConceptNet()
	ft = cc.getWord('french_toast')
	a = ft.isA()
	for i in a:
		print i
		wi = cc.getWord(i)
		ai = wi.isA()
		for ii in ai:
			print "\t"+ii
	ft = cc.getWord('french_toast')
	a = ft.isA()
	for i in a:
		print i
		wi = cc.getWord(i)
		ai = wi.isA()
		for ii in ai:
			print "\t"+ii
