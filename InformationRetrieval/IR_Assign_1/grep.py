import os
import subprocess
import copy
import time

#get file list
files =  os.listdir("./alldocs")
# print files


#get query list
file_queries = open('query.txt','r')
lines        = file_queries.readlines()
query_list   = []
for i in range(len(lines)):
	lines[i] = lines[i][:(len(lines[i])-1)]
	query_list.append(lines[i].split())
# print query_list

init_time = time.time()
for query in query_list:
	start_time = time.time()
	current_list = []
	for file in files:
		full_path = './alldocs/'+file
		index = 1
		exists_in_file = True
		while(index!=len(query)):
			result = subprocess.run(['grep',query[index],full_path], stdout=subprocess.PIPE)
			if result.stdout.decode('utf-8') == '':
				exists_in_file = False
				break
			index = index + 1
		if exists_in_file == True:
			current_list.append(file)
	print(query)
	print('time :',(time.time()-start_time),'s')
	# for file in current_list:
	# 	print(query[0],file)
		# result = subprocess.run(['grep','Cancer',full_path], stdout=subprocess.PIPE)
		# if result.stdout.decode('utf-8') == '':
		# 	print('no')
		# else:
		# 	print('yes')

print('total : '+str(time.time()-init_time))



