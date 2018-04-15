







#get output list
file_queries = open('output.txt','r')
lines        = file_queries.readlines()
file_queries.close()
actual_dict = dict()
for query in lines:
	query_no = int(query[0:3])
	if query_no  in actual_dict:
		actual_dict[query_no].append(query[4:].strip(' \n'))
	else:
		actual_dict[query_no] = [query[4:].strip(' \n')]

	# print actual_dict

#get output list
file_queries = open('lucene_output.txt','r')
lines        = file_queries.readlines()
file_queries.close()
predicted_dict = dict()
for query in lines:
	query_no = int(query[0:3])
	if query_no  in predicted_dict:
		predicted_dict[query_no].append(query[4:].strip(' \n'))
	else:
		predicted_dict[query_no] = [query[4:].strip(' \n')]

# print predicted_dict.keys()

precision_avg = 0
recall_avg = 0
for i in range(150):
	j = i +701
	if j in predicted_dict:
		print j
		precision = len(set(predicted_dict[j]).intersection(set(actual_dict[j])))*1.0/len(set(set(predicted_dict[j])))
		precision_avg += precision
		print precision
		recall= len(set(predicted_dict[j]).intersection(set(actual_dict[j])))*1.0/len(set(set(actual_dict[j])))
		recall_avg += recall
		print recall

print 'avg precision  =',  precision_avg/len(predicted_dict.keys())
print 'avg recall     =',  recall_avg/len(predicted_dict.keys())




