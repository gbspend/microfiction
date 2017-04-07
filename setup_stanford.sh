#!/bin/sh

wget https://github.com/relwell/stanford-corenlp-python/archive/master.zip
unzip master.zip
mv stanford-corenlp-python-master corenlp-python
rm master.zip

cd corenlp-python

sudo -H pip install pexpect unidecode jsonrpclib simplejson  # jsonrpclib is optional
wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-01-04.zip
unzip stanford-corenlp-full-2014-01-04.zip
rm stanford-corenlp-full-2014-01-04.zip
