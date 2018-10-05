import os, string, re

holds = [("'s","*&")] #things that should just be left in plug
def makeEmptyFormat(s):
	s = string.replace(s,'\xe2\x80\xa6','...') #elipses unicode char
	form = {'raw':s}
	plug = ''
	cap = []
	count = 0
	inWord = False
	words = []
	currWord = ''
	for h in holds:
		s = string.replace(s,h[0],h[1])
	for c in s:
		if c.isalpha() or c=='-':
			if inWord:
				currWord += c
				continue
			else:
				inWord = True
				currWord += c
				plug += 'W'
				if c.isupper():
					cap.append(count)
				count += 1 #0-indexed
		else:
			if inWord:
				words.append(currWord)
			inWord = False
			plug += c
			currWord = ''
	for h in holds:
		plug = string.replace(plug,h[1],h[0])
	form['plug'] = plug
	form['cap'] = cap
	form['words'] = words
	return form
	
def makeNode():
	return {'word':'', 'index':-1, 'pos':'', 'dep':'', 'children':[]}

def arrayIns(a,i,v):
	a += [None]*(i-len(a)+1)
	a[i]=v

def numberRec(n,i):
	n['index'] = i
	if len(n['children']) > 0:
		for c in n['children']:
			numberRec(c,i+1)

def isBadFormat(form):
	return 'root' not in form or len(form['words']) != 6

punc = ''.join(string.punctuation.split('-'))
marker = ' -> '

def setIndRec(node, correct_inds):
	node['index'] = correct_inds.index(node['index'])
	for c in node['children']:
		setIndRec(c,correct_inds)

'''
A format consists of:
	raw:	Raw story
	words:	List of words to look for in dependency tree nodes
	root:	Root node
	plug:	Numbered, punctuated "plug-in story" (e.g. "Sorry Katie," sighed Santa; "No witnesses." -> "W W," W W; "W W." (split on 'W')) 
	cap:	Set 0-indexed of capitalized words (e.g. "Sorry Katie," sighed Santa; "No witnesses." -> set([0,1,3,4]))
A node consists of:
	word:	Lower case word
	pos:	POS
	dep:	The dependency node type (root, advmod, etc)
	index:	A 0-indexed position ("index") in the story (corresponds to "plug-in story" numbers)
  children:	A list of children
	[That's it, all the "relation" processing will happen later]
	[Intentionally doesn't include raw line, because the number is irrelevantdue to "needShift"]
'''
def makeRawForms(fname):
	ret = []
	with open(fname) as f:
	    content = f.readlines()
	curr = None
	last = []
	used_indices = set()
	for line in content:
		line = line.strip()
		if not line:
			continue
		if marker not in line:
			if curr is not None and not isBadFormat(curr):
				#postprocess fixing indexes (currently they are in the correct order but not necessarily
				setIndRec(curr['root'], sorted(list(used_indices))) #the raw index's index in "used_indices" is correct index :P
				ret.append(curr)
			curr = makeEmptyFormat(line)
			last = []
			used_indices = set()
		else:
			parts = line.split()
			n = int(parts[0])
			wordparts = parts[2].split('/')
			word = wordparts[0]
			if not any(c.isalpha() for c in word) or word not in curr['words']:
				continue #if there are no letters in the dependency node or if it's not a word in the story
			if any(c in word for c in punc):
				print curr['raw']
				print word,"HAS PUNCT"
			node = makeNode()
			node['word'] = word.lower()
			node['pos'] = wordparts[1]
			node['dep'] = parts[3][1:-1]
			node['index'] = int(parts[4]) #not guaranteed to be 0-5
			used_indices.add(node['index'])
			if len(last) == 0:
				last.append(node)
				curr['root'] = node
			else:
				if n-1 > len(last)-1:
					n = len(last)
				arrayIns(last,n,node)
				last[n-1]['children'].append(node)
	return ret
			
#0 -> friend/NN (root)

def makeAllRawForms():
	path = os.getcwd()+'/corpus/'
	ret = []
	for f in os.listdir(path):
		ret += makeRawForms(path+f)
	return ret

#NOTES:
#Maybe choose some POS that are never "locked" (articles, what else?)
#Ex: try only unlocking leaf nodes in the primitive hierarchy? /shrug
