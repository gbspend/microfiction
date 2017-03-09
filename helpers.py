from nltk.corpus import wordnet as wn
import string

def synName(s):
	return s.lemma_names()[0]

def nounify(verb_word):
	set_of_related_nouns = set()

	m = wn.morphy(verb_word, wn.VERB)
	if m is not None:
		for lemma in wn.lemmas(m, pos="v"):
			for related_form in lemma.derivationally_related_forms():
				for synset in wn.synsets(related_form.name(), pos=wn.NOUN):
					if not synName(synset)[0].isupper(): #filters out proper nouns
						set_of_related_nouns.add(synset)

	return set_of_related_nouns

def baseWord(word):
	base = wn.morphy(word)
	if base is None:
		return word
	return base


def dist(s1, s2):
	if len(s1) > len(s2):
		s1, s2 = s2, s1

	distances = range(len(s1) + 1)
	for i2, c2 in enumerate(s2):
		distances_ = [i2+1]
		for i1, c1 in enumerate(s1):
			if c1 == c2:
				distances_.append(distances[i1])
			else:
				distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
		distances = distances_
	return distances[-1]

def toNoun(w):
	for ss in wn.synsets(w):
		if ss.pos() == 'n':
			return w
	related = nounify(w)
	best = w
	mindist = 100000
	for r in related:
		s = synName(r)
		d = dist(s,w)
		if d < mindist:
			mindist = d
			best = s
	return best

def strip(s):
	return str(s).translate(None, string.punctuation).lower()

def firstCharUp(s):
	return s[0].upper() + s[1:]

#takes in a list of words and returns the ones that match part of speech p ('n' or 'v' for example) (unmorphied)
#if "extra" is True: add all synset names that are related (example: 'chair' (verb) would return 'chair' and 'moderate')
def pos(a,p):
	ret = set()
	for i in a:
		m = wn.morphy(i)
		if m is None:
			continue
		for ss in wn.synsets(m):
			if ss.pos() == p:
				ret.add(i)
	return list(ret)

#Ideas:
#wn.synsets(word) -> lemmas -> names (to "cast a wider net")

#use w2v to make our own "relations": give it [(nail,hammer),(horse,ride)] and pass in king
#see nancy's notes in Slack



