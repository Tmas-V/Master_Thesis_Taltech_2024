import sys, os, subprocess, yaml
sys.path.append(".\\detectors\\")
from BaseDetector import *
################### Vigil setup ######################
from vigil.vigil import Vigil
##########################################################

class Vigil_PRSimilarity(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Vigil_PRSimilarity",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        self.vigil_conf_template_filename = ".\\detectors\\Vigil_PRSimilarity\\vigil_server_conf_template.conf"
        self.vigil_conf_filename = ".\\detectors\\Vigil_PRSimilarity\\vigil_server_conf.conf"
        self.vigil_app = self.configure_Vigil()

    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "v_run_similarity" : pd.Series([], dtype=np.bool_),
                "v_is_detected_by_similarity" : pd.Series([], dtype=np.bool_),
                "v_similarity_score" : [],
                "v_similarity_threshold" : [],
                "response" : []

            }
        )
    def analyze_input(self,
                      dict_input_row):
        vigil_output_scans_results = self.vigil_app.output_scanner.perform_scan(
                dict_input_row["prompt"],
                dict_input_row["response"]
        )

        is_detected_by_similarity = len(vigil_output_scans_results["results"].get("scanner:response-similarity", {}).keys()) > 0
        if is_detected_by_similarity:
            is_detected_by_similarity = len(vigil_output_scans_results["results"]["scanner:response-similarity"]["matches"]) > 0
        similarity_score = 0.0
        if is_detected_by_similarity:
            similarity_score = round(
                vigil_output_scans_results["results"]["scanner:response-similarity"]["matches"][0]["score"],
                9
            )

        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "v_run_similarity" : pd.Series([self.run_similarity], dtype=np.bool_),
                "v_is_detected_by_similarity" : pd.Series([is_detected_by_similarity], dtype=np.bool_),
                "v_similarity_score" : [similarity_score],
                "v_similarity_threshold" : [self.similarity_threshold],
                "response" : [dict_input_row["response"]]
        }
        return pd.DataFrame(output_row)



    def run(self):
        if not self.run_similarity:
            sys.exit(0)
        super().run()

#################################################################################################

    def configure_Vigil(self):
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        
        self.run_similarity = dict_conf["vigil"]["output_scanners"]["similarity"]["use_scanner"]
        self.similarity_threshold = dict_conf["vigil"]["output_scanners"]["similarity"]["threshold"]
        self.openai_api_key = open(".\\env.list", "r").read().strip("\n").split("=")[1]

        str_vigil_template_conf = open(self.vigil_conf_template_filename, "r").read()
        str_vigil_conf = str_vigil_template_conf.format(
            openai_api_key = self.openai_api_key,
            similarity_threshold = self.similarity_threshold
        )
        open(self.vigil_conf_filename, "w").write(str_vigil_conf)
        return Vigil.from_config(self.vigil_conf_filename)

# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] Vigil Vigil_PRSimilarity error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Vigil Vigil_PRSimilarity error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Vigil_PRSimilarity(str_input_filepath,
                                 str_output_filepath)
    detector.run()
    sys.exit(1)

