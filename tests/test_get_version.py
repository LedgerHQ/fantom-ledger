#!/usr/bin/env python
import re
from pathlib import Path
from conftest import wait_for_text, SearchStrings

home_txt: SearchStrings = {"nano": "Fantom", "stax": "This app confirms"}

def get_makefile_version():
    path = str(Path(__file__).parent.parent.resolve()) + "/Makefile"
    makefile = open(path, "r").read()
    major = re.findall("(APPVERSION_M=)(.*)", makefile)[0][1]
    minor = re.findall("(APPVERSION_N=)(.*)", makefile)[0][1]
    patch = re.findall("(APPVERSION_P=)(.*)", makefile)[0][1]
    return major,minor,patch
    
def test_get_version(cmd,firmware,backend):
    wait_for_text(backend,firmware,home_txt)
    
    result: list = []
    
    m,n,p = get_makefile_version()

    with cmd.get_version(result=result) as ex:
        pass

    assert int(m) == result[0]
    assert int(n) == result[1]
    assert int(p) == result[2]
