import sys, os, subprocess, yaml, time
sys.path.append(".\\detectors\\")
from BaseDetector import *

class CanaryDetector(BaseDetector):
    def __init__(self,
                 _canary_type,
                 _str_input_filepath,
                 _str_output_filepath,
                 _interim_samples_count):
        super().__init__(_canary_type,
                 _str_input_filepath,
                 _str_output_filepath,
                 _interim_samples_count)
        self.tmp_latest_used_conf_filepath = self.tmp_savepath + "latest_conf.json"
        
        self.server_host = "localhost"
        self.server_port = 5000
        self.tmp_client_input_filepath = self.tmp_savepath + "{}_samples.parquet".format(self.type)
        self.tmp_client_output_filepath = self.tmp_savepath + "{}_responses.parquet".format(self.type)
        self.venv_conf_filepath = ".\\venvs.yaml"
        self.client_py_path = ".\\client\\AutoClient.py"
        self.server_py_path = ".\\server\\BasicServer.py"

        self.run_canary = False
        self.canary_model_name = ""
        self.canary_usage_type = ""
        self.canary_word = ""
        
        self.server_system_message = open(".\\system_message.txt", "r").read()
        self.buffed_server_system_message = self.server_system_message

        self.conf_root_key = "canary_detector"
        self.columnname_prompt = "prompt"
        self.columnname_run_canary = "run_canary"
        self.columnname_canary_model_name = "canary_model_name"
        self.columnname_canary_usage_type = "canary_usage_type"
        self.columnname_canary_word = "canary_word"
        self.columnname_buffed_system_message = "buffed_system_message"
        self.columnname_response_to_canary = "response_to_canary"
        self.columnname_is_detected_by_canary = "is_detected_by_canary"
        
    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                self.columnname_prompt : [],
                self.columnname_run_canary : pd.Series([], dtype=np.bool_),
                self.columnname_canary_model_name : [],
                self.columnname_canary_usage_type: [],
                self.columnname_canary_word: [],
                self.columnname_buffed_system_message: [],
                self.columnname_response_to_canary: [],
                self.columnname_is_detected_by_canary : pd.Series([], dtype=np.bool_)
            }
        )
    def produce_processed_dataset(self,
                                  _input_dataset):
        unprocessed_canary_inputs, processed_canary_inputs = self.get_unprocessed_and_processed_canary_inputs(_input_dataset)

        if unprocessed_canary_inputs.empty:
            return processed_canary_inputs
        
        # Save current configuration as latest used conf in tmp folder
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        dict_conf[self.conf_root_key]["canary_check"]["canary_word"] = self.canary_word
        dict_conf[self.conf_root_key]["canary_check"]["buffed_system_message"] = self.buffed_server_system_message
        with open(self.tmp_latest_used_conf_filepath, 'w') as f:
            json.dump(dict_conf, f, indent=4)
        # Run client-server to generate responses from canary-protected app
        parquet.write_table(pyarrow.Table.from_pandas(unprocessed_canary_inputs),
                            self.tmp_client_input_filepath)
        server_process = self.run_server()
        #choice = input("[?] Run client to run canary check experiments?(y/n)")
        time.sleep(30)
        choice = "y"
        if choice == "y":
            client_process = self.run_client(
                       self.tmp_client_input_filepath,
                       self.tmp_client_output_filepath)
            client_process.wait()
        server_process.kill()
        if not os.path.exists(self.tmp_client_output_filepath):
            print("[!] Error canary check experiments: temporary output file not found!")
            return self.create_empty_dataset()
        tmp = parquet.read_pandas(self.tmp_client_output_filepath,
                                  columns=[self.columnname_prompt, "response"]).to_pandas()
        now_processed_canary_inputs = self.create_empty_dataset()
        now_processed_canary_inputs[self.columnname_prompt] = tmp[self.columnname_prompt]
        now_processed_canary_inputs[self.columnname_run_canary] = self.run_canary
        now_processed_canary_inputs[self.columnname_canary_model_name] = self.canary_model_name
        now_processed_canary_inputs[self.columnname_canary_usage_type] = self.canary_usage_type
        now_processed_canary_inputs[self.columnname_canary_word] = self.canary_word
        now_processed_canary_inputs[self.columnname_buffed_system_message] = self.buffed_server_system_message
        now_processed_canary_inputs[self.columnname_response_to_canary] = tmp["response"]
        now_processed_canary_inputs[self.columnname_is_detected_by_canary] = now_processed_canary_inputs[self.columnname_response_to_canary].map(
            lambda response: response.find(self.canary_word) != -1
        )
        
        # merge previously-processed, and just-processed (tmp) output datasets
        processed_canary_inputs = pd.concat([processed_canary_inputs, now_processed_canary_inputs], ignore_index=True)

        # reorder all processed rows in the same order as in _input_dataset
        produced_processed_samples = self.create_empty_dataset()
        for index, row in _input_dataset.iterrows():
            produced_processed_samples = pd.concat([produced_processed_samples, processed_canary_inputs[processed_canary_inputs[self.columnname_prompt] == row[self.columnname_prompt]]], ignore_index=True)
        
        return produced_processed_samples


    def run(self):
        if not self.run_canary:
            sys.exit(0)
        samples = parquet.read_pandas(self.input_filepath,
                                      columns=[self.columnname_prompt]).to_pandas()
        
        output_dataset = self.produce_processed_dataset(samples)            
        output_filename = self.output_filepath.split("\\")[-1]
        output_filename_noext = output_filename.split(".")[0]
        detector_specific_output_filepath = "\\".join(self.output_filepath.split("\\")[:-1]) + "\\" + "{}({}).parquet".format(output_filename_noext, self.type)
        parquet.write_table(pyarrow.Table.from_pandas(output_dataset),
                            detector_specific_output_filepath)

#################################################################################################

    def check_if_already_processed(self,
                                   _input_dataset):
        if not os.path.exists(self.output_filepath):
            return None
        existing_output_dataset = parquet.read_pandas(self.output_filepath).to_pandas()
        input_dataset = pd.DataFrame(
            {
                self.columnname_prompt : [],
                self.columnname_run_canary : pd.Series([], dtype=np.bool_),
                self.columnname_canary_model_name : [],
                self.columnname_canary_usage_type: []
            }
        )
        input_dataset[self.columnname_prompt] = _input_dataset[self.columnname_prompt]
        input_dataset[self.columnname_run_canary] = self.run_canary
        input_dataset[self.columnname_canary_model_name] = self.canary_model_name
        input_dataset[self.columnname_canary_usage_type] = self.canary_usage_type

        return input_dataset.equals(existing_output_dataset[[self.columnname_prompt, self.columnname_run_canary, self.columnname_canary_model_name, self.columnname_canary_usage_type]])

    def get_unprocessed_and_processed_canary_inputs(self,
                                                    _input_dataset):
        output_dataset_status = self.check_if_already_processed(_input_dataset)
        # If output dataset is not found - return all inputs as unprocessed, and empty dataset as processed
        if output_dataset_status == None:
            return _input_dataset, self.create_empty_dataset()
        # If output dataset is full and corresponds to input dataset - return empty unprocessed, and output as processed
        if output_dataset_status == True:
            return pd.Dataframe({self.columnname_prompt: []}), parquet.read_pandas(self.output_filepath).to_pandas()

        processed_canary_inputs = self.create_empty_dataset()
        output_dataset = parquet.read_pandas(self.output_filepath).to_pandas()
        tmp_output_dataset = self.create_empty_dataset()
        if os.path.exists(self.tmp_client_output_filepath) and os.path.exists(self.tmp_latest_used_conf_filepath):
            tmp = parquet.read_pandas(self.tmp_client_output_filepath, columns=[self.columnname_prompt, "response"]).to_pandas()
            latest_dict_conf = json.loads(open(self.tmp_latest_used_conf_filepath, "r").read())
            
            tmp_output_dataset[self.columnname_prompt] = tmp[self.columnname_prompt]
            tmp_output_dataset[self.columnname_run_canary] = latest_dict_conf[self.conf_root_key]["canary_check"]["use_scanner"]
            tmp_output_dataset[self.columnname_canary_model_name] = latest_dict_conf[self.conf_root_key]["canary_check"]["model_name"]
            tmp_output_dataset[self.columnname_canary_usage_type] = latest_dict_conf[self.conf_root_key]["canary_check"]["usage_type"]
            tmp_output_dataset[self.columnname_canary_word] = latest_dict_conf[self.conf_root_key]["canary_check"]["canary_word"]
            tmp_output_dataset[self.columnname_buffed_system_message] = latest_dict_conf[self.conf_root_key]["canary_check"]["buffed_system_message"]
            tmp_output_dataset[self.columnname_response_to_canary] = tmp["response"]
            tmp_output_dataset[self.columnname_is_detected_by_canary] = tmp_output_dataset[self.columnname_response_to_canary].map(
                lambda response: response.find(latest_dict_conf[self.conf_root_key]["canary_check"]["canary_word"]) != -1
            )
        unprocessed_canary_inputs = pd.DataFrame(
            {
                self.columnname_prompt : [],
                "response" : []
            }
        )
        for index, row in _input_dataset.iterrows():
            inclusion_verdict = False
            df_to_include = None
            existing_out_df = output_dataset[output_dataset[self.columnname_prompt] == row[self.columnname_prompt]]
            existing_tmp_out_df = tmp_output_dataset[tmp_output_dataset[self.columnname_prompt] == row[self.columnname_prompt]]
            input_df = pd.DataFrame({
                    self.columnname_prompt : [row[self.columnname_prompt]],
                    self.columnname_run_canary : pd.Series([self.run_canary], dtype=np.bool_),
                    self.columnname_canary_model_name : [self.canary_model_name],
                    self.columnname_canary_usage_type: [self.canary_usage_type]
                }
            )
            if not existing_out_df.empty:
                if input_df.equals(existing_out_df[[self.columnname_prompt, self.columnname_run_canary, self.columnname_canary_model_name, self.columnname_canary_usage_type]]):
                    inclusion_verdict = True
                    df_to_include = existing_out_df

            if not inclusion_verdict and not existing_tmp_out_df.empty:
                if input_df.equals(existing_tmp_out_df[[self.columnname_prompt, self.columnname_run_canary, self.columnname_canary_model_name, self.columnname_canary_usage_type]]):
                    inclusion_verdict = True
                    df_to_include = existing_tmp_out_df

            if inclusion_verdict:
                processed_canary_inputs = pd.concat([processed_canary_inputs, df_to_include], ignore_index=True)
            else:
                unprocessed_canary_inputs = pd.concat([unprocessed_canary_inputs, pd.DataFrame(row)], ignore_index=True)

        return unprocessed_canary_inputs, processed_canary_inputs
 
            

    def run_server(self):
        """
        Returns server subprocess.
        """
        venv_path = ""
        with open(self.venv_conf_filepath, "r") as file:
            conf_data = yaml.safe_load(file)
            venv_path = os.path.abspath(conf_data["default"])
        cwd_path = os.path.abspath(".\\")
        server_py_path = os.path.abspath(self.server_py_path)        
        server_args = [venv_path,
                       server_py_path,
                       str(self.server_host), # host
                       str(self.server_port), # port
                       str(self.buffed_server_system_message), # buffed_system message
                       str(self.canary_model_name) # llm model name
                       ]
#        for s in server_args + [cwd_path]:
#            print(s)
        return subprocess.Popen(args = server_args,
                       cwd = cwd_path,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)
        
    def run_client(self,
                   _str_samples_source_filepath,
                   _str_samples_result_filename):
        """
        Returns client subprocess.
        """
        venv_path = ""
        with open(self.venv_conf_filepath, "r") as file:
            conf_data = yaml.safe_load(file)
            venv_path = os.path.abspath(conf_data["default"])
        cwd_path = os.path.abspath(".\\")
        client_py_path = os.path.abspath(self.client_py_path)
        client_args = [venv_path,
                       client_py_path,
                       str(self.server_host), # host
                       str(self.server_port), # port
                       os.path.abspath(_str_samples_source_filepath),
                       os.path.abspath(_str_samples_result_filename)]
        print(client_args)
        return subprocess.Popen(args = client_args,
                       cwd = cwd_path,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)



