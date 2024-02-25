import ngram as ngram_fun
import unigram
import bigram
import trigram

def perplexity_unigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test unigram
    print("testing unigram...")
    file_name_uni = "unigram_table.bin"
    uni_gram = ngram_fun.read_ngram_table(file_name_uni)
    print("perplexity of unigram: ", ngram_fun.perplexity_unigram(uni_gram, file))
    file.close()

def perplexity_bigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test bigram
    print("testing bigram...")
    file_name_bi = "bigram_table.bin"
    bi_gram = ngram_fun.read_ngram_table(file_name_bi)
    print("perplexity of bigram: ", ngram_fun.perplexity_bigram(bi_gram, file))
    file.close()

def perplexity_trigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test trigram
    print("testing trigram...")
    print("perlexity of trigram: ", trigram.perplexity_trigram())
    file.close()

def sentence_unigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test unigram
    print("testing unigram...")
    file_name_uni = "unigram_table.bin"
    uni_gram = ngram_fun.read_ngram_table(file_name_uni)
    sentence = unigram.generate_random_sentence_unigram(uni_gram)
    print("sentence of unigram: ", sentence)
    file.close()

def sentence_bigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test bigram
    print("testing bigram...")
    file_name_bi = "bigram_table.bin"
    bi_gram = ngram_fun.read_ngram_table(file_name_bi)
    sentence = bigram.generate_random_sentence_bigram(bi_gram)
    print("sentence of bigram: ", sentence)
    file.close()

def sentence_trigram_fun():
    file = open(ngram_fun.test_name, "r", encoding="utf-8")
    # test trigram
    print("testing trigram...")
    sentence = trigram.generate_random_sentence_trigram()
    print("sentence of trigram: ", sentence)
    file.close()



