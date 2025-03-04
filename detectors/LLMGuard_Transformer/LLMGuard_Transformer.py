import sys, os
sys.path.append(".\\detectors\\")
from BaseDetector import *
################### Setup LLM-Guard ######################
from llm_guard.input_scanners import PromptInjection
from llm_guard.input_scanners.prompt_injection import MatchType, V1_MODEL, V2_MODEL, V2_SMALL_MODEL
##########################################################

class LLMGuard_Transformer(BaseDetector):
    def __init__(self,
                 _str_input_filepath,
                 _str_output_filepath):
        super().__init__("LLMGuard_Transformer",
                 _str_input_filepath,
                 _str_output_filepath,
                 20)
        dict_conf = json.loads(open(self.conf_filepath, "r").read())
        self.transformer_threshold = dict_conf["llm guard"]["input_scanners"]["transformer"]["threshold"]
        self.transformer_matchtype = dict_conf["llm guard"]["input_scanners"]["transformer"]["match_type"]
        self.transformer_matchtype_short = ""
        self.transformer_model = dict_conf["llm guard"]["input_scanners"]["transformer"]["model"]
        self.transformer_model_short = ""
        
        match_type = None
        if self.transformer_matchtype == "FULL":
            match_type = MatchType.FULL
            self.transformer_matchtype_short = "F"
        else:
            self.transformer_matchtype = "SENTENCE"
            match_type = MatchType.SENTENCE
            self.transformer_matchtype_short = "S"

        model_type = None
        if self.transformer_model == "ProtectAI/deberta-v3-base-prompt-injection":
            model_type = V1_MODEL
            self.transformer_model_short = "V1"
        elif self.transformer_model == "ProtectAI/deberta-v3-base-prompt-injection-v2":
            model_type = V2_MODEL
            self.transformer_model_short = "V2"
        elif self.transformer_model == "ProtectAI/deberta-v3-small-prompt-injection-v2":
            model_type = V2_SMALL_MODEL
            self.transformer_model_short = "V2_SMALL"
        
        self.scanner = PromptInjection(model=model_type,
                                       threshold=self.transformer_threshold,
                                       match_type=match_type)



        tmp = self.output_filepath.split(".")
        self.output_filepath = ".".join(tmp[:-1]) + "(model={};mode={})".format(self.transformer_model_short, self.transformer_matchtype_short) + "." + tmp[-1]
        print()
        print(self.output_filepath)

    def create_empty_dataset(self):
        return pd.DataFrame(
            {
                "prompt" : [],
                "llmg_is_detected_by_transformer" : pd.Series([], dtype=np.bool_),
                "llmg_risk_score" : [],
                "llmg_threshold" : [],
                "llmg_match_type": [],
                "llmg_sanitized_prompt" : []
            }
        )
    def analyze_input(self,
                      dict_input_row):
        sanitized_prompt, is_valid, risk_score = self.scanner.scan(dict_input_row["prompt"])
        output_row = {
                "prompt" : [dict_input_row["prompt"]],
                "llmg_is_detected_by_transformer" : pd.Series([not is_valid], dtype=np.bool_),
                "llmg_risk_score" : [risk_score],
                "llmg_threshold" : [self.transformer_threshold],
                "llmg_match_type": [self.transformer_matchtype],
                "llmg_sanitized_prompt" : [sanitized_prompt]
        }
        return pd.DataFrame(output_row)

# sys.argv = [prg, str_input_filepath, str_output_filepath]
if __name__ == "__main__":
    try:
        str_input_filepath = str(sys.argv[1])
        str_output_filepath = str(sys.argv[2])
        
        if not os.path.exists(str_input_filepath):
            print("[!] LLMGuard Tranformer error: input dataset not found!")
            input("(Press any key)")
            sys.exit(-1)
    except:
        print("[!] LLMGuard Tranformer error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(-1)
    detector = LLMGuard_Transformer(str_input_filepath,
                                   str_output_filepath)
    detector.run()
    sys.exit(1)

