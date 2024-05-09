import sys
sys.path.append("..")
import pi_attacks as pi_att
from llm_agent_client import *


def retrieve_IsDetected(all_column_values):
    is_valid_value = all_column_values["scan_results"]["input_scan_results"]["transformer"]["is_valid"]
    return not is_valid_value

def retrieve_DetectionScore(all_column_values):
    risk_score_value = all_column_values["scan_results"]["input_scan_results"]["transformer"]["risk_score"]
    return round(risk_score_value, 9)

def test_IsDetected(all_column_values):
    is_detected_value = retrieve_IsDetected(all_column_values)
    return is_detected_value == "True"

def Benign_Experiment_with_LLMGuard(_str_promptsamples_source_filepath,
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
                              "is_detected",
                              "detection_score"
                          ],
                          {
                              "is_detected": lambda all_column_values : retrieve_IsDetected(all_column_values),
                              "detection_score": lambda all_column_values : retrieve_DetectionScore(all_column_values)
                          },
                          {
                          },
                          {
                          }
    )

def PromptLeak_Experiment_with_LLMGuard(_str_promptsamples_source_filepath,
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
                                     "is_detected",
                                     "detection_score"
                                 ],
                                 {
                                     "is_detected": lambda all_column_values : retrieve_IsDetected(all_column_values),
                                     "detection_score": lambda all_column_values : retrieve_DetectionScore(all_column_values)
                                 },
                                 {
                                 },
                                 {
                                 }
    )


pi_objective_to_experiment = {
    "benign": Benign_Experiment_with_LLMGuard,
    "promptleak": PromptLeak_Experiment_with_LLMGuard
}



#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Bare.parquet'

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_IgnoreJailbreak.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_PromptLeak_IgnoreJailbreak.parquet'
#str_detected_samples_parquet_filename = "LLM-Guard_PromptLeak_IgnoreJailbreak(Detected).parquet"
#str_undetected_samples_parquet_filename = "LLM-Guard_PromptLeak_IgnoreJailbreak(Undetected).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Leet.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_PromptLeak_Leet.parquet'
#str_detected_samples_filename = "LLM-Guard_PromptLeak_Leet(Detected).parquet"
#str_undetected_samples_filename = "LLM-Guard_PromptLeak_Leet(Undetected).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Leet.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_PromptLeak_TEST.parquet'
#str_detected_samples_filename = "LLM-Guard_PromptLeak_TEST(Detected).parquet"
#str_undetected_samples_filename = "LLM-Guard_PromptLeak_TEST(Undetected).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Leet.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_PromptLeak_TEST.parquet'
#str_detected_samples_filename = "LLM-Guard_PromptLeak_TEST(Detected).parquet"
#str_undetected_samples_filename = "LLM-Guard_PromptLeak_TEST(Undetected).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_PrefixInjection.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_PromptLeak_PrefixInjection.parquet'
#str_detected_samples_filename = "LLM-Guard_PromptLeak_PrefixInjection(Detected).parquet"
#str_undetected_samples_filename = "LLM-Guard_PromptLeak_PrefixInjection(Undetected).parquet"

#str_samples_parquet_filename = '..\\_BenignSamples\\BenignSamples.parquet'
#str_promptleak_allresults_filename = 'LLM-Guard_BenignSamples.parquet'
#str_detected_samples_filename = "LLM-Guard_BenignSamples(Detected).parquet"
#str_undetected_samples_filename = "LLM-Guard_BenignSamples(Undetected).parquet"



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



