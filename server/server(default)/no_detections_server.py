import sys, json
sys.path.append("..")
import llm_agent_server as las

docs_dirpath = "..\\_docs"
system_message = open("..\\..\\system_message.txt", "r").read()
openaiapikey = open("..\\..\\env.list", "r").read().strip("\n").split("=")[1]
dict_conf = json.loads(open("conf.json", "r").read())
port = dict_conf["port"]
server_type = dict_conf["server_type"]

las.llmApp = las.BaseLLMApp(las.app,
                        port,
                        openaiapikey,
                        system_message,
                        docs_dirpath
)

if __name__ == "__main__":
        las.llmApp.Run(server_type)
