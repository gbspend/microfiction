# microfiction
CS673 - Winter 2017

***Setup***

install:

	apt-get install python-dev g++ python-tk
	
	pip install numpy scipy matplotlib cython word2vec requests nltk pattern 
	

download:

	https://drive.google.com/file/d/1srOUFidQ9fV240wyF7GW4eqF6raCawBV/view (place posttagged_wikipedia_for_word2vec.bin in /data folder and rename to tagged.bin)
	
	https://github.com/danielricks/penseur (place in /penseur folder)

run:
	In /data folder-
	
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
