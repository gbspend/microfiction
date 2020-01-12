import word2vec, random, newpriority, formatssw, sys
import helpers as h
from penseur import penseur
import wordbags as wb
from itertools import chain, izip_longest
import conceptnet as cn
import re
from collections import defaultdict
import hashlib
from pattern.en import article
from itertools import combinations

#newpriority = reload(newpriority)
#formats = reload(formats)

maxRoots = 60

#=FORMATS===========================================

badstory = 'plunger volcano paper the mug switches'
#axes = ('plunger volcano paper the mug switches',['bridge standoff gunshot the revolution begins','eternity loneliness homecoming the tail wags'])

#word, start, and end are untagged
def w2vChoices(word,start,startTag,end,endTag,w2v,rmax=30,rmin=10):
	assert rmax > rmin
	#1/6/2020 note: this pos/neg and tag allocation (agreement) are correct!
	maxset = set(h.get_scholar_rels(word+startTag,[(start,end)],w2v,startTag,endTag,rmax))
	minset = set(h.get_scholar_rels(word+startTag,[(start,end)],w2v,startTag,endTag,rmin))
	#print maxset-minset, minset
	return list(maxset-minset)

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
def fillRootCache(root,w2v):
	global rootCache,maxRoots
	pos = root['pos']
	rootCache = wb.getAll(pos)
	if rootCache is None:
		return False
	if len(rootCache) > maxRoots:
		rootCache = [h.strip_tag(w).lower() for w in h.w2vsortlistNew([x+'_'+pos for x in rootCache],[root['word']+'_'+root['pos']],w2v)[:maxRoots]]
	#remove top 10% (likely uninteresting)
	rootCache = rootCache[:int(len(rootCache)*.1)]
	return True
		
#takes root node (pos), returns lowercase word
def genRoot(root,w2v):
	global rootCache
	if not rootCache:
		if not fillRootCache(root,w2v):
			return None
	return random.choice(rootCache).lower()

choiceCache = {}
relsCache = {}
#node is current node
#parent is parent node
#prev is previously generated word (remember parent -> child words are just a _relation_; prev is the word that rel will be applied to)
#force is boolean to force regen (ignore lock)
#w2v is w2v
#fillin is out var; starts as lock, fill in other words (replace if forced)
def genrec(node,parent,prev,force,w2v,fillin,w2vmax,w2vmin,verbgen):
	i = node['index']
	if not force and fillin[i]:
		word = fillin[i]
		if parent:
			force = True #only force regen if its not the root (i.e. it has a parent)
	else:
		if parent['replace']:
			parent = parent['replace']
		nodep = node['pos']
		startTag = '_'+parent['pos']
		endTag = '_'+nodep
		#maybe just have a set list to draw from for some restricted POS like IN, etc?
		cacheK = (prev,parent['word'],node['word'])
		if parent['dep'] == 'root' and cacheK in choiceCache:
			choices = choiceCache[cacheK]
		else:
			
			choices = w2vChoices(prev,parent['word'],startTag,node['word'],endTag,w2v,w2vmax,w2vmin)
			if parent['dep'] == 'root': #only cache choices from root (more likely to be used, caching all is too much data for too little overlap)
				choiceCache[cacheK] = choices

		cacheK = (parent['word'],node['word'])
		if cacheK not in relsCache:
			relsCache[cacheK] = cn.getRels(parent['word'],node['word'])
		cnRels = relsCache[cacheK]
		for rel in cnRels:
			choices += [cn.stripPre(t[0]) for t in cn.getOutgoing(prev, rel)]

		final = []
		for c in choices:
			if c == node['word']: #try to find a different word
				continue
			p = h.getPOS(c)
			if p == nodep:
				final.append(c)
			elif p in nodep or nodep in p or ('VB' in p and 'VB' in nodep):
				newc = h.tryPOS(c,p,nodep)
				if newc:
					final.append(newc)

		if not final:
			word = wb.get(nodep)#grab from wordbag insteadof using node['word']
		else:
			if verbgen:
				print parent['word'],":",node['word'],"::",prev,":\n",final
				print
			word = random.choice(final) #Can this be smarter?
		if not word:
			word = node['word']

		fillin[i]=word
	if len(node['children']):
		for child in node['children']:
			genrec(child,node,word,force,w2v,fillin,w2vmax,w2vmin,verbgen)

def gen(fraw,w2v,lock,w2vmax=30,w2vmin=10,verbgen=False):
	#traverse tree; if parent locked, regen all children (set a force flag)
	root = fraw['root']
	if lock[root['index']] is None:
		new_root = genRoot(root,w2v)
		if not new_root:
			return None
		lock[root['index']] = new_root
	genrec(root,None,None,False,w2v,lock,w2vmax,w2vmin,verbgen) #lock is out var
	if None in lock:
		return None
	for i in range(len(lock)):
		if i+1 < len(lock) and (lock[i] == 'a' or lock[i] == 'an'):
			lock[i] = article(lock[i+1])
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

def allIndices(node,seen=None):
	if seen is None:
		seen = set()
	seen.add(node['index'])
	for c in node['children']:
		seen = allIndices(c,seen)
	return seen
	
def checkChars(str_to_search):
	return not bool(re.compile(r'[^! ",.;:?W]').search(str_to_search))

def posListRec(node,curr):
	p = node['pos']
	equivs = ['VB','NN','JJ','PRP','RB']
	for e in equivs:
		if p.startswith(e):
			p=e
			break
	curr[node['index']]=p
	for c in node['children']:
		posListRec(c,curr)
	return curr
	
def getstory(i,fmts):
	return h.strip(fmts[i][3]['raw'])

def garbrec(node,isRoot,curr):
	if isRoot:
		w = node['word']
	else:
		choices = wb.getAll(node['pos'])
		if not choices:
			return None
		w = random.choice(choices)
	curr[node['index']]=w
	for c in node['children']:
		garbrec(c,False,curr)
	return curr
		
def testaxes(ai1,ai2,interis,p,fmts):
	goods = [getstory(i,fmts) for i in interis if i!=ai1 and i!=ai2]
	bads = [garbrec(fmts[i][3]['root'],True,[None,None,None,None,None,None]) for i in interis] #don't necessarily need one per i... maybe just half? max 10?
	if type(ai1) == int:
		s1 = getstory(ai1,fmts)
	else:
		s1=ai1
	if type(ai2) == int:
		s2 = getstory(ai2,fmts)
	else:
		s2=ai2
	allsc = h.getSkipScores(badstory,s1,s2,goods+bads,p) #all at once is faster
	goodsc = allsc[:len(goods)]
	badsc = allsc[len(goods):]
	sumgood = sum(goodsc)
	sumbad = sum(badsc)
	return sumgood-sumbad

def makeFormats(w2v,pens,bestaxes=True,w2vmax=30,w2vmin=10,backoff=False,verbgen=False):
	ret = []
	ex = 0
	seen = set()
	for fraw in formatssw.makeAllRawForms():
		if fraw['raw'] in seen:
			continue
		seen.add(fraw['raw'])
		s = allIndices(fraw['root'])
		if s != set([0,1,2,3,4,5]) or not checkChars(fraw['plug']):
			#print "SKIP:", fraw['raw'], s
			ex +=1
			continue
		processPOS(fraw['root'],w2v) #Preprocess each node by checking whether word_pos is in w2v and massage them if possible
		genf = lambda lock, fraw=fraw, w2v=w2v, w2vmax=w2vmax, w2vmin=w2vmin, verbgen=verbgen: gen(fraw,w2v,lock,w2vmax,w2vmin,verbgen)
		regen = range(6)
		del regen[fraw['root']['index']]
		goodstory = h.strip(" ".join(fraw['words']))
		ret.append([genf,[badstory, goodstory, goodstory, True],regen,fraw])
	if ex:
		print "Number of excluded (bad) formats:",ex,"(%d total, %f%%)"%(len(ret),(float(ex)/len(ret)*100))
	
	poss = []
	for tup in ret:
		f = tup[3]
		poss.append(''.join(posListRec(f['root'],[None,None,None,None,None,None])))
	interpos = defaultdict(list) #dictionary of format index to list of other indices that have same POS
	for i,c in enumerate(poss):
		for j,p in enumerate(poss):
			if c == p and i != j:
				interpos[i].append(j)
	
	if not bestaxes:
		for i,tup in enumerate(ret):
			sames = interpos[i]
			otheraxis = None
			axes = tup[1]
			if len(sames) < 1:
				otheraxis = axes[1] #duplicate single good axis
			else:
				otheraxis = h.strip(ret[random.choice(sames)][3]['raw'])
			axes[2] = otheraxis
	else:
	#==========
	# calculated best axes for each cluster of 3+ stories (or read from file if stored there)
	# all 1- or 2-cluster formats will get 1 or 2 different axes, respectively, and be flagged (axes[3] == True) that they need the "10-20% cutoff" instead

		possets = []
		for k in interpos:
			found = False
			for s in possets:
				if k in s:
					found = True
					break
			if found:
				continue
			possets.append(set(interpos[k] + [k]))
		
		scoresfn = 'axesscores'
		axscores = {}
		with open(scoresfn,'r') as f:
			for line in f:
				line = line.strip()
				parts = line.split('\t')
				axscores[parts[0]] = float(parts[1])

		for interis in possets:
			if len(interis) == 2:
				newaxes = [getstory(j,ret) for j in interis]
				for i in interis:
					ret[i][1] = ret[i][1][:1] + newaxes + [True] #note: difference between l[:1] and 1[0] is that the former returns a list!
				continue
			#else: use non-exemplar best axes
			candidates = {}
			for ai1,ai2 in combinations(interis,2):
				k = getstory(ai1,ret)+"; "+getstory(ai2,ret)
				v = 0
				if k in axscores:
					v = axscores[k]
				else:
					v = testaxes(ai1,ai2,interis,pens,ret)
					axscores[k] = v #for posterity
				candidates[k] = v
			best = sorted(candidates.keys(),key=lambda k:candidates[k],reverse=True)
			for i in interis:
				exemplar = getstory(i,ret)
				besti = 0
				while exemplar in best[besti]: #pick the best axes that don't include the format's exemplar (avoid plagiarism)
					besti += 1
				newaxes = best[besti].split('; ')
				ret[i][1] = ret[i][1][:1] + newaxes
				

		with open(scoresfn, 'w') as fout:
			for k in axscores:
				fout.write(k+"\t"+str(axscores[k])+"\n")
	#==========
	
	if backoff:
		bests = []
		partial = []
		for f in ret:
			s = h.strip(f[3]['raw'])
			if s not in f[1]:
				bests.append(f)
			elif s != f[1][2]:
				partial.append(f)
		if bests:
			return bests
		if partial:
			return partial
	return ret

#===================================================

def randomScores(ss):
	return [h.rangify(int(hashlib.md5(s).hexdigest(),16),0,int("1"*128,2),-0.20662908,1.3317157) for s in ss]
	#from 128-bit MD5 digest ("random") to min--max from basic1D.csv (ignoring distribution)
	#The skipthought scorer _does_ output a gaussian, but maybe that's irrelevant...?

def doit(formats,w2v,pens,forcef=None,normalize=True):
	global rootCache
	rootCache = None
	
	if not forcef:
		f = random.choice(formats)
	else:
		f = forcef
	genf = f[0]
	axis = f[1]
	#print axis #TEMP
	canRegen = f[2]
	print f[3]['raw']
	root = f[3]['root']
	
	if not fillRootCache(root,w2v):
		print "Couldn't fill rootChache for root", root
		return None
	#print len(rootCache)
	stories = []
	for r in rootCache:
		temp = None
		count = 0
		while temp is None and count < 5:
			lock = [None,None,None,None,None,None]
			lock[root['index']] = r
			temp = genf(lock)
			count+=1
		if temp:
			s,fraw = temp
			stories.append(s)
			#print s
	if not stories:
		return None
	scoref = lambda x: h.getSkipScores(axis[0],axis[1],axis[2],x,pens)
	if False:
		scoref = randomScores
	temp = newpriority.best(stories,genf,canRegen,scoref,fraw,normalize)
	if temp:
		s,sc,top = temp
		return top #Below doesn't work :( They all need to get mixed together to get the best stories, and any given story may have been scored by best axes or not...
		
		#DEAD
		returnnum = 10
		if len(axis) > 3 and axis[3]: #need to take "top 20% minus top 10%":
			return top[returnnum:returnnum*2]
		else:
			return top[:returnnum]
		#return s,sc,f[3]['raw'],top
	else:
		return None

if __name__ == "__main__":
	paramsfn='params'
	
	params = {}
	params['best_axes']=True
	params['bottom_percent']=20
	params['top_percent']=10
	params['normalize']=True
	params['w2v_max']=30
	params['w2v_min']=10
	params['backoff']=False #<reducto>BACK OFF!</reducto>
	params['verb_gen']=False #verbose generation; prints x:y::a:[list]
	
	with open(paramsfn,'r') as f:
		for line in f:
			line = line.strip()
			if '=' not in line:
				continue
			k,v = line.split('=')
			v = v.strip()
			if v.isdigit():
				v = int(v)
			elif v == 'True':
				v = True
			else:
				v = False
			params[k.strip()] = v
			
	assert params['bottom_percent'] > params['top_percent']
	for k in params:
		print k,params[k]

	times = 30
	if len(sys.argv) > 1:
		times = int(sys.argv[1])
	w2v = word2vec.load('data/tagged.bin')
	print "Word2Vec Loaded"
	pens = penseur.Penseur()
	print "Penseur Loaded"

	formats = makeFormats(w2v,pens,params['best_axes'],params['w2v_max'],params['w2v_min'],params['backoff'],params['verb_gen'])
	print "Formats:",len(formats)
	
	allres = []
	for i in range(times):
		allres += doit(formats,w2v,pens,None,params['normalize'])
	allres = [a for a in allres if a]
	#print allres
	
	finalout = sorted(allres,reverse=True,key=lambda s: s[1])
	top = int(params['top_percent']/100.0*len(allres))
	bottom = int(params['bottom_percent']/100.0*len(allres))
	if top > 0 and bottom > 0:
		if top == bottom:
			top -= 1
		assert top < bottom, str(top)+", "+str(bottom)+", "+str(params['top_percent'])+", "+str(params['bottom_percent'])+", "+str(len(allres))
		if (bottom - top) > top:
			finalout = finalout[top:bottom]
	print "\nOUTPUT"
	for f in finalout:
		print f
	
	

