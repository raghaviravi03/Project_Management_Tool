# database.py

from pymongo import MongoClient
from bson import ObjectId
import sys
import streamlit as st
import ssl

MONGO_URI = st.secrets['MONGO_URI']

client = MongoClient(MONGO_URI, ssl_cert_reqs=ssl.CERT_NONE)

def get_db(company_name):
    # client = MongoClient(config("MONGO_URI"))
    db = client[company_name]
    return db

def get_users_collection():  # Add this function
    # client = MongoClient(config("MONGO_URI"))
    db = client['global_users']  # Name of the global users collection
    collection = db["users"]
    print(collection)
    return collection

