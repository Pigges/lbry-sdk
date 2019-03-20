from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict


class Signable:

    __slots__ = (
        'message', 'version', 'signature',
        'signature_type', 'unsigned_payload', 'signing_channel_id'
    )

    message_class = None

    def __init__(self, message=None):
        self.message = message or self.message_class()
        self.version = 2
        self.signature = None
        self.signature_type = 'SECP256k1'
        self.unsigned_payload = None
        self.signing_channel_id = None

    @property
    def is_undetermined(self):
        return self.message.WhichOneof('type') is None

    @property
    def is_signed(self):
        return self.signature is not None

    def to_dict(self):
        return MessageToDict(self.message)

    def to_message_bytes(self) -> bytes:
        return self.message.SerializeToString()

    def to_bytes(self) -> bytes:
        pieces = bytearray()
        if self.is_signed:
            pieces.append(1)
            pieces.extend(self.signing_channel_id)
            pieces.extend(self.signature)
        else:
            pieces.append(0)
        pieces.extend(self.to_message_bytes())
        return bytes(pieces)

    @classmethod
    def from_bytes(cls, data: bytes):
        signable = cls()
        if data[0] == 0:
            signable.message.ParseFromString(data[1:])
        elif data[0] == 1:
            signable.signing_channel_id = data[1:21]
            signable.signature = data[21:85]
            signable.message.ParseFromString(data[85:])
        else:
            raise DecodeError('Could not determine message format version.')
        return signable

    def __len__(self):
        return len(self.to_bytes())

    def __bytes__(self):
        return self.to_bytes()
