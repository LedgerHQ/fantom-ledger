import pytest
from ragger.conftest import configuration
from fantom_client.fantom_cmd import FantomCommand
from time import time, sleep
###########################
### CONFIGURATION START ###
###########################
MNEMONIC = "glory promote mansion idle axis finger extra february uncover one trip resource lawn turtle enact monster seven myth punch hobby comfort wild raise skin"

configuration.OPTIONAL.BACKEND_SCOPE = "session"
configuration.OPTIONAL.CUSTOM_SEED = MNEMONIC

def wait_for_home_screen(backend,firmware):
    start = time()
    timeout = 25
    home_screen_text = "Fantom"
    if firmware.device == "stax":
        home_screen_text = "This app confirms"
    while not backend.compare_screen_with_text(home_screen_text):
        # Give some time to other threads, and mostly Speculos one
        backend.wait_for_screen_change()
        if (time() - start > timeout):
            raise TimeoutError("Timeout waiting for home screen")            
    # Speculos has received at least one new event to redisplay the screen
    # Wait a bit to ensure the event batch is received and processed by Speculos before returning
    sleep(0.2)

def wait_loading_screen(backend,firmware):
    start = time()
    timeout = 25
    home_screen_text = "Please"
    if firmware.device == "stax":
        home_screen_text = "Loading"
    while backend.compare_screen_with_text(home_screen_text):
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
