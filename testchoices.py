import datamuse as dm
import conceptnet as cn
import sys
import helpers as h

dmrs = ['bga','trg'] #Datamuse relations
cnrs = ['CapableOf','UsedFor','Desires'] #ConceptNet relations

def isint(value):
	try:
		int(value)
		return True
	except ValueError:
		return False

def addScore(d,source,score):
	if source not in d:
		d[source] = 0
	d[source] += score

#adds every element of list a to set s
def addAllDict(d,a,source):
	for i in a:
		if i not in d:
			d[i] = {'score':0, 'sources':set()}
		d[i]['sources'].add(source)

def ask(topic,noun,word):
	m = "[0-10] How related to "+noun+"("+topic+") is the word: "+word+"\n"
	s = 'nope'
	while not isint(s):
		s = raw_input(m)
		if isint(s):
			i = int(s)
			if i < 0 or i > 10:
				s = 'nope'
	return int(s)

def doit(topic, parent,pos):
	choices = {}
	for r in dmrs:
		addAllDict(choices,h.pos([x[0] for x in dm.query(dm.related(r,noun),dm.topics(topic))],pos),'dm:'+r)
	for r in cnrs:
		for phrase in [x[1] for x in cn.getOutgoing(noun,r)]:
			addAllDict(choices,h.pos(phrase.split(),pos),'cn:'+r)
	#add w2v "custom relation" thing
	print len(choices.keys())
	scores = {}
	for k in choices.keys():
		s = ask(topic,noun,k)
		s -= 5 #(-5 to 5 scale)
		choices[k]['score'] += s
		for src in choices[k]['sources']:
			addScore(scores,src,s)
	print "Best words",sorted(choices.keys(), key=lambda x:choices[x]['score'], reverse=True)
	print "Best sources",scores

if __name__ == "__main__":
	doit(sys.argv[1],sys.argv[2],sys.argv[3])
