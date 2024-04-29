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
