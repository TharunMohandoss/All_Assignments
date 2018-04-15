
import sys, lucene
from os import path, listdir

from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import RAMDirectory
from datetime import datetime

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory

# Retriever imports:
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser

#get file list
files =  os.listdir("./alldocs")

def create_document(file_name):
    path = './alldocs/'+file_name
    file = open(path)
    doc = Document()
    doc.add(StringField("title", input_file, Field.Store.YES))
    doc.add(TextField("text", file.read(), Field.Store.YES))
    file.close()
    return doc

# Initialize lucene and the JVM
lucene.initVM()


directory = RAMDirectory()
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, NoT)
config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
writer = IndexWriter(directory, config)


print "Number of indexed documents: %d\n" % writer.numDocs()
for input_file in listdir(INPUT_DIR):
    print "Current file:", input_file
    doc = create_document(input_file)
    writer.addDocument(doc)

print "\nNumber of indexed documents: %d" % writer.numDocs()
writer.close()
print "Indexing done!\n"
print "------------------------------------------------------"

