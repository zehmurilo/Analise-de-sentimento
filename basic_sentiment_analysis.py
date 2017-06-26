from pprint import pprint
import nltk
import yaml
import sys
import os
import re

saida = ""
increment, decrement, inverse, positiveTag, negativeTag, neutralTag = 0, 0, 0, 0, 0, 0
totalIncrement, totalDecrement, totalInverse, totalPositiveTag, totalNegativeTag, totalNeutralTag = 0, 0, 0, 0, 0, 0


class Splitter(object):

    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):

    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

class DictionaryTagger(object):

    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

def value_of(sentiment):
    if sentiment == 'positive':
        global positiveTag, totalPositiveTag
        positiveTag +=1 
        totalPositiveTag +=1
        return 1
    if sentiment == 'negative':
        global negativeTag, totalNegativeTag
        negativeTag +=1
        totalNegativeTag +=1
        return -1
    if sentiment != 'positive' and sentiment != 'negative':
        global neutralTag, totalNeutralTag
        neutralTag +=1
        totalNeutralTag +=1
        return 0
    return 0

def sentence_score(sentence_tokens, previous_token, acum_score):    
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
                global increment, totalIncrement
                increment += 1
                totalIncrement +=1
            elif 'dec' in previous_tags:
                token_score /= 2.0
                global decrement, totalDecrement
                decrement +=1
                totalDecrement +=1
            elif 'inv' in previous_tags:
                token_score *= -1.0
                global inverse, totalInverse
                inverse +=1
                totalInverse +=1
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])


def runSentiment(splitSentences, posTagSentences, dictSentences):
    totalScore = 0
    splitter = Splitter()
    postagger = POSTagger()
    dicttagger = DictionaryTagger([ 'dicts/positive.yml', 'dicts/negative.yml', 
                                    'dicts/inc.yml', 'dicts/dec.yml', 'dicts/inv.yml'])
    outputFile = open("output/output.txt", 'w')
    file_count = len([name for name in os.listdir('database')])
    for x in range(1,file_count  + 1):
        text = open('database/document' + str(x) + '.txt', 'r').read()
        print ("Analyzing Document " + str(x))
        splitted_sentences = splitter.split(text)
        #TODO - na interface deixar opção para selecionar ou nao, splitted_sentences, pos_tagged_sentences and dict_tagger_sentences
        if(splitSentences == 1):
            pprint(splitted_sentences)
        
        pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
        if(posTagSentences == 1):
            pprint(pos_tagged_sentences)

        dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)
        if(dictSentences == 1):
            pprint(dict_tagged_sentences)
        
        print("analyzing sentiment...")
        score = sentiment_score(dict_tagged_sentences)
        totalScore += score
        print(score)

        outputFile.write("Document " + str(x))
        global increment, decrement, inverse, positiveTag, negativeTag, neutralTag
        outputFile.write(" Increment Value: " + str(increment))
        outputFile.write(" Decrement Value: " + str(decrement))
        outputFile.write(" Inverse Value: " + str(inverse))
        outputFile.write(" Positive words: " + str(positiveTag))
        outputFile.write(" Negative words: " + str(negativeTag))
        outputFile.write(" Neutral words: " + str(neutralTag))
        outputFile.write(" Sentimental Score: " + str(score))
        outputFile.write("\n")

        increment, decrement, inverse, positiveTag, negativeTag, neutralTag = 0, 0, 0, 0, 0, 0

    outputFile.write("\n")
    global totalIncrement, totalDecrement, totalInverse, totalPositiveTag, totalNegativeTag, totalNeutralTag
    outputFile.write("Total de documentos analisados: " + str(file_count) + "\n")
    outputFile.write(" Total de palavras incrementais: " + str(totalIncrement) + "\n")
    outputFile.write(" Total de palavras decrementais: " + str(totalDecrement) + "\n")
    outputFile.write(" Total de palavras inversas: " + str(totalInverse) + "\n")
    outputFile.write(" Total de palavras positivas: " + str(totalPositiveTag) + "\n")
    outputFile.write(" Total de palavras negativas: " + str(totalNegativeTag) + "\n")
    outputFile.write(" Total de palavras neutras: " + str(totalNeutralTag) + "\n")
    outputFile.write(" Sentimental Score Total: " + str(totalScore) + "\n")

    totalIncrement, totalDecrement, totalInverse, totalPositiveTag, totalNegativeTag, totalNeutralTag = 0, 0, 0, 0, 0, 0


    print("Documento com dados das analises gerado com sucesso")
    outputFile.close()

    
    
    

    

