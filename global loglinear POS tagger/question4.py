import sys
import subprocess
from collections import defaultdict

def read_model(file):
    # read in model from file
    model = defaultdict(int)
    for line in file:
        if line.strip():
            tokens = line.strip().split(" ")
            model[tokens[0]] = float(tokens[1])
    return model


def tagging(model, file_test):
    # generate tags of sentence with highest score
    enum_popen = subprocess.Popen(['python', 'tagger_history_generator.py', 'ENUM'],
                                 stdin = subprocess.PIPE, stdout = subprocess.PIPE )
    decode_propen = subprocess.Popen(['python', 'tagger_decoder.py', 'HISTORY'],
                                    stdin = subprocess.PIPE, stdout = subprocess.PIPE )
    while 1:
        sen = gen_sen(file_test)    # sentence with words separated by \n
        if sen:
            histories = call_popen(enum_popen, sen)
            sentence = sen.strip().split("\n")
            scores = get_scores(model, histories, sentence)
            sen_tag = call_popen(decode_propen, scores)
            for i in range(len(sentence)):
                tokens = sen_tag[i].split()
                print sentence[i]+" "+tokens[2]
            print
        else:
            break

def get_scores(model, histories, sentence):
    # get scores of local histories based on model
    # histories: [history, ]
    scores = ""
    for hist in histories:
        f = []
        tokens_h = hist.split()     # tokens_h: [0]=i  [1]=t(i-1)  [2]=t(i)
        f.append("BIGRAM:"+tokens_h[1]+":"+tokens_h[2])
        tokens_s = sentence[int(tokens_h[0])-1].split()        # tokens_s: [0]=word  [1]=tag
        word = tokens_s[0]
        f.append("TAG:"+word+":"+tokens_h[2])
        if len(word)>2:
            f.append("SUFF:"+word[-3:]+":"+tokens_h[2])
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
        elif len(word)>1:
            f.append("SUFF:"+word[-2:]+":"+tokens_h[2])
        f.append("SUFF:"+word[-1:]+":"+tokens_h[2])
        score = 0
        for feature in f:
            score += model[feature]
        scores += (hist+" "+str(score)+"\n")
    return scores+"\n"


def gen_sen(file_test):
    # read in sentences from file
    sen = ""
    for line in file_test:
        if line.strip():
            sen += line
        else:
            sen += '\n'
            return sen

def call_popen(popen, input):
    # input to subprocess and return output
    popen.stdin.write(input)
    output = []
    line = popen.stdout.readline()
    while line.strip():
        output.append(line.strip())
        line = popen.stdout.readline()
    return output


if __name__ == "__main__":
    # argv[1] = tag.model
    # argv[2] = tag_dev.dat

    file_model = open(sys.argv[1], 'r')
    file_test = open(sys.argv[2], 'r')

    model = read_model(file_model)
    tagging(model, file_test)
