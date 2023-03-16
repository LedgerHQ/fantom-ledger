import pytest
from ragger.conftest import configuration
from fantom_client.fantom_cmd import FantomCommand

###########################
### CONFIGURATION START ###
###########################
MNEMONIC = "glory promote mansion idle axis finger extra february uncover one trip resource lawn turtle enact monster seven myth punch hobby comfort wild raise skin"

configuration.OPTIONAL.BACKEND_SCOPE = "session"
configuration.OPTIONAL.CUSTOM_SEED = MNEMONIC

@pytest.fixture()
def cmd(backend): 
    yield FantomCommand(client=backend,debug=True)

#########################
### CONFIGURATION END ###
#########################

# Pull all features from the base ragger conftest using the overridden configuration
pytest_plugins = ("ragger.conftest.base_conftest",)
