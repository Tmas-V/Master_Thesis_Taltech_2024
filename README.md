# Master_Thesis_Taltech_2024
This is a repo of source code used to conduct experiments within my Master Thesis research at Taltech 2024.

To run automated sample testing or manual prompting experimentation run **main.py** in *default* virtual python environment. Before doing it you should setup the necessary virtual environments and write into required configuration files.

## Configuration files
You are required to write following settings in following configuration files:
*env.list* - write OpenAI API key
*server/server(default)/conf.json* - configure LLM application server with no detection solutions used
*server/server(LLM Guard)/conf.json* - configure LLM application server with LLM Guard scanners used
*server/server(Vigil)/conf.json* - configure LLM application server with Vigil scanners used
*server/server(Rebuff)/conf.json* - configure LLM application server with Rebuff scanners used
**Whenever changing configured ports for LLM app servers don't forget to make corresponding changes ro corresponding** *conf.json* **files under** *client* **directory.**

## Running LLM app without detections
First, create python virtual environment. Install packages stated in *server/server(default)/requirements.txt*. This same environment should be used when running **main.py**.
Write the path to py executable of this environment to *venvs.yaml* under **default server venv path**.

## Running LLM app with LLM Guard
First, create python virtual environment. Install packages stated in *server/server(LLM Guard)/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **LLMGuard server venv path**.

## Running LLM app with Vigil
First, create python virtual environment. Install packages stated in *server/server(Vigil)/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **Vigil server venv path**.
Update *server/server(Vigil)/conf.json* with paths to vdb and yara directory, which reside in the directory of cloned version of Vigil.

## Running LLM app with Rebuff
First, create python virtual environment. Install packages stated in *server/server(Rebuff)/requirements.txt*.
Write the path to py executable of this environment to *venvs.yaml* under **Rebuff server venv path**.
Then you have to setup and run server hosting Rebuff's python SDK. To do this go under *server/server(Rebuff)/host_Rebuff_sdk_as_server* and install *requirements.txt* in it in another virtual environment.
Change the IP address and port for this hosting server in *rebuff_server.py*. Do not forget to do corresponding changes in *client/client(Rebuff)/conf.json*.
Write OpenAI API key in *env.list* in this directory, as well as Pinecone API key in *pinecone.env* file.
Run *rebuff_server.py*. Now you can run experiments on Rebuff via *main.py*.