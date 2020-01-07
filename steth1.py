from collections import defaultdict
import word2vec, newmicro
w2v = word2vec.load('data/tagged.bin')

def get_scholar_rels(start, relations, w2v, tag1, tag2,num=10):
	counts = defaultdict(float)
	ret = []
	for rel in relations:
		positives = [rel[1] + tag2, start]
		negatives = [rel[0] + tag1]
		flag = False
		for w in positives+negatives:
			if w not in w2v:
				print w,"not in w2v"
				flag = True
				break
		if flag:
			print "some words not in w2v"
			continue

		idxs, metrics = w2v.analogy(pos=positives, neg=negatives, n=num)
		res = w2v.generate_response(idxs, metrics).tolist()
		ret += res
		for x in res:
			counts[x[0]] += x[1]

	ret = [x[0] for x in ret]
	ret = sorted(ret, key=counts.get, reverse=True)
	ret = [x[:-(len(x)-x.find('_'))] for x in ret]
	ret = list(set(ret)) # remove duplicates

	return ret
	
def onlyPosMatches(tagged_res,pos):
	ret = []
	for w in tagged_res:
		i = w.find('_')
		if w[-(len(w)-i):] == pos:
			ret.append(w[:-(len(w)-i)])
	return ret

def test1(w2v,poss,negs,num=10):
	for w in poss+negs:
		if w not in w2v:
			print w,"not in w2v!"
			return None
	
	idxs, metrics = w2v.analogy(pos=poss, neg=negs, n=num)
	ret = w2v.generate_response(idxs, metrics).tolist()
	
	ret.sort(key=lambda t:t[1], reverse=True)
	ret = [x[0] for x in ret]
	
	#ret = [x[:-(len(x)-x.find('_'))] for x in ret]
	ret = list(set(ret)) # remove duplicates
	return ret

#relations:
#	boy->prince
#	man->king
#query:
#	woman->???
#tag1/2: POS tag preceded by _ ("_NN")
#LHS (boy, man) negative, RHS + query (king, prince, woman) positive
#LHS + query use tag1, RHS use tag2
#filter by tag2
def untagged1(w2v,query, relations, tag1, tag2, num=10):
	ret = []
	for rel in relations:
		positives = [rel[1] + tag2, query + tag1]
		negatives = [rel[0] + tag1]
		flag = False
		for w in positives+negatives:
			if w not in w2v:
				flag = True
				break
		if flag:
			continue
	
		idxs, metrics = w2v.analogy(pos=positives, neg=negatives, n=num)
		res = w2v.generate_response(idxs, metrics).tolist()
		ret += res
	
	ret = [x[0] for x in ret]
	ret = onlyPosMatches(ret,tag2)
	ret = list(set(ret)) # remove duplicates (undoes sort!)
	return ret

#same as untagged1, but puts all relations into one analogy
def untagged2(w2v,query, relations, tag1, tag2, num=10):
	positives = [query + tag1]
	negatives = []
	for rel in relations:
		newpos = rel[1] + tag2
		newneg = rel[0] + tag1
		if newpos in w2v and newneg in w2v:
			positives.append(newpos)
			negatives.append(newneg)
	
	idxs, metrics = w2v.analogy(pos=positives, neg=negatives, n=num)
	ret = w2v.generate_response(idxs, metrics).tolist()
	
	ret = [x[0] for x in ret]
	ret = onlyPosMatches(ret,tag2)
	ret = list(set(ret)) # remove duplicates (undoes sort!)
	return ret

'''

test1(w2v,["dog_NN","cat_NN"],["meow_VB"],30)

#compare!
untagged1(w2v,"woman",[("boy","prince"),("man","king")],"_NN","_NN",10)
untagged2(w2v,"woman",[("boy","prince"),("man","king")],"_NN","_NN",10)
onlyPosMatches(test1(w2v,["king_NN","prince_NN","woman_NN"],["man_NN","boy_NN"],10),"_NN")

idxs, metrics = w2v.analogy(pos=["king_NN","prince_NN","woman_NN"],neg=["man_NN","boy_NN"],n=10)
ret = w2v.generate_response(idxs, metrics).tolist()

'''






























