#python infstories.py > /dev/null 2>&1 &
#jobs -l
#kill [PID]
import micro, newmicro, word2vec, os, random
from penseur import penseur

#lines is array
def writeList(fname, lines):
	if os.path.exists(fname):
		o = 'a' # append if already exists
	else:
		o = 'w' # make a new file if not
	with open(fname,o) as f:
		f.write('\n'.join(lines)+'\n')

if __name__ == "__main__":
	w2v = word2vec.load('data/tagged.bin')
	pens = penseur.Penseur()
	formats = newmicro.makeFormats(w2v)
	for i in range(1000):#while True:
		form = random.choice(formats)
		s,score = newmicro.doit(formats,w2v,pens,forcef=form)
		l = [form[3]['raw'], s,str(score),'']
		writeList('newstories',l)



