from time import sleep
from pathlib import Path
from inspect import currentframe
from fantom_client.transaction import Transaction
from ragger.navigator import NavInsID, NavIns
from ragger.backend import RaisePolicy
from ragger.error import ExceptionRAPDU

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

def test_sign_simple(cmd,navigator,firmware):
    if firmware.device == "stax":
        sleep(4) # Wait for idle menu to be displayed to get back in correct state.
    else:
        sleep(1)
    
    bip32_path="44'/60'/1'/0/0"

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
        sleep(1)
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK)],screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545))],screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    with cmd.simple_sign_tx_finalize() as ex:
        sleep(3) # Wait for loading screen to disappear.
        path = Path(str(path)+"_finalize")
        if firmware.device == "nanos":
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOS_NAV_INSTRUCTIONS,screen_change_after_last_instruction = False)
        elif firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOXSP_NAV_INSTRUCTIONS,screen_change_after_last_instruction = False)
        else:
            navigator.navigate_until_text_and_compare(NavIns(NavInsID.TOUCH, (200,545)),[NavIns(NavInsID.USE_CASE_REVIEW_CONFIRM)],"Hold",
                                                            Path(__file__).parent.resolve(),path,
                                                            screen_change_before_first_instruction = False,
                                                            screen_change_after_last_instruction = False)


def test_sign_warning_unusual(cmd,navigator,firmware):
    sleep(1)
    
    bip32_path="44'/60'/1/0/0" # Unhardened account ID.

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
        sleep(0.5)
        if firmware.device.startswith("nano"):
            pass
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK),NavIns(NavInsID.BOTH_CLICK)], screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545)),NavIns(NavInsID.TOUCH, (200,545))],screen_change_before_first_instruction = False,screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    with cmd.simple_sign_tx_finalize() as ex:
        sleep(2) # Wait for loading screen to disappear.
        path = Path(str(path)+"_finalize")
        if firmware.device == "nanos":
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOS_NAV_INSTRUCTIONS,screen_change_after_last_instruction = False)
        elif firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,NANOXSP_NAV_INSTRUCTIONS,screen_change_after_last_instruction = False)
        else:
            navigator.navigate_until_text_and_compare(NavIns(NavInsID.TOUCH, (200,545)),[NavIns(NavInsID.USE_CASE_REVIEW_CONFIRM)],"Hold",
                                                            Path(__file__).parent.resolve(),path,
                                                            screen_change_before_first_instruction = False,
                                                            screen_change_after_last_instruction = False)


def test_sign_reject_by_user(cmd,navigator,backend,firmware):
    bip32_path="44'/60'/1'/0/0"

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
        sleep(0.5)
        if firmware.device.startswith("nano"):
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.BOTH_CLICK)],screen_change_after_last_instruction = False)
        else:
            navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,[NavIns(NavInsID.TOUCH, (200,545))],screen_change_after_last_instruction = False)
        
    with cmd.simple_sign_tx(transaction=transaction) as ex:
        pass
        
    try:
        with cmd.simple_sign_tx_finalize() as ex:
            sleep(2) # Wait for loading screen to disappear.
            path = Path(str(path)+"_finalize")
            backend.raise_policy = RaisePolicy.RAISE_ALL
            if firmware.device == "nanos":
                Instructions = NANOS_NAV_INSTRUCTIONS[:]
                Instructions.insert(-1,NavIns(NavInsID.RIGHT_CLICK))
                navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,Instructions,screen_change_after_last_instruction = False)
            elif firmware.device.startswith("nano"):
                Instructions = NANOXSP_NAV_INSTRUCTIONS[:]
                Instructions.insert(-1,NavIns(NavInsID.RIGHT_CLICK))
                navigator.navigate_and_compare(Path(__file__).parent.resolve(),path,Instructions,screen_change_after_last_instruction = False)
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
    bip32_path="44'/60'/1'/0/0"

    transaction = Transaction(
        txType=0xEB,
        nonce=0,
        gasPrice=0x0306dc4200,
        gasLimit=0x5208,
        to="0x5a321744667052affa8386ed49e00ef223cbffc3",
        value=0x6f9c9e7bf61818,
        chainID=0xf9,
    )

    sleep(3) # Wait to get back on the idle menu so currentIns == INS_NONE
    backend.raise_policy = RaisePolicy.RAISE_ALL_BUT_0x9000
    with cmd.simple_sign_tx_init(bip32_path=bip32_path) as ex:
        sleep(0.5)
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
