import helpers as h
import random

class Settings:
	#rf is function that takes a "locks" list (see "formats" functions in micro.py)
	#canR is list of indices that can be regenerated
	#sf is a score function that takes a string (artifact) and returns a score where higher is better
	def __init__(self,rf,canR,sf):
		self.regen = rf
		self.canRegen = canR
		self.calcScore = sf

class Node:
	#s is string (artifact)
	#sett is Settings object
	def __init__(self,s,sett):
		self.sett = sett
		self.s = s
		self.words = h.strip(s).split()
		self.score = sett.calcScore(s)
		self.count = len(sett.canRegen)
		self.children = [None] * len(sett.canRegen)
		#print "Created node [",s,"]",self.score

	def getChild(self,i):
		if self.children[i] == None:
			lock = self.words[:]
			lock[i] = None
			news = self.sett.regen(lock)
			self.children[i] = Node(news,self.sett)
		return self.children[i]

#s is initial artifact
#regenf,canRegen,scoref: see Settings __init__ (identical params)
def best(s,regenf,canRegen,scoref):
	root = Node(s,Settings(regenf,canRegen,scoref))
	best = bestrec(root,root.score,0)
	return best[0].s,best[1] #return with score for now

#returns string,score
def bestrec(node,bestsc,ts):
	bestch = None
	for i in range(node.count):
		n = node.getChild(i)
		if n.score > node.score and n.score > bestsc: #IMPORTANT: search can't find "hidden" bests. Maybe OK, revisit!
			print "\t"*ts,"Examining:",n.s
			bestch,bestsc = bestrec(n,bestsc,ts+1)
			print "\t"*ts,"Current best:",bestch.s,bestsc
	if bestch == None:
		bestch = node
	return bestch, bestsc
