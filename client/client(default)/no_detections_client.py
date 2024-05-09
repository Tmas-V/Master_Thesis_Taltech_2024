import sys, json, time
sys.path.append("..")
import pi_attacks as pi_att
from llm_agent_client import *

def Benign_Experiment(_str_promptsamples_source_filepath,
                      _str_results_dirpath,
                      _str_results_filename):
    dict_conf = json.loads(open(".\\conf.json", "r").read())
    port = dict_conf["port"]
    client_type = dict_conf["client_type"]

    benign_samples = parquet.read_pandas(_str_promptsamples_source_filepath,
                                             columns=["prompt"]).to_pandas()["prompt"].tolist()
    
    pi_att.Base_Experiment(port,
                          promptleak_samples,
                          _str_results_dirpath,
                          _str_results_filename,
                          [],
                          {
                          },
                          {
                          },
                          {
                          }
    )

def PromptLeak_Experiment_with_NoProtection(_str_promptsamples_source_filepath,
                                            _str_results_dirpath,
                                            _str_results_filename):
    dict_conf = json.loads(open(".\\conf.json", "r").read())
    port = dict_conf["port"]
    client_type = dict_conf["client_type"]
    system_message = open("..\\..\\system_message.txt", "r").read()

    promptleak_samples = parquet.read_pandas(_str_promptsamples_source_filepath,
                                             columns=["prompt"]).to_pandas()["prompt"].tolist()
    _str_results_all_filename = "(unfiltered).".join(_str_results_filename.split("."))
    
    pi_att.Promptleak_Experiment(port,
                          system_message,
                          promptleak_samples,
                          _str_results_dirpath,
                          _str_results_all_filename,
                          [],
                          {
                          },
                          {
                              "successful_prompts" : _str_results_filename
                          },
                          {
                              "successful_prompts" : lambda all_column_values : (all_column_values["success"] == 1)
                          }
    )


pi_objective_to_experiment = {
    "benign": Benign_Experiment,
    "promptleak": PromptLeak_Experiment_with_NoProtection
}

#cli(5003, with_memory=False)
#quit()

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Bare.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Bare(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_RepeatChars.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_RepeatChars(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_PrefixInjection.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_PrefixInjection(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_IgnoreJailbreak.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_IgnoreJailbreak(Unfiltered).parquet'

######str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_RefusalSuppression.parquet'
######str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_RefusalSuppression(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Bare.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Bare(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Ignore+Leet.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Ignore+Leet(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Base64.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Base64(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_ROT13.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_ROT13(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_PayloadSplit.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_PayloadSplit(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Ignore+Base64.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Ignore+Base64(Unfiltered).parquet'

#str_promptleak_filtered_filename = 'NoProtection_PromptLeaks_Ignore+PayloadSplit.parquet'
#str_promptleak_unfiltered_filename = 'NoProtection_PromptLeaks_Ignore+PayloadSplit(Unfiltered).parquet'

#str_results_save_dirpath = 'PromptLeak experiment\\'

#promptleak_samples = ObfuscateLeet(prompt_samples)
#promptleak_samples = Apply_IgnoreJailbreak(prompt_samples)
#promptleak_samples = ObfuscateBASE64(promptleak_samples)
#promptleak_samples = ObfuscateROT13(promptleak_samples)
#promptleak_samples = ObfuscatePayloadSplit(promptleak_samples)





if __name__ == "__main__":
    #print(sys.argv)

    #if len(sys.argv) != 5:
    #    print("[!] Error: client received incorrect number of parameters")
    #    quit(0)
    pi_att.sample_retry_count = 2
    pi_att.retest_promptleaks = False
    str_pi_objective = sys.argv[1]
    str_promptsamples_source_filepath = sys.argv[2]
    str_results_save_dirpath = sys.argv[3]
    str_promptsamples_successful_filename = sys.argv[4]

    pi_objective_to_experiment[str_pi_objective](str_promptsamples_source_filepath,
                                                 str_results_save_dirpath,
                                                 str_promptsamples_successful_filename)

