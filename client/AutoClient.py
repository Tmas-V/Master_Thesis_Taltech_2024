import sys, os, json
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet
sys.path.append(".\\client\\")
import BaseClient as bclient

class AutoClient(bclient.BaseClient):
    def __init__(self,
                 _server_host,
                 _port,
                 _str_tmp_source_dataset_filepath,
                 _str_tmp_output_dataset_filepath
                 ):
        dict_conf = json.loads(open(".\\client\\conf.json", "r").read())
        self.server_host = _server_host#dict_conf["host"]
        self.port = _port#dict_conf["port"]
        self.useMemory = dict_conf["useMemory"]

        self.source_dataset_filepath = _str_tmp_source_dataset_filepath
        self.output_dataset_filepath = _str_tmp_output_dataset_filepath
    def run(self):
        prompts = parquet.read_pandas(self.source_dataset_filepath,
                                      columns=["prompt"]).to_pandas()["prompt"].tolist()
        df_output = pd.DataFrame({
            "prompt" : [],
            "response" : []
        })
        int_interim_save_count = 20
        counter = 0
        for prompt in prompts:
            server_response_dict = self.send(prompt)
            if type(server_response_dict["llm_response"]) is list:
                server_response_dict["llm_response"] = server_response_dict["llm_response"][0]["text"]
            new_row = pd.DataFrame({
                "prompt" : [server_response_dict["prompt"]],
                "response" : [server_response_dict["llm_response"]]
            })
            df_output = pd.concat([df_output, new_row], ignore_index = True)
            counter += 1
            print("Samples used {}/{}".format(df_output.shape[0], len(prompts)))
            if counter == int_interim_save_count:
                parquet.write_table(pyarrow.Table.from_pandas(df_output),
                                    self.output_dataset_filepath)
                counter = 0
                print("Saving interim results...")
        parquet.write_table(pyarrow.Table.from_pandas(df_output),
                            self.output_dataset_filepath)
        return 1


# sys.argv = [prg, host, port, tmp_source_filepath, tmp_output_filepath]

if __name__ == "__main__":
#    sys.argv = ['.\\client\\AutoClient.py',
#                'localhost',
#                '5000',
#                '.\\tmp\\samples.parquet',
#                '.\\tmp\\responses.parquet']
    autoclient = ""
    host = ""
    port = 5000
    source_dataset_filepath = ""
    output_dataset_filepath = ""
    try:
        host = str(sys.argv[1])
        port = int(sys.argv[2])
        source_dataset_filepath = str(sys.argv[3])
        output_dataset_filepath = str(sys.argv[4])
    except:
        print("[!] AutoClient error: invalid program parameters...")
        input("(Press any key)")
        quit(0)
    autoclient = AutoClient(
        host,
        port,
        source_dataset_filepath,
        output_dataset_filepath)
    autoclient.run()

