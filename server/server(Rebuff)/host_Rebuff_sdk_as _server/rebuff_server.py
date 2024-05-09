from datetime import datetime
import os

from flask import Flask, render_template, request, json
################### Setup Rebuff ######################
from rebuff import RebuffSdk, RebuffDetectionResponse
from rebuff.detect_pi_openai import (
    call_openai_to_detect_pi,
    render_prompt_for_pi_detection,
)
openaiapikey = open("env.list", "r").read().strip("\n").split("=")[1]
pineconeapikey = open("pinecone.env", "r").read().strip("\n").split("=")[1]
pineconeindexname = "rebuff-db"
openaimodel = "gpt-3.5-turbo"
rebuff = RebuffSdk(    
    openaiapikey,
    pineconeapikey,    
    pineconeindexname,
    openaimodel # openai_model is optional, defaults to "gpt-3.5-turbo"
)

################## Server setup #########################
str_host_ip = "192.168.247.162"
str_host_port = 5555

#########################################################

def log_err(log_objects, logfile_path):
	file = ""
	if not os.path.exists(logfile_path):
		open(logfile_path, "x")
	file = open(logfile_path, "a")
	for i in range(0, len(log_objects)):
		log_object = log_objects[i]
		log_object["time"] = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
		str_content = json.dumps(log_object, indent = "\t") + "\n"
		file.write(str_content)
	file.close()

def scan_input_with_Rebuff(_prompt,
			_check_heuristic,
			_heuristics_threshold,
			_check_vector,
			_vector_threshold,
			_check_llm,
			_llm_threshold):
	global rebuff
	global openaiapikey, openaimodel
	scanResults = {}
	try:
		scanResults = rebuff.detect_injection(_prompt,
			check_heuristic = _check_heuristic,
			max_heuristic_score = _heuristics_threshold,
			check_vector = _check_vector,
			max_vector_score = _vector_threshold,
			check_llm = _check_llm,
			max_model_score = _llm_threshold)
		rebuff_openai_prompt = render_prompt_for_pi_detection(_prompt)
		rebuff_openai_response = call_openai_to_detect_pi(
			rebuff_openai_prompt, openaimodel, openaiapikey
		)
		model_response = str(rebuff_openai_response.get("completion", 0))
		scanResults.openai_score = float(model_response)
		scanResults.injection_detected = (scanResults.openai_score > scanResults.max_model_score)
		rebuff_err_log_obj = {
			"prompt": _prompt,
			"response_to_rendered_input": model_response
		}
		print("Model check response: {}".format(model_response))
		log_err([rebuff_err_log_obj], "rebuff.log")
	except:
		scanResults = rebuff.detect_injection(_prompt,
			check_heuristic = _check_heuristic,
			max_heuristic_score = _heuristics_threshold,
			check_vector = _check_vector,
			max_vector_score = _vector_threshold,
			check_llm = False,
			max_model_score = _llm_threshold)
		scanResults.openai_score = 0.0

		rebuff_openai_prompt = render_prompt_for_pi_detection(_prompt)
		rebuff_openai_response = call_openai_to_detect_pi(
			rebuff_openai_prompt, openaimodel, openaiapikey
		)
		rebuff_err_log_obj = {
			"prompt": _prompt,
			"response_to_rendered_input": str(rebuff_openai_response.get("completion", 0))
		}
		log_err([rebuff_err_log_obj], "rebuff_modelcheck_err.log")

	print("Vector store score: {}".format(scanResults.vector_score))
	return scanResults

def add_canary_word_with_Rebuff(system_prompt):
        global rebuff
        buffed_system_prompt, canary_word = rebuff.add_canary_word(system_prompt)
        return buffed_system_prompt, canary_word
def check_canary_word_with_Rebuff(user_input, response, canary_word):
	global rebuff
	if canary_word == "":
		return False
	return rebuff.is_canary_word_leaked(user_input, response, canary_word, log_outcome = False)

app = Flask(__name__)

@app.route("/")
def index():
	return "Rebuff server."

@app.route("/scan", methods=["POST"])
def return_scan_results():
	userPrompt = request.json["prompt"]
	check_heuristic = request.json["check_heuristic"]
	heuristics_threshold = request.json["heuristics_threshold"]
	check_vector = request.json["check_vector"]
	vector_threshold = request.json["vector_threshold"]
	check_llm = request.json["check_llm"]
	model_threshold = request.json["model_threshold"]

	if check_heuristic or check_vector or check_llm:
		Rebuff_input_scan_response = scan_input_with_Rebuff(userPrompt,
			check_heuristic,
			heuristics_threshold,
			check_vector,
			vector_threshold,
			check_llm,
			model_threshold)
		return {"input_scan_results": {
			"heuristic_score": Rebuff_input_scan_response.heuristic_score,
			"max_heuristic_score": Rebuff_input_scan_response.max_heuristic_score,
		        
			"openai_score": Rebuff_input_scan_response.openai_score,
		        "max_model_score": Rebuff_input_scan_response.max_model_score,
		                
		        "vector_score": Rebuff_input_scan_response.vector_score,
		        "max_vector_score": Rebuff_input_scan_response.max_vector_score,

		        "injection_detected": Rebuff_input_scan_response.injection_detected
		                
		}}
	else:
		return {"input_scan_results": {
			"heuristic_score": 0.0,
			"max_heuristic_score": 1.0,
		        
			"openai_score": 0.0,
		        "max_model_score": 1.0,
		                
		        "vector_score": 0.0,
		        "max_vector_score": 1.0,

		        "injection_detected": False
		                
		}}	


@app.route("/add_canary", methods=["POST"])
def return_add_canary():
	system_message = request.json['system_message']
	buffed_system_message, canary_word = add_canary_word_with_Rebuff(system_message)
	return {
		"buffed_system_prompt" : buffed_system_message,
		"canary_word" : canary_word
	}

@app.route("/check_canary", methods=["POST"])
def return_check_canary():
	userPrompt = request.json['prompt']
	llmresponse = request.json['response']
	canary_word = request.json['canary_word']
	return {
		"canary_check" : check_canary_word_with_Rebuff(userPrompt, llmresponse, canary_word)
	}

    
if __name__ == "__main__":
	app.run(host = str_host_ip, port = str_host_port)

        

