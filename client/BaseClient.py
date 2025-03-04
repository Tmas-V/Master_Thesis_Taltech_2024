import requests, json
import os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet


class BaseClient:
    def __init__(self,
                 _server_host,
                 _port,
                 _useMemory
                 ):
        self.server_host = _server_host
        self.port = _port
        self.useMemory = _useMemory

    def send(self,
             prompt):
        endpoint = ""
        if self.useMemory:
            endpoint = "chat_with_mem"
        else:
            endpoint = "chat_with_no_mem"
        str_url = "http://{}:{}/{}".format(self.server_host,
                                           self.port,
                                           endpoint)
        dict_headers = {
                "Content-Type": "application/json",
                "Host": self.server_host
        }
        payload = {
            "prompt": prompt
        }
        response = ""
        ret_dict = {
            "prompt": prompt,
            "llm_response": "",
            "scan_results": {}
            }
        try:
            response = requests.post(url=str_url, headers=dict_headers, data=json.dumps(payload))
        except:
            print("[-] Error requesting the server.")
            return ret_dict
        try:
            response = response.json()
        except:
            print("[-] Error parsing response into JSON.")
            return ret_dict
        try:
            llm_response = response["llm_response"]
            ret_dict["llm_response"] = llm_response
        except:
            print("[-] Error retrieving LLM response from parsed response.")
            return ret_dict
        try:
            scan_results = response["scan_results"]
            ret_dict["scan_results"] = scan_results
        except:
            pass
        return ret_dict

    def clear_memory(self):
        if not self.useMemory:
            return
        str_url = "http://{}:{}/{}".format(self.server_host,
                                           self.port,
                                           "reset")
        dict_headers = {
                "Host": self.server_host
        }
        response = ""
        try:
            response = requests.get(url=str_url, headers=dict_headers)
        except:
            print("[-] Error requesting the server.")

