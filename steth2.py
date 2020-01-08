import os
import word2vec
from steth1 import untagged1

def doit(w2v,fname):
	print fname
	in10 = 0
	in30 = 0
	total = 0.0
	with open(fname,'r') as f:
		for line in f.readlines():
			if not line:
				continue
			total +=1.0
			parts = line.split(" ")
			s = parts[0]
			tag1 = s[-(len(s)-s.find("_")):]
			s = parts[1]
			tag2 = s[-(len(s)-s.find("_")):]
			w1 = parts[0]
			w1 = w1[:-(len(w1)-w1.find('_'))]
			w2 = parts[1]
			w2 = w2[:-(len(w2)-w2.find('_'))]
			rels = [(w1,w2)]
			query = parts[2]
			target = parts[3]
			target = target[:-(len(target)-target.find('_'))]
			#print "st2:",query, rels, tag1, tag2
			res = untagged1(w2v,query, rels, tag1, tag2, 10)
			#print target, res
			if target in res:
				in10+=1
			else: #if not in 10, try 30
				res = untagged1(w2v,query, rels, tag1, tag2, 30)
				if target in res:
					in30+=1
	in30+=in10 #together
	print "total:",total
	print "in10:",in10,in10/total
	print "in30:",in30,in30/total

if __name__ == '__main__':
	w2v = word2vec.load('data/tagged.bin')
	dir = "bard"
	for fname in os.listdir(dir):
		if not fname.endswith("txt"):
			continue
		else:
			doit(w2v,os.path.join(dir,fname))