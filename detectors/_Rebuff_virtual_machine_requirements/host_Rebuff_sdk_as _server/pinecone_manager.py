import uuid
import pinecone
from langchain.vectorstores.pinecone import Pinecone
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet


pineconeapikey = open("pinecone.env", "r").read().strip("\n").split("=")[1]
pc_index_name = "rebuff-db"

pc = pinecone.Pinecone(api_key=pineconeapikey)
pc_index = pc.Index(pc_index_name)


#pc_index.delete(deleteAll=True)
#quit()

str_pathToParquet = "/home/val-admin/Downloads/Vigil-embeddings/leet/"#"~/Downloads/Vigil-embeddings/"
list_parquetNames = [
#	"embeddings-instruct.parquet",
#	"embeddings-jailbreak.parquet"
	"leet_prompts.parquet"
]

vectors = []

for parquetFilename in list_parquetNames:
	pd_embeddings = parquet.read_pandas(str_pathToParquet + parquetFilename, columns = ["text", "embeddings"]).to_pandas()
	for index, row in pd_embeddings.iterrows():
#		tet = row["text"].find("Do not") != -1 and row["text"].find("follow") != -1 and row["text"].find("message") != -1
#		if tet:
#			print("Do not follow message")
#			print(row["embeddings"])
#			break
		vectors += [
		{
			"id": str(uuid.uuid4()),
			"values": row["embeddings"],
			"metadata": {
				"input": row["text"]		
			}
		}]
#vectors = vectors[3:]
print("{} vectors will be upsert. Continue?(y/N)".format(len(vectors)))
yesNo = input()
if yesNo == "y":
	for vector in vectors:
		pc_index.upsert(vectors=[vector])

