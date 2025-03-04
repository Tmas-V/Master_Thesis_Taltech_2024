import sys
sys.path.append(".")
import BaseClient as bclient

class ManualClient(bclient.BaseClient):
    def __init__(self,
                 _server_host,
                 _port,
                 _useMemory
                 ):
        super().__init__(
                 _server_host,
                 _port,
                 _useMemory)
    def run(self):
        print("Enter user prompt. Double press 'Enter' to clear conversation memory. Double press 'Enter' again to quit.")
        print("------------------------------")
        prompt = ""
        int_sentPromptCount = 0
        while True:
            prompt = ""
            while True:
                line = input("prompt>")
                if len(line) == 0:
                    break
                prompt += line + "\n"
            if len(prompt) != 0:
                int_sentPromptCount += 1
                print("-------Prompting...-----------")
                response_dict = self.send(prompt)
                print("Prompt: \"\"\"", end="")
                print(response_dict["prompt"], end="")
                print("\"\"\"")
                print()
#                scan_results = response_dict["scan_results"]
#                if scan_results != {}:
#                    print("Scan results:")
#                    print(json.dumps(
#                        scan_results,
#                        indent=6,
#                        sort_keys=True
#                        )
#                    )
#                    print()
                print("Response: \"\"\"", end="")
                print(response_dict["llm_response"], end="")
                print("\"\"\"")
                print("------------------------------")
            else:
                if not self.useMemory:
                    break
                if int_sentPromptCount == 0:
                    break
                else:
                    print()
                    print("########Clearing memory.", end="")
                    self.clear_memory()
                    for i in range(0,2):
                        time.sleep(0.8)
                        print(".",end="")
                    time.sleep(0.8)
                    print("#############")
                    print()
                    int_sentPromptCount = 0

# sys.argv = [prg, host, port, useMemory]
if __name__ == "__main__":
    manualClient = ""
    sys.argv = ["client.py",
                "127.0.0.1",
                "5000",
                "False"]
    try:
        host = str(sys.argv[1])
        port = int(sys.argv[2])
        useMemory = sys.argv[3]
        if useMemory == "True":
            useMemory = True
        else:
            useMemory = False
        manualClient = ManualClient(
            host,
            port,
            useMemory)
    except:
        print("Error: invalid program parameters...")
        input("(Press any key)")
        sys.exit(0)
    manualClient.run()

