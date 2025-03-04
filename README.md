# Comparative analysis of prompt leak detection of LLM Guard, Vigil, and Rebuff
This is a repo of source code used to conduct experiments under work "Enhancing Security in LLM Applications: A Performance Evaluation of Early Detection Systems".

To run automated sample testing or manual prompting experimentation run **main.py** in *default* virtual python environment. Before doing it you should setup the necessary virtual environments and write into required configuration files.

## Configuration files
You are required to write following settings in following configuration files:
*venv.yaml* - write paths to python executable in corresponding virtual environments, created from corresponding requirements, which can be found under ./detectors/_..._requirements/requirements.txt
*env.list* - write OpenAI API key
*detector/.../conf.json* - update any configuration JSON file under each scanner working directory at *./detectors/*
*server/conf.json* - update configuration file with network specs for hosting LLM application's server
*client/conf.json* - update tis configuration file with same network specs as for the server
**Whenever changing configured ports for LLM app server don't forget to make corresponding changes ro corresponding** *conf.json* **files under** *client* **directory.**

## Running LLM app for sample validation
First, create python virtual environment. Install packages stated in *./requirements.txt*. This same environment should be used when running **main.py**.
Write the path to py executable of this environment to *venvs.yaml* under **default**.

## Running any scanner from LLM Guard
First, create python virtual environment. Install packages stated in *./detectors/_LLMGuard_requirements/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **LLMGuard**.

## Running any scanner from Vigil
First, create python virtual environment. Install packages stated in *./detectors/_Vigil_requirements/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **Vigil**.
Update *vigil_server_conf.conf* and *vigil_server_conf_template.conf* under any Vigil scanner at *./detectors* with paths to vdb and yara directory, which reside in the directory of cloned version of Vigil.

## Running any scanner from Rebuff
First, create virtual machine and create a python virtual environment in it. Install packages stated in *./detectors/_Rebuff_virtual_machine_requirements/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **Rebuff**.
Copy files from *./detectors/_Rebuff_virtual_machine_requirements/host_Rebuff_sdk_as _server/* to the virtual machine. 
Change the IP address and port for this hosting server in *rebuff_server.py*. Do not forget to do corresponding changes in *./detectors/Rebuff_.../conf.json*.
Write OpenAI API key in the copied *env.list*, as well as Pinecone API key in *pinecone.env* file.
Run *rebuff_server.py* in the created virtual environment. Now you can run experiments on Rebuff via *main.py*.
