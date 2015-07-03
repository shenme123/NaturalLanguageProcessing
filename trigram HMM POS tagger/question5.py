import sys
import math
from collections import defaultdict
from count_freqs import Hmm
import question4

def calc_3gram_q(counts):
	# takes in the word counts and ngrams counts,
	# calculate the 3gram probabilities in log_2 form
	counts_2gram = {}
	counts_3gram = []
	tags = []
	q_3gram = {}
	# read file and store counts
	line = counts.readline()
	while line:
		line = line.strip()
		if line:
			fields = line.split(" ")
			if fields[1] == "1-GRAM":
				tags.append(fields[2])
			elif fields[1] == "2-GRAM":
				counts_2gram[fields[2]+" "+fields[3]] = int(fields[0])
			elif fields[1] == "3-GRAM":
				trigram = [fields[2]+" "+fields[3], fields[2]+" "+fields[3]+" "+fields[4], float(fields[0])]
				counts_3gram.append(trigram)
		line = counts.readline()
	# calculate 3gram probabilities
	for trigram in counts_3gram:
		q_3gram[trigram[1]] = math.log(trigram[2]/counts_2gram[trigram[0]], 2)
	return [q_3gram, tags]

def read_em_prob(em_file):
	# read emission probabilities from file and return
	# it in a dict {'word tag':prob}
	em_prob = {}
	line = em_file.readline()
	while line:
		line = line.strip()
		if line:
			fields = line.split(" ")
			em_prob[fields[0]+" "+fields[1]] = float(fields[2])
		line = em_file.readline()
	return em_prob

def readin_wl(wl_file):
	# read in word list from file and save it in set
	wl = set()
	line = wl_file.readline()
	while line:
		line = line.strip()
		if line:
			wl.add(line)
		line = wl_file.readline()
	return wl

def to_rare(wl, test_data):
	# read in the test_data and change rare and unseen words into _RARE_
	# return list of list of original words and revised words with _RARE_
	test_data_orig = []
	test_data_rev = []
	line = test_data.readline()
	while line:
		line = line.strip()
		test_data_orig.append(line)
		if line:
			if line not	in wl:
				test_data_rev.append("_RARE_")
			else:
				test_data_rev.append(line)
		else:
			test_data_rev.append("")
		line = test_data.readline()
	return [test_data_rev, test_data_orig]

def calc_tagging_3gram(test, em_prob, q_3gram, tags):	
	# takes in test data, emission prob, 3gram q prob and tag list
	# calculate tags by calling viterbi algorithm and return list of tags
	taggings = []
	sentence = []
	# call viterbi_3gram when seeing empty line
	for word in test:
		word = word.strip()
		if word:
			sentence.append(word)
		else:
			sentence.append("STOP")
			res = viterbi_3gram(sentence, em_prob, q_3gram, tags)
			taggings = taggings+res
			sentence = []
	return taggings

def viterbi_3gram(sen, e, q, tags):
	# implement viterbi algorithm, takes in sentence, emission
	# probabilites, 3gram q prob and list of tags
	bps = []
	bps.append({})
	all_pis = []
	all_pis.append({})
	pis_pre = {}
	pis_pre['* *'] = 1
	# loop through each word in sentence
	for k in range(1, len(sen)):
		if k == 1:
			Kw = ['*']
			Ku = ['*']
		elif k == 2:
			Kw = ['*']
			Ku = tags
		else:
			Kw = tags
			Ku = tags
		Kv = tags
		pis = {}
		bps_k = {}
		# loop through u, v
		for u in Ku:
			for v in Kv:
				pi_max = 0
				bp = ''
				# find max prob and the w correspont to it
				for w in Kw:
					wuv = w + ' ' + u + ' ' + v
					xv = sen[k - 1] + ' ' + v
					if wuv in q and xv in e:
						pi = pis_pre[w + ' ' + u] * (2**q[wuv]) * (2 ** e[xv])
						if pi > pi_max:
							pi_max = pi
							bp = w
				pis[u + ' ' + v] = pi_max
				bps_k[u + ' ' + v] = bp
		pis_pre = pis
		all_pis.append(pis)
		bps.append(bps_k)
	# find yn and y_n-1 that maxmize the prob of sentence
	max = 0
	y_rev = ['','']
	for uv in pis:
		uvS = uv + ' STOP'
		if uvS in q:
			pr = pis[uv] * (2**q[uvS])
			if pr > max:
				max = pr
				u_v = uv.split(" ")
				y_rev[0] = u_v[1]
				y_rev[1] = u_v[0]
	if y_rev[1] == '*':
		y_rev.pop()
	# back tracking the labels
	for k in range(2, len(sen) - 1):
		y_rev.append(bps[len(sen) - k + 1][y_rev[-1]+" "+y_rev[-2]])
	probs = []
	n = len(y_rev)
	y = y_rev[::-1]
	# find probs till each word
	prob = math.log(all_pis[1]['* '+y[0]],2)
	probs.append(prob)
	for k in range(n-1):
		prob = math.log(all_pis[k+2][y[k]+' '+y[k+1]],2)
		probs.append(prob)
	for k in range(n):
		y[k] = y[k]+' '+str(probs[k])
	y.append('')
	return y


if __name__ == "__main__":
	# assign args
	# argv[1] = ner.counts_rare		
	# argv[2] = emission_prob
	# argv[3] = ner_dev.dat
	# argv[4] = wordlist_5_or_more
	counts = file(sys.argv[1], "r")
	emission = file(sys.argv[2], "r")
	test_data = file(sys.argv[3], "r")
	wl_train = file(sys.argv[4], "r")

	# calculate qs of 3-grams   
	# format : q_3gram = {"w1 w2 w3" : q}
	res = calc_3gram_q(counts)
	q_3gram  = res[0]
	tags = res[1]
	
	# read in emissions from q4  
	# format : em_prob = {"word tag" : log(emis_prob)]
	em_prob = read_em_prob(emission)
	# change unseen and rare words to "_RARE_" in test
	wordlist_train = readin_wl(wl_train)
	test_data_ = to_rare(wordlist_train, test_data)
	test_data_rev = test_data_[0]
	test_data_orig = test_data_[1]
	# calculate tags accorting to 3gram Viterbi
	taggings = calc_tagging_3gram(test_data_rev, em_prob, q_3gram, tags)
	# output result
	for i in range(len(test_data_orig)):
		print test_data_orig[i]+' '+taggings[i]
