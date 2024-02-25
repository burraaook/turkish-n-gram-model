import ngram as ngram_fun
import random
import pickle

# calculate probability with good turing smoothing
def bi_gram_prob(bi_gram, uni_gram_counts):
    # <tuple[syllable1, syllable2], count> -> <tuple[syllable1, syllable2], probability>
    
    # p(a|b) = c(a,b) / c(b)
    # gt smoothing

    # calculate frequency of frequencies
    freq_of_freq = {}

    for count in bi_gram.values():
        if count not in freq_of_freq:
            freq_of_freq[count] = 0
        freq_of_freq[count] += 1

    print("size of freq_of_freq: ", len(freq_of_freq))

    # calculate smoothed probabilities
    smoothed_bi_gram = {}

    for key, count in bi_gram.items():
        if count + 1 in freq_of_freq:
            smoothed_count = (count + 1) * freq_of_freq[count + 1] / freq_of_freq[count]
        else:
            smoothed_count = count
        smoothed_bi_gram[key] = smoothed_count / uni_gram_counts[key[0]]

    return smoothed_bi_gram

def create_empty_bigram(uni_gram):
    # data structure for bi-gram: <tuple[syllable1, syllable2], count>
    bigram = {}

    # create empty bi-gram table
    for key1 in uni_gram.keys():
        for key2 in uni_gram.keys():
            bigram[(key1, key2)] = 0
    
    return bigram

# generate random sentence with shannon's method
# sentences ends with "." or "!" or "?"
# choose next syllable from 5 most probable syllables
def generate_random_sentence_bigram(bigram):
    current_syllable = random.choice(list(bigram.keys()))
    sentence = current_syllable[0] + current_syllable[1]

    while not sentence.endswith(('.', '!', '?')) and len(sentence.split()) < 100:
        # get the 5 most probable syllables
        next_syllables = sorted([(k, v) for k, v in bigram.items() if k[0] == current_syllable[1]], key=lambda x: x[1], reverse=True)[:5]
        
        # if there are no next syllables, break the loop
        if not next_syllables:
            break

        # choose the next syllable with weighted probabilities
        syllables, probabilities = zip(*[(k[1], v) for k, v in next_syllables])
        next_syllable = random.choices(syllables, weights=probabilities, k=1)[0]

        sentence += next_syllable

        # update the current syllable
        current_syllable = (current_syllable[1], next_syllable)

    return sentence

# after (' ', ' ') is the most probable 5 starter syllables
def most_probable_starter_syllables(file):
    # set file pointer to the beginning
    file.seek(0)

    # array of starter syllables
    starter_syllabes = []

    # TODO

    return starter_syllabes

def create_bigram():
    unigram = ngram_fun.read_ngram_table("unigram_counts.bin")
    bigram = create_empty_bigram(unigram)

    # fill bi-gram table
    print("filling bi-gram table...")
    file = open(ngram_fun.corpus_name, "r", encoding="utf-8")
    for line in file:

        # pass wiki doc tags
        if line.startswith("<doc") or line.startswith("</doc"):
            continue

        # preprocess line
        syllables = ngram_fun.preprocess(line)

        # add_to_n_gram(uni_gram, syllables, n)
        ngram_fun.fill_gram(bigram, syllables, 2)

    # save bi_gram counts to binary file
    # open file
    file2 = open(ngram_fun.dir_name + "bigram_counts.bin", "wb")
    bigram2 = {}

    # remove zero counts
    for key, value in bigram.items():
        if value > 80:
            bigram2[key] = value

    # write to file
    pickle.dump(bigram2, file2)

    # write to txt file
    # ngram_fun.write_to_file_txt(bigram2, "bigram_counts.txt")

    file2.close()
    
    print("size bi-gram non-zero: ", len(bigram2))
    bigram2.clear()

    print("calculating probabilities of bi-gram table...")
    bigram = bi_gram_prob(bigram, unigram)
    ngram_fun.write_to_file(bigram, "bigram_table.bin")
    ngram_fun.write_to_file_txt(bigram, "bigram_table.txt")



