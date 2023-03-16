from ast import List
from contextlib import contextmanager
from typing import Tuple

from ragger.backend import BackendInterface

from fantom_client.fantom_cmd_builder import FantomCommandBuilder, InsType
from fantom_client.transaction import Transaction
from fantom_client.utils import parse_sign_response

class FantomCommand:
    def __init__(self,
                 client: BackendInterface,
                 debug: bool = False) -> None:
        self.client = client
        self.builder = FantomCommandBuilder(debug=debug)
    
    @contextmanager
    def get_public_key(self, bip32_path: str, result: List) -> None:
        chunk: bytes = self.builder.get_public_key(bip32_path=bip32_path)

        with self.client.exchange_async_raw(chunk) as e:
            yield e

        response = self.client.last_async_response
        
        assert len(response.data) == response.data[0]*2 + 1
        
        received_chaincode = response.data[33:]
        received_pubkey = bytearray(response.data[::-1][32:-1]) # Reverse byte order and take last 32 bytes.
        received_pubkey[0] = received_pubkey[0] - 0x80 # Last byte has 0x80 added to it in extractRawPublicKey, not explained in docs.

        result.append(received_pubkey)
        result.append(received_chaincode)

    @contextmanager
    def get_address(self, bip32_path: str, result: List) -> None:
        chunk: bytes = self.builder.get_address(bip32_path=bip32_path)

        with self.client.exchange_async_raw(chunk) as e:
            yield e

        response = self.client.last_async_response
        
        assert len(response.data) == response.data[0] + 1
        
        received_address = response.data[1:]

        result.append(received_address)
    
    @contextmanager
    def get_version(self, result: List) -> None:
        chunk: bytes = self.builder.get_version()

        with self.client.exchange_async_raw(chunk) as e:
            yield e

        response = self.client.last_async_response
        
        assert len(response.data) == 4
        m = response.data[0]
        n = response.data[1]
        p = response.data[2]

        result.append(m)
        result.append(n)
        result.append(p)

    @contextmanager
    def simple_sign_tx(self, transaction: Transaction) -> None:       
        chunk: bytes = self.builder.simple_sign_tx(transaction=transaction)
        with self.client.exchange_async_raw(chunk) as e:
            yield e
    
    @contextmanager
    def simple_sign_tx_finalize(self) -> None:            
        chunk: bytes = self.builder.simple_sign_tx_finalize()
        with self.client.exchange_async_raw(chunk) as e:
            yield e
    
    @contextmanager
    def simple_sign_tx_init(self, bip32_path: str) -> None:
        chunk: bytes = self.builder.simple_sign_tx_init(bip32_path=bip32_path)
        with self.client.exchange_async_raw(chunk) as e:
            yield e


