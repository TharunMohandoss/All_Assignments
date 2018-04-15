import os
import numpy as np
import pickle
import re
from copy import deepcopy
import os
import subprocess
import copy
import time
import sys, lucene
import re
import pickle
from os import path, listdir
from java.io import File
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import RAMDirectory, SimpleFSDirectory
import time
import os
import math
import gc

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory

# Retriever imports:
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from nltk.corpus import stopwords



files =  os.listdir("./alldocs")
vocab = []


i=0
for file in files:
	print i,len(files)
	i = i +1
	openFile             = open('./alldocs/'+file)
	stringText           = openFile.read()
	text                 = re.sub("[^a-zA-Z]+"," ",stringText)
	text         	     = text.lower()
	words                = text.split()#[x for x in text.split(' ') if not x in stop_words]

	vocab += words
	vocab = list(set(words))




file_queries = open('query.txt','r')
lines        = file_queries.readlines()
for query in lines:
    current_query = query[5:].strip()
    vocab += re.sub("[^a-zA-Z]+"," ",current_query).split(' ')
    vocab = list(set(vocab))

pickle_out = open("vocab_2.pickle","wb")
pickle.dump(vocab, pickle_out)
pickle_out.close()
file_queries.close()

vocab = set(vocab)

# pickle_in = open("vocab_2.pickle","rb")
# vocab = pickle.load(pickle_in)
# pickle_in.close()


file_open = open('glove.840B.300d.txt','r')


i=0
word_to_num = dict()
num_to_word = dict()
line = file_open.readline()

print 'len :',len(vocab)

numpy_array = np.zeros((len(vocab),300),dtype=float)
while line:
	# print i
	terms = line.split(' ')
	if terms[0] in vocab:
		print i
		word_to_num[terms[0]] = i
		num_to_word[i]        = terms[0]
		j = 1
		while j < 301:
			numpy_array[i][j-1] = float(terms[j].strip('\n').strip('\r'))
			if numpy_array[i][j-1] == 0:
				print 'zero : ',terms[j].strip('\n').strip('\r')
			if np.isnan(numpy_array[i][j-1]):
				print 'nan : ',terms[j].strip('\n').strip('\r')
			j = j +1
		if numpy_array[i][1] == 0:
			print 'zero : ',line
		if np.isnan(numpy_array[i][1]):
			print 'nan : ',line
		i = i +1
	line = file_open.readline()

print 'words used : ',i
words_used = i
file_open.close()

pickle_out = open("numpy.pickle","wb")
pickle.dump(numpy_array, pickle_out)
pickle_out.close()

pickle_out = open("word_to_num.pickle","wb")
pickle.dump(word_to_num, pickle_out)
pickle_out.close()

pickle_out = open("num_to_word.pickle","wb")
pickle.dump(num_to_word, pickle_out)
pickle_out.close()

pickle_in = open("numpy.pickle","rb")
numpy_array = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open("word_to_num.pickle","rb")
word_to_num = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open("num_to_word.pickle","rb")
num_to_word = pickle.load(pickle_in)
pickle_in.close()

normalized_numpy_array = deepcopy(numpy_array)
for i in range(len(word_to_num)):
	if np.isnan(np.sqrt(np.sum(np.square(normalized_numpy_array[i])))):
		print i
		print normalized_numpy_array[i]
		print numpy_array[i]
	normalized_numpy_array /= np.sqrt(np.sum(np.square(normalized_numpy_array[i])))

#correct files
query_answers = dict()
results_open = open('output.txt','r')
for line in results_open.read().split('\n'):
	# print line
	if int(line[0:3]) not in query_answers:
		query_answers[int(line[0:3])] = [line[4:].strip()]
	else:
		query_answers[int(line[0:3])].append(line[4:].strip())
results_open.close()


#get file list
files =  os.listdir("./alldocs")
vocab = dict()

def create_document(file_name):
    path = './alldocs/'+file_name # assemble the file descriptor
    file = open(path) # open in read mode
    doc = Document() # create a new document
    # add the title field
    doc.add(StringField("title", file_name, Field.Store.YES))
    # add the whole book
    doc.add(TextField("text", file.read(), Field.Store.YES))
    file.close() # close the file pointer
    return doc

class docInfo(object):
	"""Class to store info about each doc"""
	def __init__(self, fileName):
		self.fileName = fileName
		
#lucene stuff
lucene.initVM()
directory = RAMDirectory()
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, 1000000)
config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
writer = IndexWriter(directory, config)

i=0
for file in files:
	print i,len(files)
	i = i +1
	doc = create_document(file)
	writer.addDocument(doc)

writer.close()


searcher = IndexSearcher(DirectoryReader.open(directory))

file_expanded_queries = open('expanded_query','wb')
file_expanded_queries_vector = open('query_vector','wb')
file_expanded_queries_performance = open('Performance_after_query_expansion','wb')
file_queries = open('query.txt','r')
lines        = file_queries.readlines()
avg_prec       = 0 
avg_recall     = 0 
avg_fScore     = 0
avg_prec_new   = 0
avg_recall_new = 0 
avg_fScore_new = 0
for query in lines:
    current_query = query[5:].strip()
    print 'query : ',len(current_query),':',current_query
    file_expanded_queries.write(current_query+'|')
    file_expanded_queries_vector.write('query : '+current_query+'\n')
    file_expanded_queries_performance.write(query[0:5]+' ')
    query2 = QueryParser(Version.LUCENE_CURRENT, "text", analyzer).parse(current_query)
    scoreDocs = searcher.search(query2, 50).scoreDocs
    results_obtained = []
    for scoreDoc in scoreDocs:
    	results_obtained.append(searcher.doc(scoreDoc.doc).get("title").strip())
        # print scoreDoc
    # print query
    precision  = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(results_obtained))
    recall     = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(query_answers[int(query[0:3])]))
    # print precision
    # print recall
    # print precision*recall/(precision+recall)
    avg_prec   += precision
    avg_recall += recall
    avg_fScore += 2.0*precision*recall/(precision+recall)
    new_query_vector = dict()
    query_words = re.sub("[^a-zA-Z]+"," ",current_query).split(' ')
    vector = np.zeros((300),dtype = float)
    for word in query_words:
    	if word in word_to_num:
	    	vector += numpy_array[word_to_num[word]]
    for vectorVal in vector:
    	file_expanded_queries_vector.write(str(vectorVal)+' ')
    file_expanded_queries_vector.write('\n')

    values = np.matmul(normalized_numpy_array,vector)
    sorting_list = []
    for i in range(len(word_to_num)):
    	sorting_list.append((values[i],num_to_word[i]))
    sorting_list.sort(reverse=True)
    words_added = 0
    k = 0
    words_to_add = []
    while words_added < 5:
    	if sorting_list[k][1] not in query_words:
    		words_added += 1
    		words_to_add.append(sorting_list[k][1])
    	k = k +1

    new_query = current_query+ ' ' +' '.join(words_to_add)
    file_expanded_queries.write(new_query+'\n')
    query2 = QueryParser(Version.LUCENE_CURRENT, "text", analyzer).parse(new_query)
    scoreDocs = searcher.search(query2, 50).scoreDocs
    results_obtained = []
    for scoreDoc in scoreDocs:
    	results_obtained.append(searcher.doc(scoreDoc.doc).get("title").strip())
    precision  = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(results_obtained))
    recall     = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(query_answers[int(query[0:3])]))
    avg_prec_new   += precision
    avg_recall_new += recall
    avg_fScore_new += 2.0*precision*recall/(precision+recall)
    file_expanded_queries_performance.write(str(precision)+' ')
    file_expanded_queries_performance.write(str(recall)+' ')
    file_expanded_queries_performance.write(str(2.0*precision*recall/(precision+recall))+' ')
    file_expanded_queries_performance.write('\n')

    
avg_recall /= len(lines)
avg_prec   /= len(lines)
avg_fScore /= len(lines)
avg_recall_new /= len(lines)
avg_prec_new   /= len(lines)
avg_fScore_new /= len(lines)
print 'average prec : ',avg_prec
print 'average recall : ',avg_recall
print 'average fScore : ',avg_fScore
print 'average prec_new : ',avg_prec_new
print 'average recall_new : ',avg_recall_new
print 'average fScore_new : ',avg_fScore_new

file_expanded_queries_performance.write('average prec_new : '+str(avg_prec_new)+'\n')
file_expanded_queries_performance.write('average recall_new : '+str(avg_recall_new)+'\n')
file_expanded_queries_performance.write('average fScore_new : '+str(avg_fScore_new)+'\n')





file_expanded_queries.close()
file_expanded_queries_vector.close()
file_expanded_queries_performance.close()






