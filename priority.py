import helpers as h
import random
import heapq as hq
import oxdict as od

numChildren = 10
strikes = 7#10

class Niche:
	def __init__(self,v, node):
		self.verb = v
		self.intrans = od.checkVerb(v)
		self.isDead = not self.intrans
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
			print "NEW BEST:",self.bestch.s,self.bestch.score
			return True
		return False

	def push(self,node):
		if self.stale > strikes or not self.intrans:
			return
		if not self.heap:
			#if self.isDead:
			#	print self.verb, "REANIMATED"
			self.isDead = False
		hq.heappush(self.heap,(-node.score,node))

	def step(self):
		if self.isDead:
			return []
		if not self.heap:
			self.isDead = True
			#print self.verb, "DIED: heap empty"
			return []
		curr = hq.heappop(self.heap)[1]
		#print curr.s,curr.score
		if not self.checkBest(curr):
			self.stale += 1
			if self.stale > strikes:
				self.isDead = True
				#print self.verb, "DIED: struck out"
				return []
		childs = []
		for i in xrange(numChildren):
			newch = curr.getChild()
			if newch is not None:
				childs.append(newch)
		return childs
'''
		if not childs:
			return []
		raw = [" ".join(c.words) for c in childs]
		scores = self.scoref(raw)
		ret = []
		for i,child in enumerate(childs):
			child.score = scores[i]
			if h.getV(child.s) != self.verb:
				ret.append(child)
			else:
				hq.heappush(self.heap,(-child.score,child))
		return ret
'''


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
		news = self.sett.regen(lock)
		if not news:
			return None
		node = Node(news,self.sett)
		if len(set(node.words)) != len(node.words) or node.s == self.s: #duplicate or didn't change
			return None
		return node


def best(s,regenf,canRegen,scoref):
	niches = {}
	verb = h.getV(s)
	root = Node(s,Settings(regenf,canRegen))
	root.score = scoref([s])[0]
	ni = Niche(verb,root)
	niches[verb] = ni
	while True:
		print "--------------------------------"
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
			v = h.getV(child.s)
			if v not in niches:
				ni2 = Niche(v,child)
				niches[v] = ni2
			else:
				niches[v].push(child)
	choices = []
	for v in niches:
		n = niches[v]
		if not n.intrans:
			continue
		print n.bestch.s,n.bestsc
		choices.append((n.bestch,n.bestsc))
	m = min([c[1] for c in choices])
	if m >=0:
		m = 0
	i = h.weighted_choice(choices,-m)
	best = choices[i][0]
	return best.s,best.score

'''
heap = []
#s is initial artifact
#regenf,canRegen,scoref: see Settings __init__ (identical params)
def best(s,regenf,canRegen,scoref):
	root = Node(s,Settings(regenf,canRegen))
	root.score = scoref([s])[0]
	hq.heappush(heap,(-root.score,root))
	bestsc = root.score
	bestch = root
	count = 0
	print "starting priority loop"
	while True:
		if not heap:
			break
		curr = hq.heappop(heap)[1]
		print curr.s,curr.score
		if curr.score > bestsc:
			bestsc = curr.score
			bestch = curr
			count = 0
			print "NEW BEST:",bestch.s,bestch.score
		else:
			count += 1
			if count > strikes:
				break
		childs = []
		for i in xrange(numChildren):
			newch = curr.getChild()
			if newch is not None:
				childs.append(newch)
		if not childs:
			continue
		raw = [" ".join(c.words) for c in childs]
		scores = scoref(raw)
		for i,child in enumerate(childs):
			child.score = scores[i]
			hq.heappush(heap,(-child.score,child))
	return bestch.s,bestsc
'''
