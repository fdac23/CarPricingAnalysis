from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

# Create a new client and connect to the server
client = MongoClient (MONGO_URI)

def addToMongo(zip_code, data):
	db = client ['test']
	coll = db [zip_code]
	print(coll)

	coll.insert_one(data)
