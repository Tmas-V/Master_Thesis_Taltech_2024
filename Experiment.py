import yaml, json
import sys, os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

class Experiment:
    def __init__(self,
                 _label):
        self.attack_type = "promptleak"
        self.attack_enhancements = []
        self.gen_samples_limit = 2000
        self.val_samples_limit = 1000
        self.rerun_validation = False
        self.model_name = "model"

        self.conf_save_path = ".\\experiments\\"
        self.label = _label
        self.conf_filename = self.label + ".yaml"
        self.conf_filepath = self.conf_save_path + self.conf_filename
        self.load_from_self_yaml()

        self.generated_save_path = ".\\results\\{}\\generated\\{}\\"
        self.validated_save_path = ".\\results\\{}\\validated\\{}\\"
        self.processed_save_path = ".\\results\\{}\\processed\\{}\\"

        self.gen_columns = ["prompt"]
        self.gen_scored_columns = ["prompt", "response", "model_name", "threshold", "score", "success", "system_message"]
        self.val_columns = ["prompt", "response", "model_name"]

        self.set_model(self.model_name)

    def processed_dataset_filepath(self, _str_detector_type):
        ret = self.processed_save_path.format(self.model_name, self.label)
        if not os.path.exists(ret):
            os.mkdir(ret)
        ret += "{}\\".format(_str_detector_type)
        if not os.path.exists(ret):
            os.mkdir(ret)
        return ret + self.label + "(processed).parquet"

    def create_folderpath_if_not_exist(self, _folderpath):
        if os.path.exists(_folderpath):
            return
        os.mkdir(_folderpath)

    def conf_exists(self):
        return os.path.exists(self.conf_filepath)
    def gen_exists(self):
        return os.path.exists(self.gen_filepath)
    def scored_exists(self):
        return os.path.exists(self.gen_scored_filepath)
    def val_exists(self):
        return os.path.exists(self.valid_filepath)
    def debug_log(self):
        conf_data = yaml.safe_load(open(self.conf_filepath, "r"))
        print("============ Loaded experiment =============")
        print(json.dumps(conf_data, indent = "\t"))
        print("============================================")
        print("")
#        data = {
#            "attack_type" : self.attack_type,
#           "attack_enhancements" : self.attack_enhancements,
#            "gen_samples_limit" : self.gen_samples_limit,
#            "val_samples_limit" : self.val_samples_limit,
#            "rerun_validation" : self.rerun_validation
#        }
#        print("============ Data in experiment =============")
#        print(json.dumps(data, indent = "\t"))
#        print("============================================")
#        print("")

    def set_model(self, _new_model_name):
        self.model_name = _new_model_name
        ##############################
        self.gen_filename = self.label + "(generated).parquet"
        self.gen_filepath = self.generated_save_path.format(self.model_name, self.label)
        self.create_folderpath_if_not_exist(self.gen_filepath)
        self.gen_filepath += self.gen_filename
        ##############################
        self.gen_scored_filename = self.label + "(response+score).parquet"
        self.gen_scored_filepath = self.validated_save_path.format(self.model_name, self.label)
        self.create_folderpath_if_not_exist(self.gen_scored_filepath)
        self.gen_scored_filepath += self.gen_scored_filename
        ##############################
        self.valid_filename = self.label + "(validated).parquet"
        self.valid_filepath = self.validated_save_path.format(self.model_name, self.label)
        self.create_folderpath_if_not_exist(self.valid_filepath)
        self.valid_filepath += self.valid_filename
#########################################################################################
    def load_from_yaml(self,
                       _filepath):
        try:
            with open(_filepath, "r") as file:
                conf_data = yaml.safe_load(file)
                self.attack_type = conf_data["attack_type"]
                self.attack_enhancements = conf_data["attack_enhancements"]
                self.gen_samples_limit = conf_data["gen_samples_limit"]
                self.val_samples_limit = conf_data["val_samples_limit"]
                self.rerun_validation = conf_data["rerun_validation"]
                self.model_name = conf_data["model_name"]
                self.use_valid_as_gen = conf_data["use_valid_as_gen"]
        except:
            print("[!] Experiment error: {} file read incorrectly.".format(_filepath))
    def load_from_self_yaml(self):
        try:
            self.load_from_yaml(self.conf_filepath)
        except:
            print("[!] Experiment error: failed loading '{}' config!".format(self.label))

    def save_to_yaml(self,
                     _filepath):
        data = {
            "attack_type" : self.attack_type,
            "attack_enhancements" : self.attack_enhancements,
            "gen_samples_limit" : self.gen_samples_limit,
            "val_samples_limit" : self.val_samples_limit,
            "rerun_validation" : self.rerun_validation,
            "model_name" : self.model_name,
            "use_valid_as_gen" : self.use_valid_as_gen
        }
        with open(_filepath, "w") as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
    def save_to_yaml_self(self):
        try:
            self.save_to_yaml(self.conf_filepath)
        except:
            print("[!] Experiment error: {} file wrote incorrectly.".format(_filepath))
#####################################################################################
    def get_previous_experiment(self):
        prev_label = self.attack_type
        for enhancement in self.attack_enhancements[:-1]:
            prev_label += "_" + enhancement["name"]
        return Experiment(prev_label)
    def get_intermediate_experiments_labels(self):
        ret_list = []
        str_filename = self.attack_type
        ret_list += [str_filename]
        for enhancement in self.attack_enhancements:
            str_filename += "_" + enhancement["name"]
            ret_list += [str_filename]
        return ret_list
    def get_intermediate_experiments(self):
        ret_list = []
        labels = self.get_intermediate_experiments_labels()
        for label in labels:
            ret_list += [Experiment(label)]
        return ret_list
##########################################################################################
    def empty_dataframe(self, _columns):
        df = {}
        for column in _columns:
            df[column] = []
        return pd.DataFrame(df)
    def empty_gen_dataframe(self):
        return self.empty_dataframe(self.gen_columns)
    def empty_gen_scored_dataframe(self):
        ret = self.empty_dataframe(self.gen_scored_columns)
        ret["success"] = pd.Series([], dtype=np.bool_)
        return ret
    def empty_val_dataframe(self):
        return self.empty_dataframe(self.val_columns)
    
    def read_dataset(self, _filepath, _columns):
        if not os.path.exists(_filepath):
            return self.empty_dataframe(_columns), {}
        hashset = {}
        samples = parquet.read_pandas(_filepath,
                                             columns=_columns).to_pandas()
        prompt_samples = samples["prompt"].tolist()
        for prompt_sample in prompt_samples:
            hashset[prompt_sample] = 1
        return (samples, hashset)
    def read_gen_dataset(self):
        return self.read_dataset(self.gen_filepath, self.gen_columns)
    def read_scored_dataset(self):
        if not os.path.exists(self.gen_scored_filepath):
            return self.empty_gen_scored_dataframe(), {}
        hashset = {}
        samples = parquet.read_pandas(self.gen_scored_filepath,
                                             columns=self.gen_scored_columns).to_pandas()
        for index, row in samples.iterrows():
            hashset[row["prompt"]] = (row["score"], row["success"])
        return (samples, hashset)
    def read_val_dataset(self):
        return self.read_dataset(self.valid_filepath, self.val_columns)


    def write_dataset(self, _filepath, _columns, _df_dataset, _int_write_limit, _overwrite_existing_rows = False):
        # Assuming _df_dataset is compatible for saving at _filepath
        # And assuming all the folders in _filepath exist
        prompt_samples = _df_dataset["prompt"].to_list()
        _hashset = {}
        for prompt_sample in prompt_samples:
            _hashset[prompt_sample] = 1

        if not os.path.exists(_filepath) or _overwrite_existing_rows:
            # no written data exists, simply write dataset while conforming to write limit
            # completely overwrite the file, following the limit
            if _int_write_limit > 0:
                _df_dataset = _df_dataset.head(_int_write_limit)
            parquet.write_table(pyarrow.Table.from_pandas(_df_dataset),
                                _filepath)
            return 1            

        # written dataset exists; if existing dataset conforms write limit - do nothing
        # else - add top missing rows to existing rows and overwrite dataset
        df_exist_dataset, exist_hashset = self.read_dataset(_filepath, _columns)
        if _int_write_limit > 0 and len(exist_hashset) == _int_write_limit:
            return 1
        if _int_write_limit > 0 and len(exist_hashset) > _int_write_limit:
            df_exist_dataset = df_exist_dataset.head(_int_write_limit)
            parquet.write_table(pyarrow.Table.from_pandas(df_exist_dataset),
                                _filepath)
            return 1

        int_count_diff = -1
        if _int_write_limit > 0:
            int_count_diff = _int_write_limit - len(exist_hashset.keys())
        i = 0
        for index, row in _df_dataset.iterrows():
            if not row["prompt"] in exist_hashset.keys():
                df_row = {}
                for column in _columns:
                    df_row[column] = [row[column]]
                df_row = pd.DataFrame(df_row)
                df_exist_dataset = pd.concat([df_exist_dataset, df_row], ignore_index = True)
                i += 1
                if i == int_count_diff:
                    break

        parquet.write_table(pyarrow.Table.from_pandas(df_exist_dataset),
                            _filepath)
        return 1

    def write_gen_dataset(self, _df_dataset, _overwrite_existing_rows = False):
        self.write_dataset(self.gen_filepath, self.gen_columns, _df_dataset, self.gen_samples_limit, _overwrite_existing_rows)

    def write_scored_dataset(self, _df_dataset, _overwrite_existing_rows = False):
        self.write_dataset(self.gen_scored_filepath, self.gen_scored_columns, _df_dataset, self.gen_samples_limit, _overwrite_existing_rows)

    def write_val_dataset(self, _df_dataset, _overwrite_existing_rows = False):
        self.write_dataset(self.valid_filepath, self.val_columns, _df_dataset, self.val_samples_limit, _overwrite_existing_rows)

    def write_gen_empty_dataset(self):
        self.write_gen_dataset(self.empty_gen_dataframe())
    def write_scored_empty_dataset(self):
        self.write_scored_dataset(self.empty_gen_scored_dataframe())
    def write_val_empty_dataset(self):
        self.write_val_dataset(self.empty_val_dataframe())
