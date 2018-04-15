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

def tfIdfCalculator(tf,idf,N):
	return math.log(1+tf)*math.log(N*1.0/idf)

stop_words = set(stopwords.words('english'))


#correct files
query_answers = dict()
results_open = open('output.txt','r')
for line in results_open.read().split('\n'):
	# print line
	if int(line[0:3]) not in query_answers:
		query_answers[int(line[0:3])] = [line[4:].strip()]
	else:
		query_answers[int(line[0:3])].append(line[4:].strip())


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



#empty documentInfoList
docInfoList = dict()

#initialize empty vocab
vocab = dict()

#get query list
file_queries = open('query.txt','r')
lines        = file_queries.readlines()
query_list   = []
file_queries.close()
for i in range(len(lines)):
	lines[i] = lines[i][:(len(lines[i])-1)]
	query_list.append(lines[i].split())

i=0
for file in files:
	print i,len(files)
	i = i +1
	doc                  = docInfo(file)
	openFile             = open('./alldocs/'+file)
	stringText           = openFile.read()
	text                 = re.sub("[^a-zA-Z0-9]+"," ",stringText)
	text         	     = text.lower()
	words                = text.split()#[x for x in text.split(' ') if not x in stop_words]
	# doc.wordList = words
	doc.tf       = dict()
	for word in words:
		if word in doc.tf:
			doc.tf[word] +=  1
		else:
			doc.tf[word] = 1
	for word in set(words):
		if word in vocab:
			vocab[word] += 1
		else:
			vocab[word] = 1
	docInfoList[file] = doc
	openFile.close()

for document in docInfoList:
	doc = docInfoList[document]
	normalization_constant = 0
	for word in doc.tf:
		value        = tfIdfCalculator(doc.tf[word],vocab[word],len(vocab))
		doc.tf[word] = value
		normalization_constant += value*value
	normalization_constant = math.sqrt(normalization_constant)
	for word in doc.tf:
		doc.tf[word] /= normalization_constant

pickle_out = open("doc_info_list.pickle","wb")
pickle.dump(docInfoList, pickle_out)
pickle_out.close()

pickle_out = open("vocab.pickle","wb")
pickle.dump(vocab, pickle_out)
pickle_out.close()

# pickle_in = open("doc_info_list.pickle","rb")
# docInfoList = pickle.load(pickle_in)
# pickle_in.close()

# pickle_in = open("vocab.pickle","rb")
# vocab = pickle.load(pickle_in)
# pickle_in.close()

#query results
# results_obtained = dict()

#get queries and process
file_queries = open('query.txt','r')
file_expanded_queries_performance_initial = open('Performance_before_relevance_feedback','wb')
file_expanded_queries_performance_final = open('Performance_after_relevance_feedback','wb')
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
    file_expanded_queries_performance_initial.write(query[0:5]+' ')
    file_expanded_queries_performance_final.write(query[0:5]+' ')
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
    file_expanded_queries_performance_initial.write(str(precision)+' ')
    file_expanded_queries_performance_initial.write(str(recall)+' ')
    file_expanded_queries_performance_initial.write(str(2.0*precision*recall/(precision+recall))+'\n')
    new_query_vector = dict()
    query_words = re.sub("[^a-zA-Z]+"," ",current_query).split(' ')
    new_query_tfIdf = dict()
    for word in query_words:
        if word in new_query_tfIdf:
            new_query_tfIdf[word] += 1
        else:
            new_query_tfIdf[word] = 1
    normalization_constant = 0
    for word in new_query_tfIdf:
        if word in vocab:
            value = tfIdfCalculator(new_query_tfIdf[word],vocab[word],len(vocab))
            normalization_constant +=  value*value
            new_query_tfIdf[word] = value
        else:
            new_query_tfIdf[word] = 1
    normalization_constant = math.sqrt(normalization_constant)
    for word in new_query_tfIdf:
        if word in vocab:
            new_query_tfIdf[word] /= normalization_constant

    beta = 0.65
    top_N = 10
    i=0
    while i<top_N:
        docName = searcher.doc(scoreDocs[i].doc).get("title").strip()
        doc = docInfoList[docName]
        for word in doc.tf:
            if word in new_query_tfIdf:
                new_query_tfIdf[word] += beta*doc.tf[word]/top_N
            else:
                new_query_tfIdf[word] = beta*doc.tf[word]/top_N
        i = i + 1
    sorting_list = []
    for word in new_query_tfIdf:    
        sorting_list.append((new_query_tfIdf[word],word))
    sorting_list.sort(reverse = True)
    # print sorting_list
    final_word_list = []
    i = 0
    top_N_words = 10
    while i < top_N_words:
        final_word_list.append(sorting_list[i][1])
        i = i  + 1
    final_query_string = ' '.join(final_word_list)
    print 'changed query : ',final_query_string
    query2 = QueryParser(Version.LUCENE_CURRENT, "text", analyzer).parse(final_query_string)
    scoreDocs = searcher.search(query2, 50).scoreDocs
    results_obtained = []
    for scoreDoc in scoreDocs:
    	results_obtained.append(searcher.doc(scoreDoc.doc).get("title").strip())
    precision  = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(results_obtained))
    recall     = len(set(results_obtained).intersection(set(query_answers[int(query[0:3])])))*1.0/(len(query_answers[int(query[0:3])]))
    avg_prec_new   += precision
    avg_recall_new += recall
    avg_fScore_new += 2.0*precision*recall/(precision+recall)
    file_expanded_queries_performance_final.write(str(precision)+' ')
    file_expanded_queries_performance_final.write(str(recall)+' ')
    file_expanded_queries_performance_final.write(str(2.0*precision*recall/(precision+recall))+'\n')

file_expanded_queries_performance_initial.close()
file_expanded_queries_performance_final.close()
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





file_queries.close()


