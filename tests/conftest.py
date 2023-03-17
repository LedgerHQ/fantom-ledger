import pytest
from ragger.conftest import configuration
from fantom_client.fantom_cmd import FantomCommand
from time import time, sleep
from typing import TypedDict
###########################
### CONFIGURATION START ###
###########################
MNEMONIC = "glory promote mansion idle axis finger extra february uncover one trip resource lawn turtle enact monster seven myth punch hobby comfort wild raise skin"

configuration.OPTIONAL.BACKEND_SCOPE = "session"
configuration.OPTIONAL.CUSTOM_SEED = MNEMONIC

class SearchStrings(TypedDict):
    nano: str
    stax: str
    
def wait_for_text(backend,firmware,texts:SearchStrings,wait_until_not_displayed:bool = False):
    start = time()
    timeout = 25
    print(f"Wait for text ({wait_until_not_displayed}) : {texts[firmware.device[:4]]}")
    while wait_until_not_displayed == backend.compare_screen_with_text(texts[firmware.device[:4]]):
        # Give some time to other threads, and mostly Speculos one
        backend.wait_for_screen_change()
        if (time() - start > timeout):
            raise TimeoutError("Timeout waiting for home screen")            
    # Speculos has received at least one new event to redisplay the screen
    # Wait a bit to ensure the event batch is received and processed by Speculos before returning
    sleep(0.2)

@pytest.fixture()
def cmd(backend): 
    yield FantomCommand(client=backend,debug=True)

#########################
### CONFIGURATION END ###
#########################

# Pull all features from the base ragger conftest using the overridden configuration
pytest_plugins = ("ragger.conftest.base_conftest",)
