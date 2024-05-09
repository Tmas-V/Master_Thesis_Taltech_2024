import sys
sys.path.append("..")
import pi_attacks as pi_att
from llm_agent_client import *

######################################### PromptLeak experiment-related functions #################################################
def retrieve_HeuristicsScore(all_column_values):
    return all_column_values["scan_results"]["input_scan_results"]["heuristic_score"]

def retrieve_IsDetectedByHeuristics(all_column_values):
    heur_matches = all_column_values["scan_results"]["input_scan_results"]["heuristic_score"]
    max_heur_matches = all_column_values["scan_results"]["input_scan_results"]["max_heuristic_score"]
    return heur_matches > max_heur_matches

def retrieve_OpenAIScore(all_column_values):
    return all_column_values["scan_results"]["input_scan_results"]["openai_score"]

def retrieve_IsDetectedByOpenAI(all_column_values):
    openai_matches = all_column_values["scan_results"]["input_scan_results"]["openai_score"]
    max_openai_matches = all_column_values["scan_results"]["input_scan_results"]["max_model_score"]
    return openai_matches > max_openai_matches

def retrieve_VectorDBScore(all_column_values):
    return all_column_values["scan_results"]["input_scan_results"]["vector_score"]

def retrieve_IsDetectedByVectorDB(all_column_values):
    vectordb_matches = all_column_values["scan_results"]["input_scan_results"]["vector_score"]
    max_vectordb_matches = all_column_values["scan_results"]["input_scan_results"]["max_vector_score"]
    return vectordb_matches > max_vectordb_matches

def retrieve_IsDetectedByCanary(all_column_values):
    is_detected_by_canary = all_column_values["scan_results"]["canary_check"]
    return is_detected_by_canary 

def retrieve_IsDetected(all_column_values):
    is_detected = all_column_values["scan_results"]["input_scan_results"]["injection_detected"]
    return is_detected


def test_IsDetectedByHeuristics(all_column_values):
    return retrieve_IsDetectedByHeuristics(all_column_values)

def test_IsDetectedByOpenAI(all_column_values):
    return retrieve_IsDetectedByOpenAI(all_column_values)

def test_IsDetectedByVectorDB(all_column_values):
    return retrieve_IsDetectedByVectorDB(all_column_values)

def test_IsDetectedByCanary(all_column_values):
    return retrieve_IsDetectedByCanary(all_column_values)

def test_IsDetectedByAny(all_column_values):
    return retrieve_IsDetected(all_column_values)



def Benign_Experiment_with_Rebuff(_str_promptsamples_source_filepath,
                      _str_results_dirpath,
                      _str_results_filename):
    dict_conf = json.loads(open(".\\conf.json", "r").read())
    port = dict_conf["port"]
    client_type = dict_conf["client_type"]

    benign_samples = parquet.read_pandas(_str_promptsamples_source_filepath,
                                             columns=["prompt"]).to_pandas()["prompt"].tolist()
    
    pi_att.Base_Experiment(port,
                          benign_samples,
                          _str_results_dirpath,
                          _str_results_filename,
                          [
                              "heuristics_score",
                              "is_detected_by_heuristics",
                              "model_score",
                              "is_detected_by_openai",
                              "vector_score",
                              "is_detected_by_vectordb",
                              "is_detected_by_canary",
                              "is_detected"
                          ],
                          {
                              "heuristics_score": lambda all_column_values : retrieve_HeuristicsScore(all_column_values),
                              "is_detected_by_heuristics": lambda all_column_values : retrieve_IsDetectedByHeuristics(all_column_values),
                              "model_score": lambda all_column_values : retrieve_OpenAIScore(all_column_values),
                              "is_detected_by_openai": lambda all_column_values : retrieve_IsDetectedByOpenAI(all_column_values),
                              "vector_score": lambda all_column_values : retrieve_VectorDBScore(all_column_values),
                              "is_detected_by_vectordb": lambda all_column_values : retrieve_IsDetectedByVectorDB(all_column_values),
                              "is_detected_by_canary": lambda all_column_values : retrieve_IsDetectedByCanary(all_column_values),
                              "is_detected": lambda all_column_values : retrieve_IsDetected(all_column_values)
                          },
                          {
                          },
                          {
                          }
    )


def PromptLeak_Experiment_with_Rebuff(_str_promptsamples_source_filepath,
                                            _str_results_dirpath,
                                            _str_results_filename):
    dict_conf = json.loads(open(".\\conf.json", "r").read())
    port = dict_conf["port"]
    client_type = dict_conf["client_type"]
    system_message = open("..\\..\\system_message.txt", "r").read()

    promptleak_samples = parquet.read_pandas(_str_promptsamples_source_filepath,
                                             columns=["prompt"]).to_pandas()["prompt"].tolist()
    
    pi_att.Promptleak_Experiment(port,
                                 system_message,
                                 promptleak_samples,
                                 _str_results_dirpath,
                                 _str_results_filename,
                                 [
                                    "heuristics_score",
                                    "is_detected_by_heuristics",
                                    "model_score",
                                    "is_detected_by_openai",
                                    "vector_score",
                                    "is_detected_by_vectordb",
                                    "is_detected_by_canary",
                                    "is_detected"
                                  ],
                                  {
                                      "heuristics_score": lambda all_column_values : retrieve_HeuristicsScore(all_column_values),
                                      "is_detected_by_heuristics": lambda all_column_values : retrieve_IsDetectedByHeuristics(all_column_values),
                                      "model_score": lambda all_column_values : retrieve_OpenAIScore(all_column_values),
                                      "is_detected_by_openai": lambda all_column_values : retrieve_IsDetectedByOpenAI(all_column_values),
                                      "vector_score": lambda all_column_values : retrieve_VectorDBScore(all_column_values),
                                      "is_detected_by_vectordb": lambda all_column_values : retrieve_IsDetectedByVectorDB(all_column_values),
                                      "is_detected_by_canary": lambda all_column_values : retrieve_IsDetectedByCanary(all_column_values),
                                      "is_detected": lambda all_column_values : retrieve_IsDetected(all_column_values)
                                  },
                                  {
                                  },
                                  {
                                  }
    )


pi_objective_to_experiment = {
    "benign": Benign_Experiment_with_Rebuff,
    "promptleak": PromptLeak_Experiment_with_Rebuff
}



#str_samples_parquet_filename = '..\\_BenignSamples\\BenignSamples.parquet'
#str_promptleak_allresults_filename = 'Rebuff_BenignSamples.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_BenignSamples(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_BenignSamples(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_BenignSamples(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_BenignSamples(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_BenignSamples(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Bare.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_Bare.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_Bare(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_Bare(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_Bare(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_Bare(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_Bare(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_IgnoreJailbreak.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_IgnoreJailbreak.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_IgnoreJailbreak(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_IgnoreJailbreak(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_IgnoreJailbreak(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_IgnoreJailbreak(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_IgnoreJailbreak(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Leet.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_Leet.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_Leet(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_Leet(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_Leet(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_Leet(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_Leet(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Ignore+Leet.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_Ignore+Leet.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_Ignore+Leet(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_Ignore+Leet(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_Ignore+Leet(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_Ignore+Leet(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_Ignore+Leet(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_PrefixInjection.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_PrefixInjection.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_PrefixInjection(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_PrefixInjection(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_PrefixInjection(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_PrefixInjection(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_PrefixInjection(Detected by Any).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_RepeatChars.parquet'
#str_promptleak_allresults_filename = 'Rebuff_PromptLeak_RepeatChars.parquet'
#str_detectedHeuristicssamples_filename = "Rebuff_PromptLeak_RepeatChars(Detected by Heuristics).parquet"
#str_detectedOpenAIsamples_filename = "Rebuff_PromptLeak_RepeatChars(Detected by OpenAI).parquet"
#str_detectedVectorsamples_filename = "Rebuff_PromptLeak_RepeatChars(Detected by Vector).parquet"
#str_detectedCanarysamples_filename = "Rebuff_PromptLeak_RepeatChars(Detected by Canary).parquet"
#str_detectedDetectedsamples_filename = "Rebuff_PromptLeak_RepeatChars(Detected by Any).parquet"


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("[!] Error: client received incorrect number of parameters")
        quit(0)
    pi_att.sample_retry_count = 1
    pi_att.retest_promptleaks = False
    str_pi_objective = sys.argv[1]
    str_promptsamples_source_filepath = sys.argv[2]
    str_results_save_dirpath = sys.argv[3]
    str_promptsamples_successful_filename = sys.argv[4]

    pi_objective_to_experiment[str_pi_objective](str_promptsamples_source_filepath,
                                                 str_results_save_dirpath,
                                                 str_promptsamples_successful_filename)




