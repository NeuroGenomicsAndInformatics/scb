# used to populate mongodb server

import sys
from pymongo import MongoClient
import pandas as pd


# take db connection stirng from the commandline as an argument
cstring = sys.argv[1]

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient(cstring)
db=client.admin

fileList = ["test1.txt", "test2.txt", "test3.txt", "test4.txt", "test5.txt", "test6.txt", "test7.txt", "test8.txt", "test9.txt", "test10.txt", "test11.txt", "test12.txt", "test13.txt", "test14.txt", "test15.txt", "test16.txt", "test17.txt", "test18.txt", "test19.txt", "test20.txt", "test21.txt", "test22.txt", "test23.txt", "test24.txt", "test25.txt", "test26.txt"]


for link in fileList:
	df2 = pd.read_csv(link, delimiter=' ')
	querylist = []
	#print (df2.columns)
	for gene in df2.index.values:
	    book = {}
	    curGene = df2.loc[ gene , : ]
		
	    for i in range(0, len(df2.loc[ gene , : ])):
	        if curGene[i] != 0:
	        	book[str(i)] = int(curGene[i])
	    query = {
	        'name': gene,
	        'values': book
	    }
		
	    querylist.append(query)

	db.genesfull.insert(querylist)       
