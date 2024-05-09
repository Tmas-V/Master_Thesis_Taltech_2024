import sys
sys.path.append("..")
import llm_agent_server as las
import requests, json
################### Setup Rebuff ######################
dict_conf = json.loads(open("conf.json", "r").read())
rebuffSDKServer_address = dict_conf["rebuff"]["server_address"]
rebuffSDKServer_port = dict_conf["rebuff"]["server_port"]
str_rebuffSDKServer_scanEnd = "scan"
str_rebuffSDKServer_addCanaryEnd = "add_canary"
str_rebuffSDKServer_checkCanaryEnd = "check_canary"

class RebuffServerScanRequestObj:
    def __init__(
        self,
        _prompt,
        _check_heuristic,
        _heuristics_threshold,
        _check_vector,
        _vector_threshold,
        _check_llm,
        _model_threshold):

        self.prompt = _prompt
        self.check_heuristic = _check_heuristic
        self.heuristics_threshold = _heuristics_threshold
        self.check_vector = _check_vector
        self.vector_threshold = _vector_threshold
        self.check_llm = _check_llm
        self.model_threshold = _model_threshold
    def json(self):
        return {
            "prompt": self.prompt,
            "check_heuristic": self.check_heuristic,
            "heuristics_threshold": self.heuristics_threshold,
            "check_vector": self.check_vector,
            "vector_threshold": self.vector_threshold,
            "check_llm": self.check_llm,
            "model_threshold": self.model_threshold
        }

def send(host, port, endpoint, obj):
    str_url = "http://{}:{}/{}".format(host, port, endpoint)
    dict_headers = {
            "Content-Type": "application/json",
            "Host": host
    }    
    response = ""
    try:
        response = requests.post(url=str_url, headers=dict_headers, data=json.dumps(obj))
    except:
        print("[-] Error requesting RebuffSDK server.")
        return {}
    try:
        response = response.json()
    except:
        print("[-] Error parsing RebuffSDK server response.")
        response = {}
        pass
    return response

def scan_input_with_Rebuff(_rebuffServerScanRequestObj):
    global rebuffSDKServer_address
    global rebuffSDKServer_port
    global str_rebuffSDKServer_scanEnd

    obj = _rebuffServerScanRequestObj.json()

    response_obj = send(rebuffSDKServer_address,
                        rebuffSDKServer_port,
                        str_rebuffSDKServer_scanEnd,
                        obj)
    if response_obj == {}:
        return {}
    return response_obj

def add_canary_word_with_Rebuff(system_prompt):
    global rebuffSDKServer_address
    global rebuffSDKServer_port
    global str_rebuffSDKServer_addCanaryEnd

    obj = {
        "system_message": system_prompt
    }

    response_obj = send(rebuffSDKServer_address,
                        rebuffSDKServer_port,
                        str_rebuffSDKServer_addCanaryEnd,
                        obj)
    if response_obj == {}:
        canary_word = ""
        return system_prompt, canary_word
    buffed_system_prompt = response_obj["buffed_system_prompt"]
    canary_word = response_obj["canary_word"]
    return buffed_system_prompt, canary_word

def check_canary_word_with_Rebuff(user_input, response, canary_word):
    global rebuffSDKServer_address
    global rebuffSDKServer_port
    global str_rebuffSDKServer_checkCanaryEnd

    obj = {
        "prompt": user_input,
        "response": response,
        "canary_word": canary_word
    }

    response_obj = send(rebuffSDKServer_address,
                        rebuffSDKServer_port,
                        str_rebuffSDKServer_checkCanaryEnd,
                        obj)
    return response_obj


################### Langchain agent definition ######################
class Rebuff_LLMApp(las.BaseLLMApp):
    def __init__(self,
                 _flaskApp,
                 _port,
                 _openai_api_key,
                 _system_message,
                 _agent_docs_dir_path,
                 _useScansOnIntermediateSteps):
        dict_conf = json.loads(open("conf.json", "r").read())
        self.run_heuristics = dict_conf["rebuff"]["input_scanners"]["heuristics"]["use_scanner"]
        self.run_vectordb = dict_conf["rebuff"]["input_scanners"]["vectordb"]["use_scanner"]
        self.run_model = dict_conf["rebuff"]["input_scanners"]["model"]["use_scanner"]
        self.run_canary = dict_conf["rebuff"]["canary_check"]["use_scanner"]

        self.heuristics_threshold = dict_conf["rebuff"]["input_scanners"]["heuristics"]["threshold"]
        self.vector_threshold = dict_conf["rebuff"]["input_scanners"]["vectordb"]["threshold"]
        self.model_threshold = dict_conf["rebuff"]["input_scanners"]["model"]["threshold"]
        
        system_message_to_use = _system_message
        if self.run_canary:
            canary_check_conf = dict_conf["rebuff"]["canary_check"]["usage_type"]
            if canary_check_conf == "default":
                system_message_to_use, self.canary_word = add_canary_word_with_Rebuff(system_message_to_use)
            elif canary_check_conf == "modified_no_instruct":
                _, self.canary_word = add_canary_word_with_Rebuff("")
                system_message_words = system_message_to_use.split(".")
                system_message_to_use = ".".join(system_message_words[:2] + [self.canary_word] + system_message_words[2:])
            elif canary_check_conf == "modified_no_instruct_v2":
                canary_with_delims, self.canary_word = add_canary_word_with_Rebuff("")
                canary_with_delims = canary_with_delims.strip("\n")
                system_message_words = system_message_to_use.split(".")
                system_message_to_use = ".".join(system_message_words[:2] + [canary_with_delims] + system_message_words[2:])
        else:
            self.canary_word = ""
        super().__init__(
            _flaskApp,
            _port,
            _openai_api_key,
            system_message_to_use,
            _agent_docs_dir_path)
        self.useScansOnIntermediateSteps = _useScansOnIntermediateSteps
            
    def construct_json_response(self,
                                user_prompt,
                                intermediate_steps,
                                llm_output):
        response = {}
        ### Rebuff checks ###
        rebuffScanRequestObj = RebuffServerScanRequestObj(user_prompt,
                                                          self.run_heuristics,
                                                          self.heuristics_threshold,
                                                          self.run_vectordb,
                                                          self.vector_threshold,
                                                          self.run_model,
                                                          self.model_threshold)
        Rebuff_input_scan_response = scan_input_with_Rebuff(rebuffScanRequestObj)
        Rebuff_canary_check = {
            "canary_check": False
        }
        if self.run_canary:
            Rebuff_canary_check = check_canary_word_with_Rebuff(user_prompt, llm_output, self.canary_word)
	###
        response["llm_response"] =  llm_output
        response["scan_results"] = {
                "input_scan_results": Rebuff_input_scan_response["input_scan_results"],
                "canary_check": Rebuff_canary_check["canary_check"]
        }
        if self.useScansOnIntermediateSteps:
            response["scan_results"]["intermediate_scans"] = []
            for intermediate_step in intermediate_steps:
                rebuffScanRequestObj = RebuffServerScanRequestObj(intermediate_step,
                                                                  self.run_heuristics,
                                                                  self.heuristics_threshold,
                                                                  self.run_vectordb,
                                                                  self.vector_threshold,
                                                                  self.run_model,
                                                                  self.model_threshold)
                Rebuff_input_scan_response = scan_input_with_Rebuff(rebuffScanRequestObj)
                Rebuff_canary_check = {
                    "canary_check": False
                }
                if self.run_canary:
                    Rebuff_canary_check = check_canary_word_with_Rebuff(user_prompt, intermediate_step, self.canary_word)
                response["scan_results"]["intermediate_scans"] += [{
                    "intermediate_step": intermediate_step,
                    "input_scan_results": Rebuff_input_scan_response["input_scan_results"],
                    "canary_check": Rebuff_canary_check["canary_check"]
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

        log_object["rebuff-scans"] = constructed_json_response["scan_results"]
        log_object["buffed_system_message"] = self.system_message

        return log_object

docs_dirpath = "..\\_docs"
system_message = open("..\\..\\system_message.txt", "r").read()
openaiapikey = open("..\\..\\env.list", "r").read().strip("\n").split("=")[1]
dict_conf = json.loads(open("conf.json", "r").read())
port = dict_conf["port"]
server_type = dict_conf["server_type"]
scaIntermediateSteps = dict_conf["scan_intermediate_agent_steps"]

las.llmApp = Rebuff_LLMApp(las.app,
                        port,
                        openaiapikey,
                        system_message,
                        docs_dirpath,
                        scaIntermediateSteps
)

if __name__ == "__main__":
        las.llmApp.Run(server_type)

