# %%
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.adapters.openai import convert_openai_messages
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ChatMessageHistory
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain import hub
from langchain.tools.render import render_text_description
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
import streamlit as st
import requests
import os

async def getAnswer(initial_messages,inputVal):
        try:  
            openai_api_key = st.secrets["OPENAI_API_KEY"]
            serpapi_api_key = st.secrets["SERPAPI_API_KEY"]
        
            # Set environment variables
            os.environ["OPENAI_API_KEY"] = openai_api_key
            os.environ["SERPAPI_API_KEY"] = serpapi_api_key

            # %%
            search = SerpAPIWrapper()
            tools = [
                Tool(
                    name="Internet Search",
                    func=search.run,
                    description="useful for when you need to answer questions that the API query cannot help you with. Strictly only to be used when the answer from the API query doesn't suffice. The output returned by the search must be taken as is, as the answer.",
                ),
            ]

            # %%
            prompt = hub.pull("hwchase17/react-chat-json")
            chat_model = ChatOpenAI(temperature=0.63,streaming=True)

            # %%
            prompt = prompt.partial(
                tools=render_text_description(tools),
                tool_names=", ".join([t.name for t in tools]),
            )

            # %%
            chat_model_with_stop = chat_model.bind(stop=["\nObservation"])

            # %%
            from langchain.agents.output_parsers import JSONAgentOutputParser
            from langchain.agents.format_scratchpad import format_log_to_messages

            # We need some extra steering, or the chat model forgets how to respond sometimes
            TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
            ---------------------
            {observation}

            USER'S INPUT
            --------------------

            Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what! Whenever you produce a Final Answer, take that Final answer and analyse if you can return that as the output. If you can, return it, or else try again."""

            agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_log_to_messages(
                        x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
                    ),
                    "chat_history": lambda x: x["chat_history"],
                }
                | prompt
                | chat_model_with_stop
                | JSONAgentOutputParser()
            )

            # %%
            apikey="58b759c4a72292de344787ad7e9ae4f3"

            # %%
            messages=convert_openai_messages(initial_messages)

            messages

            # %%
            chat_history=ChatMessageHistory(messages=messages)

            chat_history

            # %%
            from langchain.agents import AgentExecutor

            memory = ConversationSummaryBufferMemory(llm=chat_model,memory_key="chat_history", return_messages=True, chat_memory=chat_history)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True) 
            response = agent_executor.invoke({"input": inputVal})["output"]
            if (response.startswith("https")):
                x = requests.get(response)
                return x.text
            else:
                return response
        except Exception as e:
             return f"Error : {e}"
        
def getAnswerV2(initial_messages,inputVal):
        try:  
            os.environ["SERPAPI_API_KEY"] = "68a5c3217c4a355f3100da0fc8e384f7d60bcc32b681cd87569d4bcabcaf1331"

            os.environ["OPENAI_API_KEY"] = "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"

            # %%
            search = SerpAPIWrapper()
            tools = [
                Tool(
                    name="Internet Search",
                    func=search.run,
                    description="useful for when you need to answer Marvel related questions. Strictly only to be used to answer questions regarding Marvel Comics or the MCU. The output returned by the search must be taken as is, as the answer.",
                ),
            ]

            # %%
            prompt = hub.pull("hwchase17/react-chat-json")
            chat_model = ChatOpenAI(temperature=0.63,streaming=True)

            # %%
            prompt = prompt.partial(
                tools=render_text_description(tools),
                tool_names=", ".join([t.name for t in tools]),
            )

            # %%
            chat_model_with_stop = chat_model.bind(stop=["\nObservation"])

            # %%
            from langchain.agents.output_parsers import JSONAgentOutputParser
            from langchain.agents.format_scratchpad import format_log_to_messages

            # We need some extra steering, or the chat model forgets how to respond sometimes
            TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
            ---------------------
            {observation}

            USER'S INPUT
            --------------------

            Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what! Whenever you produce a Final Answer, take that Final answer and analyse if you can return that as the output. If you can, return it, or else try again."""

            agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_log_to_messages(
                        x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
                    ),
                    "chat_history": lambda x: x["chat_history"],
                }
                | prompt
                | chat_model_with_stop
                | JSONAgentOutputParser()
            )
            # %%
            messages=convert_openai_messages(initial_messages)

            # %%
            chat_history=ChatMessageHistory(messages=messages)

            # %%
            from langchain.agents import AgentExecutor

            def _handle_error(error) -> str:
                split_strings=error.split(".")
                joined_strings=".".join(split_strings)
                return joined_strings

            memory = ConversationSummaryBufferMemory(llm=chat_model,memory_key="chat_history", return_messages=True, chat_memory=chat_history)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=_handle_error) 
            response = agent_executor.invoke({"input": inputVal})["output"]
            if (response.startswith("https")):
                x = requests.get(response)
                return x.text
            else:
                return response
        except Exception as e:
             return f"Error : {e}"
