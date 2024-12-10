.PHONY: init-cpu init-gpu docker-up docker-down init-docker-cpu init-docker-gpu \
		init-working-dir setup-vscode setup-poetry setup-container \
		reset-notebook start-jupyter fix ruff-fix \
		lint ruff-check ruff-format mypy-check

init-runtime-cpu: 
	@echo "RUNTIME=cpu" >> ./.env_project

init-runtime-gpu: 
	@echo "RUNTIME=gpu" >> ./.env_project

init-working-dir:
	@echo "WORKING_DIR=$(shell basename $(shell dirname $(shell pwd)))" >> ./.env_project

init-base:
	@echo -n > .env_project
	@echo "PROJECT=$(shell basename $(shell pwd))" >> ./.env_project
	@echo "USER_UID=$(shell id -u $(USER))" >> ./.env_project
	@echo "USER_GID=$(shell id -g $(USER))" >> ./.env_project
	$(MAKE) init-working-dir

init-cpu: 
	$(MAKE) init-base
	$(MAKE) init-runtime-cpu

init-gpu: 
	$(MAKE) init-base
	$(MAKE) init-runtime-gpu

docker-up-cpu:
	@. ./.env_project && docker compose --env-file .env_project -f context/cpu/docker-compose.yml -p $${PROJECT}-$${USER_UID} up -d

docker-up-gpu:
	@. ./.env_project && docker compose --env-file .env_project -f context/gpu/docker-compose.yml -p $${PROJECT}-$${USER_UID} up -d

docker-down:
	@. ./.env_project && docker compose -p $${PROJECT}-$${USER_UID} down

docker-stop:
	@. ./.env_project && docker compose -p $${PROJECT}-$${USER_UID} stop

init-docker-cpu:
	$(MAKE) init-cpu
	$(MAKE) docker-up-cpu

init-docker-gpu:
	$(MAKE) init-gpu
	$(MAKE) docker-up-gpu

reset-notebook:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	@jupyter nbconvert --clear-output --inplace `find $(arg1) -name *ipynb`

setup-vscode:
	@code --install-extension ms-python.python
	@code --install-extension ms-python.mypy-type-checker
	@code --install-extension charliermarsh.ruff
	@code --install-extension mhutchie.git-graph
	@code --install-extension GitHub.copilot
	@code --install-extension ms-toolsai.jupyter

setup-poetry:
	@poetry config virtualenvs.in-project true
	@poetry install


start-jupyter:
	@. ./.env_project && docker exec $${PROJECT}_$${USER_UID} /bin/bash -c \
		poetry config virtualenvs.in-project true \
		&& poetry install --with jupyter \
		&& poetry run ipython kernel install --user --name=$${PROJECT} \
		&& poetry run jupyter lab --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token=''"

lint:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	$(MAKE) ruff-check $(arg1); \
	$(MAKE) ruff-format $(arg1); \
	$(MAKE) mypy-check $(arg1)

ruff-check:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	poetry run ruff check $(arg1) --config ./pyproject.toml

ruff-format:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	poetry run ruff format --check $(arg1) --config ./pyproject.toml

mypy-check:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	poetry run mypy $(arg1) --config-file ./pyproject.toml

fix:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	$(MAKE) ruff-fix $(arg1)

ruff-fix:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	poetry run ruff --fix $(arg1) --config ./pyproject.toml; \
	poetry run ruff format $(arg1) --config ./pyproject.toml

to-notion:
	$(eval args := $(filter-out $@,$(MAKECMDGOALS)))
	$(eval arg1 := $(word 1, $(args)))
	$(eval arg2 := $(word 2, $(args)))
	@echo "notebook: $(arg1)"
	@echo "notion page title: $(arg2)"
	@poetry run python ./libs/abeja-toolkit/notebook_exporter/export.py notion -nb $(arg1) --title $(arg2)

%:
	@: