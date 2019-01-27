import helpers as h
import random
import heapq as hq

numChildren = 4
strikes = 3
maxSpecies = 10

class Species:
	def __init__(self,s,node):
		self.seed = s
		self.isDead = False
		self.heap = []
		self.stale = 0
		self.bestsc = node.score
		self.bestch = node
		self.push(node)

	def checkBest(self,curr):
		if curr.score > self.bestsc:
			self.bestsc = curr.score
			self.bestch = curr
			self.stale = 0
			return True
		return False

	def push(self,node):
		if self.stale > strikes:
			return
		if not self.heap:
			self.isDead = False
		hq.heappush(self.heap,(-node.score,node))

	def step(self):
		if self.isDead:
			return []
		if not self.heap:
			self.isDead = True
			return []
		curr = hq.heappop(self.heap)[1]
		if not self.checkBest(curr):
			self.stale += 1
			if self.stale > strikes:
				self.isDead = True
				return []
		childs = []
		for i in xrange(numChildren):
			newch = curr.getChild()
			if newch is not None:
				childs.append(newch)
		return childs


class Settings:
	#rf is function that takes a "locks" list (see "formats" functions in micro.py)
	#canR is list of indices that can be regenerated
	def __init__(self,rf,canR):
		self.regen = rf
		self.canRegen = canR

class Node:
	#s is string (artifact)
	#sett is Settings object
	def __init__(self,s,sett):
		self.sett = sett
		self.s = s
		self.words = h.strip(s).split()
		self.score = None#sett.calcScore
		#print "--Created node [",s,"]",self.score

	def getChild(self):
		i = random.choice(self.sett.canRegen)
		lock = self.words[:]
		lock[i] = None
		temp = self.sett.regen(lock)
		if not temp:
			return None
		news,fraw = temp
		if not news:
			return None
		child = Node(news,self.sett)
		#TODO! This rejects too many, I think? Test more! Maybe make it not match the original story...?
		#if h.numMatch(self.words,child.words) > 2: #too similar
		#	print self.words,child.words
		#	return None
		return child
		
def getIndex(story, i):
	return h.strip(story.split(' ')[i])

#stories can be a string or list
#NOT STRIPPED
def best(stories,regenf,canRegen,scoref,fraw):
	if type(stories) != list:
		stories = [stories]
	species = {}
	seedi = fraw['root']['index']
	
	bad = True
	for s in stories:
		if not s:
			continue
		seed = getIndex(s,seedi)
		root = Node(s,Settings(regenf,canRegen))
		root.score = scoref([s])[0]
		species[seed] = Species(seed,root)
		bad = False
	if bad:
		print "Refiner got no stories!"
		return None
		
	while True:
		#print "--------------------------------"
		children = []
		allDead = True
		for k in sorted(species.keys(),key=lambda x: species[x].bestsc,reverse=True)[:maxSpecies]:
			p = species[k]
			if not p.isDead:
				allDead = False
				children += p.step()
		if allDead and not children:
			break
		if not children:
			continue
		#print "Num species, children:",len(species.keys()),",",len(children)
		#raw = [h.strip(c.s) for c in children]
		scores = scoref([c.s for c in children])
		for i,child in enumerate(children):
			child.score = scores[i]
			k = getIndex(child.s,seedi)
			if k not in species:
				ni2 = Species(k,child)
				species[k] = ni2
			else:
				species[k].push(child)
		#print len(species)
	choices = []
	for k in species:
		p = species[k]
		#print p.bestch.s,p.bestsc
		choices.append((p.bestch,p.bestsc))
	choices = sorted(choices,key=lambda x: x[1],reverse=True)[:maxSpecies]
	top = []
	for c in choices:
		top.append((c[0].s,c[1]))
		print c[0].s,c[1]
	m = min([c[1] for c in choices])
	if m >=0:
		m = 0
	i = h.weighted_choice(choices,-m)
	best = choices[i][0]
	return best.s,best.score,top
