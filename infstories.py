#python infstories.py > /dev/null 2>&1 &
#ps aux | grep 
#jobs -l
#kill [PID]
import micro, newmicro, word2vec, os, random, sys
from penseur import penseur

#lines is array
def writeList(fname, lines):
	if os.path.exists(fname):
		o = 'a' # append if already exists
	else:
		o = 'w' # make a new file if not
	with open(fname,o,0) as f:
		f.write('\n'.join(lines)+'\n')

if __name__ == "__main__":
	w2v = word2vec.load('data/tagged.bin')
	pens = penseur.Penseur()
	formats = newmicro.makeFormats(w2v)
	for i in range(1000):#while True:
		try:
			temp = newmicro.doit(formats,w2v,pens)
			if temp:
				s,score,raws = temp
				l = [raws,s,str(score),'']
				print l
				writeList('newstories',l)
		except:
			print "Unexpected error:", sys.exc_info()[0]
			print "continuing..."


