import streamlit as st
from st_files_connection import FilesConnection
import uuid
import sys
import os
import re

# import kendra_chat_bedrock_claudev2 as bedrock_claudev2
import toml


USER_ICON = "images/user-icon.png"
AI_ICON = "images/ai-icon.jpg"
MAX_HISTORY_LENGTH = 5

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.join(os.path.dirname(__file__), '.streamlit'), "config.toml")
load_dotenv(dotenv_path)

if os.environ.get("AWS_REGION") is None:
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["AWS"]["AWS_DEFAULT_REGION"]
    os.environ["KENDRA_INDEX_ID"] = st.secrets["AWS"]["KENDRA_INDEX_ID"]
    os.environ["S3_BUCKET"] = st.secrets["AWS"]["S3_BUCKET"]
    os.environ["AWSAccessKeyId"] = st.secrets["AWS"]["AWSAccessKeyId"]
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["AWS"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS"]["AWS_SECRET_ACCESS_KEY"]

conn = st.experimental_connection('s3', type=FilesConnection)
st.write(conn)

conn = st.experimental_connection("s3", type=FilesConnection)
df = conn.read(f"test-kendra-2/requirements.txt", input_format='text')

# SOURCES_DICT = {
#   f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Internal%20Audit%20LMO%20June%202023.pptx": {
#     "link": f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Internal%20Audit%20LMO%20June%202023.pptx?AWSAccessKeyId={os.environ['AWSAccessKeyId']}&Signature=9H9obJLIlDN8h1A5loU35toqipY%3D&Expires=1702482499",
#     "file_name": "Internal Audit LMO June 2023.pptx"
#   },
#   f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/LMO-FOCUS-Presentation_Oct-2023.pptx": {
#     "link": f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/LMO-FOCUS-Presentation_Oct-2023.pptx?AWSAccessKeyId={os.environ['AWSAccessKeyId']}&Signature=wf6uQLxEt1L9d%2F9nJnWwtrsttBs%3D&Expires=1702482582",
#     "file_name": "LMO-FOCUS-Presentation_Oct-2023.pptx"
#     },
#   f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Risk%20%26%20Insurance%20LMO%202023.pptx": {
#     "link": f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Risk%20%26%20Insurance%20LMO%202023.pptx",
#     "file_name": "Risk & Insurance LMO 2023.pptx"
#   },
#   f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Payroll_HRIS+LMO_2023_+.pptx": {
#     "link": f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Payroll_HRIS%20LMO_2023_%20.pptx?AWSAccessKeyId={os.environ['AWSAccessKeyId']}&Signature=tld2ByoZViqZgk%2BqVOF%2B%2F1pzE6g%3D&Expires=1702482647",
#     "file_name": "Payroll_HRIS LMO_2023_ .pptx"
#   },
#   f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Procurement%20LMO%202023%20Rev%20A%20JRM.pptx": {
#     "link": f"https://{os.environ['S3_BUCKET']}.s3.amazonaws.com/Procurement%20LMO%202023%20Rev%20A%20JRM.pptx?AWSAccessKeyId={os.environ['AWSAccessKeyId']}&Signature=uDNd9Eyq2%2BInBdpJQvXhY8bbPbc%3D&Expires=1702484661",
#     "file_name": "Procurement LMO 2023 Rev A JRM.pptx"
#   }
# }

# # Check if the user ID is already stored in the session state
# if 'user_id' in st.session_state:
#     user_id = st.session_state['user_id']

# # If the user ID is not yet stored in the session state, generate a random UUID
# else:
#     user_id = str(uuid.uuid4())
#     st.session_state['user_id'] = user_id


# st.session_state['llm_app'] = bedrock_claudev2
# st.session_state['llm_chain'] = bedrock_claudev2.build_chain()

# if 'chat_history' not in st.session_state:
#     st.session_state['chat_history'] = []
    
# if "chats" not in st.session_state:
#     st.session_state.chats = [
#         {
#             'id': 0,
#             'question': '',
#             'answer': ''
#         }
#     ]

# if "questions" not in st.session_state:
#     st.session_state.questions = []

# if "answers" not in st.session_state:
#     st.session_state.answers = []

# if "input" not in st.session_state:
#     st.session_state.input = ""


# st.markdown("""
#         <style>
#                .block-container {
#                     padding-top: 32px;
#                     padding-bottom: 32px;
#                     padding-left: 0;
#                     padding-right: 0;
#                 }
#                 .element-container img {
#                     background-color: #000000;
#                 }

#                 .main-header {
#                     font-size: 24px;
#                 }
#         </style>
#         """, unsafe_allow_html=True)

# def write_logo():
#     col1, col2, col3 = st.columns([5, 1, 5])
#     with col2:
#         st.image(AI_ICON, use_column_width='always') 


# def write_top_bar():
#     col1, col2, col3 = st.columns([1,10,2])
#     with col1:
#         st.image(AI_ICON, use_column_width='always')
#     with col2:
#         header = f"Hi, it's your onboarding assistant!"
#         st.write(f"<h2 class='main-header'>{header}</h2>", unsafe_allow_html=True)
#     with col3:
#         clear = st.button("Clear Chat")
#     return clear

# clear = write_top_bar()

# if clear:
#     st.session_state.questions = []
#     st.session_state.answers = []
#     st.session_state.input = ""
#     st.session_state["chat_history"] = []

# def handle_input():
#     input = st.session_state.input
#     question_with_id = {
#         'question': input,
#         'id': len(st.session_state.questions)
#     }
#     st.session_state.questions.append(question_with_id)

#     chat_history = st.session_state["chat_history"]
#     if len(chat_history) == MAX_HISTORY_LENGTH:
#         chat_history = chat_history[:-1]

#     llm_chain = st.session_state['llm_chain']
#     chain = st.session_state['llm_app']
#     result = chain.run_chain(llm_chain, input, chat_history)

#     result["answer"] = re.sub("<knowledge>", "", result["answer"])
#     result["answer"] = re.sub("</knowledge>", "",  result["answer"])

#     answer = result['answer']
#     chat_history.append((input, answer))
    
#     document_list = []
#     if 'source_documents' in result:
#         for d in result['source_documents']:
#             if not (d.metadata['source'] in document_list):
#                 document_list.append((d.metadata['source']))

#     st.session_state.answers.append({
#         'answer': result,
#         'sources': document_list,
#         'id': len(st.session_state.questions)
#     })
#     st.session_state.input = ""

# def write_user_message(md):
#     col1, col2 = st.columns([1,12])
    
#     with col1:
#         st.image(USER_ICON, use_column_width='always')
#     with col2:
#         st.warning(md['question'])


# def render_result(result):
#     answer, sources = st.tabs(['Answer', 'Sources'])
#     with answer:
#         render_answer(result['answer'])
#     with sources:
#         if 'source_documents' in result:
#             render_sources(result['source_documents'])
#         else:
#             render_sources([])

# def render_answer(answer):
#     col1, col2 = st.columns([1,12])
#     with col1:
#         st.image(AI_ICON, use_column_width='always')
#     with col2:
#         st.info(answer['answer'])

# def render_sources(sources):
#     col1, col2 = st.columns([1,12])
#     with col2:
#         with st.expander("Sources"):
#             for s in sources:
#                 st.markdown(f"<a href='{SOURCES_DICT[s]['link']}'>{SOURCES_DICT[s]['file_name']}</a>", unsafe_allow_html=True)

    
# #Each answer will have context of the question asked in order to associate the provided feedback with the respective question
# def write_chat_message(md, q):
#     chat = st.container()
#     with chat:
#         render_answer(md['answer'])
#         render_sources(md['sources'])
    
        
# with st.container():
#   for (q, a) in zip(st.session_state.questions, st.session_state.answers):
#     write_user_message(q)
#     write_chat_message(a, q)

# st.markdown('---')
# input = st.text_input("It's your an AI-based assistant. How can I help you?", key="input", on_change=handle_input)
