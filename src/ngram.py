from turkishnlp import detector
import sys
import pickle
import os
import math

dir_name = "ngram_tables/"
corpus_name = "turkish_dump_input"
test_name = "turkish_dump_test"

def separator(obj, line):
    # end of sentence and punctuations are also considered as syllable
    syllables = []

    splitted = line.split()
    # save each syllable, space, punctuation as a separate element
    for word in splitted:
        # if word 
        word_syllables = obj.syllabicate(word)
        for syllable in word_syllables:
            
            # if syllable has punctuation, separate it
            if syllable[-1] in [".", ",", ";", ":", "?", "!", "/", "\\", "'", "\"", "(", ")"]:
                syllables.append(syllable[:-1])
                syllables.append(syllable[-1])

            # if syllable has punctution at start, separate it
            elif syllable[0] in [".", ",", ";", ":", "?", "!", "/", "\\", "'", "\"", "(", ")"]:
                syllables.append(syllable[0])
                syllables.append(syllable[1:])
            else:
                syllables.append(syllable)

        # if it is not the last word, add space
        if word != splitted[-1]:
            syllables.append(" ")

    return syllables

def preprocess(line):
    obj = detector.TurkishNLP()

    # convert all of them to lowercase
    line = line.lower()

    # convert turkish characters to english characters
    line = line.replace("ç", "c")
    line = line.replace("ğ", "g")
    line = line.replace("ı", "i")
    line = line.replace("ö", "o")
    line = line.replace("ş", "s")
    line = line.replace("ü", "u")

    # separate words to syllables
    syllables = separator(obj, line)
    # print(syllables)

    return syllables

def write_to_file(n_gram, file_name):

    # create directory if not exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # write n-gram table to file
    with open(dir_name + file_name, "wb") as file:
        pickle.dump(n_gram, file)

    # clear n-gram table
    # n_gram.clear()

# create all possible turkish syllables and store them in dictionary with key as syllable and value as count
def turkish_syllabes():

    dict = {}
    vowels = ["a", "e", "i", "o", "u"]
    consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l",
                  "m", "n", "p", "r", "s", "t", "v", "y", "z"]
    # 1. only vowels v
    
    for vowel in vowels:
        dict[vowel] = 0

    # 2. vowel + consonant -> vc + cv
    for vowel in vowels:
        for consonant in consonants:
            dict[vowel + consonant] = 0
            dict[consonant + vowel] = 0

    # 3. consonant + vowel + consonant -> cvc + vcc
    for consonant in consonants:
        for vowel in vowels:
            for consonant2 in consonants:
                dict[consonant + vowel + consonant2] = 0
                dict[vowel + consonant + consonant2] = 0

    # 4. consonant + vowel + consonant + consonant -> cvcc 
    for consonant in consonants:
        for vowel in vowels:
            for consonant2 in consonants:
                for consonant3 in consonants:
                    dict[consonant + vowel + consonant2 + consonant3] = 0
                    #dict[consonant3 + consonant + vowel + consonant2] = 0

    # add punctuations
    dict["."] = 0
    dict[","] = 0
    dict[";"] = 0
    dict[":"] = 0
    dict["?"] = 0
    dict["!"] = 0
    dict["/"] = 0
    dict["\\"] = 0
    dict["'"] = 0
    dict["\""] = 0
    dict["("] = 0
    dict[")"] = 0
    dict[" "] = 0
    dict["\""] = 0

    return dict

# add if only key exists
def fill_gram(n_gram, syllables, n):
    # if n is 1, key is string, if n is more than 1, key is tuple
    # do not add if key is not in n-gram table
    if n == 1:
        for syllable in syllables:
            if syllable in n_gram:
                n_gram[syllable] += 1
    else:
        for i in range(len(syllables)-n+1):
            key = tuple(syllables[i:i+n])
            if key in n_gram:
                n_gram[key] += 1

# fill gram for trigram
# trigram: <((syllable1, syllable2), syllable3), count>
def fill_gram_tri(n_gram, syllables):
    for i in range(len(syllables)-2):
        key = ((syllables[i], syllables[i+1]), syllables[i+2])
        if key in n_gram:
            n_gram[key] += 1

def write_to_file_txt(n_gram, file_name):
    # write n-gram table to file
    with open(file_name, "w", encoding="utf-8") as file:
        for key, value in n_gram.items():
            file.write(str(key) + " " + str(value) + "\n")

def read_ngram_table(file_name):
    # read n-gram table from file, if not exists throw error
    if not os.path.exists(dir_name + file_name):
        print("unigram not found: ", file_name)
        sys.exit()

    # read n-gram table from file
    file = open(dir_name + file_name, "rb")

    # print("file_name: ", file_name)
    n_gram = pickle.load(file)

    file.close()

    return n_gram

# trigram: <tuple[syllable1, syllable2, syllable3], count>
def read_trigram_table(file_name):
    # read n-gram table from file, if not exists throw error
    if not os.path.exists(dir_name + file_name):
        print("trigram not found: ", file_name)
        sys.exit()

    # read n-gram table from file
    with open(dir_name + file_name, "rb") as file:
        trigram = {}
        while True:
            try:
                key, value = pickle.load(file)
                trigram[key] = value
            except EOFError:
                break

    return trigram

def perplexity_unigram(uni_gram, file):

    # set file pointer to the beginning
    file.seek(0)

    # unigram is: <syllable, probability>
    log_perplexity = 0
    N = 0  # total number of syllables

    # read test file
    for line in file:

        syllables = preprocess(line)
        N += len(syllables)

        for syllable in syllables:
            if syllable in uni_gram:
                log_perplexity -= math.log(uni_gram[syllable])
            else:
                # calculate probability of unseen syllables
                log_perplexity -= math.log(0.000001)
                


    perplexity = math.exp(log_perplexity / float(N))
    return perplexity

def perplexity_bigram(bi_gram, file):

    # set file pointer to the beginning
    file.seek(0)

    # bigram is: <tuple[syllable1, syllable2], probability>
    log_perplexity = 0
    N = 0  # total number of syllables

    # read test file
    for line in file:

        syllables = preprocess(line)
        N += len(syllables) - 1

        for i in range(len(syllables)-1):
            if (syllables[i], syllables[i+1]) in bi_gram:
                log_perplexity -= math.log(bi_gram[(syllables[i], syllables[i+1])])
            else:
                # handle unseen syllables
                log_perplexity -= math.log(0.000001)


    perplexity = math.exp(log_perplexity / float(N))
    return perplexity

    


