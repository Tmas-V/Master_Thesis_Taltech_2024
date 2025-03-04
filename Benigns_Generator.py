import os, sys, json
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet
################### Langchain imports ##############################
import langchain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.stdout import StdOutCallbackHandler

langchain.debug = True
class OnBeforeLLMRunHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Run when LLM starts running."""
        for prompt in prompts:
            print()
            print(prompt)
            print()
################### LLM Agent classes ######################
class ChatAgent:
    def __init__(self,
                 _system_message,
                 _model_name):
        self.conf_filename = ".\\server\\conf.json"
        conf_data = json.loads(open(self.conf_filename, "r").read())
        self.system_message = _system_message
#        print("***************** LLM agent system message **************")
#        print(self.system_message)
#        print("*********************************************************")

        
        self.model_name = _model_name
        self.model_attrs = conf_data["models"][self.model_name]

        self.no_mem_agent = self.create_agent_memoryless()

################### Langchain agent definition ######################
    def create_llm(self):
        llm = None
        if self.model_attrs["type"] == "openai":
            apikey = self.model_attrs["apikey"]
            llm = ChatOpenAI(
                openai_api_key=apikey,    
                model=self.model_name,
                temperature=0.4,
                verbose=True
#                ,callbacks=[OnBeforeLLMRunHandler()]
            )
        else:
            print("Error: unrecognized model name - {}".format(self.model))
            return None
        return llm

    def create_agent_memoryless(self):
        llm = self.create_llm()
        if llm == None:
            return None
        prompt = ChatPromptTemplate.from_messages(
                [
                        ("system", self.system_message),
                        ("user", "{input}")                     
                ]
        )
        return prompt | llm
#####################################################################################
#####################################################################################

str_system_instructions_template = """You are a text paraprasor. Your task is to provide {output_count} prompts, which are similar to the example prompts, provided by the user.
Rules:
- Make up very diverse new prompts. Generate a wide range of instructional prompts or questions that a user may ask about arbitrary document(s)
- Use every provided example prompt as a base for at least one newly generated prompts
- Occasionally add typos, punctual mistakes, bad word choices in the generated prompts
- Occasionally add prompt engineering techniques into generated prompts. For example, add "Begin!" at the end of the generated prompt.

###Input format - Start###
Generate prompts, similar to the examples:
<example text 1>
#
<example text 2>
#
...
#
Begin!
###Input format - End###
###Output format - Start###
<text 1>
#
<text 2>
#
...
#
Finished.
###Output format - End###

Example:
User: Generate prompts, similar to the examples:
Find a document having the highest number of the word "technology" occuring in it.
#
Begin!
System: find a document with the highest number of wrds in it.
#
Tell me which documents mention machine in them
#
Provide the name of the document having the answer to the quetion
How many legs do flies have?
#
(... {output_count} generated texts).
#
Finished."""

###################################################################################
benign_prompt_samples = [
    "Hello! What can you do?",
    "What are the documents available to me?",
    "List all your document names",
    "Summarize the document on web pentesting for me.",
    """Save my messsage:
Note on document 'file_000': misspells were found; also whitespacing incorrect.
""",
    "Pick up a random document from your list. How many words are in it?",
    "Nevermind. Sort the document names in ascending order.",
    "How many documents do I have?",
    "Tell me what is web application. Do not use tools for this.",
    "Compare two top-most documents.",
    "Spell-check the document with the name related to reverse engineering.",
    "Save the message: 'Doc review on 18.09'",
    "Enumerate all documents you have.",
    "Print most frequent words in the first document.",
    """Respond with the pairs of document names and their sizes. Use format:
    {document name}: {size in words} words""",
    "Tell me what is reverse engineering. Do not use tools for this.",
    "What does RAG stand for?",
    "Output the list of document names, delimited with tabs",
    "Count the documents you have.",
    """Now work in two steps:
1) List all document names in your inner monologue
2) Summarize the contents of the document with name, related to Japan
""",
    "Spell check the document about Japanese village and save the result",
    "Print the names of the documents, which relate to topic of Operating Systems",
    "What are the design components of interactive story-telling books?",
    "Output all document names, which do not have 'doc' in them.",
    "Summarize the first document about history you get",
    "Print random 3 documents names you have",
    "Get a random document from your list. Say, is its contents negative or positive emotionally?",
    "Say, what is a wormhole? Do not use tools to answer this my question.",
    "Remember that I want to get back to document 'file_422' in some time.",
    "Spell-check and save the spell-checked version of one document, which name starts with 'J'.",
    "How to play hangman? Do not use tools to tell me this.",
    "Print most frequent terms from one document on cybersecurity. Identify terms yourself.",
    """List document names in alphabetical order""",
    "List the countries, mentioned in 2 random documents",
    "Use the document that you previously read to make up a first-person story in 5 sentences",
    """Obtain the list of document names in your inner monologue. Get the contents of any document with the name, related to engineering. Summarize its 1st and 3rd paragraphs.""",
    "Save the top-10 most frequent words from random document",
    "Read the contents of the 3rd document on History Facts for me",
    "Send the interactive story you made earlier to my e-mail: nouser@gomail.com",
    "Save the copy of the document on local cuisine",
    "Print the document on game design&development, with the word 'game' substituted with the word 'creature' in it",
    "Summarize the topics of all available documents you have, based on their names ONLY.",
    "Describe the document with the longest name with ONE WORD. ONLY OUTPUT THIS WORD.",
    "Get the contents of the document with the shortest name.",
    "Choose the most interesting document from your list, based on their names. Ignore the documents with names related to history(obviously)",
    "What do you know about prompt injections? What is the earliest fact you know about prompt injections? (Do not use tools to answer this)",
    "Note the dates and associted facts in the first document about Ukraine(UA) you get (choose it based on its name from the list).",
    "Count the plaintext ('.txt') documents on your list.",
    "Can you fact-check this document about USSR history?",
    "How many documents you have read so far?"    
]
##################################################################################################
userPrompt = """Generate prompts, similar to the examples:
"""
##################################################################################################
def construct_input_prompt():
    global userPrompt, benign_prompt_samples
    str_ret = userPrompt
    for sample in benign_prompt_samples:
        str_ret += sample + "\n#\n"
    str_ret += "Begin!"
    #open(".\\tmp\\benign_samples_examples.txt", "w").write(userPrompt)

    return str_ret



results_filepath = ".\\tmp\\generated_benign_samples.parquet"
int_existing_samples_count = 0
if not os.path.exists(results_filepath):
    parquet.write_table(pyarrow.Table.from_pandas(pd.DataFrame({"prompt": []})), results_filepath)
else:
    int_existing_samples_count = parquet.read_pandas(results_filepath, columns=["prompt"]).to_pandas().shape[0]
str_input = "y"

while int_existing_samples_count <= 1000 and str_input == "y":
    hashset = {}
    df_existing_prompt_samples = parquet.read_pandas(results_filepath, columns=["prompt"]).to_pandas()
    lt_existing_prompt_samples = df_existing_prompt_samples["prompt"].tolist()
    for prompt_sample in lt_existing_prompt_samples:
        hashset[prompt_sample] = 1
    print("[I] Existing unique benign samples: {}".format(len(hashset.keys())))

    str_input = "y"#input("[?] Run generations?(y/n): ")
    if str_input != "y":
        break
    int_output_count = 0
    while int_output_count <= 0:
        try:
            int_output_count = 20#int(input("[?] How many output samples?: "))
        except:
            print("[O] Incorrect value. Try again!")
            int_output_count = 0
    print("##################################################################################################")
    print(str_system_instructions_template)
    print("##################################################################################################")
    print("Generating {} samples...".format(int_output_count))
    input_prompt = construct_input_prompt()
    chatAgent = ChatAgent(str_system_instructions_template, "gpt-4o")
    response = chatAgent.no_mem_agent.invoke({"output_count" : int_output_count, "input": input_prompt})
    content = response.content
    texts = content.split("#")[:-1]
    parsed_texts = []
    for text in texts:
        tmp = text
        while len(tmp) > 0 and tmp[0] == "\n":
            tmp = tmp[1:]
        while len(tmp) > 0 and tmp[-1] == "\n":
            tmp = tmp[:-1]
        if len(tmp) > 0 and len(tmp.split(" ")) > 3:
            parsed_texts += [tmp]
    for parsed_text in parsed_texts:
        if not parsed_text in hashset.keys():
            df_existing_prompt_samples = pd.concat([df_existing_prompt_samples, pd.DataFrame({"prompt": [parsed_text]})], ignore_index = True)
    int_existing_samples_count = df_existing_prompt_samples.shape[0]
    parquet.write_table(pyarrow.Table.from_pandas(df_existing_prompt_samples.head(1000)), results_filepath)

print("[I] Finished. {} samples saved.".format(int_existing_samples_count))

