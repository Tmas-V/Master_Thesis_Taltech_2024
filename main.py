import sys, os
from Experiment import *
from Generator import *
from Processor import *


str_conf_files_dirpath = ".\\experiments\\"

def generate_experiment_conf_data():
    data = {
        "attack_type" : "promptleak",
        "attack_enhancements" : [
        {
            "type": "technique",
            "name": "prefix"
        },
        {
            "type": "technique",
            "name": "ignore"
        },
        {
            "type": "obfuscation",
            "name": "leet"
        },
        {
            "type": "technique",
            "name": "repeat"
        },        
        ],
        "gen_samples_limit" : 1000,
        "val_samples_limit" : 1000,
        "rerun_validation" : False,
        "model_name": "gpt-3.5-turbo",
        "use_valid_as_gen": False
    }
    label = data["attack_type"]
    for enhancement in data["attack_enhancements"]:
        label += "_" + enhancement["name"]
    if label[-1] == "_":
        label = label[:-1]
    filepath = str_conf_files_dirpath + label + ".yaml"
    with open(filepath, "w") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
'''
generate_experiment_conf_data()
sys.exit(0)
'''


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
    print("*) All")
    print("---------------------------------")
    print("(Type 0 to end program)")
    print("")
    int_choice = -1
    str_chosen_filename = ""
    bool_run_experiment = True
    bool_run_noconfirm = False
    while int_choice < 0 or int_choice >= len(list_conf_files):
        int_choice = input("Conf to use ({}-{}, *): ".format(1, len(list_conf_files)))
        if int_choice == "*":
            list_chosen_exp_labels = [item.split(".")[0] for item in list_conf_files]
            bool_run_noconfirm = True
            break
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
            list_chosen_exp_labels = [list_conf_files[int_choice].split(".")[0]]
    if bool_run_experiment:
        for str_chosen_exp_label in list_chosen_exp_labels:
            experiment = Experiment(str_chosen_exp_label)
            experiment.debug_log()
            gen_val_result = 1
            if not bool_run_noconfirm:
                generator = Generator(experiment)
                gen_val_result = generator.run()
            if gen_val_result == 1:
                print("[0] Generation and Validation were successful!")
                str_processor_types = [
                    "LLMGuard_Transformer",
                    "Vigil_Yara",
                    "Vigil_Transformer",
                    "Vigil_VDB",
                    "Vigil_Canary",
                    "Vigil_PRSimilarity",
                    "Rebuff_Heuristics",
                    "Rebuff_Model",
                    "Rebuff_VDB",
                    "Rebuff_Canary"
                ]
                for str_processor_type in str_processor_types:
                    processor = Processor(str_processor_type, experiment)
                    processor_result = processor.run()
                    if processor_result == 1:
                        print("[0] Detector {} was successful!".format(str_processor_type))
                    elif processor_result == 0:
                        print("[0] Detector {} was not run.".format(str_processor_type))
                    else:
                        print("[!] Detector {} HAS FAILED!".format(str_processor_type))
            else:
                print("[!] Generation and Validation failed!")



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
    
    




