#!/usr/bin/env python
from pathlib import Path
from inspect import currentframe
from time import sleep
from ragger.navigator import NavInsID, NavIns
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from conftest import MNEMONIC, SearchStrings, wait_for_text

home_txt: SearchStrings = {"nano": "Fantom", "stax": "This app confirms"}
address_txt: SearchStrings = {"nano": "Address", "stax": "Verify"}

def test_get_address(cmd,navigator,firmware,backend):
    wait_for_text(backend,firmware,home_txt)
    result: list = []

    bip32_path="m/44'/60'/0'/0/0"

    path = Path(currentframe().f_code.co_name)
    
    with cmd.get_address(bip32_path=bip32_path, result=result) as ex:
        wait_for_text(backend,firmware,address_txt)
        if firmware.device == "nanos":
            intructions = [NavIns(NavInsID.RIGHT_CLICK),NavIns(NavInsID.RIGHT_CLICK),NavIns(NavInsID.BOTH_CLICK)]
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,intructions, screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)
        elif firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK)], screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545)),NavIns(NavInsID.TOUCH, (200,545))], screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)

    # Verify received address.
    # Generate from mnemonic
    seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM).DeriveDefaultPath()
    assert result[0].hex() == bip44_mst_ctx.PublicKey().ToAddress().lower()[2:]