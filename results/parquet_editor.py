import os
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet
base_dir = ".\\_DEFAULTS(1000)\\"
pi_dirs = [
#    "promptleak",
    "promptleak_ignore",
    "promptleak_ignore_leet",
    "promptleak_ignore_repeat",
#    "promptleak_leet",
#    "promptleak_pi",
#    "promptleak_repeat"
]
det_dirs = [
    "LLM Guard",
    "Vigil",
    "Rebuff"
]
dirs = []
for pi_dir in pi_dirs:
    dirs += [base_dir + pi_dir]
    for det_dir in det_dirs:
        dirs += [base_dir + pi_dir + "\\" + det_dir]

filenames = []
for _dir in dirs:
    items = os.listdir(_dir)
    filenames += [_dir + "\\" + item for item in items if item.endswith(".parquet")]

for filename in filenames:
    existing_rows = parquet.read_pandas(filename).to_pandas()
    saved_rows = []
    counter = 0
    for index, row in existing_rows.iterrows():
        if counter >= 1000:
            break
        saved_rows += [row]
        counter += 1
    columns = saved_rows[0].keys()
    saved_frame = {}
    for column in columns:
        saved_frame[column] = []
    saved_pd = pd.DataFrame(saved_frame)
    for row in saved_rows:
        saved_row = {}
        for column in columns:
            saved_row[column] = [row[column]]
        saved_pd = pd.concat([saved_pd, pd.DataFrame(saved_row)],
                             ignore_index = True)

    table = pyarrow.Table.from_pandas(saved_pd)
    print(filename)
    new_filename = "\\".join(filename.split("\\")[:-1]) + "\\_" + filename.split("\\")[-1]
    parquet.write_table(table, new_filename)
