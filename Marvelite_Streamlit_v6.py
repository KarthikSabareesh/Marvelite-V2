import uuid
from Marvelite_v2 import getAnswerV2
import streamlit as st
from trubrics_utils import trubrics_config
from trubrics.integrations.streamlit import FeedbackCollector
from langchain.llms import OpenAI
import os
from langchain.llms import HuggingFaceHub
import pymongo

openai_api_key = st.secrets["OPENAI_API_KEY"]
mongodb_atlas_url = st.secrets["MONGODB_ATLAS_URL"]
huggingfacehub_api_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

# Set environment variables
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["MONGODB_ATLAS_URL"] = mongodb_atlas_url
os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingfacehub_api_token

# Retrieve the MongoDB Atlas URL from the environment variable
mongodb_atlas_url = os.environ.get("MONGODB_ATLAS_URL")

myclient = pymongo.MongoClient(mongodb_atlas_url)
mydb = myclient["MarveliteDB"]
mycol = mydb["Messages"]

st.title("Marvelite")
st.subheader("Your Friendly Neighbourhood Chatbot")


with st.sidebar:
    email, password = trubrics_config()
    st.divider()

if not email or not password:
    st.info(
        "To chat with an LLM and save your feedback to Trubrics, add your email and password in the sidebar."
        " Don't have an account yet? Create one for free [here](https://trubrics.streamlit.app/)!"
    )
    st.stop()


@st.cache_data
#Logging into Trubrics
def init_trubrics(email, password):
    try:
        collector = FeedbackCollector(email=email, password=password, project="Marvelite")
        return collector
    except Exception:
        st.error(f"Error authenticating '{email}' with [Trubrics](https://trubrics.streamlit.app/). Please try again.")
        st.stop()


collector = init_trubrics(email, password)

if "initial_messages" not in st.session_state:
    st.session_state.initial_messages = list(mycol.find({},{ "_id": 0, "role": 1, "content": 1 }))
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you today?"}]
if "prompt_ids" not in st.session_state:
    st.session_state["prompt_ids"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())


tags = [f"Marvelite_llm_chatbot.py"]

messages = st.session_state.messages
mylist=[]

#For Feedback (taking and recording)
for n, msg in enumerate(messages):
    st.chat_message(msg["role"]).write(msg["content"])

    if msg["role"] == "assistant" and n > 1:
        feedback_key = f"feedback_{int(n / 2)}"
        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None
        #Trubrics Streamlit-integrated feedback collector
        feedback = collector.st_feedback(
            component="default",
            feedback_type="thumbs",
            open_feedback_label="[Optional] Provide additional feedback",
            model="gpt-3.5-turbo",
            tags=tags,
            key=feedback_key,
            prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
            user_id=email,
        )
        if feedback:
            with st.sidebar:
                st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
                st.write(feedback)
                if feedback["user_response"]["score"] == "👍":
                    mylist.append(messages[n-1])
                    mylist.append({"role": "assistant", "content": msg["content"]})
                    x = mycol.insert_many(mylist)
                    st.write("Successfully inserted with : ",x.inserted_ids)
    mylist.clear()

# Chat section of the project
if prompt := st.chat_input("Ask your question"):
    st.session_state.initial_messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Loading your answer..."):
            #Checking relation to domain
            llm = OpenAI(temperature=0.63) #(You can use another OpenAI LLM like shown in this line or use a model from HF Hub like shown below)
            # repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1"
            # llm = HuggingFaceHub(
            #     repo_id=repo_id, model_kwargs={"temperature": 0.63}
            # )
            llm_prompt = f'''Could the question {prompt} be related to Marvel Comics or Marvel Cinematic Universe and not inappropriate? Give a "Yes" or "No" answer'''
            print(llm_prompt)
            llm_response=llm.invoke(llm_prompt)
            print(llm_response)
            if '\n\nYes' in llm_response:
                #Finding answer if domain-related
                full_response = getAnswerV2(initial_messages=st.session_state.initial_messages,inputVal=prompt)
            else:
                full_response= f'''I'm sorry, but the question '{prompt}' is either inappropriate or out of my domain. If you have any questions related to Marvel Entertainment, please fire away!!!'''
        #Logging user prompt
        logged_prompt = collector.log_prompt(
            config_model={"model": "gpt-3.5-turbo"},
            prompt=prompt,
            generation=full_response,
            session_id=st.session_state.session_id,
            tags=tags,
            user_id=email,
        )
        #Adding the question and answer to temporary memory for context remembrance.
        st.session_state.prompt_ids.append(logged_prompt.id)
        st.session_state.initial_messages.append({"role": "assistant", "content": full_response})
        messages.append({"role": "assistant", "content": full_response})
        st.rerun()  # force rerun of app, to load last feedback component
