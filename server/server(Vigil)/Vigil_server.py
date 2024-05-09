import sys, json
sys.path.append("..")
import llm_agent_server as las
################### Vigil setup ######################
from vigil.vigil import Vigil
##########################################################


def scan_input_with_Vigil(prompt, vigil_app):
        return vigil_app.input_scanner.perform_scan(
                prompt
        )

def add_canary_word_with_Vigil(system_prompt,
                               vigil_app,
                               use_always = False,
                               canary_word_len = 16,
                               canary_word_header = "<-@!-- {canary} --@!->"):
        return vigil_app.canary_tokens.add(
                prompt=system_prompt,
                always=use_always,
                length=canary_word_len,
                header=canary_word_header
        )

def check_canary_word_with_Vigil(response, vigil_app):
        return vigil_app.canary_tokens.check(response)
##########################################################




class Vigil_LLMApp(las.BaseLLMApp):
        def __init__(self,
                     _flaskApp,
                     _port,
                     _openai_api_key,
                     _system_message,
                     _agent_docs_dir_path,
                     _useScansOnIntermediateSteps):
                dict_conf = json.loads(open("conf.json", "r").read())
                self.run_yara = dict_conf["vigil"]["input_scanners"]["yara"]["use_scanner"]
                self.run_transformer = dict_conf["vigil"]["input_scanners"]["transformer"]["use_scanner"]
                self.run_vectordb = dict_conf["vigil"]["input_scanners"]["vectordb"]["use_scanner"]
                self.run_canary = dict_conf["vigil"]["canary_check"]["use_scanner"]
                
                self.vigil_conf_template_filename = "vigil_server_conf_template.conf"
                self.vigil_conf_filename = "vigil_server_conf.conf"
                self.vigil_app = self.configure_Vigil(_openai_api_key)

                system_message_to_use = _system_message
                if self.run_canary:
                        canary_check_conf = dict_conf["vigil"]["canary_check"]["usage_type"]
                        if canary_check_conf == "default":
                                system_message_to_use = add_canary_word_with_Vigil(system_message_to_use,
                                                                                   self.vigil_app)
                        elif canary_check_conf == "modified_no_instruct":
                                canary_word = add_canary_word_with_Vigil("",
                                                                         self.vigil_app).strip("\n")
                                system_message_words = system_message_to_use.split(".")
                                system_message_to_use = ".".join(system_message_words[:2] + [canary_word] + system_message_words[2:])
                super().__init__(
                        _flaskApp,
                        _port,
                        _openai_api_key,
                        system_message_to_use,
                        _agent_docs_dir_path)
                self.useScansOnIntermediateSteps = _useScansOnIntermediateSteps

        def configure_Vigil(self,
                            _openai_api_key):
                dict_conf = json.loads(open("conf.json", "r").read())
                str_vigil_template_conf = open(self.vigil_conf_template_filename, "r").read()
                str_activated_input_scanners = ""
                if self.run_yara:
                        if str_activated_input_scanners != "":
                                str_activated_input_scanners += ","
                        str_activated_input_scanners += "yara"
                if self.run_transformer:
                        if str_activated_input_scanners != "":
                                str_activated_input_scanners += ","
                        str_activated_input_scanners += "transformer"
                if self.run_vectordb:
                        if str_activated_input_scanners != "":
                                str_activated_input_scanners += ","
                        str_activated_input_scanners += "vectordb"

                str_vigil_conf = str_vigil_template_conf.format(
                        openai_api_key = _openai_api_key,
                        vigil_vdb_dirpath = dict_conf["vigil"]["input_scanners"]["vectordb"]["vdb_dirpath"],
                        input_scanners = str_activated_input_scanners,
                        yara_dirpath = dict_conf["vigil"]["input_scanners"]["yara"]["yara_rules_dirpath"],
                        vdb_threshold = dict_conf["vigil"]["input_scanners"]["vectordb"]["threshold"],
                        transformer_model = dict_conf["vigil"]["input_scanners"]["transformer"]["model"],
                        transformer_threshold = dict_conf["vigil"]["input_scanners"]["transformer"]["threshold"],
                )
                open(self.vigil_conf_filename, "w").write(str_vigil_conf)
                #return Vigil.from_config('vigil-llm-0.10.3-alpha\\conf\\server.conf')
                return Vigil.from_config(self.vigil_conf_filename)

        def construct_json_response(self,
                                    user_prompt,
                                    intermediate_steps,
                                    llm_output):
                ### Vigil checks ###
                Vigil_input_scan_response = scan_input_with_Vigil(user_prompt, self.vigil_app)
                
                Vigil_canary_check = False
                if self.run_canary:
                        Vigil_canary_check = check_canary_word_with_Vigil(llm_output, self.vigil_app)
                ###
                response = {}
                response["llm_response"] =  llm_output
                response["scan_results"] = {
                        "input_scan_results": Vigil_input_scan_response,
                        "canary_check": Vigil_canary_check
                }
                if self.useScansOnIntermediateSteps:
                        response["scan_results"]["intermediate_scans"] = []
                        for intermediate_step in intermediate_steps:
                                Vigil_input_scan_response = scan_input_with_Vigil(intermediate_step, self.vigil_app)
                                Vigil_canary_check = False
                                if self.run_canary:
                                        Vigil_canary_check = check_canary_word_with_Vigil(intermediate_step, self.vigil_app)
                                response["scan_results"]["intermediate_scans"] += [{
                                        "intermediate_step": intermediate_step,
                                        "input_scan_results": Vigil_input_scan_response,
                                        "canary_check": Vigil_canary_check
                                }]
                return response

        def construct_json_log(self,
                               user_prompt,
                               intermediate_steps,
                               constructed_json_response):
                log_object = self.log_obj
                log_object["prompt"] = user_prompt
                log_object["intermediate_steps"] = intermediate_steps
                log_object["response"] = constructed_json_response["llm_response"]

                log_object["vigil-scans"] = constructed_json_response["scan_results"]
                log_object["buffed_system_message"] = self.system_message
                return log_object


docs_dirpath = "..\\_docs"
system_message = open("..\\..\\system_message.txt", "r").read()
openaiapikey = open("..\\..\\env.list", "r").read().strip("\n").split("=")[1]
dict_conf = json.loads(open("conf.json", "r").read())
port = dict_conf["port"]
server_type = dict_conf["server_type"]
scaIntermediateSteps = dict_conf["scan_intermediate_agent_steps"]

las.llmApp = Vigil_LLMApp(las.app,
                        port,
                        openaiapikey,
                        system_message,
                        docs_dirpath,
                        scaIntermediateSteps
)

if __name__ == "__main__":
        las.llmApp.Run(server_type)

        
