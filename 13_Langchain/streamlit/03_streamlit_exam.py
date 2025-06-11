import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if 'storage' not in st.session_state:
    st.session_state['storage'] = {}

st.title("GPT-4o-mini Tutorial")
st.write(st.session_state['messages'])
for message in st.session_state["messages"]:
    with st.chat_message(message['role']):
        st.write(message['content'])

@st.cache_resource
# Note that we should clear cache When modifying codes.
def get_runnable():
    load_dotenv()
    model = ChatOpenAI(model_name = 'gpt-4o-mini')

    def get_session_history(session_id):
        if session_id not in st.session_state['storage']:
            st.session_state['storage'][session_id] = InMemoryChatMessageHistory()
        return st.session_state['storage'][session_id]

    prompt_template = ChatPromptTemplate([
    ('system', '당신은 AI 전문가입니다. 한국어로 답변해주시되, 전문 용어들을 영문 원어 그대로 사용해주세요.'),
    MessagesPlaceholder(variable_name='history', optional = True),
    ('human', '{query}')
    ])

    chain = prompt_template | model

    return RunnableWithMessageHistory(
    runnable = chain,
    get_session_history = get_session_history,
    input_messages_key = 'query',
    history_messages_key = 'history'
    )

chain = get_runnable()

prompt = st.chat_input("User Prompt")


if prompt:
    st.session_state["messages"].append({'role':'user', 'content':prompt})
    with st.chat_message('user'):
        st.write(prompt)

    with st.chat_message('ai'):
        message_placeholder = st.empty()   # Updatable Container
        full_message = ""
        output_generator = chain.stream({'query':prompt}, {'configurable':{'session_id':'userName'}})
        message_placeholder.write_stream(output_generator)
        print(output_generator)
        for token in output_generator:
            print('token :: '+token)
            full_message += token.content
        
        st.session_state["messages"].append({"role":"ai", "content":full_message})