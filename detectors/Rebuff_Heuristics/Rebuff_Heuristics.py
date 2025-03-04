import sys, os, subprocess, yaml
import requests, json
sys.path.append(".\\detectors\\")
from BaseDetector import *


class Rebuff_Heuristics(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Rebuff_Heuristics",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        self.rebuffSDKServer_address = dict_conf["rebuff"]["server_address"]
        self.rebuffSDKServer_port = dict_conf["rebuff"]["server_port"]
        self.str_rebuffSDKServer_scanEnd = "scan"
        self.run_heuristics = dict_conf["rebuff"]["input_scanners"]["heuristics"]["use_scanner"]
        self.heuristics_threshold = dict_conf["rebuff"]["input_scanners"]["heuristics"]["threshold"]

        output_filename = self.output_filepath.split("\\")[-1]
        output_filename_noext = output_filename.split(".")[0]
        self.output_filepath = "\\".join(self.output_filepath.split("\\")[:-1]) + "\\" + "{}({}).parquet".format(output_filename_noext, "Rebuff_Heur")

    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "r_run_heuristics" : pd.Series([], dtype=np.bool_),
                "r_is_detected_by_heuristics" : pd.Series([], dtype=np.bool_),
                "r_heuristics_score" : [],
                "r_heuristics_threshold" : []
            }
        )
    def analyze_input(self,
                      dict_input_row):
        rebuff_input_scans_results = self.query_RebuffSDK_Server(
                dict_input_row["prompt"]
        )

        heuristics_score = rebuff_input_scans_results["input_scan_results"]["heuristic_score"]
        heuristics_threshold = rebuff_input_scans_results["input_scan_results"]["max_heuristic_score"]
        is_detected_by_heuristics = False
        if heuristics_score > heuristics_threshold:
            is_detected_by_heuristics = True


        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "r_run_heuristics" : pd.Series([self.run_heuristics], dtype=np.bool_),
                "r_is_detected_by_heuristics" : pd.Series([is_detected_by_heuristics], dtype=np.bool_),
                "r_heuristics_score" : [heuristics_score],
                "r_heuristics_threshold" : [heuristics_threshold]
        }
        return pd.DataFrame(output_row)


    def run(self):
        if not self.run_heuristics:
            sys.exit(0)
        super().run()

#################################################################################################

    def query_RebuffSDK_Server(self,
                               _input_prompt):
        rebuffSDK_request_data = {
            "prompt": _input_prompt,
            "check_heuristic": self.run_heuristics,
            "heuristics_threshold": self.heuristics_threshold,
            "check_vector": False,
            "vector_threshold": 0,
            "check_llm": False,
            "model_threshold": 0
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
            print("[!] Rebuff Heuristics error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Rebuff Heuristics error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Rebuff_Heuristics(str_input_filepath,
                          str_output_filepath)
    detector.run()
    sys.exit(1)

