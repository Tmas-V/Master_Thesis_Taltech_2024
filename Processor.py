import os, sys
import subprocess

from Experiment import *

class Processor:
    def __init__(self,
                 _str_type,
                 _experiment
                 ):
        self.type = _str_type
        self.experiment = _experiment
        self.detector_py_path_dict = {
            "LLMGuard_Transformer"  : ".\\detectors\\LLMGuard_Transformer\\LLMGuard_Transformer.py",
            "Vigil_Yara"            : ".\\detectors\\Vigil_Yara\\Vigil_Yara.py",
            "Vigil_Transformer"     : ".\\detectors\\Vigil_Transformer\\Vigil_Transformer.py",
            "Vigil_VDB"             : ".\\detectors\\Vigil_VDB\\Vigil_VDB.py",
            "Vigil_Canary"          : ".\\detectors\\Vigil_Canary\\Vigil_Canary.py",
            "Vigil_PRSimilarity"    : ".\\detectors\\Vigil_PRSimilarity\\Vigil_PRSimilarity.py",
            "Rebuff_Heuristics"     : ".\\detectors\\Rebuff_Heuristics\\Rebuff_Heuristics.py",
            "Rebuff_Model"          : ".\\detectors\\Rebuff_Model\\Rebuff_Model.py",
            "Rebuff_VDB"            : ".\\detectors\\Rebuff_VDB\\Rebuff_VDB.py",
            "Rebuff_Canary"         : ".\\detectors\\Rebuff_Canary\\Rebuff_Canary.py"
        }

    def process_dataset(self,
                        _str_input_filepath,
                        _str_output_filepath):
        #choice = input("[?] Run detections with '{}' for '{}' samples?(y/n)".format(self.type, self.experiment.label))
        print("[0] Running {} processor for {} samples...".format(self.type, self.experiment.label))
        choice = "y"
        if choice == "y":
            venv_conf_data = yaml.safe_load(
                    open(".\\venvs.yaml", "r")
            )
            detector_source = self.type.split("_")[0]
            detector_venv_path = os.path.abspath(
                venv_conf_data[detector_source]
            )
            detector_cwd_path = os.path.abspath(".\\")
            detector_py_path = os.path.abspath(self.detector_py_path_dict[self.type])
            detector_process_args = [detector_venv_path,
                                     detector_py_path,
                                     _str_input_filepath,
                                     _str_output_filepath]
            detector_process = subprocess.Popen(args = detector_process_args,
                           cwd = detector_cwd_path,
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            exit_code = detector_process.wait()
            return exit_code
        return 0

    def run(self):
        str_input_filepath = os.path.abspath(self.experiment.valid_filepath)
        str_output_filepath = os.path.abspath(self.experiment.processed_dataset_filepath(self.type))
        return self.process_dataset(str_input_filepath,
                                    str_output_filepath)
