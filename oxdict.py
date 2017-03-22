import requests

app_id = '2c9ba5ba'
app_key = '2dca6744ee6251d8ef081ada48d40772'

language = 'en'
word_id = 'Ace'

url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/en/'

def lookup(word):
	r = requests.get(url + word.lower(), headers = {'app_id': app_id, 'app_key': app_key})
	if r.status_code != 200:
		return None
	return r.json()['results'][0]['lexicalEntries']

#r is oxdict.lookup response object
#pos is like "Verb" or "Noun"
#returns object with the following keys: ['pronunciations', 'text', 'lexicalCategory', 'language', 'entries'], entries is most useful
def getpos(r,pos):
	for e in r:
		if e['lexicalCategory'] == pos:
			return e
	return None

#takes a word and a POS ("Verb","Noun") and returns True if OxDict says that word is that POS
def ispos(word,pos):
	r = lookup(word)
	if r is None:
		return False
	return getpos(r,pos) is not None

gf = 'grammaticalFeatures'

#returns True if Ox Dict thinks the word is a verb and it is intransitive, False otherwise
def checkTransitivity(word):
	r = lookup(word)
	if r is None:
		return False #TODO: revisit? do we want to exclude a verb if OxDict doesnt list it?
	v = getpos(r,'Verb')
	if v is None:
		return False #not a verb
	for i in [x[gf] for x in v['entries'] if gf in x]:
		for e in i:
			if 'text' in e and e['text'] == "Transitive":
				return False #transitive
	return True #an intransitive verb

#this is important for "punchies", but I think it's not perfect (example: 'time')
def isMass(word):	
	r = lookup(word)
	if r is None:
		return False
	v = getpos(r,'Noun')
	if v is not None:
		for i in [x[gf] for x in v['entries'] if gf in x]:
			for e in i:
				if 'text' in e and e['text'] == "Mass":
					return True
	return False

