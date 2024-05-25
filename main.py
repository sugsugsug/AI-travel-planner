import os
import time
from getpass import getpass

from friendli import Friendli
import gradio as gr

from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.chat_models.friendli import ChatFriendli

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


# Input secrets

FRIENDLI_TOKEN = getpass("Friendli Token: ")
MONGODB_ATLAS_CLUSTER_URI = getpass("MongoDB Atlas cluster URI: ")
OPENAI_API_KEY = getpass("OpenAI API Key: ")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Open database
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
client.server_info()

database = client["team-16"]
mongodb_collections = [database[name] for name in database.list_collection_names()]

# Instantiate retriever
index_names = [
    "team_16_rag_flight",
    "team_16_rag_weather",
    "hotel2",
    "team_16_rag_todo_2",
]
retrievers = []
for collection, index_name in zip(mongodb_collections, index_names):
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        index_name=index_name,
    )
    retrievers.append(vector_store.as_retriever(search_kwargs={"k": 2}))


# Retrieve & generate
def chat_function(message, history):
    llm = ChatFriendli(model="meta-llama-3-70b-instruct", friendli_token=FRIENDLI_TOKEN)

    template = """Use the following pieces of context to answer the question at the end.
    If you don’t know the answer, just say that you don’t know, don’t try to make up an answer.

    Flight context: {context0}
    Weather context: {context1}
    Hotel context: {context2}
    Activity context: {context3}

    Question: {question}

    Helpful Answer:"""

    prompt = PromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context0": retrievers[0] | format_docs,
            "context1": retrievers[1] | format_docs,
            "context2": retrievers[2] | format_docs,
            "context3": retrievers[3] | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    output = rag_chain.invoke(message)
    for i in range(len(output)):
        time.sleep(0.01)
        yield output[: i + 1]


gr.ChatInterface(chat_function).launch()
