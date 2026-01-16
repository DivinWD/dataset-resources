# DivinWD dataset resources
This repository provides resources and instructions for reproducing the research presented in the [DivinWD](https://divinwd.dev) project. It includes environment setup guidelines, configuration files, and code to help researchers replicate our findings. The [dataset file](https://zenodo.org/records/18234750) is available on Zenodo; details about its content are available in this repository under the ```database/``` directory.

The code is released under the MIT license. Data, charts, and other content is released under the [Creative Commons CC0](https://creativecommons.org/publicdomain/zero/1.0/) dedication (public domain).

## Quickstart with QLever and Docker
We recommend using [QLever](https://github.com/ad-freiburg/qlever), a fast graph database implementing the RDF and SPARQL standards. The most practical way to use QLever is via its command-line interface, which leverages [Docker](https://www.docker.com), making configuration and management easier.

Before moving on, make sure to have Docker installed, along with the QLever tool:
```
pip install qlever
```

To get started, clone this repository and go to the ```database``` directory (or wherever the ```Qleverfile```, the configuration file of the database, is stored), and run the following commands:
```
qlever get-data  # download the dataset
qlever index     # build the database index (this may take a few minutes)
qlever start     # start the database and its endpoint
```
After the last command is run, a Docker container with a QLever instance in it should pop up on your machine.

If something goes wrong during setup, please refer to the official QLever documentation:
* ```qlever``` utility: [https://github.com/qlever-dev/qlever-control](https://github.com/qlever-dev/qlever-control)
* QLever database: [https://github.com/ad-freiburg/qlever](https://github.com/ad-freiburg/qlever)

## Run the QLever Web UI
```qlever start``` simply runs a QLever instance. You can optionally add a Web UI consisting of a console for writing SPARQL queries. QLever creates the UI in a separate container, which in turn connects to the database. To start the UI, make sure to run the following command in the ```database``` directory, or wherever the dedicated configuration file (```Qleverfile-ui.yml```) is stored:
```
qlever ui
```

Then, open your favorite browser and type ```http://localhost:8176/wikidata``` in the search bar.

## Queries and figures
The ```queries``` directory contains Python scripts that automatically query the endpoint and produce a figure as output. Each script has its own, hardcoded SPARQL query, which can be copy-pasted in the Web UI. Before executing the scripts, you need to provide the QLever endpoint location using the ```--url``` option; make sure to use the database endpoint! For example, the instructions showed in the previous paragraphs should produce a QLever instance that can be queried at the default URL ```http://localhost:8888```.

Try running ```queries/year/year.py``` with the command below:
```
python3 year.py --url http://localhost:8888
```
This should output a figure that shows the number of articles published each year.
