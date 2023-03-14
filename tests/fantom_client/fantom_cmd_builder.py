import enum
import logging
import struct
from typing import List, Tuple, Union, Iterator, cast

from fantom_client.transaction import Transaction
from ragger.bip import pack_derivation_path

MAX_APDU_LEN: int = 255

def chunked(size, source):
    for i in range(0, len(source), size):
        yield source[i:i+size]

def chunkify(data: bytes, chunk_len: int) -> Iterator[Tuple[bool, bytes]]:
    size: int = len(data)

    if size <= chunk_len:
        yield True, data
        return

    chunk: int = size // chunk_len
    remaining: int = size % chunk_len
    offset: int = 0

    for i in range(chunk):
        yield False, data[offset:offset + chunk_len]
        offset += chunk_len

    if remaining:
        yield True, data[offset:]

class InsType(enum.IntEnum):
    INS_GET_APP_VER             = 0x01
    INS_GET_PUBLIC_KEY          = 0x10
    INS_GET_ADDRESS             = 0x11
    INS_SIGN_TX                 = 0x20

class FantomCommandBuilder:
    """APDU command builder.

    Parameters
    ----------
    debug: bool
        Whether you want to see logging or not.

    Attributes
    ----------
    debug: bool
        Whether you want to see logging or not.

    """
    CLA: int = 0xE0

    def __init__(self, debug: bool = False):
        """Init constructor."""
        self.debug = debug

    def serialize(self,
                  cla: int,
                  ins: Union[int, enum.IntEnum],
                  p1: int = 0,
                  p2: int = 0,
                  cdata: bytes = b"") -> bytes:
        """Serialize the whole APDU command (header + data).

        Parameters
        ----------
        cla : int
            Instruction class: CLA (1 byte)
        ins : Union[int, IntEnum]
            Instruction code: INS (1 byte)
        p1 : int
            Instruction parameter 1: P1 (1 byte).
        p2 : int
            Instruction parameter 2: P2 (1 byte).
        cdata : bytes
            Bytes of command data.

        Returns
        -------
        bytes
            Bytes of a complete APDU command.

        """
        ins = cast(int, ins.value) if isinstance(ins, enum.IntEnum) else cast(int, ins)

        header: bytes = struct.pack("BBBBB",
                                    cla,
                                    ins,
                                    p1,
                                    p2,
                                    len(cdata))  # add Lc to APDU header

        if self.debug:
            logging.info("header: %s", header.hex())
            logging.info("cdata:  %s", cdata.hex())

        return header + cdata

    def get_public_key(self, bip32_path: str) -> bytes:
        """Command builder for INS_GET_PUBLIC_KEY.

        Parameters
        ----------
        bip32_path: str
            String representation of BIP32 path.
        display : bool
            Whether you want to display the address on the device.

        Returns
        -------
        bytes
            APDU command for INS_GET_PUBLIC_KEY.

        """
        cdata = pack_derivation_path(bip32_path)
          
        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_GET_PUBLIC_KEY,
                              p1=0x00,
                              p2=0x00,
                              cdata=cdata)
    
    def get_address(self, bip32_path: str) -> bytes:
        """Command builder for INS_GET_ADDRESS.

        Parameters
        ----------
        bip32_path: str
            String representation of BIP32 path.
        display : bool
            Whether you want to display the address on the device.

        Returns
        -------
        bytes
            APDU command for INS_GET_ADDRESS.

        """
        cdata = pack_derivation_path(bip32_path)
        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_GET_ADDRESS,
                              p1=0x02, # Display address
                              p2=0x00,
                              cdata=cdata)
    
    def get_version(self) -> bytes:
        """Command builder for INS_GET_APP_VER.
        Parameters
        ----------
        bip32_path: str
            String representation of BIP32 path.
        display : bool
            Whether you want to display the address on the device.

        Returns
        -------
        bytes
            APDU command for INS_GET_APP_VER.

        """
        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_GET_APP_VER,
                              p1=0x00,
                              p2=0x00)

    def simple_sign_tx(self, transaction: Transaction) -> bytes:
        """Command builder for INS_SIGN_TX.

        Parameters
        ----------
        transaction : Transaction
            Representation of the transaction to be signed.

        Yields
        -------
        bytes
            APDU command chunk for INS_SIGN_TX.

        """
        
        tx: bytes = transaction.serialize()

        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_SIGN_TX,
                              p1=0x01,
                              p2=0x00,
                              cdata=tx)
    
    def simple_sign_tx_finalize(self) -> bytes:
        """Command builder for INS_SIGN_TX.

        Parameters
        ----------
        transaction : Transaction
            Representation of the transaction to be signed.

        Yields
        -------
        bytes
            APDU command chunk for INS_SIGN_TX.

        """

        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_SIGN_TX,
                              p1=0x80,
                              p2=0x00)

    def simple_sign_tx_init(self, bip32_path: str) -> bytes:
        """Command builder for INS_SIGN_TX.

        Parameters
        ----------
        bip32_path : str
            String representation of BIP32 path.

        Yields
        -------
        bytes
            APDU command chunk for INS_SIGN_TX.

        """
        cdata = pack_derivation_path(bip32_path)
        
        return self.serialize(cla=self.CLA,
                              ins=InsType.INS_SIGN_TX,
                              p1=0x00,
                              p2=0x00,
                              cdata=cdata)