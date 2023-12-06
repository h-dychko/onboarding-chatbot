# from aws_langchain.kendra import AmazonKendraRetriever #custom library
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.llm import LLMChain

import boto3
from langchain.llms import Bedrock

import sys
import os
import streamlit as st
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.join(os.path.dirname(__file__), '.streamlit'), "config.toml")
load_dotenv(dotenv_path)

if os.environ.get("AWS_REGION") is None:
    os.environ["AWS_REGION"] = st.secrets["AWS"]["AWS_REGION"]
    os.environ["KENDRA_INDEX_ID"] = st.secrets["AWS"]["KENDRA_INDEX_ID"]
    os.environ["S3_BUCKET"] = st.secrets["AWS"]["S3_BUCKET"]
    os.environ["AWSAccessKeyId"] = st.secrets["AWS"]["AWSAccessKeyId"]
    os.environ["ACCESS_ID"] = st.secrets["AWS"]["ACCESS_ID"]
    os.environ["ACCESS_KEY"] = st.secrets["AWS"]["ACCESS_KEY"]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MAX_HISTORY_LENGTH = 5

def build_chain():
  region = os.environ["AWS_REGION"]
  kendra_index_id = os.environ["KENDRA_INDEX_ID"]
  access_key_id = os.environ["ACCESS_ID"]
  secret_access_key = os.environ["ACCESS_KEY"]

  session = boto3.Session(
      region_name = region,
      aws_access_key_id = access_key_id,
      aws_secret_access_key = secret_access_key
  )
  boto3_bedrock = session.client(
    service_name = "bedrock-runtime",  
    aws_access_key_id = access_key_id,
    aws_secret_access_key = secret_access_key
  )



         
  llm = Bedrock(
      client=boto3_bedrock,
      region_name = region,
      model_kwargs={"max_tokens_to_sample":300,"temperature":1,"top_k":250,"top_p":0.999,"anthropic_version":"bedrock-2023-05-31"},
      model_id="anthropic.claude-v2:1"
  )

  retriever = AmazonKendraRetriever(index_id=kendra_index_id,top_k=5,region_name=region, aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)

  prompt_template = """
  Human: You will be acting as an onboarding assistant for a newcomer location manager.

    You'll receive a newcomer's question and a piece of text from a .pptx presentation to generate an answer to the user's query. 

    Text from a .pptx presentation will be inside the block <knowledge></knowledge>.

    Firstly, you have to generate an answer to the question based on the input information in the block <knowledge></knowledge>.  
    Secondly, provide the exact truncated quotes with only relevant information for your answer.

    In case the knowledge block doesn't contain an answer to the user's query, write, "I'm sorry, but I couldn't extract the answer from the knowledge base. 
    The most relevant information I have is <knowledge></knowledge>", 
    where instead of <knowledge></knowledge> put the information from the <knowledge></knowledge> block.
    If there is no information in the knowledge blovk, you need to write the sentence: "I'm sorry, but I couldn't extract the answer from the knowledge base".

    You are forbidden to use any additional information except from the knowledge block.
    You are forbidden to rephrase the same information in one answer for more or equal one time. 
    You are forbidden to cite yourself in the answer. You're allowed to cite knowledge block only and no more than one time.

    Do not repeat the question in your answer; do not rephrase the question block in your answer.
    You are forbidden to include intro and summary/conclusion parts and anything except neat and short-spoken information in your answer. 
    You are forbidden to include synonyms of the phrase 'my answer' with meaning that it's your answer in your answer.


  Human: Here are a few pieces of knowledge in <knowledge> tags:
  <knowledge>
  {context}
  </knowledge>

    Based on the above knowledge, provide a short informative answer for {question}. 
    In case the knowledge block doesn't contain an answer to the user's query, write exactly 
    "I'm sorry, but I couldn't extract the answer from the knowledge base. The most relevant information I have is <knowledge></knowledge>", 
    where instead of knowledge put the information from the knowledge block.
    You are forbidden to use any additional information except from the knowledge block. 
    
    Do not repeat the question in your answer; do not rephrase the question block in your answer.
    You are forbidden to include intro and summary/conclusion parts and anything except neat and short-spoken information in your answer. 
    You are forbidden to include synonyms of the phrase 'my answer' with meaning that it's your answer in your answer.


  Assistant:
  """
  PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )

  condense_qa_template = """{chat_history}
  Human:
  Given the previous conversation and a follow up question below, rephrase the follow up question
  to be a standalone question.

  Follow Up Question: {question}
  Standalone Question:

  Assistant:"""
  standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)


  
  qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        condense_question_prompt=standalone_question_prompt, 
        return_source_documents=True, 
        combine_docs_chain_kwargs={"prompt":PROMPT},
        verbose=True)

  return qa


def run_chain(chain, prompt: str, history=[]):
  return chain({"question": prompt, "chat_history": history})


# if __name__ == "__main__":
#   chat_history = []
#   qa = build_chain()
#   print(bcolors.OKBLUE + "Hello! How can I help you?" + bcolors.ENDC)
#   print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
#   print(">", end=" ", flush=True)
#   for query in sys.stdin:
#     if (query.strip().lower().startswith("new search:")):
#       query = query.strip().lower().replace("new search:","")
#       chat_history = []
#     elif (len(chat_history) == MAX_HISTORY_LENGTH):
#       chat_history.pop(0)
#     result = run_chain(qa, query, chat_history)
#     import re
    
#     result["answer"] = re.sub("<knowledge>", result["answer"], "")
#     result["answer"] = re.sub("</knowledge>", result["answer"], "")

#     chat_history.append((query, result["answer"]))
#     print(bcolors.OKGREEN + result['answer'] + bcolors.ENDC)
#     if 'source_documents' in result:
#       print(bcolors.OKGREEN + 'Sources:')
#       for d in result['source_documents']:
#         print(d.metadata['source'])
#     print(bcolors.ENDC)
#     print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
#     print(">", end=" ", flush=True)
#   print(bcolors.OKBLUE + "Bye" + bcolors.ENDC)
  
