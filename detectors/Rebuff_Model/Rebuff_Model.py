import sys, os, subprocess, yaml
import requests, json
sys.path.append(".\\detectors\\")
from BaseDetector import *


class Rebuff_Model(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Rebuff_Model",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        self.rebuffSDKServer_address = dict_conf["rebuff"]["server_address"]
        self.rebuffSDKServer_port = dict_conf["rebuff"]["server_port"]
        self.str_rebuffSDKServer_scanEnd = "scan"
        self.run_model = dict_conf["rebuff"]["input_scanners"]["model"]["use_scanner"]
        self.model_threshold = dict_conf["rebuff"]["input_scanners"]["model"]["threshold"]

        tmp = self.output_filepath.split(".")
        self.output_filepath = ".".join(tmp[:-1]) + "(model=gpt-4o)" + "." + tmp[-1]
        
    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "r_run_model" : pd.Series([], dtype=np.bool_),
                "r_is_detected_by_model" : pd.Series([], dtype=np.bool_),
                "r_model_score" : [],
                "r_model_threshold" : [],
                "r_secondary_model" : [],
                "r_secondary_model_prompt": [],
                "r_secondary_model_response": []
            }
        )
    def analyze_input(self,
                      dict_input_row):
        rebuff_input_scans_results = self.query_RebuffSDK_Server(
                dict_input_row["prompt"]
        )

        model_score = rebuff_input_scans_results["input_scan_results"]["openai_score"]
        model_threshold = rebuff_input_scans_results["input_scan_results"]["max_model_score"]
        model_sec_name = rebuff_input_scans_results["input_scan_results"]["secondary_model"]
        model_sec_prompt = rebuff_input_scans_results["input_scan_results"]["secondary_prompt_template"]
        model_sec_response = rebuff_input_scans_results["input_scan_results"]["secondary_response"]
        
        is_detected_by_model = False
        if model_score > model_threshold:
            is_detected_by_model = True


        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "r_run_model" : pd.Series([self.run_model], dtype=np.bool_),
                "r_is_detected_by_model" : pd.Series([is_detected_by_model], dtype=np.bool_),
                "r_model_score" : [model_score],
                "r_model_threshold" : [self.model_threshold],
                "r_secondary_model" : [model_sec_name],
                "r_secondary_model_prompt": [model_sec_prompt],
                "r_secondary_model_response": [model_sec_response]
            }
        return pd.DataFrame(output_row)


    def run(self):
        if not self.run_model:
            sys.exit(0)
        super().run()

#################################################################################################

    def query_RebuffSDK_Server(self,
                               _input_prompt):
        rebuffSDK_request_data = {
            "prompt": _input_prompt,
            "check_heuristic": False,
            "heuristics_threshold": 0,
            "check_vector": False,
            "vector_threshold": 0,
            "check_llm": self.run_model,
            "model_threshold": self.model_threshold
        }
        str_url = "http://{}:{}/{}".format(self.rebuffSDKServer_address,
                                           self.rebuffSDKServer_port,
                                           self.str_rebuffSDKServer_scanEnd)
        dict_headers = {
            "Content-Type": "application/json",
            "Host": self.rebuffSDKServer_address
        }
        response = ""
        try:
            response = requests.post(url=str_url,
                                     headers=dict_headers,
                                     data=json.dumps(rebuffSDK_request_data))
        except:
            print("[!] Error requesting RebuffSDK server.")
            sys.exit(-1)
        try:
            response = response.json()
        except:
            print("[!] Error parsing RebuffSDK server response.")
            sys.exit(-1)
        return response

# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] Rebuff Model error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Rebuff Model error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Rebuff_Model(str_input_filepath,
                          str_output_filepath)
    detector.run()
    sys.exit(1)

