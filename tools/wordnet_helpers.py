from nltk.corpus import wordnet as wn

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
	while True:
		last = word
		word = wn.morphy(word)
		if word is None:
			return last
		if last == word:
			return word

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

# Need something better for this.
def is_noun(word):
	return wn.morphy(word, wn.NOUN) == word
