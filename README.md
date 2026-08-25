# Digital Twin Library

A lightweight layer for executing Digital Twin scenarios using the DISSECT-CF-Fog simulator in Swarmchestrate.


## Getting started with DISSECT-CF-Fog

Prerequisites:
 - **JDK 17**
 - **Apache Maven 3.9** 

At the moment, the Maven project is located in the `simulator` directory of the `refactor` branch:

`https://github.com/sed-inf-u-szeged/DISSECT-CF-Fog/tree/refactor/simulator`

Run the Maven build command in that directory:

```bash
mvn clean package
```

In case of failing tests: 

Compile tests, but don't run them:
```bash
mvn clean package -DskipTests 
```

Neither compile nor run tests:
```bash
mvn package -Dmaven.test.skip=true
```

After a successful build, the simulator JAR will be created in:

`DISSECT-CF-Fog/simulator/target/dissect-cf-fog-1.0.0-SNAPSHOT-jar-with-dependencies.jar`

***Alternatively, IntelliJ IDEA simplifies the setup with built-in Maven support and integrated JDK management.***


### Running the Simulator Manually

The simulator can also be run directly from the command line for testing purposes. It expects two command-line arguments:

1. Path to the Digital Twin input JSON file
2. Path to the noise dataset CSV file

```bash
java -cp path/to/simulator.jar \
  hu.u_szeged.inf.fog.simulator.agent.demo.DigitalTwinDemo \
  path/to/dt-input.json \
  path/to/noise-data.csv
```


## Local Testing (CLI)

The Digital Twin engine can be executed locally using the provided CLI interface.

Prerequisites:
 - **Python 3.12**
 - The simulator JAR must be built separately (see previous section)

Create a virtual environment (optional):

```bash
python -m venv .my_env
source .my_env/bin/activate   # Linux/macOS
.my_env\Scripts\activate      # Windows
```

Run the CLI from the project root directory:

```bash
python -m dt.cli \
  --input path/to/dt-input.json  \
  --jar path/to/simulator.jar \
  --noise-csv path/to/noise-data.csv \
  --output path/to/output_dir \
  --max-workers 4 \            # parallel executions
  --timeout 60                 # timeout per scenario (seconds)
  --keep-files                 # keep the simulator result directory (optional)
```

Alternatively, install the project in editable mode to run it from anywhere:

```
pip install -e .
python -m dt.cli --help
```


## Using Digital Twin as a Library

The Digital Twin engine can also be used as a Python library and integrated into other systems. 

Install directly from GitHub:

```bash
pip install git+https://github.com/Swarmchestrate/digital-twin.git
```

Example:

```python
from dt.engine import DtEngine

engine = DtEngine(
    input_path="path/to/dt-input.json",
    jar="path/to/simulator.jar",
    noise_csv_path="path/to/noise-data.csv",
    output_path="path/to/output_dir",
    max_workers=4,    # parallel executions
    timeout=60,       # timeout per scenario (seconds)
    keep_files=True,  # keep the simulator result directory (optional)
)

result = engine.evaluate_file()
```
