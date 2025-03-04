import sys, os, json
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet


class BaseDetector:
    def __init__(self,
                 _str_detector_type,
                 _str_input_filepath,
                 _str_output_filepath,
                 _int_interim_save_count):
        self.type = _str_detector_type
        self.conf_filepath = os.path.abspath(
            ".\\detectors\\{}\\conf.json".format(self.type)
        )      
        self.input_filepath = os.path.abspath(_str_input_filepath)
        self.output_filepath = os.path.abspath(_str_output_filepath)
        output_filename = self.output_filepath.split("\\")[-1]
        output_filename_noext = output_filename.split(".")[0]
        self.output_filepath = "\\".join(self.output_filepath.split("\\")[:-1]) + "\\" + "{}({}).parquet".format(output_filename_noext, self.type)

        self.tmp_savepath = os.path.abspath(".\\detectors\\{}\\tmp".format(self.type)) + "\\"
        self.interim_savefilepath = self.tmp_savepath + "{}_interim_output_dataset.parquet".format(self.type)
        self.interim_save_count = _int_interim_save_count
        self.tmp_latest_used_conf_filepath = self.tmp_savepath + "latest_conf.json"

    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "response": []
            }
        )
    def analyze_input(self,
                      dict_input_row):
        return self.create_empty_dataset()
    def produce_processed_dataset(self,
                                  _input_dataset):
        output_dataset = self.create_empty_dataset()
        counter = 0
        global_counter = 0
        total_samples_number = len(_input_dataset["prompt"].to_list())

        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        with open(self.tmp_latest_used_conf_filepath, 'w') as f:
            json.dump(dict_conf, f, indent=4)
        
        for index, row in _input_dataset.iterrows():
            new_row = self.analyze_input(row)
            output_dataset = pd.concat([output_dataset, new_row], ignore_index=True)
            global_counter += 1
            print("Samples processed {}/{}".format(global_counter, total_samples_number))
            counter += 1
            if counter >= self.interim_save_count:
                parquet.write_table(pyarrow.Table.from_pandas(output_dataset),
                                    self.interim_savefilepath)
                counter = 0
                print("Saving interim results...")
        parquet.write_table(pyarrow.Table.from_pandas(output_dataset),
                            self.interim_savefilepath)        
        return output_dataset
    def run(self):
        samples = parquet.read_pandas(self.input_filepath,
                                      columns=["prompt", "response"]).to_pandas()
        output_dataset = self.produce_processed_dataset(samples)
        print()
        print(self.output_filepath)
        parquet.write_table(pyarrow.Table.from_pandas(output_dataset),
                            self.output_filepath)
        
        
                
        
        

