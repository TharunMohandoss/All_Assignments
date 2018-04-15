#Author : M Tharun
#Information Retrieval assignment 2
#Degree centrality algorithm and TextRank algorithm 

import os
import re
import math
import numpy
from collections import defaultdict
from pythonrouge.pythonrouge import Pythonrouge
import nltk
from copy import deepcopy

#defining global variables
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#class storing information about each sentence
class sentenceInfo:
	def __init__(self,sentenceString):
		self.sentenceString = sentenceString


#do thresholding, just delete edges whose strength doesn't cross threshold
def thresholdGraph(sentences,threshold):
	for  i in range(len(sentences)):
		for j in sentences[i].adjacencyList.keys():
			if sentences[i].adjacencyList[j] < threshold:
				del sentences[i].adjacencyList[j]


def adjustGraph(graph,nodeIndex):
	for j in graph[nodeIndex].adjacencyList.keys():
		del graph[nodeIndex].adjacencyList[j]
		del graph[j].adjacencyList[nodeIndex]
		for k in graph[j].adjacencyList.keys():
			del graph[j].adjacencyList[k]
			del graph[k].adjacencyList[j]

def degreeCentrality(sentences,wordLimit,outputFolder,threshold):
	words = 0
	summary_sentences = []
	while True:
		#find best candidate
		maximumValue = 0
		maximumIndex = -1
		for sentence in sentences:
			if len(sentence.adjacencyList) > maximumValue:
				maximumValue = len(sentence.adjacencyList)
				maximumIndex = sentence.index

		#exit condition
		words =  words + len(sentences[maximumIndex].sentenceString.split(' '))
		if maximumValue == 0 or words > wordLimit:
			break

		#remove the node and neighbours and add sentence to summary
		adjustGraph(sentences,maximumIndex)
		summary_sentences.append(maximumIndex)


	#write summary to output file and preprocess the sentences in summary
	outFile = open(outputFolder+'summary_degree_'+str(threshold)+'.txt','w')
	summary_sentenceList=[]
	for m in summary_sentences:
		curr_sent = ' '.join(sentences[m].sentenceString.strip().split('\n'))
		outFile.write(curr_sent)
		outFile.write('\n')
		summary_sentenceList.append(curr_sent)
	outFile.close()

	return summary_sentenceList

#LexRank summary
def LexRank(sentences,wordLimit,outputFolder,threshold):
	normalizationConstant = 0.01
	error_tolerance       = 0.0001

	#inititalize adjacency matrix
	adjacencyMatrix = numpy.zeros((len(sentences),len(sentences)))
	degree          = numpy.zeros((len(sentences)))
	for i in range(len(sentences)):
		for j in sentences[i].adjacencyList:
			adjacencyMatrix[i][j] = 1.0	
			degree[i] += 1
	for i in range(len(sentences)):
		for j in sentences[i].adjacencyList:
			adjacencyMatrix[i][j] /=degree[i]

	#assign prestige values by using power method
	p = numpy.ones((len(sentences)))*1.0/len(sentences)
	error = 1000  #just inititalization
	while error > error_tolerance:
		p_old = p
		p = numpy.ones((len(sentences)))*normalizationConstant*1.0/len(sentences) + (1-normalizationConstant)*numpy.matmul(adjacencyMatrix.transpose(),p)
		error = numpy.sum(numpy.absolute(p_old-p))

	#sort according to prestige values
	sentence_prestige_list = []
	sentence_index_list    = []
	for i in range(len(sentences)):
		sentence_prestige_list.append(p[i])
		sentence_index_list.append(i)

	sentence_prestige_list, sentence_index_list = (list(t) for t in zip(*sorted(zip(sentence_prestige_list, sentence_index_list))))
	sentence_index_list.reverse()

	summary_sentences_list = []
	outFile = open(outputFolder+'summary_lexRank_'+str(threshold)+'.txt','w')
	word_count = 0
	for sent_index in sentence_index_list:
		word_count += len(sentences[sent_index].sentenceString.strip().split(' '))
		if word_count >wordLimit:
			break
		curr_sent = ' '.join(sentences[sent_index].sentenceString.split('\n'))
		summary_sentences_list.append(curr_sent)
		outFile.write(curr_sent)
		outFile.write('\n')
	outFile.close()
	return summary_sentences_list


def get_tfIdf(sentences):
	#create a dict to maintain count of how many time a word occurs
	# and also calclate tf value of each word in each sentence
	vocab_dict = defaultdict(lambda:1)
	for sentence in sentences:
		wordsList = filter(lambda a:(a!=''),preprocess(sentence))
		wordSet  = set(wordsList)
		sentence.tf       = defaultdict(lambda:0)
		for word in wordSet:
			sentence.tf[word] = 0
			vocab_dict[word] += 1
		for word in wordsList:
			sentence.tf[word] +=  1

	#calculate and store tf-idf word wise for each sentence, then normalize
	for sentence in sentences:
		#calculate unnormalized
		sentence.tfIdf = dict()
		for word in sentence.tf:
			sentence.tfIdf[word] = math.log(1+sentence.tf[word])*math.log(len(vocab_dict.keys())*1.0/vocab_dict[word])

		#calculate magnitude
		magnitude = 0
		for word in sentence.tf:
			magnitude = magnitude + sentence.tfIdf[word]*sentence.tfIdf[word]
		magnitude = math.sqrt(magnitude)

		#normalize
		for word in sentence.tf:
			sentence.tfIdf[word] = sentence.tfIdf[word]/magnitude

def readTopic(topic):
	#read and parse
	sentences = []
	files = os.listdir('./'+topic)
	for file in files:
		file_open = open('./'+topic+'/'+file,'r')
		file_text = file_open.read()
		sentences = sentences + get_sentences(file_text)
	return sentences

def constructGraph(sentences):
	#assign index to each sentence and initialize empty adjacency list
	i = 0 
	for sentence in sentences:
		sentence.index = i
		sentence.adjacencyList =dict()
		i = i + 1

	#add to adjacency list if non-zero cosine
	i = 0
	length_loop = len(sentences)
	while i < length_loop:
		j = i + 1
		while j < length_loop:
			cosineValue = 0
			set1 = set(sentences[i].tfIdf.keys())
			set2 = set(sentences[j].tfIdf.keys())
			set_intersection = set1.intersection(set2)
			for word in set_intersection:
				cosineValue += sentences[i].tfIdf[word]*sentences[j].tfIdf[word]
			if cosineValue > 0.0:
				sentences[i].adjacencyList[j] = cosineValue
				sentences[j].adjacencyList[i] = cosineValue
			j = j + 1
		i = i + 1



def get_sentences(inputText):
	#Get paras
	sentence_list = []
	start_index = 0
	while (True):
		start = inputText.find('<P>',start_index) 
		end   = inputText.find('</P>',start)
		if start == -1:
			break
		sentenceList = tokenizer.tokenize(inputText[start+3:end])
		for i in range(len(sentenceList)):
			sentenceList[i] = sentenceInfo(sentenceList[i])
		sentence_list = sentence_list + sentenceList
		start_index = end
	return sentence_list

def preprocess(sentence):
	words = re.sub("[^a-zA-Z]+", " ", sentence.sentenceString)
	words = words.lower()
	words = words.split(' ')
	return words

def RougeEvaluation(refFile,summary_sentences_list):
	file_open = open(refFile,"r")
	gold_standard = tokenizer.tokenize(file_open.read())
	rouge = Pythonrouge(summary_file_exist=False,
                    summary=[summary_sentences_list], reference=[[gold_standard]],
                    n_gram=2, ROUGE_SU4=False, ROUGE_L=True,
                    recall_only=False, stemming=True, stopwords=False,
                    word_level=True, length_limit=True, length=5000,
                    use_cf=False, cf=95, scoring_formula='average',
                    resampling=True, samples=1000, favor=True, p=0.5)
	score = rouge.calc_score()
	print(score)
	print '\n'


#Starting the main program
topics = ['Topic1','Topic2','Topic3','Topic4','Topic5']
thresholds = [0.1,0.2,0.3]

#Go topicwise
for topic in topics:
	print 'TOPIC : ',topic, '\n\n'

	#create tf-idf vectors, construct full graph
	sentences = readTopic(topic)
	get_tfIdf(sentences)
	constructGraph(sentences)

	#run for each threshold
	for threshold in thresholds:
		#degreeCentrality
		sentences_copy = deepcopy(sentences)
		thresholdGraph(sentences_copy,threshold)
		summ = degreeCentrality(sentences_copy,250,'./'+topic+'_summary/',threshold)
		print 'DegreeCentrality, threshold = ',threshold
		RougeEvaluation('./'+topic+'_baseline/'+topic+'.1',summ)

		#LexRank
		sentences_copy = deepcopy(sentences)
		thresholdGraph(sentences_copy,threshold)
		summ = LexRank(sentences_copy,250,'./'+topic+'_summary/',threshold)
		print 'LexRank, threshold = ',threshold
		RougeEvaluation('./'+topic+'_baseline/'+topic+'.1',summ)

	print '\n\n\n\n'




