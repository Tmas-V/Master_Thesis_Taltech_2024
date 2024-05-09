import sys
sys.path.append("..")
import pi_attacks as pi_att
from llm_agent_client import *

######################################### PromptLeak experiment-related functions #################################################
def retrieve_IsDetectedByYara(all_column_values):
    try:
        yara_matches = all_column_values["scan_results"]["input_scan_results"]["results"]["scanner:yara"]["matches"]
        return len(yara_matches) > 0
    except:
        return False

def retrieve_IsDetectedByTransformer(all_column_values):
    try:
        transformer_matches = all_column_values["scan_results"]["input_scan_results"]["results"]["scanner:transformer"]["matches"]
        return len(transformer_matches) > 0
    except:
        return False

def retrieve_TransformerScore(all_column_values):
    try:
        transformer_matches = all_column_values["scan_results"]["input_scan_results"]["results"]["scanner:transformer"]["matches"]
        if len(transformer_matches) <= 0:
            return 0.0
        score = transformer_matches[0]["score"]
        return round(score, 9)
    except:
        return 0.0

def retrieve_IsDetectedByVectorDB(all_column_values):
    try:
        vectordb_matches = all_column_values["scan_results"]["input_scan_results"]["results"]["scanner:vectordb"]["matches"]
        return len(vectordb_matches) > 0
    except:
        return False

def retrieve_VectorDBScore(all_column_values):
    try:
        vectordb_matches = all_column_values["scan_results"]["input_scan_results"]["results"]["scanner:vectordb"]["matches"]
        if len(vectordb_matches) <= 0:
            return 0.0
        score = vectordb_matches[0]["distance"]
        return round(score, 9)
    except:
        return 0.0

def retrieve_IsDetectedByCanary(all_column_values):
    try:
        is_detected_by_canary = all_column_values["scan_results"]["canary_check"]
        return is_detected_by_canary
    except:
        return False



def test_IsDetectedByYara(all_column_values):
    return retrieve_IsDetectedByYara(all_column_values)

def test_IsDetectedByTransformer(all_column_values):
    return retrieve_IsDetectedByTransformer(all_column_values)

def test_IsDetectedByVectorDB(all_column_values):
    return retrieve_IsDetectedByVectorDB(all_column_values)

def test_IsDetectedByCanary(all_column_values):
    return retrieve_IsDetectedByCanary(all_column_values)


def Benign_Experiment_with_Vigil(_str_promptsamples_source_filepath,
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
                              "is_detected_by_yara",
                              "is_detected_by_transformer",
                              "transformer_score",
                              "is_detected_by_vectordb",
                              "vectordb_score",
                              "is_detected_by_canary"
                          ],
                          {
                              "is_detected_by_yara": lambda all_column_values : retrieve_IsDetectedByYara(all_column_values),
                              "is_detected_by_transformer": lambda all_column_values : retrieve_IsDetectedByTransformer(all_column_values),
                              "transformer_score": lambda all_column_values : retrieve_TransformerScore(all_column_values),
                              "is_detected_by_vectordb": lambda all_column_values : retrieve_IsDetectedByVectorDB(all_column_values),
                              "vectordb_score": lambda all_column_values : retrieve_VectorDBScore(all_column_values),
                              "is_detected_by_canary": lambda all_column_values : retrieve_IsDetectedByCanary(all_column_values)
                          },
                          {
                          },
                          {
                          }
    )

def PromptLeak_Experiment_with_Vigil(_str_promptsamples_source_filepath,
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
                                     "is_detected_by_yara",
                                     "is_detected_by_transformer",
                                     "transformer_score",
                                     "is_detected_by_vectordb",
                                     "vectordb_score",
                                     "is_detected_by_canary"
                                 ],
                                 {
                                     "is_detected_by_yara": lambda all_column_values : retrieve_IsDetectedByYara(all_column_values),
                                     "is_detected_by_transformer": lambda all_column_values : retrieve_IsDetectedByTransformer(all_column_values),
                                     "transformer_score": lambda all_column_values : retrieve_TransformerScore(all_column_values),
                                     "is_detected_by_vectordb": lambda all_column_values : retrieve_IsDetectedByVectorDB(all_column_values),
                                     "vectordb_score": lambda all_column_values : retrieve_VectorDBScore(all_column_values),
                                     "is_detected_by_canary": lambda all_column_values : retrieve_IsDetectedByCanary(all_column_values)
                                  },
                                  {
                                  },
                                  {
                                  }
    )


pi_objective_to_experiment = {
    "benign": Benign_Experiment_with_Vigil,
    "promptleak": PromptLeak_Experiment_with_Vigil
}




#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Bare.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeak_Bare.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeak_Bare(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeak_Bare(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeak_Bare(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeak_Bare(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_IgnoreJailbreak.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeaks_IgnoreJailbreak.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeaks_IgnoreJailbreak(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeaks_IgnoreJailbreak(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeaks_IgnoreJailbreak(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeaks_IgnoreJailbreak(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Leet.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeaks_Leet.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeaks_Leet(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeaks_Leet(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeaks_Leet(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeaks_Leet(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_Ignore+Leet.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeaks_PromptLeaks_Ignore+Leet.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeaks_PromptLeaks_Ignore+Leet(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeaks_PromptLeaks_Ignore+Leet(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeaks_PromptLeaks_Ignore+Leet(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeaks_PromptLeaks_Ignore+Leet(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_RepeatChars.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeaks_RepeatChars.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeaks_RepeatChars(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeaks_RepeatChars(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeaks_RepeatChars(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeaks_RepeatChars(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_PromptLeaks\\NoProtection_PromptLeaks_PrefixInjection.parquet'
#str_promptleak_allresults_filename = 'Vigil_PromptLeaks_PrefixInjection.parquet'
#str_detectedYarasamples_filename = "Vigil_PromptLeaks_PrefixInjection(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_PromptLeaks_PrefixInjection(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_PromptLeaks_PrefixInjection(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_PromptLeaks_PrefixInjection(Detected by Canary).parquet"

#str_samples_parquet_filename = '..\\_BenignSamples\\BenignSamples.parquet'
#str_promptleak_allresults_filename = 'Vigil_BenignSamples.parquet'
#str_detectedYarasamples_filename = "Vigil_BenignSamples(Detected by Yara).parquet"
#str_detectedTransformersamples_filename = "Vigil_BenignSamples(Detected by Transformer).parquet"
#str_detectedVectorDBsamples_filename = "Vigil_BenignSamples(Detected by VectorDB).parquet"
#str_detectedCanarysamples_filename = "Vigil_BenignSamples(Detected by Canary).parquet"


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


