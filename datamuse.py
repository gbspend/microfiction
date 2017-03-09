import requests

url = 'http://api.datamuse.com'
maxWords = 100
#vocab = 'en' #maybe use 'enwiki' instead?

def spaceToPlus(w):
	return w.replace(' ','+')

def meansLike(w):
	return 'ml='+spaceToPlus(w)

def soundsLike(w):
	return 'sl='+spaceToPlus(w)

def spelledLike(w):
	return 'sp='+spaceToPlus(w)

#rel={jja, jjb, syn, trg, ant, spc, gen, com, par, bga, bgb, rhy, nry, hom, cns} see API
def related(rel,w):
	return 'rel_'+rel+'='+spaceToPlus(w)

#At most 5 words can be specified. Space or comma delimited. Nouns work best.
def topics(t):
	return 'topics='+t

def leftContext(w):
	return 'lc='+spaceToPlus(w)

def rightContext(w):
	return 'rc='+spaceToPlus(w)

#any combo of d,p,s,r,f
def metadata(m):
	return 'md='+m

#returns array for word/metadata tuple in the order the API returned them (usu. sorted by score)
def query(*args):
	ret = []
	u = url+'/words?max='+str(maxWords)+'&' + '&'.join(str(a) for a in args)
	obj = requests.get(u).json()
	for o in obj:
		if 'score' not in o:
			o['score']=0
		ret.append((o['word'],o))
	return ret