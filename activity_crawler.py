from pymongo import MongoClient

from seleniumwire import webdriver
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.document_loaders import TextLoader
import os
from pymongo.operations import SearchIndexModel
from langchain_community.chat_models.friendli import ChatFriendli

MONGODB_ATLAS_CLUSTER_URI = 'mongodb+srv://team-16:wyzhdh3McMrcPtss@cluster0.tyqdayd.mongodb.net/'

client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

DB_NAME = "team-16"
COLLECTION_NAME = "todo_2"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "team_16_rag_todo_2"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
client.server_info()


os.environ['FRIENDLI_TOKEN'] = 'flp_uZdkc5WuvEeB0ztSXJjlaeXj3HplqQaUWvMGnTcfT3y5b'
llm = ChatFriendli(model="meta-llama-3-70b-instruct")


search_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "numDimensions": 1536,
                "path": "embedding",
                "similarity": "cosine",
                "type": "vector"
            }
        ]
    },
    name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    type="vectorSearch",
)


def insert_into_db(html, meta):
    with open(f'source.txt', 'w') as f:
        f.write(html)
    loader = TextLoader(f'source.txt')
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(data)
    for document in docs:
        document.metadata = dict(document.metadata, **meta)
    
    print(docs)

    os.environ['OPENAI_API_KEY'] = 'FILL'
    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=MONGODB_COLLECTION,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    )
    return vector_store.as_retriever()

import requests
from bs4 import BeautifulSoup


todo_result = ''
retriever = None
for destination in ['london', 'sydney', 'montreal', 'budapest']:
    for keyword in ['news', 'things-to-do','food-drink','culture','travel','hotels','time-out-market']:
        print('for ', destination ,keyword)
        html = requests.get(f'https://www.timeout.com/{destination}/{keyword}').text
        retriever = insert_into_db(html, {'city': destination, 'article_type': keyword})
    
