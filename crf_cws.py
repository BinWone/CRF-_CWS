# -*- coding: utf-8 -*-
#
# CRF Segmenter based character tagging:
#     4 tags for character tagging: B(Begin), E(End), M(Middle), S(Single)

import codecs
import sys

import CRFPP

# 载入词典，用来做前后向最大匹配分词
def load_dict(filename): 
    f = codecs.open(filename, 'r', encoding = 'utf-8')
    maxLen = 1 
    word_set = set()
    
    for line in f.readlines()[1:]:
        if not line:
            continue
        word = line.split('\t')[0]
        word_set.add(word)
        if len(word) > maxLen:  
            maxLen = len(word) 
    return word_set, maxLen

# 前向最大匹配分词
def split_word_fmm(sentence,max_len,word_set):
    begin = 0
    words = []
    while begin < len(sentence):
        for end in range(min(begin + max_len,len(sentence)),begin,-1):
            if sentence[begin:end] in word_set or end == begin + 1:
                words.append(sentence[begin:end])
                break
        begin = end
    return words

# 后向最大匹配分词
def get_k_words(text,i,k):
    if i+1<k:
        return text[0:i+1],i+1
    else:
        return text[i-(k-1):i+1],k

def split_word_rmm(text,k,dict_words):
    seg_words = ""
    i=len(text)-1
    while i>=0:
        tmp_words,length = get_k_words(text,i,k)
        tmp_len=0
        for j in range(length):
            if tmp_words[j:length] in dict_words:
                seg_words+=(tmp_words[j:length]+" ")
                tmp_len=length-j
                break
            if j==length-1 and not tmp_words[j:length] in dict_words:
                seg_words+=(tmp_words[j:length]+" ")
                tmp_len=length-j
        i = i-tmp_len

    return seg_words.strip().split()[::-1]

"""
def is_punc(word):
    punc = [u'，', u',', u'"', u'“', u'”', u'、', u'：',  u'。', u'！', u'？', u'【', u'】', u'[', u']', u'（', u'）', u'：', u'《', u'》', u'-', u'-', u'%', u'*', u'/', u'.', u'°', u'—']
    if word in punc:
        return 'PUNC'
    else:
        return 'NPUNC'
"""

def cat(word):
    
    num = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0',
           u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'○' ,u'零', u'个', u'十', u'百', u'千', u'万', u'亿']
    time = [u'年', u'月', u'日', u'时', u'分', u'秒']
    punc = [u'，', u',', u'"', u'“', u'”', u'、', u'：',  u'。', u'！', u'？', u'【', u'】', u'[', u']', u'（', u'）', u'：', u'《', u'》', u'-', u'-', u'%', u'*', u'/', u'.', u'°', u'—']

    
    if word in num:
        return 'NUM'
    elif word in time:
        return 'TIM'
    elif word in punc:
        return 'PUNC'
    else:
        return 'CN'

def crf_segmenter(sentence, tagger):
    sentence = ''.join([i.strip() for i in sentence])
    output_data = ''
    tagger.clear()
    sentence_fmm = split_word_fmm(sentence, max_len, word_set)
    sentence_rmm = split_word_rmm(sentence, max_len, word_set)
    # print sentence_fmm, sentence_rmm
    fmm_res, rmm_res = [], []
    for word in sentence_fmm:
        if len(word) == 1:
            fmm_res.append('S')
        else:
            fmm_res.append('B')
            for w in word[1:len(word)-1]:
                fmm_res.append('M')
            fmm_res.append('E')
    for word in sentence_rmm:
        if len(word) == 1:
            rmm_res.append('S')
        else:
            rmm_res.append('B')
            for w in word[1:len(word)-1]:
                rmm_res.append('M')
            rmm_res.append('E')
    idx = 0
    for word in sentence.strip():
        word = word.strip()
        if word:
            word_tags = word + '\t' + cat(word) + '\t' + fmm_res[idx] + '\t' + rmm_res[idx] + "\tB"
            tagger.add(word_tags.encode('utf-8'))  # CN\tS\tS
            idx += 1
    tagger.parse()
    size = tagger.size()
    xsize = tagger.xsize()
    #print(type(tagger),size,xsize)
    for i in range(0, size):
        #for j in range(0, xsize):
        char = tagger.x(i, 0).decode('utf-8')
        tag = tagger.y2(i)
        #print tagger.x(i, 0),tag
        if tag == 'B':
            output_data += ' ' + char
        elif tag == 'M':
            output_data += char
        elif tag == 'E':
            output_data += char + ' '
        else: # tag == 'S'
            output_data += ' ' + char + ' '
    return output_data

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "pls use: python crf_cws.py model input output"
        sys.exit()
    max_len = 5  # 前后向最大匹配分词的词最大长度 
    word_set, _ = load_dict("./dict.utf8")
    crf_model = sys.argv[1]
    tagger = CRFPP.Tagger("-m " + crf_model)
    if len(sys.argv) == 4:
        input_file = sys.argv[2]
        output_file = sys.argv[3]

        input_data = codecs.open(input_file, 'r', 'utf-8')
        output_data = codecs.open(output_file, 'w', 'utf-8')
        for line in input_data.readlines():
            crf_cws_res = crf_segmenter(line, tagger)
            print crf_cws_res
            output_data.write(crf_cws_res + '\n')
        input_data.close()
        output_data.close()
    

