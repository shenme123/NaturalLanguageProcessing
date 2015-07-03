import sys
import math
from collections import defaultdict
from count_freqs import Hmm

def count_total_freqs(freqs):
	# takes in frequencies of word-tag combination 
	# and calculate the total frequence of each word
    total_freqs = defaultdict(int)
    for line in freqs:
        line = line.strip()
        if line:
            fields = line.split(" ")
            if fields[1] == "WORDTAG":
                total_freqs[fields[3]] += int(fields[0])
    return total_freqs

def low_freq_to_rare(total_freqs, datafile):
	# takes in the total frequencies of words and training data
	# change all rare (count<5) words to label _RARE_
	datafile_revised = []
	line = datafile.readline()
	while line:
		line = line.strip()
		if line:
			fields = line.split(" ")
			if total_freqs[fields[0]]<5:
				datafile_revised.append("_RARE_ %s" % fields[1])
			else:
				datafile_revised.append(line)
		else:
			datafile_revised.append("")
		line = datafile.readline()
	return datafile_revised

def calc_emission_prob(freqs, ngrams):
	# takes in the frequences of words and the ngrams counts,
	# based on which calculate the emission probabilities in log_2 form
	count_y = {}
	emission_prob = []
	for line in ngrams:
		line = line.strip()
		if line:
			fields = line.split(" ")
			if fields[1]=="1-GRAM":
				count_y[fields[2]] = int(fields[0])
	# calc and output emission_prob
	for line in freqs:
		fields = line.split(" ")
		s = "%s %s %f" % (fields[3], fields[2], math.log(float(fields[0])/count_y[fields[2]],2))
		emission_prob.append(s)
	return emission_prob

def calc_tagging_baseline(emission_prob, test_data):
	# takes in the emission probabilities and testing data,
	# calculate the tags only based on emission probs
	emission_prob_hi = {}
	for line in emission_prob:
		line = line.strip()
		if line:
			fields = line.split()
			if fields[0] not in emission_prob_hi or float(emission_prob_hi[fields[0]][1]) < float(fields[2]):
				emission_prob_hi[fields[0]] = [fields[1], fields[2]]
	# save a wordlist with counts>5
	wl = open('wordlist_5_or_more', 'w')
	for word in emission_prob_hi:
		wl.write(word+"\n")
	wl.close()
	# read test data and print out the tagging result
	tagging_baseline = {}
	line = test_data.readline()
	while line:
		line = line.strip()
		if line:
			if line in emission_prob_hi:
				print "%s %s %s" % (line, emission_prob_hi[line][0], emission_prob_hi[line][1])
			else:
				print "%s %s %s" % (line, emission_prob_hi["_RARE_"][0], emission_prob_hi["_RARE_"][1])
		else:
			print ""
		line = test_data.readline()


if __name__ == "__main__":
	# argv[1] = ner_train.dat	
	# argv[2] = ner_dev.dat
	train_data = file(sys.argv[1], "r")
	test_data = file(sys.argv[2], "r")
	# Initialize a trigram counter
	counter = Hmm(3)
	# Collect counts
	counter.train(train_data)
	# store the counts
	train_freqs = []
	for word, ne_tag in counter.emission_counts:	
		s = str(counter.emission_counts[(word, ne_tag)])+" WORDTAG "+ne_tag+" "+word
		train_freqs.append(s)
	# count total freqs
	train_total_freqs = count_total_freqs(train_freqs)
	# revise train data with _RARE_
	train_data = file(sys.argv[1], "r")
	train_data_revised = low_freq_to_rare(train_total_freqs, train_data)
	# recount freqs
	counter2 = Hmm(3)
	counter2.train_data(train_data_revised)
	train_freqs_re = []
	# write to file 'ner.counts_rare'
	counts_rare = open('ner.counts_rare', 'w')
	for word, ne_tag in counter2.emission_counts:	
		s = str(counter2.emission_counts[(word, ne_tag)])+" WORDTAG "+ne_tag+" "+word
		counts_rare.write(s+"\n")
		train_freqs_re.append(s)
	printngrams=[1, 2, 3]
	train_ngrams_re = []
	for n in printngrams:
		for ngram in counter2.ngram_counts[n - 1]:
			ngramstr = " ".join(ngram)
			s ="%i %i-GRAM %s" % (counter2.ngram_counts[n - 1][ngram], n, ngramstr)
			counts_rare.write(s+"\n")
			train_ngrams_re.append(s)
	counts_rare.close()
	# calculate emission_prob
	emission_prob = calc_emission_prob(train_freqs_re, train_ngrams_re)
	# save emission_prob
	em_prob = open('emission_prob', 'w')
	for prob in emission_prob:
		em_prob.write(prob+"\n")
	em_prob.close()
	# calculate baseline
	calc_tagging_baseline(emission_prob, test_data)