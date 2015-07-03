import sys
import subprocess
from question4 import *
from collections import defaultdict
import time

start = time.time()
def gen_model(sentences):
    # train model from training set
    model = defaultdict(int)
    gold_tags = []
    sen_features = []
    # for 5 iterations of perceptron
    for t in range(5):
        # update v for each sentence
        for i in range(len(sentences)):
            if t==0:
                gold_tag = call_popen(gold_popen, sentences[i])
                gold_tag_ = " ".join(gold_tag.split())
                gold_tags.append(gold_tag_)
                sen_f = gen_features(sentences[i], gold_tag)
                sen_features.append(sen_f)
            hists_possible = call_popen(enum_popen, sentences[i]).strip().split("\n")
            scores_hists = get_scores(model, hists_possible, sentences[i])
            sen_tag = call_popen(decode_propen, scores_hists)
            sen_tag_ = " ".join(sen_tag.split())
            if sen_tag_ != gold_tags[i]:
                sen_features_ = gen_features(sentences[i], sen_tag)
                for fe in sen_features[i]:
                    model[fe] += sen_features[i][fe]
                for fe in sen_features_:
                    model[fe] -= sen_features_[fe]
    # output model to file
    model2 = defaultdict(int)
    for v in model:
        if model[v] != 0:
            file_model.write(v+" "+str(model[v])+"\n")
            model2[v] = model[v]
    return model2

def get_scores(model, histories, sentence):
    # get scores of local histories based on model
    # histories: [history, ]
    scores = ""
    for hist in histories:
        f = []
        sen = sentence.strip().split("\n")
        tokens_h = hist.split()     # tokens_h: [0]=i  [1]=t(i-1)  [2]=t(i)
        # bigram feature
        f.append("BIGRAM:"+tokens_h[1]+":"+tokens_h[2])
        tokens_s = sen[int(tokens_h[0])-1].split()        # tokens_s: [0]=word  [1]=tag
        word = tokens_s[0]
        # tag feature
        f.append("TAG:"+word+":"+tokens_h[2])
        # capital first
        if word[0].isupper():
            f.append("CapInit:"+word+":"+tokens_h[2])
        # capital all
        if word.isupper():
            f.append("CapAll:"+word+":"+tokens_h[2])
        # suffix and prefix features
        if len(word)>2:
            f.append("SUFF:"+word[-3:]+":"+tokens_h[2])
            f.append("PREF:"+word[:3]+":"+tokens_h[2])
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
            f.append("PREF:"+word[:2]+":"+tokens_h[2])
        elif len(word)>1:
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
            f.append("PREF:"+word[:2]+":"+tokens_h[2])
        f.append("SUFF:"+word[-1:]+":"+tokens_h[2])
        f.append("PREF:"+word[:1]+":"+tokens_h[2])
        # calculate score
        score = 0
        for feature in f:
            score += model[feature]
        scores += (hist+" "+str(score)+"\n")
    return scores+"\n"

def gen_features(sentence, tagging):
    # generate features from training sentence
    features = defaultdict(int)
    histories = tagging.strip().split("\n")
    sen = sentence.strip().split("\n")
    for i in range(len(sen)):
        f = []
        tokens_h = histories[i].split()   # tokens_h: [0]=i  [1]=t(i-1)  [2]=t(i)
        # bigram feature
        f.append("BIGRAM:"+tokens_h[1]+":"+tokens_h[2])
        tokens_s = sen[i].split()         # tokens_s: [0]=word  [1]=tag
        word = tokens_s[0]
        # tag feature
        f.append("TAG:"+word+":"+tokens_h[2])
        # capital first
        if word[0].isupper():
            f.append("CapInit:"+word+":"+tokens_h[2])
        # capital all
        if word.isupper():
            f.append("CapAll:"+word+":"+tokens_h[2])
        # suffix and prefix features
        if len(word)>2:
            f.append("SUFF:"+word[-3:]+":"+tokens_h[2])
            f.append("PREF:"+word[:3]+":"+tokens_h[2])
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
            f.append("PREF:"+word[:2]+":"+tokens_h[2])
        elif len(word)>1:
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
            f.append("PREF:"+word[:2]+":"+tokens_h[2])
        f.append("SUFF:"+word[-1:]+":"+tokens_h[2])
        f.append("PREF:"+word[:1]+":"+tokens_h[2])
        for feature in f:
            features[feature] += 1
    return features

def call_popen(popen, input):
    # input to subprocess and return output
    popen.stdin.write(input)
    output = ""
    line = popen.stdout.readline()
    while line.strip():
        if line.strip().split()[2]!="STOP":
            output += line
        line = popen.stdout.readline()
    return output

def read_sen_n_tag(file_train):
    # read and store sentences from file
    sentences = []
    while 1:
        sen = gen_sen(file_train)   # sentence with "words tag" separated by \n
        if sen:
            sentences.append(sen)
        else:
            break
    return sentences


def tagging(model, sentences):
    # generate tags of sentence with highest score
    for sentence in sentences:
        histories = call_popen(enum_popen, sentence).strip().split("\n")
        #sentence = sen.strip().split("\n")
        scores = get_scores(model, histories, sentence)
        sen_tag = call_popen(decode_propen, scores).strip().split("\n")
        sen = sentence.strip().split("\n")
        for i in range(len(sen)):
            tokens = sen_tag[i].split()
            print sen[i]+" "+tokens[2]
        print

# open files: argv[1] = training data
#             argv[2] = testing data
file_train = open(sys.argv[1], 'r')
file_test = open(sys.argv[2], 'r')
file_model = open("suffix_prefix_cap_tagger.model", 'w')

# generate subprocesses
gold_popen = subprocess.Popen(['python', 'tagger_history_generator.py', 'GOLD'],
                              stdin = subprocess.PIPE, stdout = subprocess.PIPE)
enum_popen = subprocess.Popen(['python', 'tagger_history_generator.py', 'ENUM'],
                             stdin = subprocess.PIPE, stdout = subprocess.PIPE )
decode_propen = subprocess.Popen(['python', 'tagger_decoder.py', 'HISTORY'],
                                stdin = subprocess.PIPE, stdout = subprocess.PIPE )
# read in training sentences
sentences_train = read_sen_n_tag(file_train)
# train model
model = gen_model(sentences_train)
# read in test sentences
sentences_test = read_sen_n_tag(file_test)
# generate tags for test sentences with highest score
tagging(model, sentences_test)


end = time.time()
#print (end-start)/60