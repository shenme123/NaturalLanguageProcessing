import math

def read_q(q_file):
    # read in q's from file and return q's
    # t = {(j,i,l,m):prob}
    q = {}
    for line in q_file:
        line = line.strip().split();
        q[tuple(int(x) for x in line[:4:1])] = float(line[4])
    q_file.close()
    return q

def read_t(t_file):
    # read in t's from file and return t's
    # t = {(word_de, word_en}:prob}
    t = {}
    for line in t_file:
        line = line.strip().split();
        t[(line[0],line[1])] = float(line[2])
    t_file.close()
    return t

def read_corpus(corpus_en, corpus_de):
    # read in corpus of english and german and return as lists of lists of words
    # sens = [[word, ], ]
    sens_en = []
    sens_de = []
    for sen_en in corpus_en:
        sen_en = sen_en.strip().split()
        sens_en.append(sen_en)
        sen_de = corpus_de.readline().strip().split()
        sens_de.append(sen_de)
    return sens_en, sens_de

def align_sen(t_ibm2, q_ibm2, sen_en, sen_de):
    # compute alignment for eng-ger sentence pair
    len_de = len(sen_de)
    sen_en = ["_NULL_"] + sen_en
    len_en = len(sen_en)-1
    align = []
    p_fae = 0
    for i in range(len_de):
        a = 0
        prod = 0
        for j in range(len_en+1):
            if (sen_de[i], sen_en[j]) in t_ibm2 and (j,i,len_en,len_de) in q_ibm2:
                tq = t_ibm2[(sen_de[i], sen_en[j])]*q_ibm2[(j,i,len_en,len_de)]
                if tq> prod:
                    prod = tq
                    a = j
        if prod>0:
            p_fae += math.log(prod)
        else:
            p_fae += -100
        align.append(a)
    return p_fae, align

def unscramble(sens_en, sens_de):
    # find the english sentence with highest prob. for each german sentence
    align_list = []
    sen_en_max_list = []
    for sen_de in sens_de:
        p_fae_max = -float("inf")
        align = []
        sen_en_max = []
        for sen_en in sens_en:
            p_fae, a = align_sen(t_ibm2, q_ibm2, sen_en, sen_de)
            if p_fae > p_fae_max:
                p_fae_max = p_fae
                align = a
                sen_en_max = sen_en
        align_list.append(align)
        sen_en_max_list.append(sen_en_max)
    return align_list, sen_en_max_list

# input files
q_ibm2_file = open("q5_q_ibm2", "r")
t_ibm2_file = open("q5_t_ibm2", "r")
scram_en_file = open("scrambled.en", "r")
orig_de_file = open("original.de", "r")

# read in q's from IBM2
q_ibm2 = read_q(q_ibm2_file)
# read in t's from IBM2
t_ibm2 = read_t(t_ibm2_file)
# read in corpus as sens = [[word, ], ]
sens_en, sens_de = read_corpus(scram_en_file, orig_de_file)
# compute argmax a and e for each german sentence
align_list, sen_en_max_list = unscramble(sens_en, sens_de)
# output best matches based on IBM2 results
for sen_en in sen_en_max_list:
    print " ".join(sen_en)