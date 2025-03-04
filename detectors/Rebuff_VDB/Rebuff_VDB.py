import sys, os, subprocess, yaml
import requests, json
sys.path.append(".\\detectors\\")
from BaseDetector import *


class Rebuff_VDB(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Rebuff_VDB",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        self.rebuffSDKServer_address = dict_conf["rebuff"]["server_address"]
        self.rebuffSDKServer_port = dict_conf["rebuff"]["server_port"]
        self.str_rebuffSDKServer_scanEnd = "scan"
        self.run_vectordb = dict_conf["rebuff"]["input_scanners"]["vectordb"]["use_scanner"]
        self.vdb_threshold = dict_conf["rebuff"]["input_scanners"]["vectordb"]["threshold"]
        
        tmp = self.output_filepath.split(".")
        self.output_filepath = ".".join(tmp[:-1]) + "(extended_vdb)." + tmp[-1]

        
    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "r_run_vectordb" : pd.Series([], dtype=np.bool_),
                "r_is_detected_by_vectordb" : pd.Series([], dtype=np.bool_),
                "r_vectordb_score" : [],
                "r_vectordb_threshold" : []
            }
        )
    def analyze_input(self,
                      dict_input_row):
        rebuff_input_scans_results = self.query_RebuffSDK_Server(
                dict_input_row["prompt"]
        )

        vectordb_score = rebuff_input_scans_results["input_scan_results"]["vector_score"]
        vectordb_threshold = rebuff_input_scans_results["input_scan_results"]["max_vector_score"]
        is_detected_by_vectordb = False
        if vectordb_score > vectordb_threshold:
            is_detected_by_vectordb = True


        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "r_run_vectordb" : pd.Series([self.run_vectordb], dtype=np.bool_),
                "r_is_detected_by_vectordb" : pd.Series([is_detected_by_vectordb], dtype=np.bool_),
                "r_vectordb_score" : [vectordb_score],
                "r_vectordb_threshold" : [self.vdb_threshold]
            }
        return pd.DataFrame(output_row)


    def run(self):
        if not self.run_vectordb:
            sys.exit(0)
        super().run()

#################################################################################################

    def query_RebuffSDK_Server(self,
                               _input_prompt):
        rebuffSDK_request_data = {
            "prompt": _input_prompt,
            "check_heuristic": False,
            "heuristics_threshold": 0,
            "check_vector": self.run_vectordb,
            "vector_threshold": self.vdb_threshold,
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
            print("[!] Rebuff VectorDB error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Rebuff VectorDB error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Rebuff_VDB(str_input_filepath,
                          str_output_filepath)
    detector.run()
    sys.exit(1)

