import word2vec, random, newpriority, formats
import helpers as h
from penseur import penseur
import wordbags as wb
from itertools import chain, izip_longest
import conceptnet as cn
import wordbags as wb

newpriority = reload(newpriority)

maxRoots = 60 #Max Niches, too

#=FORMATS===========================================

badstory = 'plunger volcano paper the mug switches'
#axes = ('plunger volcano paper the mug switches',['bridge standoff gunshot the revolution begins','eternity loneliness homecoming the tail wags'])

#word, start, and end are untagged
def w2vChoices(word,start,startTag,end,endTag,w2v):
	return h.get_scholar_rels(word+startTag,[(start,end)],w2v,startTag,endTag,20)

'''
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "newmicro.py", line 148, in doit
    temp = genf([None,None,None,None,None,None])
  File "newmicro.py", line 127, in <lambda>
    genf = lambda lock, fraw=fraw, w2v=w2v: gen(fraw,w2v,lock)
  File "newmicro.py", line 94, in gen
    return plugin(fraw['plug'],lock),fraw
  File "newmicro.py", line 24, in plugin
    return ''.join([x for x in list(chain.from_iterable(izip_longest(parts, words))) if x is not None])
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 1: ordinal not in range(128)
'''
def plugin(plug,words):
	parts = plug.split('W')
	try:
		return ''.join([x for x in list(chain.from_iterable(izip_longest(parts, words))) if x is not None])
	except UnicodeDecodeError:
		print "Unicooooooooooode!"
		return None

rootCache = None
#takes root node (pos), returns lowercase word
def genRoot(root,w2v):
	global rootCache,maxRoots
	pos = root['pos']
	if not rootCache:
		rootCache = wb.getAll(pos)
		if len(rootCache) > maxRoots:
			rootCache = [h.strip_tag(w) for w in h.w2vsortlistNew([x+'_'+pos for x in rootCache],[root['word']+'_'+root['pos']],w2v)[:maxRoots]]
	return random.choice(rootCache).lower()

relsCache = {}
#node is current node
#parent is parent node
#prev is previously generated word (remember parent -> child words are just a _relation_; prev is the word that rel will be applied to)
#force is boolean to force regen (ignore lock)
#w2v is w2v
#fillin is out var; starts as lock, fill in other words (replace if forced)
def genrec(node,parent,prev,force,w2v,fillin):
	i = node['index']
	if not force and fillin[i]:
		word = fillin[i]
		if parent:
			force = True #only force regen if its not the root (i.e. it has a parent)
	else:
		nodep = node['pos']
		startTag = '_'+parent['pos']
		endTag = '_'+nodep
		#maybe just have a set list to draw from for some restricted POS like IN, etc?
		choices = w2vChoices(prev,parent['word'],startTag,node['word'],endTag,w2v) #TODO: if parent is root, cache these choices!
		cacheK = (parent['word'],node['word'])
		if cacheK in relsCache:
			cnRels = relsCache[cacheK]
		else:
			cnRels = cn.getRels(parent['word'],node['word'])
			relsCache[cacheK] = cnRels
		for rel in cnRels:
			choices += [cn.stripPre(t[0]) for t in cn.getOutgoing(prev, rel)]
		final = []
		for c in choices:
			p = h.getPOS(c)
			if p == nodep:
				final.append(c)
			elif p in nodep or nodep in p or ('VB' in p and 'VB' in nodep):
				newc = h.tryPOS(c,p,nodep)
				if newc:
					final.append(newc)

		#what to do if final is empty? Maybe just plug in original word??
		if not final:
			word = node['word']
		else:
			word = random.choice(final) #Can this be smarter?

		fillin[i]=word
	if len(node['children']):
		for child in node['children']:
			genrec(child,node,word,force,w2v,fillin)

def gen(fraw,w2v,lock):
	#traverse tree; if parent locked, regen all children (set a force flag)
	root = fraw['root']
	lock[root['index']] = genRoot(root,w2v)
	genrec(root,None,None,False,w2v,lock) #lock is out var
	if None in lock:
		return None
	for i in fraw['cap']:
		lock[i] = h.firstCharUp(lock[i])
	return plugin(fraw['plug'],lock),fraw

#this function tries to get node POS to agree with w2v. W2v isn't perfect, but the more the nodes agree with it, the more results we'll get.
def processPOS(node,w2v):
	if node['pos'][-1] == '$':
		node['pos'] = node['pos'][:-1] #w2v doesn't have $, apparently...?
	old = node['word']
	useOld = False
	do = True #ugly way of doing it all again without hyphens
	while do:
		do = False
		w = node['word']
		if w+'_'+node['pos'] not in w2v:
			p = h.getPOS(w) #try to figure out POS ourselves
			if p == node['pos'] or w+'_'+p not in w2v:
				if (p == 'NNP' or node['pos'] == 'NNP') and w+'_'+'NN' in w2v:
					p = 'NN'
				elif (p == 'NNPS' or node['pos'] == 'NNPS') and w+'_'+'NNS' in w2v:
					p = 'NNS'
				elif '-' in w:
					node['word'] = ''.join(w.split('-'))
					do = True
					useOld = True
			node['pos'] = p
	if useOld and node['word']+'_'+node['pos'] not in w2v:
		node['word'] = old
	for c in node['children']:
		processPOS(c,w2v)
	
def makeFormats(w2v):
	ret = []
	for fraw in formats.makeAllRawForms():
		processPOS(fraw['root'],w2v) #Preprocess each node by checking whether word_pos is in w2v and massage them if possible
		genf = lambda lock, fraw=fraw, w2v=w2v: gen(fraw,w2v,lock)
		regen = range(6)
		del regen[fraw['root']['index']]
		ret.append((genf,(badstory, h.strip(" ".join(fraw['words']))),regen,fraw))
	return ret

#===================================================

def doit(formats,w2v,pens,retries=0,forcef=None):
	global rootCache
	rootCache = None
	if not forcef:
		f = random.choice(formats)
	else:
		f = forcef
	print f[3]['raw']
	genf = f[0]
	axis = f[1]
	canRegen = f[2]
	scoref = lambda x: h.getSkipScores(axis[0],axis[1],axis[1],x,pens)
	temp = genf([None,None,None,None,None,None])
	if temp is None:
		if retries > 5:
			return doit(formats,w2v,pens)
		print "RETRYING"
		return doit(formats,w2v,pens,retries+1,f)
	else:
		s,fraw = temp
		#return s,scoref([h.strip(s)])
		return newpriority.best(s,genf,canRegen,scoref,fraw)[0]

if __name__ == "__main__":
	w2v = word2vec.load('data/tagged.bin')
	print "Word2Vec Loaded"
	pens = penseur.Penseur()
	print "Penseur Loaded"

	formats = makeFormats(w2v)
	doit(formats,w2v,pens)

