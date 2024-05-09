################### Setup Rebuff ######################
from rebuff import RebuffSdk
openaiapikey = open("..\env.list", "r").read().strip("\n").split("=")[1]
pineconeapikey = open("pinecone.env", "r").read().strip("\n").split("=")[1]
rebuff = RebuffSdk(    
    openaiapikey,
    pineconeapikey,    
    "rebuff-db",
    "gpt-3.5-turbo" # openai_model is optional, defaults to "gpt-3.5-turbo"
)
canary_word = ""

def scan_input_with_Rebuff(prompt):
        global rebuff
        return rebuff.detect_injection(prompt)
def add_canary_word_with_Rebuff(system_prompt):
        global rebuff, canary_word
        buffed_system_prompt, canary_word = rebuff.add_canary_word(system_prompt)
        return buffed_system_prompt
def check_canary_word_with_Rebuff(user_input, response):
        global rebuff, canary_word
        return rebuff.is_canary_word_leaked(user_input, response, canary_word)


def cli():
    print("Enter user prompt. Double press 'Enter' to clear conversation memory. Double press 'Enter' again to quit.")
    print("------------------------------")
    prompt = ""
    int_hasMemory = 1
    while True:
        prompt = ""
        while True:
            line = input("prompt>")
            if len(line) == 0:
                break
            prompt += line + "\n"
        if len(prompt) != 0:
            int_hasMemory = 1
            print("-------Prompting...-----------")
            Rebuff_input_scan_response = scan_input_with_Rebuff(prompt)
            scan_results = {
                "heuristic_score": Rebuff_input_scan_response.heuristic_score,
                "max_heuristic_score": Rebuff_input_scan_response.max_heuristic_score,        
                "openai_score": Rebuff_input_scan_response.openai_score,
                "max_model_score": Rebuff_input_scan_response.max_model_score,        
                "vector_score": Rebuff_input_scan_response.vector_score,
                "max_vector_score": Rebuff_input_scan_response.max_vector_score,
                "injection_detected": Rebuff_input_scan_response.injection_detected
                        
            }
            print('{')
            for key in scan_results.keys():
                print("\t{} : {}".format(key, scan_results[key]))
            print('}')
            print("------------------------------")
        else:
            break



cli()
