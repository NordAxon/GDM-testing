# Generative Dialogue Model Automatic Quality Assurance tool

## Description

This repository contains a framework for testing and evaluating GDMs.
There are two steps in the process:

1. Generating conversations.
- We divide the output into experiments with unique experiment ids.
- Each experiment contains a number of runs with numerical ids.
- Generated conversations are stored in ```test_data/{EXPERIMENT_ID}/run_{RUN_ID}.txt```
- The configurations for all runs in an experiment are stored in ```test_data/{EXPERIMENT_ID}/experiment_config.json```

2. Analyzing the conversations.
- Test results are stored in an SQL-database in ```test_results/{EXPERIMENT_ID}.sqlite```
- The configuration for each run is contained in the table ```runs```
- Each test-case is then imported into a separate table each.
- If we want to analyze conversations that have already been generated we can use the argument ```--read-run-ids``` to read these from the chosen .txt-files determined by the run_id.


## How to run

Install dependencies

```
# clone project
git clone git@github.com:NordAxon/GDM-testing.git

# install project
cd GDM-testing
pip install -e .
pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
```

Testing is run by:

```
# run module
python main.py <OPTIONS> [PARAMETERS]
```

Run `python main.py -h` to have the options presented, or see below:

```
# options available
usage: main.py [-h] [-eid EXPERIMENT_ID] [-v] [-ec] [-od] [-cl] [-cs] [-rcs RANDOM_CONV_START] [-a] [-cp] [-t] [-im] [-rid]

Parser for setting up the script as you want

optional arguments:
  -h, --help                show this help message and exit
  -eid, --experiment_id     We divide all runs into experiments with a unique identifier.
  -v, --verbose             Use verbose printing.
  -ec , --export-channel    Specify which channel to export the results through. Currently only 'sqlite' is available.
  -od, --overwrite-db       Specifies if the result database should be overwritten during computation.
  -cl , --conv-length       How many replies from each GDM all conversations should contain.
  -cs , --conv-starter      Testee: testee initiates every conversation.
                            Conv-partner: the conversation partner initiates all conversations. Not specified: 50-50.
  -rcs, --random-conv-start Start conversations with a random reply.
  -a , --amount-convs       How many conversations shall there be per tested GDM.
  -cp , --conv-partner_id   Specify which GDM to run your testees against.
  -t , --testee-ids         Names of local docker images to use for each run, separated by ",".
  -im, --interview-mode     Conversations are initialized as interview scenarios.
  -rid , --read-run-ids     Run ids of the runs to import.
                            No input is interpreted as such the script generates conversations using the GDMs.
                            Currently only miscellaneous .txt-files are supported.
```

### Visualise the results from the SQLite-file

1. Install and set up a Grafana-server. More information about that can be found here: https://grafana.com/docs/grafana/latest/setup-grafana/installation/.
2. Log in with username: admin, password: admin on localhost:3000 and choose a new password.
3. Install the SQLite plugin from settings/plugins.
3. Hold over the '+'-sign corresponding to the 'Create' menu. In the shown menu, click 'Import'.
4. In the box "Import via panel json", paste in the dashboard-json which can be found in the repository in the file 'dashboard-json.tex', and click load.
5. Then, hold over the 'Gear'-icon on the left to show the "Configuration". There, click "Data sources"
6. There click "Add data source" and add the path to your SQLite-file, which by default is located in your local repository.
7. When you have added the data source, the dashboard should visualise all the implemented test case results. You are also free to make new figures, to which you can fetch data from the SQLite-file by doing SQLite-queries through Grafana.

### Citation

```
@article{JohanBengtsson2022,
  title={Quality Measurement of Generative Dialogue Models for Language Practice},
  author={Johan Bengtsson},
  year={2022}
}
```

