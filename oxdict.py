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

gf = 'grammaticalFeatures'

def isTransitive(word):	
	r = lookup(word)
	v = getpos(r,'Verb')
	for i in [x[gf] for x in v['entries'] if gf in x]:
		for e in i:
			if 'text' in e and e['text'] == "Transitive":
				return True
	return False

