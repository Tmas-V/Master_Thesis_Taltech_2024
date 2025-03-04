import subprocess

from Experiment import *

sys.path.append(".\\client")
sys.path.append(".\\server")
sys.path.append(".\\attack_techniques")

import prompt_leak as pl



class Validator:
    def __init__(self,
                 _experiment):
        self.experiment = _experiment
        self.server_host = "localhost"
        self.server_port = 5000
        self.tmp_client_input_filepath = ".\\tmp\\samples.parquet"
        self.tmp_client_output_filepath = ".\\tmp\\responses.parquet"
        self.venv_conf_filepath = ".\\venvs.yaml"
        self.client_py_path = ".\\client\\AutoClient.py"
        self.server_py_path = ".\\server\\BasicServer.py"

        self.server_system_message = open(".\\system_message.txt", "r").read()

    def check_validated(self, _experiment):
        df_val_dataset, val_hashset = _experiment.read_val_dataset()
        if df_val_dataset.shape[0] == 0:
            return 0
        if _experiment.val_samples_limit > 0 and df_val_dataset.shape[0] < _experiment.val_samples_limit:
            return 0
        elif _experiment.rerun_validation == True:
            return 0
        return 1
        
    def check_scored(self, _experiment):
        df_scored_dataset, scored_hashset = _experiment.read_scored_dataset()
        if df_scored_dataset.shape[0] == 0:
            return 0
        # check if (scored) dataset has enough successful samples (i.e. number equal to val_limit)
        successful_samples_count = df_scored_dataset[df_scored_dataset.success == True].shape[0]
        if _experiment.val_samples_limit >= 0 and successful_samples_count >= _experiment.val_samples_limit:
            return 1
        return 0
        

    def update_scored_to_validated(self, _experiment):
        df_scored_dataset, scored_hashset = _experiment.read_scored_dataset()
        
        df_successful_samples = df_scored_dataset[df_scored_dataset.success == True]
        _experiment.write_val_dataset(df_successful_samples)

        print("[0] Validation results: {}/{} successful samples of '{}'.".format(df_successful_samples.shape[0],
                                                                                 df_scored_dataset.shape[0],
                                                                                 _experiment.label))
        return 1


    def generate_responses_and_scores(self, _experiment):
        print("################")
        # create parameters for server and client:
        # server - no parameters; needs cwd, and venv path to start
        # client - path to TEMPORAL gen_samples("prompt" only), and path to TEMPORAL output val_samples ("prompts" and "responses")

        # create TEMPORAL dataset from gen dataset, consisting samples not in scored and not in val, count no more than gen dataset
        #
        df_gen_dataset, gen_hashset = _experiment.read_gen_dataset()
        df_scored_dataset, scored_hashset = _experiment.read_scored_dataset()

        df_tmp_gen_dataset = _experiment.empty_gen_dataframe()
        int_gen_scored_diff = _experiment.gen_samples_limit - len(scored_hashset.keys())
        i = 0
        for index, row in df_gen_dataset.iterrows():
            if row["prompt"] in scored_hashset.keys() and _experiment.rerun_validation == False:
                continue
            if row["prompt"] in scored_hashset.keys() and scored_hashset[row["prompt"]][1] == True:
                continue
            df_row = pd.DataFrame({
                "prompt" : [row["prompt"]]
            })
            if not row["prompt"] in scored_hashset.keys():
                df_tmp_gen_dataset = pd.concat([df_tmp_gen_dataset, df_row], ignore_index = True)
                i += 1
                if i == int_gen_scored_diff:
                    break
            else:
                if row["prompt"] in scored_hashset.keys() and scored_hashset[row["prompt"]][1] == False and _experiment.rerun_validation == True:
                    df_tmp_gen_dataset = pd.concat([df_tmp_gen_dataset, df_row], ignore_index = True)

        print("[0] Validation setup: going to generate responses for {} samples of '{}'.".format(df_tmp_gen_dataset.shape[0], _experiment.label))
        if df_tmp_gen_dataset.shape[0] == 0:
            return 1
        _experiment.write_dataset(self.tmp_client_input_filepath,
                                  _experiment.gen_columns,
                                  df_tmp_gen_dataset,
                                  _experiment.gen_samples_limit)
        
        
        server_process = self.run_server()
        choice = input("[?] Run client to generate responses for '{}' samples?(y/n)".format(_experiment.label))
        if choice == "y":
            client_process = self.run_client(
                       self.tmp_client_input_filepath,
                       self.tmp_client_output_filepath)
            client_process.wait()
        server_process.kill()

        if os.path.exists(self.tmp_client_output_filepath):
            # add samples from TEMPORAL output to response_and_scored dataset, calculating scores along the way
            df_tmp_responses_dataset, tmp_responses_hashset = _experiment.read_dataset(self.tmp_client_output_filepath, ["prompt", "response"])
            print("[0] Validation interim results: generated responses for {} samples of '{}'.".format(df_tmp_responses_dataset.shape[0], _experiment.label))
            name_to_func = {}
            if _experiment.attack_type == "promptleak":
                name_to_func = pl.pi_objective_to_validate
            elif _experiment.attack_type == "benign":
                name_to_func = {
                    "benign" : lambda x: (0.0, True, 0.0)
                }
            else:
                print("[!] Validator error: unknown attack type '{}' in '{}'!".format(_experiment.attack_type,
                                                                           _experiment.label))
                return 0
            #i = 1
            for index, row in df_tmp_responses_dataset.iterrows():
                score, success, threshold = name_to_func[_experiment.attack_type](row)
                df_new_scored_row = pd.DataFrame({
                    "prompt" : [row["prompt"]],
                    "success" : pd.Series([success], dtype=np.bool_),
                    "score" : [score],
                    "threshold" : [threshold],
                    "system_message" : [self.server_system_message],
                    "model_name" : [self.experiment.model_name],
                    "response" : [row["response"]]
                })
                if df_scored_dataset[df_scored_dataset.prompt == row["prompt"]].shape[0] == 0:
                    df_scored_dataset = pd.concat([df_scored_dataset, df_new_scored_row], ignore_index = True)
                else:
                    columns = list(df_scored_dataset.columns)
                    index = df_scored_dataset.index[df_scored_dataset.prompt == row["prompt"]][0]
                    for column in columns:
                        df_scored_dataset.at[index, column] = df_new_scored_row.at[0, column]
            _experiment.write_scored_dataset(df_scored_dataset, _overwrite_existing_rows = True)
            #os.remove(self.tmp_client_output_filepath)
        else:
            print("[0] Validation interim results: no prompt-response file in temporary folder. Continuing...")
        # do not remove tmp output file - can be used if interim results are saved
        os.remove(self.tmp_client_input_filepath)
        return 1

    def validate(self, _experiment):
        if _experiment.val_exists():
            are_validated_complete = self.check_validated(_experiment)
            if are_validated_complete == 1:
                print("[0] Existing validated samples are enough.")
                return 1
        if _experiment.scored_exists():
            are_scored_complete = self.check_scored(_experiment)
            if are_scored_complete == 1:
                print("[0] Existing scored samples are enough. Writing them into validated samples.")
                self.update_scored_to_validated(_experiment)
                return 1
        # (valid) are incomplete or nonexistent, and (scored) are incomplete or nonexistent
        self.generate_responses_and_scores(_experiment)
        self.update_scored_to_validated(_experiment)
        return 1

    def run(self):
        return self.validate(self.experiment)

###################################################################
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
                       str(self.server_system_message), # system message
                       str(self.experiment.model_name) # llm model name
        ]
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
                       os.path.abspath(_str_samples_result_filename)
        ]
        return subprocess.Popen(args = client_args,
                       cwd = cwd_path,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)
