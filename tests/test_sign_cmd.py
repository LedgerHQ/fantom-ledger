from time import sleep
from pathlib import Path
from inspect import currentframe
from fantom_client.transaction import Transaction
from ragger.navigator import NavInsID, NavIns
from ragger.backend import RaisePolicy
from ragger.error import ExceptionRAPDU
from conftest import wait_for_text, SearchStrings

NANOS_NAV_INSTRUCTIONS = [NavIns(NavInsID.RIGHT_CLICK),
                         NavIns(NavInsID.RIGHT_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.RIGHT_CLICK),
                         NavIns(NavInsID.RIGHT_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.RIGHT_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK)]

NANOXSP_NAV_INSTRUCTIONS = [
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK),
                         NavIns(NavInsID.BOTH_CLICK)]

home_txt: SearchStrings = {"nano": "Fantom", "stax": "This app confirms"}
loading_txt: SearchStrings = {"nano": "Please", "stax": "Loading"}

def test_sign_simple(cmd,navigator,firmware,backend):
    wait_for_text(backend,firmware,home_txt)
    bip32_path="m/44'/60'/1'/0/0"

    transaction = Transaction(
        txType=0xEB,
        nonce=68,
        gasPrice=0x0306dc4200,
        gasLimit=0x5208,
        to="0x5a321744667052affa8386ed49e00ef223cbffc3",
        value=0x6f9c9e7bf61818,
        chainID=0xfa,
    )
    path = Path(currentframe().f_code.co_name)
    
    with cmd.simple_sign_tx_init(bip32_path=bip32_path) as ex:
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK)],screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545))],screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    with cmd.simple_sign_tx_finalize() as ex:
        wait_for_text(backend,firmware,loading_txt,wait_until_not_displayed=True)
        path = Path(str(path)+"_finalize")
        if firmware.device == "nanos":
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOS_NAV_INSTRUCTIONS,screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
        elif firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOXSP_NAV_INSTRUCTIONS,screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
        else:
            navigator.navigate_until_text_and_compare(NavIns(NavInsID.TOUCH, (200,545)),[NavIns(NavInsID.USE_CASE_REVIEW_CONFIRM)],"Hold",
                                                            Path(__file__).parent.resolve(),path,
                                                            screen_change_before_first_instruction = False,
                                                            screen_change_after_last_instruction = False)


def test_sign_warning_unusual(cmd,navigator,firmware,backend):
    wait_for_text(backend,firmware,home_txt)
    
    bip32_path="m/44'/60'/1/0/0" # Unhardened account ID.

    transaction = Transaction(
        txType=0xEB,
        nonce=68,
        gasPrice=0x0306dc4200,
        gasLimit=0x5208,
        to="0x5a321744667052affa8386ed49e00ef223cbffc3",
        value=0x6f9c9e7bf61818,
        chainID=0xfa,
    )
    path = Path(currentframe().f_code.co_name)
    
    with cmd.simple_sign_tx_init(bip32_path=bip32_path) as ex:
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK),NavIns(NavInsID.BOTH_CLICK)], screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545)),NavIns(NavInsID.TOUCH, (200,545))],screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    with cmd.simple_sign_tx_finalize() as ex:
        wait_for_text(backend,firmware,loading_txt,wait_until_not_displayed=True)
        path = Path(str(path)+"_finalize")
        if firmware.device == "nanos":
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOS_NAV_INSTRUCTIONS, screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
        elif firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOXSP_NAV_INSTRUCTIONS, screen_change_before_first_instruction = False, screen_change_after_last_instruction = False)
        else:
            navigator.navigate_until_text_and_compare(NavIns(NavInsID.TOUCH, (200,545)),[NavIns(NavInsID.USE_CASE_REVIEW_CONFIRM)],"Hold",
                                                            Path(__file__).parent.resolve(),path,
                                                            screen_change_before_first_instruction = False,
                                                            screen_change_after_last_instruction = False)


def test_sign_reject_by_user(cmd,navigator,backend,firmware):
    wait_for_text(backend,firmware,home_txt)

    bip32_path="m/44'/60'/1'/0/0"

    transaction = Transaction(
        txType=0xEB,
        nonce=0,
        gasPrice=0x0306dc4200,
        gasLimit=0x5208,
        to="0x5a321744667052affa8386ed49e00ef223cbffc3",
        value=0x6f9c9e7bf61818,
        chainID=0xfa,
    )
    
    path = Path(currentframe().f_code.co_name)
    with cmd.simple_sign_tx_init(bip32_path=bip32_path) as ex:
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK)], screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545))],screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    try:
        with cmd.simple_sign_tx_finalize() as ex:
            wait_for_text(backend,firmware,loading_txt,wait_until_not_displayed=True)
            path = Path(str(path)+"_finalize")
            backend.raise_policy = RaisePolicy.RAISE_ALL
            if firmware.device == "nanos":
                Instructions = NANOS_NAV_INSTRUCTIONS[:]
                Instructions.insert(-1,NavIns(NavInsID.RIGHT_CLICK))
                navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,Instructions,screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
            elif firmware.device.startswith("nano"):
                Instructions = NANOXSP_NAV_INSTRUCTIONS[:]
                Instructions.insert(-1,NavIns(NavInsID.RIGHT_CLICK))
                navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,Instructions,screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
            else:
                navigator.navigate_until_text_and_compare(NavIns(NavInsID.TOUCH, (200,545)),
                                                          [NavIns(NavInsID.USE_CASE_REVIEW_REJECT),NavIns(NavInsID.TOUCH, (200,545))],
                                                          "Hold",
                                                          Path(__file__).parent.resolve(),
                                                          path,
                                                          screen_change_before_first_instruction = False,
                                                          screen_change_after_last_instruction = False)

    except ExceptionRAPDU as rapdu:
        assert (rapdu.status == 0x6E07)
        
    
def test_sign_wrong_chain_id(cmd,navigator,backend,firmware):    
    wait_for_text(backend,firmware,home_txt)    

    bip32_path="m/44'/60'/1'/0/0"

    transaction = Transaction(
        txType=0xEB,
        nonce=0,
        gasPrice=0x0306dc4200,
        gasLimit=0x5208,
        to="0x5a321744667052affa8386ed49e00ef223cbffc3",
        value=0x6f9c9e7bf61818,
        chainID=0xf9,
    )

    backend.raise_policy = RaisePolicy.RAISE_ALL_BUT_0x9000
    with cmd.simple_sign_tx_init(bip32_path=bip32_path) as ex:
        backend.wait_for_screen_change()
        sleep(0.5) # Just to be sure screen is properly displayed.
        if firmware.device.startswith("nano"):
            navigator.navigate([NavIns(NavInsID.BOTH_CLICK)])
        else:
            navigator.navigate([NavIns(NavInsID.TOUCH, (200,545))])
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
    try:
        with cmd.simple_sign_tx_finalize() as ex:
            pass
    except ExceptionRAPDU as rapdu:
        assert (rapdu.status == 0x6E06)
