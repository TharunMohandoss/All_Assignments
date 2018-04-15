import sys, lucene
from os import path, listdir
from java.io import File
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import RAMDirectory, SimpleFSDirectory
import time
import os

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory

# Retriever imports:
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser

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

#get file list
file_list = os.listdir("./alldocs/")



lucene.initVM()
directory = RAMDirectory()
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, 1000000)
config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
writer = IndexWriter(directory, config)


for file in file_list:
	doc = create_document(file)
	writer.addDocument(doc)

writer.close()

searcher = IndexSearcher(DirectoryReader.open(directory))

#get queries and process
file_queries = open('query.txt','r')
lines        = file_queries.readlines()
for query in lines:
    current_query = query[5:].strip()
    query2 = QueryParser(Version.LUCENE_CURRENT, "text", analyzer).parse(current_query)
    start = time.time()
    scoreDocs = searcher.search(query2, 50).scoreDocs
    duration = time.time() - start
    print query,':',duration
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        temp_str = str(doc.get("title"))
        # print str(query[0:3]),' ',temp_str




