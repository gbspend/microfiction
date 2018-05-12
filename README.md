# microfiction
CS673 - Winter 2017

***Setup***

install:

	apt-get install python-dev g++ python-tk libblas-dev
	
	pip install matplotlib numpy scipy cython requests nltk pattern word2vec Theano
	

download:

	Download https://drive.google.com/file/d/1srOUFidQ9fV240wyF7GW4eqF6raCawBV/view (for ssh: download in OS and use (p)scp), place posttagged_wikipedia_for_word2vec.bin in ./data folder, and rename to tagged.bin (discard the rest)

	https://github.com/danielricks/penseur (place in ./penseur folder)
	
	Paste the snippet from pens_func at the bottom of ./penseur/penseur.py
	
	Touch __init__.py in ./penseur folder
	
	In ./penseur/skipthoughts.py line 94, change to Verbose=False

run:
	In ./data folder-
	
	wget http://www.cs.toronto.edu/~rkiros/models/dictionary.txt
		
	wget http://www.cs.toronto.edu/~rkiros/models/utable.npy
		
	wget http://www.cs.toronto.edu/~rkiros/models/btable.npy
		
	wget http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz
		
	wget http://www.cs.toronto.edu/~rkiros/models/uni_skip.npz.pkl
		
	wget http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz
		
	wget http://www.cs.toronto.edu/~rkiros/models/bi_skip.npz.pkl
		

in python:

	import nltk
	
	nltk.download('wordnet')
	
	nltk.download('punkt')
