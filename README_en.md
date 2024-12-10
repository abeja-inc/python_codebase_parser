[Japanese](./README.md)

# Using Project Templates
Press the `Use this template` button in the upper right corner of the screen of this repository and select `Create a new repository`.The rest is as usual. You can select this template when you create a new repository in the ABEJA organization without opening this repository screen.

# Setup docker container
## Specify Python version
Specify the Python version in `context/<cpu or gpu>` in `docker-compose.yml`. If you use Jupyter Lab, uncomment `ports`. Since port 8888 is used by default, check the available ports and change the source of `ports` in `docker-compose.yml` if you are running on a shared machine such as DGX. 

## Build & Run docker container
Execute the following command to create an image and launch a Docker container. This command creates ``.env_project` file under `experimentation/`. This `.env_project` file is used as an environment variable file in docker-compose.yml.

With cpu
```
make init-docker-cpu
```

With gpu
```
make init-docker-gpu
```

# Setup experimentation environment
## For VSCode
### Connect into docker container with VSCode
Attach VSCode to containers launched with the `Dev Containers` extension of VSCode

### Setup VSCode
Go to the `experimentation/` directory in the container and execute the following command to install the minimum VSCode extensions
```
make setup-vscode
```

## For JupyterLab
If you are in a local environment, run the following command to start Jupyter Lab.
```
make start-jupyter
```

Once started, access [http://127.0.0.1:8888/lab](http://127.0.0.1:8888/lab). If you are changing the port, change the 8888 part as appropriate. If you start up on a shared machine such as DGX, connect to the above after SSH port forwarding as follows.
```
$ ssh -N -L 8888:localhost:{Port number of the DGX connected to the container} dgx1a
```

If the host OS is Windows, create `%USERPROFILE%/.wslconfig` and describe the following. (After creation, shutdown WSL once.)
```
[wsl2] 
localhostForwarding=true
```

Shutdown JupyterLab when finished, either by shutting it down from the JupyterLab GUI, or by stopping the container with the following command.
```
make docker-stop
```

# Install Python packages
Create a virtual environment and install packages
```
make setup-poetry
```

# ディレクトリ構成
このリポジトリは以下のディレクトリで構成されています。

- .github: GitHub workflow, etc.
    - [pull_request_template.md](./.github/pull_request_template.md): PR template configuration file
    - workflows
        - [lint.yaml](./.github/workflows/lint.yaml): Dockerfile lint and Python package lint workflow configuration file
            - About lint_python_scripts
                - Run lint against the Python package containing the Python scripts with differences compared to the base commit.
                - If there is no difference, lint is not executed.
- [.vscode](./.vscode): settings file when using VSCode
    - [settings.json](./.vscode/settings.json): Please change the setting accordingly. formatOnSave is off by default.
- context: Dockerfile and docker-compose.yml for CPU and GPU environments, respectively, are stored.
    - [Dockerfile](./context/Dockerfile)
    - [.hadolint.yaml](./context/.hadolint.yaml)
    - cpu
        - [docker-compose.yml](./context/cpu/docker-compose.yml)
    - gpu
        - [docker-compose.yml](./context/gpu/docker-compose.yml)
- experimentation: Directory for storing experimental notebooks, datasets, and output
    - [dataset](./experimentation/dataset/): Directory where the data set is located
    - [latest](./experimentation/latest/): Directory for storing the latest experimental parameters and results
    - [notebooks](./experimentation/notebooks/): Directory where the experimental notebook is placed
    - [outputs](./experimentation/outputs/): Directory to store the output of the experiment
- libs: A place to put non-project specific modules and git submodules
    - [abeja-toolkit](./libs/abeja-toolkit/): Part of ABEJA's in-house Python library. The following tools are included by default
        - [notebook_exporter](./libs/abeja-toolkit/notebook_exporter/): Tool to convert notebook to notion page
        - [notion_extension](./libs/abeja-toolkit/notion_extension/): Tools for handling Notion API
        - [spreadsheet](./libs/abeja-toolkit/spreadsheet/): Tools to read data from and write data to spreadsheets
- [project_module](./project_module/): A Python package template that implements a project-specific module.This Python package is used by installing in editable mode and import in scripts or notebooks. Add scripts as needed.
    - [tests](./project_module/tests/): Implement test modules such as unit tests
    - src
        - [project_module](./project_module/src/project_module/): Scripts are stored under this directory.
            - [prediction](./project_module/src/project_module/prediction/): Directory to store scripts for the prediction and inference pipeline
                - [config.py](./project_module/src/project_module/prediction/config.py): config script to use with `PredictionPipeline`.
                - [io.py](./project_module/src/project_module/prediction/io.py): Script to define the inputs and outputs of `PredictionPipeline`.
                - [pipeline.py](./project_module/src/project_module/prediction/pipeline.py): Script to implement the `PredictionPipeline` pipeline class for prediction
            - [training](./project_module/src/project_module/training/): Directory to store scripts for the learning pipeline
                - [config.py](./project_module/src/project_module/training/config.py): config script for use with `TrainingPipeline`.
                - [io.py](./project_module/src/project_module/training/io.py): Script to define inputs and outputs for `TrainingPipeline`.
                - [pipeline.py](./project_module/src/project_module/training/pipeline.py): Script to implement the training pipeline class `TrainingPipeline`.
            - [common_config.py](./project_module/src/project_module/common_config.py): Scripts defining general config common to training and predicting or inference.
    - [pyproject.toml](./project_module/pyproject.toml): A file describing the dependencies of `project_module`.
    - [README.md](./project_module/README.md): File describing the usage of `project_module`
- [pyproject.toml](./pyproject.toml): pyproject.toml, directly under the root directory, where dependencies and other information on development packages are defined.The root directory is not considered a package because `package-mode = false` (* `package-mode` is available in poetry >= 1.8).
- README.md: A file that describes how to use this project template
- README_en.md: How to use the project template (English version)


# Linting
If you have installed the dev group dependencies, a lint check of mypy and ruf can be performed with the following command.

```shell
make lint /path/to/module
```

# NotebookをNotionページに変換する
After authentication, etc., the following command will automatically generate a Notion page with the specified title, and the Marakdown cell and cell output in the notebook will be converted to a Notion block.For detailed instructions on how to use the `notebook_exporter`, please refer to [README.md](./libs/abeja-toolkit/notebook_exporter/README.md).

```
make to-notion /path/to/notebook.ipynb <notion_page_title>
```
