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
	global bags
	if not bags:
		fillBags()
	if pos in ['JJ','JJR','JJS','RB','RBR','RBS']:
		if 'JJ' in pos:
			word = random.choice(bags['JJ'])
		else:
			word = random.choice(bags['RB'])
		if pos[-1] == 'R':
			word = comparative(word)
		elif pos[-1] == 'S':
			word = superlative(word)
		return word
	if 'VB' in pos:
		word = random.choice(bags['VB'])
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
			word = conjugate(word,tense=t)
		return word
	if 'NN' in pos:
		#separate bag for NNP?
		word = random.choice(bags['NN'])
		if pos[-1] == 'S':
			word = pluralize(word)
		return word
	if pos == 'WP$':
		return random.choice(h.WPD.values())
	if pos == 'PRP$':
		return random.choice(h.PRPD.values())
	if pos == 'WRB':
		return random.choice(['what', 'who', 'which', 'whom', 'whose'])

	if pos == 'FW':
		pos = 'NN'
	if pos in bags:
		return random.choice(bags[pos])
	else:
		print "No bag for",pos
		return None
