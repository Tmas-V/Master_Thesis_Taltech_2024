import requests, json
import time
from pi_attacks import *
import os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

str_host = "localhost"
str_memory_agent_endpoint = "chat_with_mem"
str_no_memory_agent_endpoint = "chat_with_no_mem"
str_reset_endpoint = "reset"


########################################### Request functions to LLM app endpoints ###########################################

def send(prompt, endpoint, port, verbose=False):
    global str_host
    str_url = "http://{}:{}/{}".format(str_host, port, endpoint)
    dict_headers = {
            "Content-Type": "application/json",
            "Host": str_host
    }
    payload = {
        "prompt": prompt
    }
    
    response = ""
    try:
        response = requests.post(url=str_url, headers=dict_headers, data=json.dumps(payload))
    except:
        print("[-] Error requesting the server.")
        return ("", {})
    try:
        response = response.json()
    except:
        print("[-] Error parsing response into JSON.")
        return ("", {})
    llm_response = ""
    try:
        llm_response = response["llm_response"]
    except:
        print("[-] Error retrieving LLM response from parsed response.")
        return ("",{})
    scan_results = {}
    try:
        scan_results = response["scan_results"]
    except:
        pass

    if verbose:
        print("Prompt: \"\"\"", end="")
        print(prompt, end="")
        print("\"\"\"")
        print()
        if scan_results != {}:
            print("Scan results:")
            print(json.dumps(
                scan_results,
                indent=6,
                sort_keys=True
                )
            )
            print()
        print("Response: \"\"\"", end="")
        print(llm_response, end="")
        print("\"\"\"")
    return (llm_response, scan_results)

def send_with_no_memory(prompt, port):
    return send(prompt, str_no_memory_agent_endpoint, port)
def send_with_memory(prompt, port):
    return send(prompt, str_memory_agent_endpoint, port)

def clear_memory(port):
    global str_host, str_reset_endpoint
    str_url = "http://{}:{}/{}".format(str_host, port, str_reset_endpoint)
    dict_headers = {
            "Host": str_host
    }
    
    response = ""
    try:
        response = requests.get(url=str_url, headers=dict_headers)
    except:
        print("[-] Error requesting the server.")
        return 0

            
######################################### Prompting modes functions #################################################

def cli(port, with_memory=False):
    global str_memory_agent_endpoint, str_no_memory_agent_endpoint
    print("Enter user prompt. Double press 'Enter' to clear conversation memory. Double press 'Enter' again to quit.")
    print("------------------------------")
    prompt = ""
    int_hasMemory = 1
    while True:
        prompt = ""
        while True:
            line = input("prompt>")
            if len(line) == 0:
                break
            prompt += line + "\n"
        if len(prompt) != 0:
            int_hasMemory = 1
            print("-------Prompting...-----------")
            if with_memory:
                send(prompt, str_memory_agent_endpoint, port, verbose=True)
            else:
                send(prompt, str_no_memory_agent_endpoint, port, verbose=True)   
            print("------------------------------")
        else:
            if not with_memory:
                break
            if int_hasMemory == 0:
                break
            else:
                print()
                print("########Clearing memory.", end="")
                clear_memory(port)
                for i in range(0,2):
                    time.sleep(0.8)
                    print(".",end="")
                time.sleep(0.8)
                print("#############")
                print()
                int_hasMemory = 0
def fuzz(prompts, port, int_attempt_count):
    global str_memory_agent_endpoint, str_no_memory_agent_endpoint, str_SystemPromptIndicator
    for prompt in prompts:
        print("Prompt: \"\"\"{}\"\"\"".format(prompt))
        print("\n=========================Testing above prompt for {} attempts=========================\n".format(int_attempt_count))
        int_i = 0
        while int_i < int_attempt_count:
            (llm_response, scan_results) = send(prompts[0], str_no_memory_agent_endpoint, port)
            print("Response#{}:".format(int_i))
            print("=====================================================")
            print(llm_response)
            if scan_results != {}:
                print(scan_results)
            print("=====================================================")
            time.sleep(0.8)
            int_i += 1
        print("=========================================================================================\n")

