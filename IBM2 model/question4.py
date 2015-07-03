import operator
from collections import defaultdict
import time

start = time.time()
def read_corpus(corpus_en, corpus_de):
    # read in corpus of english and german and return as lists of lists of words
    # sens = [[word, ], ]
    sens_en = []
    sens_de = []
    for sen in corpus_en:
        sen = sen.strip().split()
        sens_en.append(sen)
    for sen in corpus_de:
        sen = sen.strip().split()
        sens_de.append(sen)
    corpus_en.close()
    corpus_de.close()
    return sens_en, sens_de

def gen_t(sens_en,sens_de):
    # generate initial t's from corpus and save in dict
    # t_init = {(word_de, word_en):prob}
    t_init = {}
    words_en2de = defaultdict(set)
    words_de_all = set()
    for i in range(len(sens_en)):
        for word_en in sens_en[i]:
            for word_de in sens_de[i]:
                words_en2de[word_en].add(word_de)
        for word_de in sens_de[i]:
            words_de_all.add(word_de)
    for word_en in words_en2de:
        prob = 1.0/len(words_en2de[word_en])
        for word_de in words_en2de[word_en]:
            t_init[(word_de, word_en)] = prob
    prob = 1.0/len(words_de_all)
    for word_de in words_de_all:
        t_init[(word_de, '_NULL_')] = prob
    ############## output ###############
#    for i in t_init:
#        print i[0] + " " + i[1] + " " + str(t_init[i])
    return t_init

def ibm1_EM(sens_en, sens_de, t_init):
    # takes in english and german corpus and initial t values,
    # run EM for 5 iterations and return new t values for IBM1
    for s in range(5):
        # compute counts
        counts = defaultdict(int)
        for k in range(len(sens_en)):
            sen_de = sens_de[k]
            len_de = len(sen_de)
            for i in range(len_de):
                sum = 0
                sen_en = ["_NULL_"]+sens_en[k]
                len_en = len(sen_en)
                for j in range(len_en):
                    if (sen_de[i], sen_en[j]) in t_init:
                        sum += t_init[(sen_de[i], sen_en[j])]
                for j in range(len_en):
                    if (sen_de[i], sen_en[j]) in t_init:
                        delta = t_init[(sen_de[i], sen_en[j])]/sum
                        counts[(sen_de[i], sen_en[j])] += delta
                        counts[sen_en[j]] += delta
                        #counts[(j,i,len_en-1, len_de)] += delta[(k,i,j)]
                        #counts[(i,len_en-1,len_de)] += delta[(k,i,j)]
        # update t's
        for c_de_en in t_init:
            if c_de_en in counts:
                t_init[c_de_en] = counts[c_de_en]/counts[c_de_en[1]]
    # store t's of IBM1 to file "q4_t_ibm1"
    f = open("q4_t_ibm1", "w")
    for i in t_init:
        f.write( i[0] + " " + i[1] + " " + str(t_init[i])+"\n")
    f.close()
    return t_init

def read_devwords(dev_file):
    # read in deveowrds given and return a list of words
    devwords = []
    for word in dev_file:
        devwords.append(word.strip())
    return devwords

def test_ibm1(t_ibm1, devwords):
    # find ten german words with highest probability for each devword with IBM1 model,
    # and save to file "q4_devwords_top10"
    f = open("q4_devwords_top10", "w")
    for word in devwords:
        f.write(word+": \n")
        words2t = {}
        for de_en in t_ibm1:
            if de_en[1] == word:
                words2t[de_en] = t_ibm1[de_en]
        words2t_sorted = sorted(words2t.items(), key=operator.itemgetter(1), reverse=True)
        for i in range(10):
            f.write(words2t_sorted[i][0][0]+" "+str(words2t_sorted[i][1])+"\n")
        f.write("\n")
    f.close()

def align_20(t_ibm1, sens_en, sens_de):
    # compute alignment based on IBM1 of first 20 sentences.
    align_20 = []
    for k in range(20):
        sen_de = sens_de[k]
        sen_en = ["_NULL_"] + sens_en[k]
        align = []
        for word_de in sen_de:
            a = 0
            t = 0
            for j in range(len(sen_en)):
                if t_ibm1[(word_de, sen_en[j])] > t:
                    t = t_ibm1[(word_de, sen_en[j])]
                    a = j
            align.append(a)
        align_20.append(align)
    return align_20


# input files
corpus_en = open("corpus.en","r")
corpus_de = open("corpus.de","r")
dev_file = open("devwords.txt", "r")

# read in corpus as sens = [[word, ], ]
sens_en, sens_de = read_corpus(corpus_en, corpus_de)
# initialize t's
t_init = gen_t(sens_en,sens_de)
# calculate t's with EM for IBM1 model
t_ibm1 = ibm1_EM(sens_en, sens_de, t_init)
# read in devwords
devwords = read_devwords(dev_file)
# find ten german words with highest probability for each devword with IBM1 model
test_ibm1(t_ibm1, devwords)
# compute alignment based on IBM1 of first 20 sentences.
align_20 = align_20(t_ibm1, sens_en, sens_de)
# output first 20 alignments
for i in range(20):
    print " ".join(sens_en[i])
    print " ".join(sens_de[i])
    print align_20[i]
    print ""
end = time.time()