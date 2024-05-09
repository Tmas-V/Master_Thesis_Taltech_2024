import sys, os
from experiments import *



str_conf_files_dirpath = ".\\experiments"

def generate_experiment_conf_data():
    conf_data = Experiment("")
    conf_data.task_type = "test_attack"
    conf_data.attack_objective_class = "promptleak"
    conf_data.attack_enhancements = [{
        "type": "jailbreak",
        "name": "ignore"
        },
        {
            "type": "jailbreak",
            "name": "repeat"
        }]
    conf_data.attack_enhancements = []
    conf_data.save_to_yaml("test_(bare_promptleak).yaml")
"""
generate_experiment_conf_data()
quit(0)
"""

def run_manual_prompt():
    print("----------Choose target server----------")
    print("1) Default (no detections)")
    print("2) With LLM Guard scanners")
    print("3) With Vigil scanners")
    print("4) With Rebuff scanners")   
    print("----------------------------------")
    print("(Type 0 to end program)")
    print("")
    int_choice = -1
    while int_choice < 0 or int_choice >= 5:
        int_choice = input("Target({}-{}): ".format(1, 4))
        try:
            int_choice = int(int_choice)
        except:
            print("[!] Incorrect input. Try again.")
            int_choice = -2
            continue
    if int_choice == 0:
        return 0
    detections_choice = int_choice - 1
    int_choice = input("Use agent with memory?(y/n):")
    memory_choice = False
    if int_choice == "y":
        memory_choice = True
    server_venvs = [os.path.abspath("..\\venv310\\Scripts\\python.exe"),
                    os.path.abspath("..\\venv310_LLM-Guard\\Scripts\\python.exe"),
                    os.path.abspath("..\\venv310_Vigil\\Scripts\\python.exe"),
                    os.path.abspath("..\\venv310_Rebuff\\Scripts\\python.exe")]
    server_cwds = [os.path.abspath(".\\server\\server(default)"),
                   os.path.abspath(".\\server\\server(LLM Guard)"),
                   os.path.abspath(".\\server\\server(Vigil)"),
                   os.path.abspath(".\\server\\server(Rebuff)")]
    servers_pys = ["no_detections_server.py",
                   "LLMGuard_server.py",
                   "Vigil_server.py",
                   "Rebuff_server.py"]
    server_ports = [5000,
                    5001,
                    5002,
                    5003]
    server_venv_path = server_venvs[detections_choice]
    server_cwd_path = server_cwds[detections_choice]
    server_py_path = "{}\\{}".format(server_cwd_path, servers_pys[detections_choice])
    server_args = [server_venv_path,
                    server_py_path
                    ]
    server_process = subprocess.Popen(args = server_args,
                            cwd = server_cwd_path,
                            creationflags=subprocess.CREATE_NEW_CONSOLE)    

    client_venv = os.path.abspath("..\\venv310\\Scripts\\python.exe")
    client_cwd = os.path.abspath(".\\client")
    client_py = "manual_prompt_client.py"
    client_venv_path = client_venv
    client_cwd_path = client_cwd
    client_py_path = "{}\\{}".format(client_cwd_path, client_py)
    client_args = [client_venv_path,
                    client_py_path,
                   str(server_ports[detections_choice]),
                   str(memory_choice)
                    ]
    choice = input("Proceed to run a client?(y/n)")
    if choice == "y":
        client_process = subprocess.Popen(args = client_args,
                                cwd = client_cwd_path,
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
        client_process.wait()
    else:
        print("Quitting...")
    server_process.kill()


def run_experiment_from_conf():
    items = os.listdir(str_conf_files_dirpath)
    list_conf_files = [item for item in items if os.path.isfile(str_conf_files_dirpath + "\\" + item) and item.endswith(".yaml")]

    if len(list_conf_files) == 0:
        print("[!] No configuration files found. Quitting...")
        return 0

    print("Choose configuration file to use:")
    print("---------------------------------")
    for i in range(0, len(list_conf_files)):
        conf_filename = list_conf_files[i]
        conf_filename_no_ext = conf_filename.split(".")[0]
        print("{}) {}".format(i+1, conf_filename_no_ext))
    print("---------------------------------")
    print("(Type 0 to end program)")
    print("")
    int_choice = -1
    str_chosen_filename = ""
    bool_run_experiment = True
    while int_choice < 0 or int_choice >= len(list_conf_files):
        int_choice = input("Conf to use ({}-{}): ".format(1, len(list_conf_files)))
        try:
            int_choice = int(int_choice)
        except:
            print("[!] Incorrect input. Try again.")
            int_choice = -2
            continue
        int_choice -= 1
        if int_choice == -1:
            bool_run_experiment = False
            break
        if int_choice < 0 or int_choice >= len(list_conf_files):
            print("[!] Incorrect input. Try again.")
        else:
            str_chosen_filename = list_conf_files[int_choice]
    if bool_run_experiment:
        experiment = Experiment(str_chosen_filename)
        experiment.run()  



if __name__ == "__main__":
    print("----------Choose program----------")
    print("1) Manual prompting")
    print("2) Run experiment from configurations")
    print("----------------------------------")
    print("(Type 0 to end program)")
    print("")
    int_choice = -1
    while int_choice < 0 or int_choice >= 3:
        int_choice = input("Program({}-{}): ".format(1, 2))
        try:
            int_choice = int(int_choice)
        except:
            print("[!] Incorrect input. Try again.")
            int_choice = -2
            continue
    if int_choice == 0:
        quit(0)
    elif int_choice == 1:
        run_manual_prompt()
    elif int_choice == 2:
        run_experiment_from_conf()
    print("Program finished.")
    
    




