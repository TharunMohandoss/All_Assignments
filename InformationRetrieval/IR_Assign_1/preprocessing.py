import os
import subprocess
import copy
import time
import re
import pickle
import nltk


class IndexList:
	def __init__(self):
		self.count = 0
		self.doc_list = []

#get file list
files =  os.listdir("./alldocs")


#assign docids
name_to_docid = dict()
docid_to_name = dict()
i = 0 
for file in files:
	name_to_docid[file] = i
	docid_to_name[i]    = file
	i                   = i + 1

#make inverse index
i=0
dictionary_inverted_index = dict()
for file in files:
	print i
	file_handler = open('./alldocs/'+file,'r')
	text         = file_handler.read()
	text         =  re.sub("[^a-zA-Z]+"," ",text)
	text         = text.lower()
	words        = text.split(' ')
	stemmer = nltk.stem.porter.PorterStemmer()
	for word in words:
		word = stemmer.stem(word)
		if not word in dictionary_inverted_index:
			newList = IndexList()
			newList.count = 1
			newList.doc_list.append(i)
			dictionary_inverted_index[word] = newList
		else:
			existingList = dictionary_inverted_index[word]
			if(existingList.doc_list[-1]!=i):
				existingList.count = existingList.count  + 1
				existingList.doc_list.append(i)
	i = i + 1

pickle.dump(dictionary_inverted_index,open("save.p","w"))
dictionary_inverted_index = pickle.load( open( "save.p", "rb" ) )

print 'words : ',len(dictionary_inverted_index)


