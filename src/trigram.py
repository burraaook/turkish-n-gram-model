import ngram as ngram_fun
import unigram
import bigram
import sys
import os
import pickle
import multiprocessing
import math
import random

# 200 MB
MAX_MEMORY_USAGE = 200 * 1024 * 1024
file_name_tri = "trigram_table_"
TRIGRAM_TABLE_COUNT = 0

# useful for finding file
# <(tuple1, tuple2), count>
# <((start_key1, start_key2), start_key3), (end_key1, end_key2), end_key3), count>
tri_gram_handbook = {}

# trigram = <((syllable1, syllable2), syllable3), probability>
def create_empty_trigram(unigram, bigram):
    # data structure for trigram: <((syllable1, syllable2), syllable3), count>
    trigram = {}

    count = 0
    written = False
    bigram_keylist = sorted(list(bigram.keys()))
    unigram_keylist = sorted(list(unigram.keys()))
    # create empty trigram table
    for key1 in bigram_keylist:
        for key2 in unigram_keylist:

            written = False

            tuple = ((key1[0], key1[1]), key2)
            trigram[tuple] = 0

            # if memory usage is more than 200 MB, write to file
            if sys.getsizeof(trigram) > MAX_MEMORY_USAGE:
                # write trigram to file as trigram_table_count.bin
                ngram_fun.write_to_file(trigram, file_name_tri + str(count) + ".bin")

                # add to handbook consist of start and end tuples as key, and count as value
                #print(trigram.keys())

                # find max, and min keys
                key_list = list(trigram.keys())

                key_h1 = key_list[0]
                key_h2 = key_list[len(key_list) - 1]

                print("key1: " + str(key_h1) + ", key2: " + str(key_h2) + ", count: " + str(count))

                # add to handbook
                tri_gram_handbook[(key_h1, key_h2)] = count

                written = True
                count += 1
                # clear trigram
                trigram.clear()
    
    if not written:
        # write trigram to file as trigram_table.bin
        ngram_fun.write_to_file(trigram, file_name_tri + str(count) + ".bin")

        # add to handbook consist of start and end tuples as key, and count as value
        key_list = list(trigram.keys())
        key1 = key_list[0]
        key2 = key_list[len(key_list) - 1]

        print("key1: " + str(key1) + ", key2: " + str(key2) + ", count: " + str(count))

        # add to handbook
        tri_gram_handbook[(key1, key2)] = count
        
        written = True
        count += 1
        # clear trigram
        trigram.clear()

    # write handbook to file
    file2 = open(ngram_fun.dir_name + "trigram_handbook.bin", "wb")
    pickle.dump(tri_gram_handbook, file2)

    TRIGRAM_TABLE_COUNT = count

def tri_gram_prob(trigram, bigram):
    # <((syllable1, syllable2), syllable3), probability>
    # gt smoothing

    # calculate frequency of frequencies
    freq_of_freq = {}

    for count in trigram.values():
        if count not in freq_of_freq:
            freq_of_freq[count] = 0
        freq_of_freq[count] += 1

    print("size of freq_of_freq: ", len(freq_of_freq))

    # calculate smoothed probabilities
    smoothed_trigram = {}
    for key, count in trigram.items():
        if count + 1 in freq_of_freq:
            smoothed_count = (count + 1) * freq_of_freq[count + 1] / freq_of_freq[count]
        else:
            smoothed_count = count
        smoothed_trigram[key] = smoothed_count / bigram[key[0]]

    return smoothed_trigram

def count_trigram(trigram_file_name, bigram, unigram):
    trigram = ngram_fun.read_ngram_table(trigram_file_name)
    file = open(ngram_fun.corpus_name, "r", encoding="utf-8")

    for line in file:

        # pass wiki doc tags
        if line.startswith("<doc") or line.startswith("</doc"):
            continue

        # preprocess line
        syllables = ngram_fun.preprocess(line)

        # iterate over the syllables to create trigrams
        for i in range(len(syllables) - 2):
            # create the trigram
            trigram_key = ((syllables[i], syllables[i+1]), syllables[i+2])

            # check if syllabe is in the unigram, and bigram
            if trigram_key[0] not in bigram or trigram_key[1] not in unigram:
                continue

            if trigram_key not in trigram:
                continue
            # else:
                # print("trigram_key: " + str(trigram_key) + " found in trigram table: " + str(tri_gram_handbook[key]))
                # exit()

            # add to trigram table
            trigram[trigram_key] += 1
            # print("pid: " + str(os.getpid()) + ", trigram_key: " + str(trigram_key))

    # write the updated trigram table back to the file
    ngram_fun.write_to_file(trigram, trigram_file_name) 

# hand_book_cache = <file_count, syllables>
def calculate_log_perplexity(hand_book_cache):

    log_perplexity = 0    
    # get each list of syllables
    for file_count, syllables in hand_book_cache.items():
        # read trigram table from file
        trigram = ngram_fun.read_ngram_table(file_name_tri + str(file_count) + ".bin")

        # calculate log perplexity
        for syllable in syllables:
            log_perplexity -= math.log(trigram[syllable])

    return log_perplexity
    
def perplexity_trigram():
    # read handbook
    tri_gram_handbook = ngram_fun.read_ngram_table("trigram_handbook.bin")
    bigram = ngram_fun.read_ngram_table("bigram_counts.bin")
    unigram = ngram_fun.read_ngram_table("unigram_counts.bin")
    test_file = open(ngram_fun.test_name, "r", encoding="utf-8")

    # <file_count, syllables>: <int, list>
    hand_book_cache = {}
    count = 0
    log_perplexity = 0
    N = 0  # total number of syllables
    cache_size = 1000
    for line in test_file:

        # preprocess line
        syllables = ngram_fun.preprocess(line)
        N += len(syllables)

        # iterate over the syllables to create trigrams
        for i in range(len(syllables) - 2):
            # create the trigram
            trigram_key = ((syllables[i], syllables[i+1]), syllables[i+2])

            # check if syllabe is in the unigram, and bigram
            if trigram_key[0] not in bigram or trigram_key[1] not in unigram:
                log_perplexity -= math.log(0.000001)
                continue

            # add trigram key to handbook cache
            # determine its file_count
            for key, value in tri_gram_handbook.items():
                if key[0] <= trigram_key <= key[1]:
                    # add to handbook cache
                    if value not in hand_book_cache:
                        hand_book_cache[value] = []
                    hand_book_cache[value].append(trigram_key)
                    count += 1
                    break

    if count > 0:
        # print("count: ", count)
        # calculate log perplexity
        log_perplexity += calculate_log_perplexity(hand_book_cache)
        # clear handbook cache
        hand_book_cache.clear()

    # calculate perplexity
    perplexity = math.exp(log_perplexity / float(N))
    return perplexity

def generate_random_sentence_trigram():
    # get handbook
    tri_gram_handbook = ngram_fun.read_ngram_table("trigram_handbook.bin")
    file_count = 0

    # best_starters()
    current_syllable = pick_starter_syllable()
    next_syllable = current_syllable[1]
    sentence = current_syllable[0][0] + current_syllable[0][1] + next_syllable
    
    
    # generate rest of the sentence
    while not sentence.endswith(('.', '!', '?')) and len(sentence.split()) < 15:
        
        cur_tup = (current_syllable[0][1], current_syllable[1])
        # print("cur_syllable: ", current_syllable)
        # find the file of the current syllable
        for key, value in tri_gram_handbook.items():
            # print("key[0][0]: " + str(key[0][0]) + ", cur_tup: " + str(cur_tup) + ", key[1]: " + str(key[1][0]))
            if key[0][0] <= cur_tup <= key[1][0]:
                
                # get the file
                trigram = ngram_fun.read_ngram_table(file_name_tri + str(value) + ".bin")
                break

        # get the 5 most probable syllables
        next_syllables = sorted([(k, v) for k, v in trigram.items() if k[0] == cur_tup], key=lambda x: x[1], reverse=True)[:5]

        # if there are no next syllables, find another syllable
        if not next_syllables:
            # print("no next syllables")

            current_syllable = pick_starter_syllable()
            sentence += current_syllable[0][0] + current_syllable[0][1] + current_syllable[1]
            continue

        # choose the next syllable with weighted probabilities
        syllables, probabilities = zip(*[(k[1], v) for k, v in next_syllables])
        next_syllable = random.choices(syllables, weights=probabilities, k=1)[0]

        # print("current_syllable: ", current_syllable)
        # print("next_syllable: ", next_syllable)
        # add the next syllable to the sentence
        sentence += next_syllable

        # update the current syllable as trigram
        current_syllable = ((current_syllable[0][1], current_syllable[1]), next_syllable)
        # print("current_syllable_after: " + str(current_syllable))
        trigram.clear()

        print("current_sentence: ", sentence)
    return sentence

# find 5 best starter syllables
# best 5 syllable after ('.', ' ')
def best_starters():
    # read handbook
    tri_gram_handbook = ngram_fun.read_ngram_table("trigram_handbook.bin")
    trigram = {}
    target = ('.', ' ')
    # get the file of the ('.', ' ')
    for key, value in tri_gram_handbook.items():
        print("key: " + str(key) + ", value: " + str(value))
        if key[0][0] <= target <= key[1][0]:
            # get the file
            trigram = ngram_fun.read_ngram_table(file_name_tri + str(value) + ".bin")
            break
    
    # print("trigram: ", trigram)
    # get the 5 most probable syllables after ('.', ' ')
    most_probable_syllables = sorted([(k, v) for k, v in trigram.items() if k[0] == target], key=lambda x: x[1], reverse=True)[:15]

    # print("most_probable_syllables: ", most_probable_syllables)

    # convert them to (' ', syllable) format
    for i in range(len(most_probable_syllables)):
        most_probable_syllables[i] = (' ', most_probable_syllables[i][0][1])
    
    # print("most_probable_syllables converted: ", most_probable_syllables)

    # write to binary file
    file = open(ngram_fun.dir_name + "most_probable_starters.bin", "wb")
    pickle.dump(most_probable_syllables, file)
    file.close()

    # return the syllables
    return most_probable_syllables

def pick_starter_syllable():

    while True:
        # get most probable starters
        file = open(ngram_fun.dir_name + "most_probable_starters.bin", "rb")
        file.seek(0)
        most_probable_starters = pickle.load(file)
        file.close()
        
        # get random syllable
        most_probable_starter = random.choice(most_probable_starters)
        most_probable_starter = most_probable_starter[1]
        # print("most_probable_starter: ", most_probable_starter)

        file_count = 0

        # find the file of the current syllable
        for key, value in tri_gram_handbook.items():
            # print("key[0][0][0]: " + str(key[0][0][0]) + ", most_probable_starter: " + str(most_probable_starter) + ", key[1][0][0]: " + str(key[1][0][0]))
            if key[0][0][0] <= most_probable_starter <= key[1][0][0]:
                # get the file
                file_count = value
                break

        # read trigram table from file
        trigram = ngram_fun.read_ngram_table(file_name_tri + str(file_count) + ".bin")

        # get the 5 most probable syllables: ((most_probable_starter, syllable2), syllable3)). return list of tuples (most_probable_starter, syllable2, syllable3)
        next_syllables = sorted([(k, v) for k, v in trigram.items() if k[0][0] == most_probable_starter], key=lambda x: x[1], reverse=True)[:5]

        # print("next_syllables: ", next_syllables)
        # if there are no next syllables, find another syllable
        if not next_syllables:
            # print("no next syllables2")
            continue
        
        # choose current syllable with weighted probabilities
        syllables, probabilities = zip(*[(k, v) for k, v in next_syllables])

        current_syllable = random.choices(syllables, weights=probabilities, k=1)[0]

        # print("current_syllable: ", current_syllable)
        
        trigram.clear()
        return current_syllable
    
def create_trigram_table():
    unigram = ngram_fun.read_ngram_table("unigram_counts.bin")
    bigram = ngram_fun.read_ngram_table("bigram_counts.bin")

    # create empty trigram table
    create_empty_trigram(unigram, bigram)

    tri_gram_handbook = ngram_fun.read_ngram_table("trigram_handbook.bin")
    print("handbook: " + str(tri_gram_handbook))

    # log multi-processing
    multiprocessing.log_to_stderr()

    # read file line by line
    
    # count trigrams, create process for each trigram table, 2 processes parallel
    TRIGRAM_TABLE_COUNT = len(tri_gram_handbook)

    for i in range(0, TRIGRAM_TABLE_COUNT, TRIGRAM_TABLE_COUNT // 3):
        processes = []
        start = i
        end = min(i + TRIGRAM_TABLE_COUNT // 3, TRIGRAM_TABLE_COUNT)

        for j in range(start, end):
            # print("start: " + str(start) + ", end: " + str(end) + ", j: " + str(j))
            if j >= TRIGRAM_TABLE_COUNT:
                break

            # create process
            p = multiprocessing.Process(target=count_trigram, args=(file_name_tri + str(j) + ".bin", bigram, unigram))
            processes.append(p)
            p.start()
            print("process started: " + str(j))

        # wait for all processes in the current set to finish
        for p in processes:
            p.join()
    
    # calculate all files
    for i in range(TRIGRAM_TABLE_COUNT):
        # read trigram table from file
        trigram = ngram_fun.read_ngram_table(file_name_tri + str(i) + ".bin")
        trigram = tri_gram_prob(trigram, bigram)
        ngram_fun.write_to_file(trigram, file_name_tri + str(i) + ".bin")

    # save best 5 starter syllables
    best_starters()