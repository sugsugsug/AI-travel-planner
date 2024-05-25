from pymongo import MongoClient
from time import sleep
from flask import Flask
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire.utils import decode
from pymongo.operations import SearchIndexModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredHTMLLoader, TextLoader
from langchain_core.documents import Document
from langchain_community.chat_models.friendli import ChatFriendli
from selenium.webdriver.common.action_chains import ActionChains
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import datetime
import requests


MONGODB_ATLAS_CLUSTER_URI = "mongodb+srv://team-16:wyzhdh3McMrcPtss@cluster0.tyqdayd.mongodb.net/"  # mongodb+srv://team-xx:<password>@cluster0.tyqdayd.mongodb.net/

client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

DB_NAME = "team-16"
COLLECTION_NAME = "hotel2"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "hotel2"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
client.server_info()

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
client[DB_NAME][COLLECTION_NAME].create_search_index(search_model)


#loader = PyPDFLoader("https://openreview.net/pdf?id=HVKmLi1iR4")
#data = loader.load()

docs = None
def insert_into_db(html):
    #with open('read.txt', 'w') as f:
    #    f.write(html)
    #loader = PyPDFLoader("https://openreview.net/pdf?id=HVKmLi1iR4")
    loader = UnstructuredHTMLLoader('read.txt')
    data = loader.load()
#print(data)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(data)
    docs.append(Document(page_content=html, metadata={"source": "read.txt"}))
    print(docs)

    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=(), openai_api_key=''),
        collection=MONGODB_COLLECTION,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    )
    retriever = vector_store.as_retriever()
    return retriever



def do_():
    origin = 'seoul'
    destination = 'london'
    start_day = '2024-05-28'
    end_day = '2024-06-04'
    driver = webdriver.Chrome()
    hotel_result = None
    flight_result = None
    weather_result = None
    todo_result = None
    try:
        # Hotel
        driver.get('https://www.google.com/search?q=hotel+in+%s+from+%s+to+%s' % (destination, start_day, end_day))
        driver.maximize_window()
        go_to_hotel_detail = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "S8ee5.CwbYXd.wHYlTd"))
        )
        go_to_hotel_detail.click()
        for i, request in enumerate(driver.requests):
            if request.response:
                try:
                    response_str = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                    if response_str.find('<div ng-non-bindable=""><div class="gb_m">Google 앱</div><div class="gb_Qc">') != -1:
                    #if response_str.find('Four Points by') != -1:
                        #print(response_str)
                        hotel_result = response_str
                        print(request.url)
                        print(i)
                        print(response_str)
                        file = open('read.txt', 'w')
                        file.write(response_str)
                        file.close()
                except:
                    continue
        print('hotel done')
        """
        #Flight
        driver.get(f'https://www.google.com/travel/flights?tfs=CBwQARocagwIAhIIL20vMGhzcWZyDAgDEggvbS8wMWN4XxocagwIAxIIL20vMDFjeF9yDAgCEggvbS8waHNxZkABSAFwAYIBCwj___________8BmAEB&tfu=KgIIAw')
        driver.maximize_window()
        start_date = datetime.datetime.strptime(start_day, "%Y-%m-%d")
        start_date_str = f'{start_date.strftime("%b")} {start_date.day}'
        end_date = datetime.datetime.strptime(end_day, "%Y-%m-%d")
        end_date_str = f'{end_date.strftime("%b")} {end_date.day}'
        day_inputs = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME,"TP4Lpb.eoY5cb.j0Ppje"))
        )
        day_inputs[0].send_keys(start_date_str)
        day_inputs[1].send_keys(end_date_str)
        origin_input = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input"))
        )
        origin_input.clear()
        origin_input.send_keys(origin)
        #origin_input.send_keys(Keys.RETURN)
        destination_input = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input"))
        )
        destination_input.clear()
        destination_input.send_keys(destination)
        actions = ActionChains(driver)
        for _ in range(5):
            actions = actions.send_keys(Keys.TAB)
            actions.perform()
            sleep(1)
        actions = actions.send_keys(Keys.ENTER)
        actions.perform()
        sleep(5)

        html = driver.page_source
        for i, request in enumerate(driver.requests):
            if request.response:
                try:
                    response_str = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                    if response_str.find('China Eastern') != -1:
                        print(response_str)
                    sleep(2)

                    if response_str.find('</script><div ng-non-bindable=""><div class="gb_m">Google apps</div><div class="gb_Qc">Main menu</div></div>') != -1:
                        flight_result = response_str
                        file = open('read.txt', 'w')
                        file.write(response_str)
                        file.close()
                        print(response_str)
                        print(request.url)
                        print(i)

                except:
                    continue

        file = open('read.txt', 'w')
        html = html[:html.find('>')+1] + f"<text>{driver.current_url}</text>" + html[html.find('>')+1:]
        file.write(html)
        file.close()
        print(html)
        print('flight done')
        """
        return driver.current_url
    finally:
        driver.quit()

html = do_()
retriever = insert_into_db(html)

llm = ChatFriendli(model="meta-llama-3-70b-instruct", friendli_token='flp_tvA96ZqprR7OyaZLDXqqkNQkJ928ZI45AtqhEIwwkAcw44')


template = """Use the following pieces of context to answer the question at the end.
If you don’t know the answer, just say that you don’t know, don’t try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say “thanks for asking!” at the end of the answer.

{context}

Question: {question}

Helpful Answer:"""

prompt = PromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

rag_chain.invoke('''
    recommend me good hotels for my trip(2024-05-28 to 2024-06-04) to boston from seoul
    give me price, location, review, any facilities and link definitely please
    give me the results good to view like (1.~~~ \n 2. ~~~ \n)
''')
