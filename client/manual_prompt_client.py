import sys
from llm_agent_client import *


if __name__ == "__main__":
#    if len(sys.argv) != 3:
#        print("[!] Error: client received incorrect number of parameters")
#        quit(0)
    port = int(sys.argv[1])
    use_memory = False
    if sys.argv[2] == "True":
        use_memory = True
    cli(port, use_memory)
