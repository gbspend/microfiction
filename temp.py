import word2vec, newmicro
from penseur import penseur
w2v = word2vec.load('data/tagged.bin')
pens = penseur.Penseur()
formats = newmicro.makeFormats(w2v,pens)

newmicro.doit(formats,w2v,pens)[:3]



#recursive; returns list of POS in order
def poss(node,l = None):
	if l is None:
		l = [None,None,None,None,None,None]
	l[node['index']] = node['pos']
	for c in node['children']:
		l = poss(c,l)
	return l

from collections import defaultdict
d = defaultdict(list)
for f in formats:
	f = f[3]
	print f['raw']
	s = " ".join(poss(f['root']))
	if s in d:
		print "DUPE:",s,f['raw']
	d[s].append(f)
	print s






def icheck(node,seen=None):
	if seen is None:
		seen = set()
	seen.add(node['index'])
	for c in node['children']:
		seen = icheck(c,seen)
	return seen

for i,f in enumerate(formats):
	f = f[3]
	s = icheck(f['root'])
	if not s == set([0,1,2,3,4,5]):
		print "BAD",i,":", f['raw'], s, "(",f['plug'],")"
#newmicro now filters these out... maybe don't filter so I can poke around in REPL and see what's wrong?
	


import re
def findR(formats, regex):
	for f in formats:
		f = f[3]
		if "'" not in f['raw'] and re.search(regex, f['plug']):
			print f['raw'],f['plug']


ws = list(set([f[3]['plug'] for f in formats]))
cs = set()
for w in ws:
	for c in w:
		cs.add(c)

for c in cs:
	sub = [w for w in ws if c in w]
	if len(sub) < 5:
		print c
		for s in sub:
			print '\t%s'%s
	else:
		print c, len(sub), sub[0]




#generate list of concat'ed POS (in order!) for each story
import helpers as h
from collections import defaultdict
def posrec(node,curr):
	p = node['pos']
	equivs = ['VB','NN','JJ','PRP','RB']
	for e in equivs:
		if p.startswith(e):
			p=e
			break
	curr[node['index']]=p
	for c in node['children']:
		posrec(c,curr)
	return curr

import wordbags as wb
import random
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

poss = []
garbs = []
for tup in formats:
	f = tup[3]
	pl = posrec(f['root'],[None,None,None,None,None,None])
	poss.append(''.join(pl))
	grb = garbrec(f['root'],True,[None,None,None,None,None,None])
	if not grb or None in grb:
		garbs.append(None)
	else:
		ret = [h.strip(grb)]
		for i,w in enumerate(f['words']):
			grb[i]=w
			ret.append(h.strip(grb))
		garbs.append(ret)

interpos = defaultdict(list) #dictionary of format index to list of other indices that have same POS
for i,c in enumerate(poss):
	for j,p in enumerate(poss):
		if c == p and i != j:
			interpos[i].append(j)





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





import helpers as h

def getstory(i):
	return h.strip(formats[i][3]['raw'])

def getinterstories(i):
	ret = [getstory(i)]
	for j in interpos[i]:
		ret.append(getstory(j))
	return ret

from itertools import combinations
import matplotlib.pyplot as plt
badstory = 'plunger volcano paper the mug switches'
def testaxes(ai1,ai2,interis,p,graph=False):
	goods = [getstory(i) for i in interis if i!=ai1 and i!=ai2]
	bads = [garbs[i][0] for i in interis]
	if type(ai1) == int:
		s1 = getstory(ai1)
	else:
		s1=ai1
	if type(ai2) == int:
		s2 = getstory(ai2)
	else:
		s2=ai2
	allsc = h.getSkipScores(badstory,s1,s2,goods+bads,p)
	goodsc = allsc[:len(goods)]
	badsc = allsc[len(goods):]
	if graph:
		plt.plot(goodsc)
		plt.plot(badsc)
		plt.show()
		return None
	else:
		sumgood = sum(goodsc)
		sumbad = sum(badsc)
		#print sumgood,sumbad
		return sumgood-sumbad

scoresfn = 'axesscores'
axscores = {}
with open(scoresfn,'r') as f:
	for line in f:
		line = line.strip()
		parts = line.split('\t')
		axscores[parts[0]] = float(parts[1])

for interis in possets:
	print interis,[formats[i][3]['raw'] for i in interis]
	if len(interis) == 2:
		print "Len 2"
		newaxes = [getstory(j) for j in interis]
		for i in interis:
			print formats[i][3]['raw'],": old axes:",formats[i][1]
			formats[i][1] = formats[i][1][:1] + newaxes + [True]
			print "new axes:",formats[i][1]
		#axes[3] == True marks that it needs 10-20% cutoff because it can't have "best axes"
		continue
	#else: use non-exemplar best axes
	candidates = {}
	for ai1,ai2 in combinations(interis,2):
		k = getstory(ai1)+"; "+getstory(ai2)
		v = 0
		if k in axscores:
			v = axscores[k]
		else:
			v = testaxes(ai1,ai2,interis,pens)
			axscores[k] = v #for posterity
		candidates[k] = v
	best = sorted(candidates.keys(),key=lambda k:candidates[k],reverse=True)
	for i in interis:
		exemplar = getstory(i)
		besti = 0
		while exemplar in best[besti]: #pick the best axes that don't include the format's exemplar (avoid plagiarism)
			besti += 1
		newaxes = best[besti].split('; ')
		print formats[i][3]['raw'],": old axes:",formats[i][1]
		formats[i][1] = formats[i][1][:1] + newaxes
		print "new axes:",formats[i][1]
		

with open(scoresfn, 'w') as fout:
	for k in axscores:
		fout.write(k+"\t"+str(axscores[k])+"\n")






testn=559
interis = interpos[559] + [559]
results = {}
for ai1,ai2 in combinations(interis,2):
	k = getstory(ai1)+"; "+getstory(ai2)
	v = testaxes(ai1,ai2,interis,pens)
	print k,v,"\n"
	results[k] = v

mx = 0
nx = 100
mv = None
nv = None
for k in results:
	c = results[k]
	if c > mx:
		mx = c
		mv = k
	if c < nx:
		nx = c
		nv = k








#generate best/worst graphs
def getindex(s):
	for i,f in enumerate(formats):
		if h.strip(f[3]['raw']) == s:
			return i

def twois():
	a = random.choice(interis)
	b = random.choice(interis)
	while a == b:
		b = random.choice(interis)
	return a,b

def randmultitest():
	print
	s1,s2 = [getstory(i) for i in twois()]
	somegarbs = set()
	while len(somegarbs) < 20:
		somegarbs.add(tuple(random.choice(garbs)))
	samelevels = [[],[],[],[],[],[],[]]
	for gs in somegarbs:
		for i,g in enumerate(gs):
			samelevels[i].append(g)
	i = 0
	for l in samelevels:
		plt.plot(h.getSkipScores(badstory,s1,s2,l,pens),label=str(i))
		i+=1
	plt.legend()
	plt.show()

#randmultitest()



#a/an via pattern.en doesn't work wel...
#only switch from an to a, not vice versa...?
from pattern.en import article,suggest
import helpers as h
stories = []
with open('compareresults','r') as f:
	for line in f:
		line = line.strip()
		if line and line[-1] in "1234567890":
			stories.append(h.strip(line[:line.rfind(' ')]).split(' '))

sps = []
for s in stories:
	for w in s:
		sp = suggest(w)
		if len(sp) > 1:
			sps.append([w]+sp)

def fixaan(l):
	for i in range(len(l)):
		if l[i] == 'a' or l[i] == 'an':
			newa = article(l[i+1])
			if newa == 'an':
				print l,i
			elif newa == 'a' and newa != l[i]:
				print l,i
				l[i] = newa

for s in stories:
	fixaan(s)














