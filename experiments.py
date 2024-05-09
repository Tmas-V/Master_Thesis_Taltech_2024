import yaml, json
import sys, os
import subprocess
sys.path.append(".\\client\\")
import pi_attacks as pi_att
import pi_jailbreaks as pi_jail
import pi_obfuscations as pi_obf
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

class Experiment:
##################### Init&run functions #################################
    def __init__(self,
                 _filename):
        self.conf_save_path = ".\\experiments"
        self.results_save_path = ".\\results"
        self.results_benign_save_path = ".\\results\\benign"
        self.results_benign_filename = "benign"
        self.task_type_to_method = {
            "test_benign": self.test_benign,
            "test_attack": self.test_attack
        }
        self.task_type = "task_type"
        self.attack_objective_class = "attack_objective_class"
        self.attack_enhancements = "attack_enhancements"

        self.server_client_types = [
            "Default",
            "LLM Guard",
            "Vigil",
            "Rebuff"
        ]
        self.venv_conf_filename = ".\\venvs.yaml"
        with open(self.venv_conf_filename, "r") as file:
            conf_data = yaml.safe_load(file)
            self.server_type_to_venv = {
                self.server_client_types[0]: os.path.abspath(conf_data["default server venv path"]),
                self.server_client_types[1]: os.path.abspath(conf_data["LLMGuard server venv path"]),
                self.server_client_types[2]: os.path.abspath(conf_data["Vigil server venv path"]),
                self.server_client_types[3]: os.path.abspath(conf_data["Rebuff server venv path"]),
            }
        self.server_type_to_cwd = {
            self.server_client_types[0]: os.path.abspath(".\\server\\server(default)"),
            self.server_client_types[1]: os.path.abspath(".\\server\\server(LLM Guard)"),
            self.server_client_types[2]: os.path.abspath(".\\server\\server(Vigil)"),
            self.server_client_types[3]: os.path.abspath(".\\server\\server(Rebuff)")
        }
        self.server_type_to_py = {
            self.server_client_types[0]: "no_detections_server.py",
            self.server_client_types[1]: "LLMGuard_server.py",
            self.server_client_types[2]: "Vigil_server.py",
            self.server_client_types[3]: "Rebuff_server.py"
        }
        
        self.client_venv = self.server_type_to_venv[self.server_client_types[0]]
        self.client_type_to_cwd = {
            self.server_client_types[0]: os.path.abspath(".\\client\\client(default)"),
            self.server_client_types[1]: os.path.abspath(".\\client\\client(LLM Guard)"),
            self.server_client_types[2]: os.path.abspath(".\\client\\client(Vigil)"),
            self.server_client_types[3]: os.path.abspath(".\\client\\client(Rebuff)")
        }
        self.client_type_to_py = {
            self.server_client_types[0]: "no_detections_client.py",
            self.server_client_types[1]: "LLMGuard_client.py",
            self.server_client_types[2]: "Vigil_client.py",
            self.server_client_types[3]: "Rebuff_client.py"
        }

        try:
            self.load_from_yaml(self.conf_save_path,
                                _filename)
        except:
            pass
    def load_from_yaml(self,
                       _save_path,
                       filename):
        try:
            with open("{}\\{}".format(_save_path, filename), "r") as file:
                conf_data = yaml.safe_load(file)
                self.task_type = conf_data["task_type"]
                self.attack_objective_class = conf_data["attack_objective_class"]
                self.attack_enhancements = conf_data["attack_enhancements"]
                print("============ Loaded experiment =============")
                print(json.dumps(conf_data, indent = "\t"))
                print("============================================")
                print("")
        except:
            print("[!] Experiments error: {} file read incorrectly.".format(filename))
            return 0
    def save_to_yaml(self,
                     filename):
        data = {
            "task_type" : self.task_type,
            "attack_objective_class" : self.attack_objective_class,
            "attack_enhancements" : self.attack_enhancements
        }
        with open("{}\\{}".format(self.conf_save_path, filename), "w") as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
    def run(self):
        self.task_type_to_method[self.task_type]()
########################################################################################
########################### Experiment functions ######################################
    def run_verify_tests(self,
                         _pi_attack_class,
                         _pi_enhancements):
        """
        Iteratively generates prompt injection attack samples and verifies their work on agent with no detections
        1) Starts from generating PI objective. If parquet file with results for this objective exist - continue.
            Else - run success tests on default server via default client.
        2) Enhance resultant successful samples with the first jailbreak/obfuscation in array.
            If parquet file with results already exists - continue.
            Else - run success tests on default server via default client
        3) Repeat step 2 til the last jailbreak/obfuscation in array
        Returns (dirpath, filepath) to parquet file with results on success tests
        """
        
        str_results_piobjective_dirpath = os.path.abspath("{}\\{}".format(self.results_save_path,
                                                   _pi_attack_class))
        if not os.path.exists(str_results_piobjective_dirpath):
            os.mkdir(str_results_piobjective_dirpath)
        str_results_piobjective_filename = "bare_{}.parquet".format(_pi_attack_class)
        attack_samples = []
        str_prompts_source_filepath = os.path.abspath("{}\\{}".format(self.results_save_path,
                                                                      "{}(prompts only).parquet".format(_pi_attack_class)))
        if not os.path.exists(str_prompts_source_filepath):
            attack_samples = pi_att.pi_objective_to_generate[_pi_attack_class]()
            table = pyarrow.Table.from_pandas(pd.DataFrame({
                "prompt": attack_samples
            }))
            parquet.write_table(table,
                                str_prompts_source_filepath)
        str_prompts_dest_filepath = "{}\\{}".format(str_results_piobjective_dirpath,
                                               str_results_piobjective_filename)
        if not os.path.exists(str_prompts_dest_filepath):
            print("[?] Warning: verified prompts for {} do not exist!".format(_pi_attack_class))

        server_process = self.run_server(self.server_client_types[0])
        choice = input("Proceed to run verification tests for {} samples?(y/n)".format(_pi_attack_class))
        if choice == "y":
            client_process = self.run_client(_pi_attack_class,
                       self.server_client_types[0],
                       str_prompts_source_filepath,
                       str_results_piobjective_dirpath,
                       str_results_piobjective_filename)
            client_process.wait()
        server_process.kill()
        

        attack_samples = parquet.read_pandas(str_prompts_dest_filepath,
                                                 columns=["prompt"]).to_pandas()["prompt"].tolist()
        str_pi_enhanced_fullname = _pi_attack_class
        str_results_enhanced_dirpath = str_results_piobjective_dirpath
        str_results_enhanced_filename = str_results_piobjective_filename
        for _pi_enhancement_data in _pi_enhancements:
            _pi_enhancement_type = _pi_enhancement_data["type"]
            _pi_enhancement_name = _pi_enhancement_data["name"]
            _pi_enhancement_lambda = None
            if _pi_enhancement_type == "jailbreak":
                _pi_enhancement_lambda = pi_jail.pi_jailbreak_to_generate[_pi_enhancement_name]
            elif _pi_enhancement_type == "obfuscation":
                _pi_enhancement_lambda = pi_obf.pi_obfuscation_to_generate[_pi_enhancement_name]

            str_pi_enhanced_fullname = "{}_{}".format(str_pi_enhanced_fullname,
                                                       _pi_enhancement_name)
            str_results_enhanced_dirpath = os.path.abspath("{}\\{}".format(self.results_save_path,
                                                           str_pi_enhanced_fullname))
            if not os.path.exists(str_results_enhanced_dirpath):
                os.mkdir(str_results_enhanced_dirpath)
            str_results_enhanced_filename = "{}.parquet".format(str_pi_enhanced_fullname)
            str_prompts_source_filepath = os.path.abspath("{}\\{}".format(self.results_save_path,
                                                                          "{}(prompts only).parquet".format(str_pi_enhanced_fullname)))
            if not os.path.exists(str_prompts_source_filepath):
                attack_samples = _pi_enhancement_lambda(attack_samples)
                table = pyarrow.Table.from_pandas(pd.DataFrame({
                    "prompt": attack_samples
                }))
                parquet.write_table(table, str_prompts_source_filepath)

            str_prompts_dest_filepath = "{}\\{}".format(str_results_enhanced_dirpath,
                                                        str_results_enhanced_filename)
            if not os.path.exists(str_prompts_dest_filepath):
                print("[?] Warning: verified prompts for {} do not exist!".format(str_results_enhanced_filename))

            server_process = self.run_server(self.server_client_types[0])
            choice = input("Proceed to run verification tests for {} samples?(y/n)".format(str_pi_enhanced_fullname))
            if choice == "y":
                client_process = self.run_client(_pi_attack_class,
                           self.server_client_types[0],
                           str_prompts_source_filepath,
                           str_results_enhanced_dirpath,
                           str_results_enhanced_filename)
                client_process.wait()
            server_process.kill()

            attack_samples = parquet.read_pandas(str_prompts_dest_filepath,
                                                 columns=["prompt"]).to_pandas()["prompt"].tolist()
        
        return str_results_enhanced_dirpath, str_results_enhanced_filename

    def run_detection_tests(self,
                            _str_samples_source_dirpath,
                            _str_samples_source_filename):
        """
        
        """
        _str_samples_source_filepath = os.path.abspath("{}\\{}".format(_str_samples_source_dirpath,
                                                       _str_samples_source_filename))
        
        for detection_type in ["LLM Guard", "Vigil", "Rebuff"]:
            str_detections_results_dirpath = os.path.abspath("{}\\{}".format(_str_samples_source_dirpath,
                                                                             detection_type))
            if not os.path.exists(str_detections_results_dirpath):
                os.mkdir(str_detections_results_dirpath)
            str_detections_results_filepath = os.path.abspath("{}\\{}".format(str_detections_results_dirpath,
                                                                             _str_samples_source_filename))
            str_attack_class_name = _str_samples_source_filename.split(".")[0]
            if not os.path.exists(str_detections_results_filepath):
                print("[?] Warning: {}-tested prompts for {} do not exist!".format(detection_type, _str_samples_source_filename))
            server_process = self.run_server(detection_type)
            choice = input("Proceed to run detection tests with {} for {} samples?(y/n)".format(detection_type, str_attack_class_name))
            if choice == "y":
                client_process = self.run_client(self.attack_objective_class,
                                                 detection_type,
                                                 _str_samples_source_filepath,
                                                 str_detections_results_dirpath,
                                                 _str_samples_source_filename)
                client_process.wait()
                # Also save server's conf.json to detections folder
                str_server_conf_source_path = "{}\\conf.json".format(self.server_type_to_cwd[detection_type])
                str_server_conf_dest_path = "{}\\conf.json".format(str_detections_results_dirpath)
                with open(str_server_conf_source_path, "r") as source:
                    open(str_server_conf_dest_path, "w").write(source.read())

                # Also save server's logs/log.json to detections folder
                str_server_logs_source_path = "{}\\logs\\log.json".format(self.server_type_to_cwd[detection_type])
                str_server_logs_dest_path = "{}\\log.json".format(str_detections_results_dirpath)
                with open(str_server_logs_source_path, "r") as source:
                    open(str_server_logs_dest_path, "w").write(source.read())
                open(str_server_logs_source_path, "w").write("")
            server_process.kill()

        return 0



    def test_benign(self):
        """
        Checks if ~\benign\benign.parquet file exists. If not - throw exception.
        Then tests prompt samples from .\benign\benign.parquet on each server with detections.
        Saves results in .\benign\* directory
        """
        str_benign_dirpath = "{}\\{}".format(self.results_save_path,
                                             self.results_benign_filename)
        str_benign_filename = "{}.parquet".format(self.results_benign_filename)
        str_benign_filepath = "{}\\{}".format(str_benign_dirpath, str_benign_filename)
        if not os.path.exists(str_benign_filepath):
            print("[?] Warning: benign samples file (benign.parquet) does not exist.")
            print("[?] Run gen_benign_samples.py or create .\\results\\benign\\benign.parquet with 'prompt' column.")
            print("Quitting...")
            return 1
        choice = input("Proceed to run detection tests on benign samples?(y/n)")
        if choice == "y":
            self.run_detection_tests(str_benign_dirpath,
                                     str_benign_filename)
        else:
            print("Quitting...")
            return 0


    def test_attack(self):
        attack_samples_dirpath, attack_samples_filepath = self.run_verify_tests(self.attack_objective_class,
                                          self.attack_enhancements)
        if attack_samples_dirpath == "":
            print("Quitting...")
            return 0
        str_attack_class_name = attack_samples_filepath.split(".")[0]
        choice = input("Run detection tests for {} samples?(y/n)".format(str_attack_class_name))
        if choice == "y":
            self.run_detection_tests(attack_samples_dirpath,
                                attack_samples_filepath)
        return 0

        
########################################################################################
########################### Run server functions ######################################

    def run_server(self,
                   _server_type):
        """
        Returns server subprocess.
        """
        venv_path = self.server_type_to_venv[_server_type]
        cwd_path = self.server_type_to_cwd[_server_type]
        server_py_name = self.server_type_to_py[_server_type]
        server_py_path = "{}\\{}".format(cwd_path, server_py_name)
        server_args = [venv_path,
                       server_py_path
                       ]
        return subprocess.Popen(args = server_args,
                       cwd = cwd_path,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)

########################################################################################
########################### Run client functions ######################################

    def run_client(self,
                   _attack_objective,
                   _client_type,
                   _str_samples_source_filepath,
                   _str_samples_results_dirpath,
                   _str_samples_result_filename):
        """
        Returns client subprocess.
        """
        venv_path = self.client_venv
        cwd_path = self.client_type_to_cwd[_client_type]
        client_py_name = self.client_type_to_py[_client_type]
        client_py_path = "{}\\{}".format(cwd_path, client_py_name)
        client_args = [venv_path,
                       client_py_path,
                       _attack_objective,
                       _str_samples_source_filepath,
                       _str_samples_results_dirpath,
                       _str_samples_result_filename]
        return subprocess.Popen(args = client_args,
                       cwd = cwd_path,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)
        

########################################################################################
