import pprint
import jsonrpclib
from simplejson import loads
import socket

server = jsonrpclib.Server("http://localhost:8080")
pp = pprint.PrettyPrinter(indent=4)

def check():
	try:
		server.parse('Hello World!')
	except socket.error:
		return False
	else:
		return True

def parse(s):
	return loads(server.parse(s))

def get_nouns(s, plural=True):
	parsed = parse(s)
	res = []

	for w in parsed['sentences'][0]['words']:
		pos = w[1]['PartOfSpeech']
		if pos in ['NN','NNS','NNP','NNPS','VBG']:
			res.append(w[0])

	return res

def pretty_parse(s):
	res = parse(s)
	pp.pprint(res)

# pp print "Result", parse_sentence('Hello World!')
