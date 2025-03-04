import sys, os, subprocess, yaml
sys.path.append(".\\detectors\\")
from BaseDetector import *
################### Vigil setup ######################
from vigil.vigil import Vigil
##########################################################

class Vigil_Yara(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Vigil_Yara",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        self.vigil_conf_filename = ".\\detectors\\Vigil_Yara\\vigil_server_conf.conf"
        self.vigil_conf_template_filename = ".\\detectors\\Vigil_Yara\\vigil_server_conf_template.conf"
        self.vigil_app = self.configure_Vigil()

        
    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "v_run_yara" : pd.Series([], dtype=np.bool_),
                "v_is_detected_by_yara" : pd.Series([], dtype=np.bool_)
            }
        )
    def analyze_input(self,
                      dict_input_row):
        vigil_input_scans_results = self.vigil_app.input_scanner.perform_scan(
                dict_input_row["prompt"]
        )

        is_detected_by_yara = len(vigil_input_scans_results["results"].get("scanner:yara", {}).keys()) > 0
        if is_detected_by_yara:
            is_detected_by_yara = len(vigil_input_scans_results["results"]["scanner:yara"]["matches"]) > 0


        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "v_run_yara" : pd.Series([self.run_yara], dtype=np.bool_),
                "v_is_detected_by_yara" : pd.Series([is_detected_by_yara], dtype=np.bool_)
        }
        return pd.DataFrame(output_row)


    def run(self):
        if not self.run_yara:
            sys.exit(0)
        super().run()

#################################################################################################
    def configure_Vigil(self):
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        
        self.run_yara = dict_conf["vigil"]["input_scanners"]["yara"]["use_scanner"]
        self.yara_dirpath = dict_conf["vigil"]["input_scanners"]["yara"]["yara_rules_dirpath"]
        self.openai_api_key = open(".\\env.list", "r").read().strip("\n").split("=")[1]

        str_vigil_template_conf = open(self.vigil_conf_template_filename, "r").read()
        str_vigil_conf = str_vigil_template_conf.format(
            openai_api_key = self.openai_api_key,
            yara_dirpath = self.yara_dirpath
        )
        open(self.vigil_conf_filename, "w").write(str_vigil_conf)
        return Vigil.from_config(self.vigil_conf_filename)


# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] Vigil Yara error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Vigil Yara error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = Vigil_Yara(str_input_filepath,
                          str_output_filepath)
    detector.run()
    sys.exit(1)

