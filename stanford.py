import pprint
import jsonrpclib
import pattern.en as pen
from simplejson import loads

server = jsonrpclib.Server("http://localhost:8080")
pp = pprint.PrettyPrinter(indent=4)

def parse(s):
    return loads(server.parse(s))

def get_nouns(s, plural=True):
    parsed = parse(s)
    res = []

    for w in parsed['sentences'][0]['words']:
        if w[1]['PartOfSpeech'] == 'NN':
            if plural:
                res.append(pen.pluralize(w[1]['Lemma']))
            else:
                res.append(w[1]['Lemma'])

        elif w[1]['PartOfSpeech'] == 'NNS':
            if plural:
                res.append(w[0])
            else:
                res.append(w[1]['Lemma'])

    return res

def pretty_parse(s):
    res = parse(s)
    pp.pprint(res)

# pp print "Result", parse_sentence('Hello World!')
