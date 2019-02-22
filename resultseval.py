import pickle
from collections import defaultdict
scores = None
with open('scorepkl','rb') as f:
	scores = pickle.load(f)

assert scores

rvals = {
'Strongly agree':7,
'Agree':6,
'Somewhat agree':5,
'Neither agree nor disagree':4,
'Somewhat disagree':3,
'Disagree':2,
'Strongly disagree':1
}

coh = defaultdict(list)
imp = defaultdict(list)

with open('tabbedres.txt','r') as f:
	for line in f:
		line = line.strip() # this may remove many trailing tabs. This is OK for now, but be aware.
		parts = line.split('\t')
		id = parts.pop(0)
		s = parts.pop(0)
		sc = scores[s]
		curr = coh
		if id[-1] == '2': # id looks like "1_Q8_1"; final n: 1 is coherence, 2 is impact
			curr = imp
		for r in parts:
			if not r:
				continue
			v = rvals[r]
			curr[s].append(v)


import matplotlib.pyplot as plt
def avg(l):
	return sum(l) / float(len(l))

stories = sorted(scores.keys(),key=lambda s:scores[s],reverse=True)
scorersc = []
cohsc = []
impsc = []
for s in stories:
	scorersc.append(scores[s])
	cohsc.append(avg(coh[s]))
	impsc.append(avg(imp[s]))

plt.plot(scorersc)
plt.plot(cohsc)
plt.plot(impsc)
plt.show()


