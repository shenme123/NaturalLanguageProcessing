import json
from collections import defaultdict

def read_counts(file):
    # read in counts from file genenrated by count_cfg_freq.py
    # return counts for nonterminal, unary rules and binary rules in dicts
    nonterm = defaultdict(int)
    unary = defaultdict(int)
    binary = defaultdict(int)
    for line in file:
        if line.strip():
            fields = line.strip().split()
            if fields[1]=="NONTERMINAL":
                nonterm[fields[2]] = int(fields[0])
            elif fields[1] == "UNARYRULE":
                unary[(fields[2],fields[3])] = int(fields[0])
            elif fields[1] == "BINARYRULE":
                binary[(fields[2], fields[3], fields[4])] = int(fields[0])
    file.close()
    return nonterm, unary, binary

def calc_q(nonterm, unary, binary):
    # takes in counts of nonterminal, unary rules and binary rules, calculate the probability of rules
    q_unary = {}
    q_binary = {}
    for term in unary:
        q_unary[term] = float(unary[term])/nonterm[term[0]]
    for term in binary:
        q_binary[term] = float(binary[term])/nonterm[term[0]]
    return q_unary, q_binary

def count_freqs(test_file, words_nonrare):
    # takes in test corpus and change rare and unseen words to "_RARE_"
    # return list of original sentences and revised sentences
    counts_test = defaultdict(int)
    sentences_orig = []
    sentences_rev = []
    for line in test_file:
        if line.strip():
            words = line.strip().split()
            sentences_orig.append(words)
            words2 = words[:]
            for i in range(len(words2)):
                if words2[i] not in words_nonrare:
                    words2[i] = "_RARE_"
                counts_test[words2[i]] += 1
            sentences_rev.append(words2)
    test_file.close()
    return counts_test, sentences_orig, sentences_rev


def readin_words_nonrare(file):
    # read in list of non-rare words in train corpus from file
    words_nonrare = set()
    for line in file:
        if line.strip():
            words_nonrare.add(line.strip())
    file.close()
    return words_nonrare

def pcfg(nonterm, sen_rev, q_unary, q_binary, bi_rules, sen_orig):
    # implement pcfg to calculate the parsing tree with the highest probability
    # takes in dicts of nontermnals, unary and binary rules to probabilities, revised sentences and original sentences
    # return predicted parsing trees of test corpus
    for n in range(len(sen_rev)):
        sen = sen_rev[n]
        # initalization
        pis = {}
        bps = {}
        length = len(sen)
        for i in range(1,length+1):
            for X in nonterm:
                if (X,sen[i-1]) in q_unary:
                    pis[(i,i,X)] = q_unary[(X,sen[i-1])]
        # algorithm
        for l in range(1,length):
            for i in range(1,length-l+1):
                j = i+l
                for X in nonterm:
                    if X in bi_rules:
                        max_pi = 0
                        max_bp = ()
                        for YZ in bi_rules[X]:
                            for s in range(i,j):
                                if (i,s,YZ[0]) in pis and (s+1,j,YZ[1]) in pis:
                                    pi = q_binary[(X,)+YZ]*pis[(i,s,YZ[0])]*pis[(s+1,j,YZ[1])]
                                    if pi > max_pi:
                                        max_pi = pi
                                        max_bp = YZ
                                        max_s = s
                        if max_pi!= 0:
                            pis[(i,j,X)] = max_pi
                            #print max_pi
                            bps[(i,j,X)] = max_bp+(max_s,)
        # back track to find parsing trees
        if (1,length,'S') in pis:
            tree = gen_tree(1,length, bps, sen_orig[n], 'S')
        else:
            max_prob = 0
            max_X = ''
            for X in nonterm:
                if (1,length,X) in pis and pis[(1,length, X)] > max_prob:
                    max_X = X
            tree = gen_tree(1, length, bps, sen_orig[n], max_X)
        print json.dumps(tree)


def gen_tree(start, end, bps, sen_orig, X):
    # takes in start end end index of word in sentence, back point, origial sentence and root type
    # generate parsing tree recursively
    if start == end:
        return [X, sen_orig[start-1]]
    tree = [X]
    bp = bps[(start, end, X)]
    tree.append(gen_tree(start, bp[2], bps, sen_orig, bp[0]))
    tree.append(gen_tree(bp[2]+1, end, bps, sen_orig, bp[1]))
    return tree



def get_bi_rules(q_binary):
    # takes in binary rules and return in format that the key is nonterminals and value is list of
    # descendants according to existing binary rules
    bi_rules = {}
    for term in q_binary:
        if term[0] in bi_rules:
            bi_rules[term[0]].append((term[1],term[2]))
        else:
            bi_rules[term[0]] = [(term[1],term[2])]
    return bi_rules

# read in files: counts, test data, non-rare word list
count_file = open("cfg_rare.counts")
test_file = open("parse_dev.dat")
nonrare_file = open("words_nonrare", 'r')

words_nonrare = readin_words_nonrare(nonrare_file)
# nonterm: {X:count}    unary: {(X,word):count}     binary: {(X,Y1,Y2):count}
nonterm, unary, binary = read_counts(count_file)

# q_unary: {(X,word):prob}    q_binary: {(X,Y1,Y2):prob}
q_unary, q_binary = calc_q(nonterm, unary, binary)

bi_rules = get_bi_rules(q_binary)
# count freqs in test data, and replace rare words in sentences
# counts_test: {word:counts}     sentences_org/sentences_rev: [[words],]
counts_test, sentences_orig, sentences_rev = count_freqs(test_file, words_nonrare)
pcfg(nonterm, sentences_rev, q_unary, q_binary, bi_rules, sentences_orig)

