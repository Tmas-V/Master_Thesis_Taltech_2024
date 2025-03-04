import yaml, json
import sys, os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

from Experiment import *
from Validator import *

sys.path.append(".\\attack_techniques\\")
import prompt_leak as pl
import pi_enhancement as pe
import pi_obfuscations as po



class Generator:
    def __init__(self,
                 _experiment):
        self.experiment = _experiment
    # returns number of samples, saved at gen_dataset; or 0 if error occured
    def generate(self, _experiment):
        # create empty files as placeholders
        if not _experiment.gen_exists():
            _experiment.write_gen_empty_dataset()
        if not _experiment.scored_exists():
            _experiment.write_scored_empty_dataset()
        if not _experiment.val_exists():
            _experiment.write_val_empty_dataset()

        if _experiment.use_valid_as_gen:
            _gpt35experiment = Experiment(_experiment.label)
            _gpt35experiment.set_model("gpt-3.5-turbo")
            exist_valid, _ = _gpt35experiment.read_val_dataset()
            _experiment.write_gen_dataset(exist_valid, _overwrite_existing_rows = True)
            print("[0] Generation result: written {} sample from validated gpt-3.5-turbo data.".format(exist_valid.shape[0]))
            return exist_valid.shape[0]
        
        if len(_experiment.attack_enhancements) == 0:
            # generate bare samples - with no enhancements
            name_to_func = {}
            if _experiment.attack_type == "promptleak":
                name_to_func = pl.pi_objective_to_generate
            elif _experiment.attack_type == "benign":
                name_to_func = {
                    "benign" : lambda x: _experiment.read_gen_dataset()[0]
                }
            else:
                print("[!] Generator error: unknown attack type '{}' in '{}'!".format(_experiment.attack_type,
                                                                           _experiment.label))
                return 0
            _experiment.debug_log()
            df_gen_samples = name_to_func[_experiment.attack_type](_experiment.gen_samples_limit)
            _experiment.write_gen_dataset(df_gen_samples)
            return df_gen_samples.shape[0]
        
        # else - generate samples by applying technique/obfuscation to samples from previous validated dataset
        prev_experiment = _experiment.get_previous_experiment()
        if prev_experiment.val_exists():
            name_to_func = {}
            if _experiment.attack_enhancements[-1]["type"] == "technique":
                name_to_func = pe.pi_enhancement_to_generate
            elif _experiment.attack_enhancements[-1]["type"] == "obfuscation":
                name_to_func = po.pi_obfuscation_to_generate
            else:
                print("[!] Generator error: unknown PI enhancement '{}' in '{}'!".format(_experiment.attack_enhancements[-1]["type"],
                                                                           _experiment.label))
                return 0
            df_prev_val_samples, prev_val_hashset = prev_experiment.read_val_dataset()
            df_gen_samples = name_to_func[_experiment.attack_enhancements[-1]["name"]](df_prev_val_samples,
                                                                                       _experiment.gen_samples_limit)
            _experiment.write_gen_dataset(df_gen_samples)
            return df_gen_samples.shape[0]
        else:
            print("[!] Generator error: validated samples for '{}' are not found!".format(prev_experiment.label))
            return 0

    def run(self):
        if not self.experiment.conf_exists():
            print("[!] Generator error: config for '{}' is not found!".format(self.experiment.label))
            return 0
        intermediate_experiments = self.experiment.get_intermediate_experiments()
        for intermediate_experiment in intermediate_experiments:
            if not intermediate_experiment.conf_exists():
                print("[!] Generator error: config for '{}' is not found!".format(intermediate_experiment.label))
                return 0
            saved_gen_samples_count = self.generate(intermediate_experiment)
            if saved_gen_samples_count == 0:
                return 0
            print("[0] Generation result: {} samples were saved.".format(saved_gen_samples_count))
            choice = input("Proceed to Validation of '{}'?(y/n)".format(intermediate_experiment.label))
            if choice == "y":
                validator = Validator(intermediate_experiment)
                validator.run()

        return 1
    
    
