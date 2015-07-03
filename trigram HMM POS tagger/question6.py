import sys
import math
from collections import defaultdict
import re
from count_freqs import Hmm
from question4 import count_total_freqs
from question5 import calc_3gram_q, calc_tagging_3gram, viterbi_3gram


def low_freq_to_sets(total_freqs, datafile):
	# takes in the total frequencies of words and training data
	# change all rare (count<5) words to different labels including
	# _twoDigitNum_   _fourDigitNum_   _otherNum_   _containsDigitAndAlpha_
	# _containsDigitAndDash_   _containsDigitAndSlash_   _containsDigitAndComma_ 
	# _containsDigitAndPeriod_    _allCaps_   _capPeriod_   _firstWord_
	# _initCap_   _lowerCase_   _other_
	datafile_revised = []
	line = datafile.readline()
	flag = 0
	while line:
		line = line.strip()
		if line:
			flag +=1
			fields = line.split(" ")
			wd = fields[0]
			if total_freqs[wd]<5:
				if len(wd)==2 and wd.isdigit():
					datafile_revised.append("_twoDigitNum_ %s" % fields[1])
				elif len(wd)==4 and wd.isdigit():
					datafile_revised.append("_fourDigitNum_ %s" % fields[1])
				elif wd.isdigit():
					datafile_revised.append("_otherNum_ %s" % fields[1])
				elif re.match("^[0-9a-zA-Z-]+?$", wd) is not None:
					datafile_revised.append("_containsDigitAndAlpha_ %s" % fields[1])
				elif re.match("^[0-9-]+?$", wd) is not None:
					datafile_revised.append("_containsDigitAndDash_ %s" % fields[1])
				elif re.match("^[0-9/]+?$", wd) is not None:
					datafile_revised.append("_containsDigitAndSlash_ %s" % fields[1])
				elif re.match("^[0-9,]+?$", wd) is not None:
					datafile_revised.append("_containsDigitAndComma_ %s" % fields[1])
				elif re.match("^\d+?\.\d+?$", wd) is not None:
					datafile_revised.append("_containsDigitAndPeriod_ %s" % fields[1])
				elif re.match("^[A-Z]+?$", wd) is not None:
					datafile_revised.append("_allCaps_ %s" % fields[1])
				elif re.match("^[A-Z].$", wd) is not None:
					datafile_revised.append("_capPeriod_ %s" % fields[1])
				elif flag==1:
					datafile_revised.append("_firstWord_ %s" % fields[1])
				elif re.match("^[A-Z][a-z]+$", wd) is not None:
					datafile_revised.append("_initCap_ %s" % fields[1])
				elif wd.islower():
					datafile_revised.append("_lowerCase_ %s" % fields[1])
				else:
					datafile_revised.append("_other_ %s" % fields[1])
#				datafile_revised.append("_RARE_ %s" % fields[1])
			else:
				datafile_revised.append(line)
		else:
			datafile_revised.append("")
			flag = 0
		line = datafile.readline()
	return datafile_revised

def calc_emission_prob_(freqs, ngrams):
	# takes in the frequences of words and the ngrams counts,
	# based on which calculate the emission probabilities in log_2 form
	count_y = {}
	emission_prob = {}
	for line in ngrams:
		line = line.strip()
		if line:
			fields = line.split(" ")
			if fields[1]=="1-GRAM":
				count_y[fields[2]] = int(fields[0])
	# calc and output emission_prob
	for line in freqs:
		fields = line.split(" ")
		emission_prob[fields[3]+' '+fields[2]]= math.log(float(fields[0])/count_y[fields[2]],2)
	return emission_prob

def calc_3gram_q_(counts):
	# takes in the word counts and ngrams counts,
	# calculate the 3gram probabilities in log_2 form
	counts_2gram = {}
	counts_3gram = []
	tags = []
	q_3gram = {}
	for line in counts:
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
	# calculate 3gram probabilites
	for trigram in counts_3gram:
		q_3gram[trigram[1]] = math.log(trigram[2]/counts_2gram[trigram[0]], 2)
	return [q_3gram, tags]

def get_wl(train_freqs_re):
	# get a word list and store in a set
	wl = set()
	for line in train_freqs_re:
		line.strip()
		if line:
			fields = line.split(" ")
			wl.add(fields[3])
	return wl

def to_set(wl, test_data):
	# read in the test_data and change rare and unseen words into set labels
	# return list of list of original words and revised words with set labels
	test_data_orig = []
	test_data_rev = []
	line = test_data.readline()
	flag = 0
	while line:
		wd = line.strip()
		test_data_orig.append(wd)
		if wd:
			flag+=1
			if wd not	in wl:
				if len(wd)==2 and wd.isdigit():
					test_data_rev.append("_twoDigitNum_")
				elif len(wd)==4 and wd.isdigit():
					test_data_rev.append("_fourDigitNum_")
				elif wd.isdigit():
					test_data_rev.append("_otherNum_")
				elif re.match("^[0-9a-zA-Z-]+?$", wd) is not None:
					test_data_rev.append("_containsDigitAndAlpha_")
				elif re.match("^[0-9-]+?$", wd) is not None:
					test_data_rev.append("_containsDigitAndDash_")
				elif re.match("^[0-9/]+?$", wd) is not None:
					test_data_rev.append("_containsDigitAndSlash_")
				elif re.match("^[0-9,]+?$", wd) is not None:
					test_data_rev.append("_containsDigitAndComma_")
				elif re.match("^\d+?\.\d+?$", wd) is not None:
					test_data_rev.append("_containsDigitAndPeriod_")
				elif re.match("^[A-Z]+?$", wd) is not None:
					test_data_rev.append("_allCaps_")
				elif re.match("^[A-Z].$", wd) is not None:
					test_data_rev.append("_capPeriod_")
				elif flag==1:
					test_data_rev.append("_firstWord_")
				elif re.match("^[A-Z][a-z]+$", wd) is not None:
					test_data_rev.append("_initCap_")
				elif wd.islower():
					test_data_rev.append("_lowerCase_")
				else:
					test_data_rev.append("_other_")
			else:
				test_data_rev.append(wd)
		else:
			test_data_rev.append("")
			flag = 0
		line = test_data.readline()
	return [test_data_rev, test_data_orig]

if __name__ == "__main__":
	# argv[1] = ner_train.dat	argv[2] = ner_dev.dat
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
	train_data = file(sys.argv[1], "r")
	train_data_revised = low_freq_to_sets(train_total_freqs, train_data)
	# recount freqs	
	counter3 = Hmm(3)
	counter3.train_data(train_data_revised)
	train_freqs_re = []
	# write frequences to file 'ner.counts_sets'
	counts_sets = open('ner.counts_sets', 'w')
	for word, ne_tag in counter3.emission_counts:	
		s = str(counter3.emission_counts[(word, ne_tag)])+" WORDTAG "+ne_tag+" "+word
		counts_sets.write(s+"\n")
		train_freqs_re.append(s)
	printngrams=[1, 2, 3]
	train_ngrams_re = []
	for n in printngrams:
		for ngram in counter3.ngram_counts[n - 1]:
			ngramstr = " ".join(ngram)
			s ="%i %i-GRAM %s" % (counter3.ngram_counts[n - 1][ngram], n, ngramstr)
			counts_sets.write(s+"\n")
			train_ngrams_re.append(s)
	counts_sets.close()
	# calculate emission_prob
	# format : emimssion_prob = {"word tag" : log(emis_prob)]
	emission_prob = calc_emission_prob_(train_freqs_re, train_ngrams_re)
	# save emission_prob
	em_prob = open('emission_prob_sets', 'w')
	for prob in emission_prob:
		em_prob.write(prob+"\n")
	em_prob.close()
	# calculate qs of 3-grams   
	# format : q_3gram = {"w1 w2 w3" : q}
	res = calc_3gram_q_(train_ngrams_re)
	q_3gram  = res[0]
	tags = res[1]
	# get wordlist in training set
	wordlist_train = get_wl(train_freqs_re)
	# change unseen and rare words in test to set labels
	test_data_ = to_set(wordlist_train, test_data)
	test_data_rev = test_data_[0]
	test_data_orig = test_data_[1]
	# calculate tags based on 3gram Viterbi
	taggings = calc_tagging_3gram(test_data_rev, emission_prob, q_3gram, tags)
	# output result
	for i in range(len(test_data_orig)):
		print test_data_orig[i]+' '+taggings[i]