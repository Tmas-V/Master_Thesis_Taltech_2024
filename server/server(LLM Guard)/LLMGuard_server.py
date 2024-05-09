import sys, json
sys.path.append("..")
import llm_agent_server as las
################### Setup LLM-Guard ######################
from llm_guard.input_scanners import PromptInjection
from llm_guard.input_scanners.prompt_injection import MatchType
##########################################################




class LLMGuard_LLMApp(las.BaseLLMApp):
    def __init__(self,
                 _flaskApp,
                 _port,
                 _openai_api_key,
                 _system_message,
                 _agent_docs_dir_path,
                 _useScansOnIntermediateSteps):
            super().__init__(
                 _flaskApp,
                 _port,
                 _openai_api_key,
                 _system_message,
                 _agent_docs_dir_path)
            self.useScansOnIntermediateSteps = _useScansOnIntermediateSteps
            dict_conf = json.loads(open("conf.json", "r").read())
            llmguard_threshold = dict_conf["llm guard"]["input_scanners"]["transformer"]["threshold"]
            self.scanner = PromptInjection(threshold=llmguard_threshold, match_type=MatchType.FULL)
    def construct_json_response(self,
                                user_prompt,
                                intermediate_steps,
                                llm_output):
        sanitized_prompt, is_valid, risk_score = self.scanner.scan(user_prompt)
        response = {}
        response["llm_response"] =  llm_output
        response["scan_results"] = {
            "input_scan_results" : {
                "transformer": {
                    "is_valid": is_valid,
                    "risk_score": round(risk_score, 9)
                }
            }
        }
        if self.useScansOnIntermediateSteps:
                response["scan_results"]["intermediate_scans"] = []
                for intermediate_step in intermediate_steps:
                        sanitized_prompt, is_valid, risk_score = scanner.scan(intermediate_step)
                        response["scan_results"]["intermediate_scans"] += [
                        {
                            "intermediate_step": intermediate_step,
                            "input_scan_results":{
                                "transformer": {
                                    "is_valid" : is_valid,
                                    "risk_score" : round(risk_score, 9)
                                }
                            }
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

        log_object["llm-guard-scans"] = constructed_json_response["scan_results"]

        return log_object


docs_dirpath = "..\\_docs"
system_message = open("..\\..\\system_message.txt", "r").read()
openaiapikey = open("..\\..\\env.list", "r").read().strip("\n").split("=")[1]
dict_conf = json.loads(open("conf.json", "r").read())
port = dict_conf["port"]
server_type = dict_conf["server_type"]
scaIntermediateSteps = dict_conf["scan_intermediate_agent_steps"]

las.llmApp = LLMGuard_LLMApp(las.app,
                        port,
                        openaiapikey,
                        system_message,
                        docs_dirpath,
                        scaIntermediateSteps
)

if __name__ == "__main__":
        las.llmApp.Run(server_type)






        
