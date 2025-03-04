import sys, os, subprocess, yaml
sys.path.append(".\\detectors\\")
from CanaryDetector import *
################### Vigil setup ######################
from vigil.vigil import Vigil
##########################################################

class Vigil_Canary(CanaryDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("Vigil_Canary",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        self.configure_canary()

#################################################################################################

    def configure_canary(self):
        self.vigil_conf_template_filename = ".\\detectors\\Vigil_Canary\\vigil_server_conf_template.conf"
        self.vigil_conf_filename = ".\\detectors\\Vigil_Canary\\vigil_server_conf.conf"
        self.conf_root_key = "vigil"
        
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        self.run_canary = dict_conf[self.conf_root_key]["canary_check"]["use_scanner"]
        self.canary_model_name = dict_conf[self.conf_root_key]["canary_check"]["model_name"]
        self.canary_usage_type = dict_conf[self.conf_root_key]["canary_check"]["usage_type"]

        self.openai_api_key = open(".\\env.list", "r").read().strip("\n").split("=")[1]

        str_vigil_template_conf = open(self.vigil_conf_template_filename, "r").read()
        str_vigil_conf = str_vigil_template_conf.format(
            openai_api_key = self.openai_api_key
        )
        open(self.vigil_conf_filename, "w").write(str_vigil_conf)
        self.vigil_app = Vigil.from_config(self.vigil_conf_filename)

        self.server_system_message = open(".\\system_message.txt", "r").read()
        self.canary_word = self.vigil_app.canary_tokens.add(
            prompt="",
            always=False,
            length=16,
            header="<-@!-- {canary} --@!->"
        ).strip("\n")

        self.buffed_server_system_message = ""
        if self.canary_usage_type == "default":
            self.buffed_server_system_message = self.canary_word + "\n" + self.server_system_message
        elif self.canary_usage_type == "modified_no_instruct":
            system_message_words = self.server_system_message.split(".")
            self.buffed_server_system_message = ".".join(system_message_words[:2] + [self.canary_word] + system_message_words[2:])

        
        self.columnname_prompt = "prompt"
        self.columnname_run_canary = "v_run_canary"
        self.columnname_canary_model_name = "v_canary_model_name"
        self.columnname_canary_usage_type = "v_canary_usage_type"
        self.columnname_canary_word = "v_canary_word"
        self.columnname_buffed_system_message = "v_buffed_system_message"
        self.columnname_response_to_canary = "v_response_to_canary"
        self.columnname_is_detected_by_canary = "v_is_detected_by_canary"
             



# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] Vigil Canary error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] Vigil Canary error: invalid program parameters...")
        input("(Press any key)")
    detector = Vigil_Canary(str_input_filepath,
                            str_output_filepath)
    detector.run()
    sys.exit(1)

