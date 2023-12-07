import streamlit as st
from st_files_connection import FilesConnection
import uuid
import sys
import os
import re

import kendra_chat_bedrock_claudev2 as bedrock_claudev2
import toml

import boto3


USER_ICON = "images/user-icon.png"
AI_ICON = "images/ai-icon.jpg"
MAX_HISTORY_LENGTH = 5

from dotenv import load_dotenv

load_dotenv()

if os.environ.get("AWS_DEFAULT_REGION") is None:
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["AWS"]["AWS_DEFAULT_REGION"]
    os.environ["AWS_S3_BUCKET"] = st.secrets["AWS"]["AWS_S3_BUCKET"]
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_KENDRA_INDEX_ID"] = st.secrets["AWS"]["AWS_KENDRA_INDEX_ID"]

conn = st.connection('s3', type=FilesConnection)
df = conn.read(f"{os.environ['AWS_S3_BUCKET']}/test.txt", input_format='text')

SOURCES_DICT = {
  f"https://{os.environ['AWS_S3_BUCKET']}.s3.amazonaws.com/Internal%20Audit%20LMO%20June%202023.pptx": {
    "file_name": "Internal Audit LMO June 2023.pptx"
  },
  f"https://{os.environ['AWS_S3_BUCKET']}.s3.amazonaws.com/LMO-FOCUS-Presentation_Oct-2023.pptx": {
    "file_name": "LMO-FOCUS-Presentation_Oct-2023.pptx"
    },
  f"https://{os.environ['AWS_S3_BUCKET']}.s3.amazonaws.com/Risk%20%26%20Insurance%20LMO%202023.pptx": {
    "file_name": "Risk & Insurance LMO 2023.pptx"
  },
  f"https://{os.environ['AWS_S3_BUCKET']}.s3.amazonaws.com/Payroll_HRIS+LMO_2023_+.pptx": {
    "file_name": "Payroll_HRIS LMO_2023_ .pptx"
  },
  f"https://{os.environ['AWS_S3_BUCKET']}.s3.amazonaws.com/Procurement%20LMO%202023%20Rev%20A%20JRM.pptx": {
    "file_name": "Procurement LMO 2023 Rev A JRM.pptx"
  }
}


def create_presigned_url(bucket_name, object_name, region, secret_access_key, access_key_id, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    session = boto3.Session(
        region_name = region,
        aws_access_key_id = access_key_id,
        aws_secret_access_key = secret_access_key
    )
    boto3_s3 = session.client(
        service_name = "s3",  
        aws_access_key_id = access_key_id,
        aws_secret_access_key = secret_access_key
    )
    response = boto3_s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=expiration
    )
    return response

# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id


st.session_state['llm_app'] = bedrock_claudev2
st.session_state['llm_chain'] = bedrock_claudev2.build_chain()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    
if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""


st.markdown("""
        <style>
               .block-container {
                    padding-top: 32px;
                    padding-bottom: 32px;
                    padding-left: 0;
                    padding-right: 0;
                }
                .element-container img {
                    background-color: #000000;
                }

                .main-header {
                    font-size: 24px;
                }
        </style>
        """, unsafe_allow_html=True)

def write_logo():
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        st.image(AI_ICON, use_column_width='always') 


def write_top_bar():
    col1, col2, col3 = st.columns([1,10,2])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        header = f"Hi, it's your onboarding assistant!"
        st.write(f"<h2 class='main-header'>{header}</h2>", unsafe_allow_html=True)
    with col3:
        clear = st.button("Clear Chat")
    return clear

clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []

def handle_input():
    input = st.session_state.input
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state['llm_chain']
    chain = st.session_state['llm_app']
    result = chain.run_chain(llm_chain, input, chat_history)

    result["answer"] = re.sub("<knowledge>", "", result["answer"])
    result["answer"] = re.sub("</knowledge>", "",  result["answer"])

    answer = result['answer']
    chat_history.append((input, answer))
    
    document_list = []
    if 'source_documents' in result:
        for d in result['source_documents']:
            if not (d.metadata['source'] in document_list):
                document_list.append((d.metadata['source']))

    st.session_state.answers.append({
        'answer': result,
        'sources': document_list,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""

def write_user_message(md):
    col1, col2 = st.columns([1,12])
    
    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        st.warning(md['question'])


def render_result(result):
    answer, sources = st.tabs(['Answer', 'Sources'])
    with answer:
        render_answer(result['answer'])
    with sources:
        if 'source_documents' in result:
            render_sources(result['source_documents'])
        else:
            render_sources([])

def render_answer(answer):
    col1, col2 = st.columns([1,12])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        st.info(answer['answer'])

def render_sources(sources):
    col1, col2 = st.columns([1,12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                url = create_presigned_url(
                    os.environ['AWS_S3_BUCKET'], SOURCES_DICT[s]['file_name'], 
                    region=os.environ['AWS_DEFAULT_REGION'], 
                    secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], 
                    access_key_id=os.environ['AWS_ACCESS_KEY_ID']
                )
                st.markdown(f"<a href='{url}'>{SOURCES_DICT[s]['file_name']}</a>", unsafe_allow_html=True)

    
#Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    chat = st.container()
    with chat:
        render_answer(md['answer'])
        render_sources(md['sources'])
    
        
with st.container():
  for (q, a) in zip(st.session_state.questions, st.session_state.answers):
    write_user_message(q)
    write_chat_message(a, q)

st.markdown('---')
input = st.text_input("It's your an AI-based assistant. How can I help you?", key="input", on_change=handle_input)
