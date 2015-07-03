import sys, json
from collections import defaultdict

def readin_counts(cfile):
    # read in counts that is calculated by count_cfg_freq.py
    # cfile is the output file by count_cfg_freq.py
    # return the total counts of each terminal word
    counts = defaultdict(int)
    for line in cfile:
        if line.strip():
            fields = line.strip().split()
            # only count terminal words
            if fields[1] == "UNARYRULE":
                counts[fields[3]] += int(fields[0])
    cfile.close()
    return counts

def get_counts_nonrare(counts):
    # take in counts of all terminal words, return a set of words that have count >= 5
    counts_nonrare = set()
    for count in counts:
        if counts[count] >= 2:
            counts_nonrare.add(count)
    return counts_nonrare

def replace_rare(tfile, counts_nonrare):
    # take in the training data and set of non-rare words, output the train sentences with rare
    # words replaced by "_RARE_".  tfile is the training data, counts_nonrare is non-rare words
    # in training corpus stored in a set.
    for line in tfile:
        tree = json.loads(line)
        tree = replace(tree, counts_nonrare)
        print json.dumps(tree)
    tfile.close()

def replace(tree, counts_nonrare):
    # takes in a parsing tree and non-rare word list, return a parsing tree with rare words replaced
    if len(tree) == 2:
        if tree[1] not in counts_nonrare:
            tree[1] = "_RARE_"
    elif len(tree) == 3:
        replace(tree[1], counts_nonrare)
        replace(tree[2], counts_nonrare)
    return tree

def output_nonrare(counts_nonrare, filename):
    # output the nonrare word list as a file named "words_non_rare"
    f = open(filename, 'w')
    for word in counts_nonrare:
        f.write(word+'\n')

# read in files: counts file and train data
counts_file = open("cfg_vert.counts", 'r')
train_file = open("parse_train_vert.dat", 'r')

# collect counts of words and nonrare words. counts:{word:counts}    counts_nonrare:{word:counts}
counts = readin_counts(counts_file)
# collect non-rare words and stored in a set
counts_nonrare = get_counts_nonrare(counts)
# output the non-rare word list to file
output_nonrare(counts_nonrare, "words_nonrare_vert")
# replace rare words in training data with "_RARE_"
replace_rare(train_file, counts_nonrare)
