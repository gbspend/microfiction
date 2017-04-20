import requests

#new username is brads
#password is fowl with special char at end

app_id = '7b7ce7fa'
app_key = 'e30c7d55f087909349ccc994cb40e6f9'

url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/en/'

def lookup(word):
	r = requests.get(url + word.lower(), headers = {'app_id': app_id, 'app_key': app_key})
	if r.status_code != 200:
		if r.status_code != 404:
			print "OXDICT returned code", r.status_code
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

verbdict = {}
#returns True if Ox Dict thinks the word is a verb and it is intransitive and its not dated or archaic, False otherwise
def checkVerb(word):
	if word in verbdict:
		return verbdict[word]
	else:
		r = lookup(word)
		if r is None:
			return True #accept all if oxdict goes down (and don't cache)
		v = getpos(r,'Verb')
		if v is None:
			verbdict[word] = False
			return False #not a verb
		for i in [x[gf] for x in v['entries'] if gf in x]:
			for e in i:
				if 'text' in e and (e['text'] == "Transitive" or 'with object' in e['text']):
					verbdict[word] = False
					return False #transitive
		for i in v['entries']:
			if 'senses' in i:
				for s in i['senses']:
					if 'registers' in s:
						for rg in s['registers']:
							if rg in ['archaic','dated']:
								verbdict[word] = False
								return False
		verbdict[word] = True
		return True

mpdict = {}
#this is important for "punchies", but I think it's not perfect (example: 'time')
def isMassOrProper(word):
	if word in mpdict:
		return mpdict[word]
	else:
		r = lookup(word)
		if r is None:
			return False #don't cache in case it's unavailable
		v = getpos(r,'Noun')
		if v is not None:
			for i in [x[gf] for x in v['entries'] if gf in x]:
				for e in i:
					if 'text' in e and e['text'] in ["Mass", "Proper"]:
						mpdict[word] = True
						return True
		mpdict[word] = False
		return False
