from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import pymongo
import os

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

# Create a new client and connect to the server
client = MongoClient (MONGO_URI)
db = client ['zipCodes']

def addToMongo(zipCode, data):
	coll = db [zipCode]

	coll.insert_one(data)

def checkIfInMongo(zipCodes):
	doesNotExsist = []
	collections = db.list_collection_names()
	
	for zipCode in zipCodes:
		if (zipCode not in collections):
			doesNotExsist.append(zipCode)
		
	return doesNotExsist
	

# addToMongo('37911', {
# 	'longitude': '35.961002',
# 	'latitude': '-83.90532',
# 	'price': '1750',
# 	'numBeds': '8',
# 	'numBath': '4',
# 	'area': '750',
# 	'address': '906 Waterfront Dr, Knoxville, TN',
# 	'timeOnZillow': '73987291',
# 	'detailURL':'/apartments/knoxville-tn/south-banks-at-suttree-landing/BtBhVS/'
# })

# list = checkIfInMongo(['37909', '37910', '37916'])
# print(list)