import random, os
from pattern.en import parse, pluralize, comparative, superlative, conjugate, PRESENT, PAST, PARTICIPLE, INFINITIVE
import helpers as h

'''
CD Cardinal number
DT Determiner
EX Existential there
FW Foreign word
IN Preposition or subordinating conjunction
PRP Personal pronoun
PRP$ Possessive pronoun
UH Interjection
WP Wh-pronoun
WRB Wh-adverb
'''

bags = None
def fillBags():
	#print "FILLING BAGS"
	global bags
	path = os.getcwd()+'/bags/'
	bags = {}
	for f in os.listdir(path):
		with open(path+f) as f:
			content = f.readlines()
		for line in content:
			line = line.strip()
			parts = line.split('\t')
			h.addToDictList(bags, parts[1], parts[0])

def get(pos):
	l,f = getList(pos)
	if l is None:
		return None
	ret = random.choice(l)
	if f:
		ret = f(ret)
	return ret

def getAll(pos):
	l,f = getList(pos)
	if l is None:
		return None
	if f:
		return [f(x) for x in l]
	return l

#MD, PDT, RP, WDT scraped from exemplar stories
other = {'WRB':['what', 'who', 'which', 'whom', 'whose'],'MD': ['would', 'shall', 'could', 'should', 'will', 'can', 'must'], 'PDT': ['all', 'half'], 'RP': ['off', 'over', 'back', 'up', 'down', 'away', 'out'], 'WDT': ['whatever', 'that']}

#returns a (list,function) tuple; function may be None
def getList(pos):
	global bags
	if not bags:
		fillBags()
	f = None
	if pos in ['JJ','JJR','JJS','RB','RBR','RBS']:
		if 'JJ' in pos:
			l = bags['JJ']
		else:
			l = bags['RB']
		if pos[-1] == 'R':
			f = comparative
		elif pos[-1] == 'S':
			f = superlative
		return l,f
	if 'VB' in pos:
		l = bags['VB']
		t = ''
		if pos == 'VBD':
			t = PAST
		if pos == 'VBP':
			t = INFINITIVE
		if pos == 'VBZ':
			t = PRESENT
		if pos == 'VBN':
			t = PAST+PARTICIPLE
		if pos == 'VBG':
			t = PARTICIPLE
		if t:
			f = lambda x: conjugate(x,tense=t)
		return l,f
	if 'NN' in pos:
		#separate bag for NNP?
		l = bags['NN']
		if pos[-1] == 'S':
			f = pluralize
		return l,f
	if pos == 'WP$':
		return h.WPD.values(),None
	if pos == 'PRP$':
		return h.PRPD.values(),None
	if pos in other:
		return other[pos],None

	if pos == 'FW':
		pos = 'NN'
	if pos in bags:
		return bags[pos],None
	else:
		print "No bag for",pos
		return None,None
