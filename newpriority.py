import helpers as h
import random
import heapq as hq
import oxdict as od

numChildren = 10
strikes = 7#10

class Niche:
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
		news,fraw = self.sett.regen(lock)
		if not news:
			return None
		node = Node(news,self.sett)
		if len(set(node.words)) != len(node.words) or node.s == self.s: #duplicate or didn't change
			return None
		return node
		
def getIndex(story, i):
	return h.strip(story.split(' ')[i])

#s is story NOT STRIPPED
def best(s,regenf,canRegen,scoref,fraw):
	niches = {}
	seedi = fraw['root']['index']
	seed = getIndex(s,seedi)
	root = Node(s,Settings(regenf,canRegen))
	root.score = scoref([h.strip(s)])[0]
	niches[seed] = Niche(seed,root)
	while True:
		#print "--------------------------------"
		children = []
		allDead = True
		for k in niches:
			n = niches[k]
			if not n.isDead:
				allDead = False
				children += n.step()
		if allDead and not children:
			break
		if not children:
			continue
		raw = [" ".join(c.words) for c in children]
		scores = scoref(raw)
		for i,child in enumerate(children):
			child.score = scores[i]
			k = getIndex(child.s,seedi)
			if k not in niches:
				ni2 = Niche(k,child)
				niches[k] = ni2
			else:
				niches[k].push(child)
	choices = []
	for k in niches:
		n = niches[k]
		print n.bestch.s,n.bestsc
		choices.append((n.bestch,n.bestsc))
	m = min([c[1] for c in choices])
	if m >=0:
		m = 0
	i = h.weighted_choice(choices,-m)
	best = choices[i][0]
	return best.s,best.score
