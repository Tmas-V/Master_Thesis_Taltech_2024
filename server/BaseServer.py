from flask import Flask, render_template, request, json
import os, sys
import pyarrow as pyarrow
import pyarrow.parquet as parquet
################### Langchain imports ##############################
import langchain
import tools as agent_tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor, Tool, create_tool_calling_agent
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
################### OpenAI imports ##############################
from langchain_openai import ChatOpenAI
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
################### Anthropic imports ##############################
from langchain_anthropic import ChatAnthropic
################### LLM Agent classes ######################
class BaseServer:
    def __init__(self,
                 _flaskApp,
                 _host,
                 _port,
                 _system_message,
                 _model_name):
        self.flaskApp = _flaskApp
        self.conf_filename = ".\\server\\conf.json"
        conf_data = json.loads(open(self.conf_filename, "r").read())
        self.host = _host
        self.port = _port
        self.system_message = _system_message
        print("***************** LLM agent system message **************")
        print(self.system_message)
        print("*********************************************************")
        self.agent_docs_dir_path = ".\\server\\_docs\\"
        agent_tools.str_docs_dir_path = self.agent_docs_dir_path
        self.tools = [agent_tools.list_documents_tool,
                      agent_tools.get_document_contents_tool,
                      agent_tools.save_message_tool
        ]
        self.structtools = [agent_tools.list_documents_structtool,
                      agent_tools.get_document_contents_structtool,
                      agent_tools.save_message_structtool
        ]
        self.memory = ""
        
        self.model_name = _model_name
        self.model_attrs = conf_data["models"][self.model_name]
        
        self.mem_agent = self.create_agent_with_memory()
        self.no_mem_agent = self.create_agent_memoryless()

################### Langchain agent definition ######################
    def create_llm(self):
        llm = ""
        if self.model_attrs["type"] == "openai":
            apikey = self.model_attrs["apikey"]
            llm = ChatOpenAI(
                openai_api_key=apikey,    
                model=self.model_name,
                temperature=0,
            )
        elif self.model_attrs["type"] == "anthropic":
            apikey = self.model_attrs["apikey"]
            llm = ChatAnthropic(
                api_key=apikey,
                model=self.model_name,
                temperature=0,
                max_tokens=1024,
                timeout=None,
                max_retries=2
            )
        else:
            print("Error: unrecognized model name - {}".format(self.model))
            return None
        return llm
    def create_agent_with_memory(self):       
        self.memory = ConversationBufferMemory(
            memory_key="memory",
            return_messages=True,
            output_key="output",
            chat_memory=ChatMessageHistory(messages=[
                HumanMessage(content="Hello!"),
                AIMessage(content="Hello! How can I assist you today?")
        ]))
        llm = self.create_llm()
        if llm == None:
            return None
        prompt = ChatPromptTemplate.from_messages(
                [
                        ("system", self.system_message),
                        MessagesPlaceholder("memory"),
                        ("user", "{input}"),
                        MessagesPlaceholder("agent_scratchpad")                        
                ]
        )
        llm_with_tools = llm.bind_tools(self.tools)
        agent = (
                {
                        "input": lambda x: x["input"],
                        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                                x["intermediate_steps"]
                        ),
                        "memory": lambda x: x["memory"]
                }
                | prompt
                | llm_with_tools
                | OpenAIToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            return_intermediate_steps=True,
            max_iterations=4
        )
        return agent_executor

    def create_agent_memoryless(self):
        llm = self.create_llm()
        if llm == None:
            return None
        agent_executor = None
        if self.model_attrs["type"] == "openai":
            prompt = ChatPromptTemplate.from_messages(
                    [
                            ("system", self.system_message),
                            ("user", "{input}"),
                            MessagesPlaceholder("agent_scratchpad")                        
                    ]
            )
            llm_with_tools = llm.bind_tools(self.tools)
            agent = (
                    {
                            "input": lambda x: x["input"],
                            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                                    x["intermediate_steps"]
                            )
                    }
                    | prompt
                    | llm_with_tools
                    | OpenAIToolsAgentOutputParser()
            )
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True,
                max_iterations=4
            )
        elif self.model_attrs["type"] == "anthropic":
#            print("[!] Initializing Claude agent with tools.....")

            prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", self.system_message),
                        ("human", "{input}"),
                        ("placeholder", "{agent_scratchpad}"),
                    ]
            )
            agent = (prompt | llm)
            return agent
            
            agent = create_tool_calling_agent(llm, self.structtools, prompt)
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.structtools,
                verbose=True,
                return_intermediate_steps=True,
                max_iterations=4
            )
        return agent_executor
#####################################################################################
########################## Logging and Response #####################################
    def construct_json_response(self,
                                user_prompt,
                                intermediate_steps,
                                llm_output):
        response = {}
        response["prompt"] = user_prompt
        response["llm_response"] =  llm_output
        response["scan_results"] = {
        }
        return response
######################################################################################
    def Run(self):
        self.flaskApp.run(host = self.host, port = self.port)
        

###########################################################################
########################## Server endpoint functions #################################


flaskApp = Flask(__name__)
llmApp = None

@flaskApp.route("/")
def index():
    return "This is vulnerable LLM application."

@flaskApp.route("/chat_with_mem", methods=["POST"])
def get_mem_agent_response():
    global llmApp
    userPrompt = request.json['prompt']
    llm_response = {}
    try:
        llm_response = llmApp.mem_agent.invoke({"input": userPrompt})
        intermediate_steps = [str(step[1]) for step in llm_response["intermediate_steps"]]
        response = llmApp.construct_json_response(userPrompt,
                                                  intermediate_steps,
                                                  llm_response["output"])
    except:
        return {}    
    return response


@flaskApp.route("/chat_with_no_mem", methods=["POST"])
def get_no_mem_agent_response():
    global llmApp
    userPrompt = request.json['prompt']
    llm_response = {}
    try:
        llm_response = {}
        if llmApp.model_attrs["type"] == "openai":
            llm_response = llmApp.no_mem_agent.invoke({"input": userPrompt})
        elif llmApp.model_attrs["type"] == "anthropic":
            response = llmApp.no_mem_agent.invoke({"input": userPrompt})
            llm_response = {
                "intermediate_steps" : [],
                "output": response.content
            }
        intermediate_steps = [str(step[1]) for step in llm_response["intermediate_steps"]]
        response = llmApp.construct_json_response(userPrompt,
                                                  intermediate_steps,
                                                  llm_response["output"])
    except:
        return {}
    return response


@flaskApp.route("/reset", methods=["GET"])
def clear_memory():
    global llmApp
    llmApp.memory.clear()
    llmApp.memory.chat_memory.add_messages(messages=[
                HumanMessage(content="Hello!"),
                AIMessage(content="Hello! How can I assist you today?")
        ])
    return "Success"
