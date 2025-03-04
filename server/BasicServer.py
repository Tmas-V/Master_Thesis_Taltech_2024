import sys, os, json, time
import numpy as np
import pandas as pd
import pyarrow as pyarrow
import pyarrow.parquet as parquet

sys.path.append(".\\server\\")
import BaseServer as bserver


# sys.argv = [prg, host, port, system_message, model_name]
if __name__ == "__main__":
#    sys.argv = [
#        "server.py",
#        "127.0.0.1",
#        "5000",
#        "You are a helpful assistant. Answer questions on cybersecurity.",
#        "gpt-4o"#"claude-3-5-sonnet-20241022"
#    ]
    str_host = ""
    int_port = 5000
    str_system_message = ""
    model_name = ""
    try:
        str_host = str(sys.argv[1])
        int_port = int(sys.argv[2])
        str_system_message = str(sys.argv[3])
        model_name = str(sys.argv[4])
    except:
        print("[!] Server error: program parameters parsed incorrectly!")
        input("(Press any key)")
        quit(0)
    try:
        bserver.llmApp = bserver.BaseServer(bserver.flaskApp,
                                            str_host,
                                            int_port,
                                            str_system_message,
                                            model_name)
        bserver.llmApp.Run()
    except Exception as e:
        print(e)
        time(60)
    
