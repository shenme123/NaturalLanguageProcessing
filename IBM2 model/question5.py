from collections import defaultdict
import sys

def read_t(t_file):
    # read in t's from file and return t's
    # t = {(word_de, word_en}:prob}
    t = {}
    for line in t_file:
        line = line.strip().split();
        t[(line[0],line[1])] = float(line[2])
    t_file.close()
    return t

def read_q(q_file):
    # read in q's from file and return q's
    # t = {(j,i,l,m):prob}
    q = {}
    for line in q_file:
        line = line.strip().split();
        q[tuple(int(x) for x in line[:4:1])] = float(line[4])
    q_file.close()
    return q

def read_corpus(corpus_en, corpus_de):
    # read in corpus of english and german and return as lists of lists of words
    # and matches of length of english sentences and german sentences
    # sens = [[word, ], ],   len_en_de = set((l, m), )
    sens_en = []
    sens_de = []
    len_en_de = set()
    for sen_en in corpus_en:
        sen_en = sen_en.strip().split()
        sens_en.append(sen_en)
        sen_de = corpus_de.readline().strip().split()
        sens_de.append(sen_de)
        len_en_de.add((len(sen_en), len(sen_de)))
    return sens_en, sens_de, len_en_de

def gen_q(len_en_de):
    # initialize q's from length matches and return q's
    q_init = defaultdict(int)
    for len in len_en_de:
        for i in range(len[1]):
            for j in range(len[0]+1):
                q_init[(j,i,len[0],len[1])] = 1.0/(len[0]+1)
    return q_init

def ibm2_EM(sens_en, sens_de, t_init, q_init):
    # takes in english and german corpus and IBM1 model t values,
    # run EM for 5 iterations and return new t values for IBM2
    for s in range(5):
        # compute counts
        counts = defaultdict(int)
        for k in range(len(sens_en)):
            sen_de = sens_de[k]
            len_de = len(sen_de)
            for i in range(len_de):
                sum = 0
                sen_en = ["_NULL_"]+sens_en[k]
                len_en = len(sen_en)-1
                for j in range(len_en+1):
                    if (sen_de[i], sen_en[j]) in t_init and (j,i,len_en, len_de) in q_init:
                        sum += q_init[(j,i,len_en, len_de)]*t_init[(sen_de[i], sen_en[j])]
                for j in range(len_en+1):
                    if (sen_de[i], sen_en[j]) in t_init and (j,i,len_en, len_de) in q_init:
                        delta =q_init[(j,i,len_en, len_de)]*t_init[(sen_de[i], sen_en[j])]/sum
                        counts[(sen_de[i], sen_en[j])] += delta
                        counts[sen_en[j]] += delta
                        counts[(j,i,len_en, len_de)] += delta
                        counts[(i,len_en,len_de)] += delta
        # update t's
        for c_de_en in t_init:
            if c_de_en in counts:
                t_init[c_de_en] = counts[c_de_en]/counts[c_de_en[1]]
        # update q's
        for jilm in q_init:
            if jilm in counts:
                q_init[jilm] = counts[jilm]/counts[jilm[1:4:1]]
    f = open("q5_t_ibm2", "w")
    for i in t_init:
        f.write(i[0] + " " + i[1] + " " + str(t_init[i])+"\n")
    f.close()
    f = open("q5_q_ibm2", "w")
    for i in q_init:
        f.write(" ".join(str(x) for x in i) + " " +str(q_init[i])+"\n")
    f.close()
    return t_init, q_init

def align_20(t_ibm2, q_ibm2, sens_en, sens_de):
    # compute alignment based on IBM2 of first 20 sentences.
    align_20 = []
    for k in range(20):
        sen_de = sens_de[k]
        len_de = len(sen_de)
        sen_en = ["_NULL_"] + sens_en[k]
        len_en = len(sen_en)-1
        align = []
        for i in range(len_de):
            a = 0
            prod = 0
            for j in range(len_en+1):
                if (j,i,len_en,len_de) in q_ibm2:
                    tq = t_ibm2[(sen_de[i], sen_en[j])]*q_ibm2[(j,i,len_en,len_de)]
                    if  tq> prod:
                        prod = tq
                        a = j
            align.append(a)
        align_20.append(align)
    return align_20

# input files
corpus_en = open("corpus.en","r")
corpus_de = open("corpus.de","r")
t_ibm1_file = open("q4_t_ibm1","r")

# read in corpus as sens = [[word, ], ], length matches as len_en_de = set((l, m), )
sens_en, sens_de, len_en_de = read_corpus(corpus_en, corpus_de)
# initialize q's
q_init = gen_q(len_en_de)
# read in t's from IBM1
t_ibm1 = read_t(t_ibm1_file)
# compute t's and q's with IBM2 model
t_ibm2, q_ibm2 = ibm2_EM(sens_en, sens_de, t_ibm1, q_init)
# compute alignment based on IBM1 of first 20 sentences.
align_20 = align_20(t_ibm2, q_ibm2, sens_en, sens_de)
# output first 20 alignments
for i in range(20):
    print " ".join(sens_en[i])
    print " ".join(sens_de[i])
    print align_20[i]
    print ""