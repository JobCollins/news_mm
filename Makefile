# Makefile
ENV_NAME = llms
install:
	@echo "Activating the environment..."
	@bash -c "source $$(conda info --base)/etc/profile.d/conda.sh && conda activate $(ENV_NAME) \
   && pip install poetry \
   poetry env use $(which python)"
	@echo "Installing Packages"
	@echo "Changing to pyproject.toml location..."
	@bash -c " PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring poetry install"

run_producers:
	@echo "$(GREEN) [RUNNING] Data Gathering Pipeline Kafka Producers $(RESET)"
	@bash -c "poetry run python -m src.producer"

run_pipeline:
	@echo "$(GREEN) [RUNNING] Bytewax Pipeline $(RESET)"
	@bash -c "RUST_BACKTRACE=1 poetry run python -m bytewax.run src/start:flow"

clean_vdb:
	@echo "$(RED) [CLEANING] Upstash Vector DB $(RESET)"
	@bash -c "poetry run python -m src.helpers clean_vectordb"

run_ui:
	@echo "$(GREEN) [RUNNING] Streamlit UI interface $(RESET)"
	@bash -c "poetry run streamlit run ui.py"