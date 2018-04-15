import os
import subprocess
import copy
import time
import re
import pickle
import nltk
import time

class IndexList:
	def __init__(self):
		self.count = 0
		self.doc_list = []

#get file list
files =  os.listdir("./alldocs")

stemmer = nltk.stem.porter.PorterStemmer()

#assign docids
name_to_docid = dict()
docid_to_name = dict()
i = 0 
for file in files:
	name_to_docid[file] = i
	docid_to_name[i]    = file
	i                   = i + 1

#read inverse index
dictionary_inverted_index = pickle.load( open( "save.p", "rb" ) )

# print 'words : ',len(dictionary_inverted_index)


#get query list
file_queries = open('query.txt','r')
lines        = file_queries.readlines()
query_list   = []
for i in range(len(lines)):
	lines[i] = lines[i][:(len(lines[i])-1)]
	split = lines[i].split()
	words = split[1:]
	stemmed_words = [ stemmer.stem(word) for word in words]
	query_list.append( (split[0],stemmed_words) )
# print query_list

init_time = time.time()
for query in query_list:
	# print 'query : ',query
	current = time.time()
	if query[1][0] in dictionary_inverted_index:
		current_list = set(dictionary_inverted_index[query[1][0]].doc_list)
	else:
		current_list  = set()
	i = 1
	while i < len(query[1]):
		# print query[1][i]
		if query[1][i] in dictionary_inverted_index:
			next_list = set(dictionary_inverted_index[query[1][i]].doc_list)
			current_list = current_list.intersection(next_list)
		else:
			current_list = set()
		i = i + 1
	diff = time.time() - current
	for doc in current_list:
		print query[0],' : ',diff
print 'total :',time.time() - init_time




