import sys, os, subprocess, yaml
sys.path.append(".\\detectors\\")
from BaseDetector import *
################### Vigil setup ######################
from vigil.vigil import Vigil
##########################################################

class Vigil_Transformer(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Vigil_Transformer",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        self.vigil_conf_template_filename = ".\\detectors\\Vigil_Transformer\\vigil_server_conf_template.conf"
        self.vigil_conf_filename = ".\\detectors\\Vigil_Transformer\\vigil_server_conf.conf"
        self.vigil_app = self.configure_Vigil()

    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "v_run_transformer" : pd.Series([], dtype=np.bool_),
                "v_is_detected_by_transformer" : pd.Series([], dtype=np.bool_),
                "v_transformer_model" : [],
                "v_transformer_score" : [],
                "v_transformer_threshold" : [],

            }
        )
    def analyze_input(self,
                      dict_input_row):
        vigil_input_scans_results = self.vigil_app.input_scanner.perform_scan(
                dict_input_row["prompt"]
        )

        is_detected_by_transformer = len(vigil_input_scans_results["results"].get("scanner:transformer", {}).keys()) > 0
        if is_detected_by_transformer:
            is_detected_by_transformer = len(vigil_input_scans_results["results"]["scanner:transformer"]["matches"]) > 0
        transformer_score = 0.0
        if is_detected_by_transformer:
            transformer_score = round(
                vigil_input_scans_results["results"]["scanner:transformer"]["matches"][0]["score"],
                9
            )

        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "v_run_transformer" : pd.Series([self.run_transformer], dtype=np.bool_),
                "v_is_detected_by_transformer" : pd.Series([is_detected_by_transformer], dtype=np.bool_),
                "v_transformer_model" : [self.transformer_model],
                "v_transformer_score" : [transformer_score],
                "v_transformer_threshold" : [self.transformer_threshold],
        }
        return pd.DataFrame(output_row)



    def run(self):
        if not self.run_transformer:
            sys.exit(0)
        super().run()

#################################################################################################

    def configure_Vigil(self):
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        
        self.run_transformer = dict_conf["vigil"]["input_scanners"]["transformer"]["use_scanner"]
        self.transformer_model = dict_conf["vigil"]["input_scanners"]["transformer"]["model"]
        self.transformer_threshold = dict_conf["vigil"]["input_scanners"]["transformer"]["threshold"]
        self.openai_api_key = open(".\\env.list", "r").read().strip("\n").split("=")[1]

        str_vigil_template_conf = open(self.vigil_conf_template_filename, "r").read()
        str_vigil_conf = str_vigil_template_conf.format(
            openai_api_key = self.openai_api_key,
            transformer_model = self.transformer_model,
            transformer_threshold = self.transformer_threshold
        )
        open(self.vigil_conf_filename, "w").write(str_vigil_conf)
        return Vigil.from_config(self.vigil_conf_filename)

# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] Vigil Transformer error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Vigil Transformer error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Vigil_Transformer(str_input_filepath,
                                 str_output_filepath)
    detector.run()
    sys.exit(1)

