import sys
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

################### Setup Vigil ######################
from vigil.vigil import Vigil
vigil_app = Vigil.from_config('..\\server\\server(Vigil)\\vigil-llm-0.10.3-alpha\\conf\\server(vdb only).conf')


################### Setup Rebuff ######################
import requests, json
rebuffSDKServer_address = "192.168.247.162"
rebuffSDKServer_port = 5555
str_rebuffSDKServer_scanEnd = "scan"
str_rebuffSDKServer_addCanaryEnd = "add_canary"
str_rebuffSDKServer_checkCanaryEnd = "check_canary"

class RebuffServerScanRequestObj:
    def __init__(
        self,
        _prompt,
        _check_heuristic,
        _check_vector,
        _check_llm):

        self.prompt = _prompt
        self.check_heuristic = _check_heuristic
        self.check_vector = _check_vector
        self.check_llm = _check_llm
    def json(self):
        return {
            "prompt": self.prompt,
            "check_heuristic": self.check_heuristic,
            "check_vector": self.check_vector,
            "check_llm": self.check_llm
        }

def send(host, port, endpoint, obj):
    str_url = "http://{}:{}/{}".format(host, port, endpoint)
    dict_headers = {
            "Content-Type": "application/json",
            "Host": host
    }    
    response = ""
    try:
        response = requests.post(url=str_url, headers=dict_headers, data=json.dumps(obj))
    except:
        print("[-] Error requesting RebuffSDK server.")
        return {}
    try:
        response = response.json()
    except:
        print("[-] Error parsing RebuffSDK server response.")
        response = {}
        pass
    return response

def scan_input_with_Rebuff(_rebuffServerScanRequestObj):
        global rebuffSDKServer_address
        global rebuffSDKServer_port
        global str_rebuffSDKServer_scanEnd

        obj = _rebuffServerScanRequestObj.json()

        response_obj = send(rebuffSDKServer_address,
                            rebuffSDKServer_port,
                            str_rebuffSDKServer_scanEnd,
                            obj)
        if response_obj == {}:
                return {}
        return response_obj

#############################################################################
def empty_df():
    return pd.DataFrame({
        "prompt":[],
        "vigil_vectordb_distance": [],
        "rebuff_vectordb_score": []
    })

def new_parq_row(prompt_sample, vigil_vdb_distance, rebuff_vdb_score):
    return {
        "prompt":[prompt_sample],
        "vigil_vectordb_distance": [round(vigil_vdb_distance, 9)],
        "rebuff_vectordb_score": [round(rebuff_vdb_score, 9)]
    }

list_PromptSamples_filepaths = ["..\\client\\_PromptLeaks\\NoProtection_PromptLeaks_IgnoreJailbreak.parquet", "..\\client\\_BenignSamples\\BenignSamples.parquet"]
list_SaveFiles_filepaths = ["MaliciousSamples_scores.parquet", "BenignSamples_scores.parquet"]

for i in range(0, len(list_PromptSamples_filepaths)):
    print("Processing file {} ...".format(list_PromptSamples_filepaths[i]))
    prompt_samples = parquet.read_pandas(list_PromptSamples_filepaths[i],
                                                     columns=["prompt"]).to_pandas()["prompt"].tolist()
    parquet_PD = empty_df()
    int_rows_count = len(prompt_samples)
    int_rows_left = len(prompt_samples)
    for prompt in prompt_samples:
        vigil_scanresults = vigil_app.input_scanner.perform_scan(
            prompt
        )
        vigil_distance = vigil_scanresults["results"]["scanner:vectordb"]["matches"][0]["distance"]
        #print(vigil_score)

        #print("##################################")

        rebuff_scanrequest_obj = RebuffServerScanRequestObj(prompt, False, True, False)
        rebuff_scanresults = scan_input_with_Rebuff(rebuff_scanrequest_obj)
        rebuff_score = rebuff_scanresults["input_scan_results"]["vector_score"]
        #print(rebuff_score)

        new_row = new_parq_row(prompt, vigil_distance, rebuff_score)
        parquet_PD = pd.concat([parquet_PD, pd.DataFrame(new_row)], ignore_index = True)
        int_rows_left -= 1
        print("{}/{} rows left".format(int_rows_left, int_rows_count))
        
    table = pyarrow.Table.from_pandas(parquet_PD)
    parquet.write_table(table, list_SaveFiles_filepaths[i])

