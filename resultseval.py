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

#============
import numpy as np
import matplotlib.pyplot as plt

def estimate_coef(x, y):
	# number of observations/points
	n = np.size(x)
	# mean of x and y vector
	m_x, m_y = np.mean(x), np.mean(y)
	# calculating cross-deviation and deviation about x
	SS_xy = np.sum(y*x) - n*m_y*m_x
	SS_xx = np.sum(x*x) - n*m_x*m_x
	# calculating regression coefficients
	b_1 = SS_xy / SS_xx
	b_0 = m_y - b_1*m_x
	return(b_0, b_1)

def plot_regression_line(x, y, b,lbl):
	# predicted response vector
	y_pred = b[0] + b[1]*x
	# plotting the regression line
	plt.plot(x, y_pred, label=lbl)

def plot_regression(x,y,label=''):
	x = np.array(x)
	y = np.array(y)
	# estimating coefficients
	b = estimate_coef(x, y)
	# plotting regression line
	plot_regression_line(x, y, b, label)

#============

#plt.plot(scorersc) #messy
plt.plot(cohsc,'o',label='Average coherence')
plot_regression(list(range(115)),cohsc,label='Coherence Regression')
plt.plot(impsc,'o',label='Average impact')
plot_regression(list(range(115)),impsc,label='Impact Regression')
plt.legend()
plt.title("Average human-rated coherence and impact of stories sorted by skipthought score (descending)")
plt.show()


cohgood = []
cohbad = []
impgood = []
impbad = []

for i in range(100):
	s=stories[i]
	cohgood+=coh[s]
	impgood+=imp[s]

for i in range(100,115):
	s=stories[i]
	cohbad+=coh[s]
	impbad+=imp[s]

plt.boxplot([cohgood,cohbad])
plt.xticks([1,2], ('Top 100 skipthought-scored stories', 'Bottom 15'))
plt.title("Boxplot comparison of human-scored coherence of top and bottom skipthought-scored stories")
plt.show()
plt.boxplot([impgood,impbad])
plt.xticks([1,2], ('Top 100 skipthought-scored stories', 'Bottom 15'))
plt.title("Boxplot comparison of human-scored impact of top and bottom skipthought-scored stories")
plt.show()


from scipy.stats import ttest_ind
def printstatp(stat,p):
	ps = '%.3f'%p
	print "ps:",ps
	if ps == "0.000":
		ps = "p<0.001"
	else:
		ps = "p="+ps
	print('Statistics=%.3f, %s' % (stat, ps))

# compare samples
def comparesamp(good,bad,alpha=0.05):
	stat, p = ttest_ind(good, bad)
	printstatp(stat, p)
	#p < .001
	# interpret
	if p > alpha:
		print('Same distributions (fail to reject H0)')
	else:
		print('Different distributions (reject H0)')

print "Coherence:"
comparesamp(cohgood,cohbad)
print "Impact:"
comparesamp(impgood,impbad)

topc = sorted(stories,reverse=True,key=lambda s:cohsc[stories.index(s)])[:10]
topi = sorted(stories,reverse=True,key=lambda s:impsc[stories.index(s)])[:10]

ts = [2,4,1,1,3,1,2,1,1,1]
for i in range(10):
	print topc[i],"\t"*ts[i],topi[i]


topdiffc = sorted(stories,reverse=True,key=lambda s:cohsc[stories.index(s)]-impsc[stories.index(s)])[:10]
topdiffi = sorted(stories,reverse=True,key=lambda s:impsc[stories.index(s)]-cohsc[stories.index(s)])[:10]
