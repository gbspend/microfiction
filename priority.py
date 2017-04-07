import helpers as h
import random
import heapq as hq

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

numChildren = 10
strikes = 10 #10000?
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
