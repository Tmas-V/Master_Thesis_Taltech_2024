import os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet


def merge_for_Vigil():
    objectives = [
#        "benign",
    #    "promptleak_ignore",
    #    "promptleak_ignore_leet",
    #    "promptleak_ignore_repeat",
        "promptleak_ignore_leet_repeat",
    #    "promptleak_leet",
    #    "promptleak_pi",
    #    "promptleak_repeat"
    ]
    for objective in objectives:
        str_vigilfile_path_def = ".\\_DEFAULTS(1000)\\"+objective+"\\Vigil\\"+objective+".parquet"
        str_vigilfile_path_modif = ".\\_MODIFIED(1000)\\"+objective+"\\Vigil\\"+objective+".parquet"

        str_filename_to_save = objective+".parquet"


        modif_row_values = {}
        modif_rows = parquet.read_pandas(str_vigilfile_path_modif).to_pandas()
        for index, row in modif_rows.iterrows():
            modif_row_values[row["prompt"]] = {
                "transformer_score": row["transformer_score"],
                "is_detected_by_transformer": row["is_detected_by_transformer"],
                "is_detected_by_canary": row["is_detected_by_canary"],
    #            "score": row["score"],
    #            "success": row["success"],
                "response": row["response"]
                }

        new_rows = pd.DataFrame({
            "prompt": [],
            "response": [],
    #        "score": [],
    #        "success": [],
            "is_detected_by_yara": [],
            "transformer_score": [],
            "is_detected_by_transformer": [],
            "vectordb_score": [],
            "is_detected_by_vectordb": [],
            "is_detected_by_canary": []
            
        })
        def_rows = parquet.read_pandas(str_vigilfile_path_def).to_pandas()
        for index, row in def_rows.iterrows():
            prompt = row["prompt"]
            modif_values = modif_row_values[prompt]
            this_row = pd.DataFrame({
                "prompt": [prompt],
                "response": [modif_values["response"]],
    #            "score": [modif_values["score"]],
    #            "success": [modif_values["success"]],
                "is_detected_by_yara": [row["is_detected_by_yara"]],
                "transformer_score": [modif_values["transformer_score"]],
                "is_detected_by_transformer": [modif_values["is_detected_by_transformer"]],
                "vectordb_score": [row["vectordb_score"]],
                "is_detected_by_vectordb": [row["is_detected_by_vectordb"]],
                "is_detected_by_canary": [modif_values["is_detected_by_canary"]]
                
            })
            new_rows = pd.concat([new_rows, this_row], ignore_index = True)

        table = pyarrow.Table.from_pandas(new_rows)
        parquet.write_table(table, str_filename_to_save)



def merge_for_Rebuff():
    objectives = [
#        "benign",
#        "promptleak"
#        "promptleak_ignore",
#        "promptleak_ignore_leet",
#        "promptleak_ignore_repeat",
        "promptleak_ignore_leet_repeat",
#        "promptleak_leet",
#        "promptleak_pi",
#        "promptleak_repeat"
    ]
    for objective in objectives:
        str_path_def = ".\\_DEFAULTS(1000)\\"+objective+"\\Rebuff\\"+objective+".parquet"
        str_path_modif = ".\\_CANARY_EXPERIMENTS\\modified_v2\\"+objective+"\\Rebuff\\"+objective+".parquet"

        str_filename_to_save = objective+".parquet"


        modif_row_values = {}
        modif_rows = parquet.read_pandas(str_path_modif).to_pandas()
        for index, row in modif_rows.iterrows():
            modif_row_values[row["prompt"]] = {
                "is_detected_by_canary": row["is_detected_by_canary"],
#                "score": row["score"],
#                "success": row["success"],
                "response": row["response"]
                }

        new_rows = pd.DataFrame({
            "prompt": [],
            "response": [],
#            "score": [],
#            "success": [],
            "heuristics_score": [],
            "is_detected_by_heuristics": [],
            "model_score": [],
            "is_detected_by_openai": [],
            "vector_score": [],
            "is_detected_by_vectordb": [],
            "is_detected_by_canary": [],
            "is_detected": []
            
        })
        def_rows = parquet.read_pandas(str_path_def).to_pandas()
        for index, row in def_rows.iterrows():
            prompt = row["prompt"]
            modif_values = modif_row_values[prompt]
            is_detected = row["is_detected_by_heuristics"] or row["is_detected_by_openai"] or row["is_detected_by_vectordb"]
            this_row = pd.DataFrame({
                "prompt": [row["prompt"]],
                "response": [modif_values["response"]],
#                "score": [modif_values["score"]],
#                "success": [modif_values["success"]],
                "heuristics_score": [row["heuristics_score"]],
                "is_detected_by_heuristics": [row["is_detected_by_heuristics"]],
                "model_score": [row["model_score"]],
                "is_detected_by_openai": [row["is_detected_by_openai"]],
                "vector_score": [row["vector_score"]],
                "is_detected_by_vectordb": [row["is_detected_by_vectordb"]],
                "is_detected_by_canary": [modif_values["is_detected_by_canary"]],
                "is_detected": [is_detected]
                
            })
            new_rows = pd.concat([new_rows, this_row], ignore_index = True)

        table = pyarrow.Table.from_pandas(new_rows)
        parquet.write_table(table, str_filename_to_save)

def merge_for_VectorDB():
    objectives = [
#        "benign",
#        "promptleak_ignore",
    #    "promptleak_ignore_leet",
    #    "promptleak_ignore_repeat",
#        "promptleak_ignore_leet_repeat",
    #    "promptleak_leet",
        "promptleak_pi",
    #    "promptleak_repeat"
    ]
    for objective in objectives:
        str_vigilfile_path = ".\\_DEFAULTS(1000)\\"+objective+"\\Vigil\\"+objective+".parquet"
        str_rebufffile_path = ".\\_DEFAULTS(1000)\\"+objective+"\\Rebuff\\"+objective+".parquet"

        str_filename_to_save = objective+"_vectordbs.parquet"


        modif_row_values = {}
        modif_rows = parquet.read_pandas(str_vigilfile_path).to_pandas()
        for index, row in modif_rows.iterrows():
            modif_row_values[row["prompt"]] = {
                "vigil_vectordb_score": row["vectordb_score"]
                }

        new_rows = pd.DataFrame({
            "prompt": [],
            "response": [],
    #        "score": [],
    #        "success": [],
            "vigil_vectordb_score": [],
            "rebuff_vectordb_score": []
            
        })
        def_rows = parquet.read_pandas(str_rebufffile_path).to_pandas()
        sum_deltas = 0
        for index, row in def_rows.iterrows():
            prompt = row["prompt"]
            modif_values = modif_row_values[prompt]
            this_row = pd.DataFrame({
                "prompt": [prompt],
    #            "score": [modif_values["score"]],
    #            "success": [modif_values["success"]],
                "rebuff_vectordb_score": [row["vector_score"]],
                "vigil_vectordb_score": [modif_values["vigil_vectordb_score"]]
                
            })
            new_rows = pd.concat([new_rows, this_row], ignore_index = True)
            print("{} |\t\tV:{}\tR:{}".format(prompt, modif_values["vigil_vectordb_score"], row["vector_score"]))
            sum_deltas += abs(row["vector_score"] + modif_values["vigil_vectordb_score"] - 1)

        print("Sum of deltas: {}".format(sum_deltas))

        table = pyarrow.Table.from_pandas(new_rows)
        parquet.write_table(table, str_filename_to_save)

#merge_for_Vigil()
#merge_for_Rebuff()
merge_for_VectorDB()
