#!/usr/bin/env python
from pathlib import Path
from inspect import currentframe
from ragger.navigator import NavInsID, NavIns
from bip_utils import Bip39SeedGenerator, Bip32Secp256k1
from conftest import wait_for_text, MNEMONIC, SearchStrings

home_txt: SearchStrings = {"nano": "Fantom", "stax": "This app confirms"}
pubkey_txt: SearchStrings = {"nano": "Exporting", "stax": "Export"}

def test_get_public_key(cmd,navigator,firmware,backend):
    wait_for_text(backend,firmware,home_txt)
    result: list = []

    bip32_path="m/44'/60'/0'/0/0"

    path = Path(currentframe().f_code.co_name)
    
    with cmd.get_public_key(bip32_path=bip32_path, result=result) as ex:
        wait_for_text(backend,firmware,pubkey_txt)
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK),NavIns(NavInsID.BOTH_CLICK)], screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)
        else:
            # sleep(3)
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545)),NavIns(NavInsID.TOUCH, (200,545)),NavIns(NavInsID.TOUCH, (200,545))], screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)
   
    # Verify received pubkey and chaincode.
    # Generate from mnemonic
    seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()
    bip32_ctx = Bip32Secp256k1.FromSeedAndPath(seed_bytes,bip32_path)
    
    assert result[0] == bip32_ctx.PublicKey().RawUncompressed()[33:] # Compare raw key last 32 bytes.
    assert result[1].hex() == bip32_ctx.PublicKey().ChainCode().ToHex()
