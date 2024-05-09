import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

list_SaveFiles_filepaths = [
#    ".\\LLM Guard\\benign.parquet",
#    ".\\LLM Guard\\promptleak_ignore.parquet",
    
    ".\\Vigil\\benign.parquet",
    ".\\Vigil\\promptleak_pi.parquet",

#    ".\\Rebuff\\benign.parquet",
#   ".\\Rebuff\\promptleak_ignore.parquet"

#    ".\\promptleak_ignore(deepset).parquet",
#    ".\\promptleak_ignore(layier).parquet"
]
#score_column_name = "detection_score"

#score_column_name = "transformer_score"
score_column_name = "vectordb_score"

#score_column_name = "heuristics_score"
#score_column_name = "vector_score"
#score_column_name = "model_score"
ranges = []

for SaveFile_filepath in list_SaveFiles_filepaths:
    score_rows = parquet.read_pandas(SaveFile_filepath,
                                         columns=[score_column_name]).to_pandas()
    score_range = [0.0, 0.0]

    int_rows_processed = 0

    for index, row in score_rows.iterrows():
        score = row[score_column_name]
        if score != 0.0:
            score_range[0] = score
            score_range[1] = score
            break

    for index, row in score_rows.iterrows():
        score = row[score_column_name]

        if score_range[0] > score and score != 0.0:
            score_range[0] = score
        if score_range[1] < score:
            score_range[1] = score

        int_rows_processed += 1
    ranges += [score_range]

    print("{} rows processed".format(int_rows_processed))

    print("Score ranges for {}:\n[{} ; {}]\n".format(SaveFile_filepath,
                                                    score_range[0],
                                                    score_range[1]))
print("--------------------------------------------------------------")
print("Mean threshold 1: {}".format((ranges[0][1] + ranges[1][0])/2.0))
print()
print("Mean threshold 2: {}".format((ranges[0][0] + ranges[1][1])/2.0))
print("--------------------------------------------------------------")

