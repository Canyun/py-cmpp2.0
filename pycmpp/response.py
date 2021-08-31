from pycmpp.cmpp_defines import *
from pycmpp.utils import Unpack, Pack


class ResponseInstance(object):
    length = 0
    command_id = 0
    seq_id = -1
    raw_message_body = b''

    def resolve(self, response_message):
        """
        解析消息
        :param response_message:
        :return:
        """
        raise NotImplementedError()

    def create(self, seq_id):
        """
        创建响应
        :param seq_id:
        :return:
        """
        raise NotImplementedError()


class ConnectResponseInstance(ResponseInstance):
    status = -1
    authenticator_ISMG = None
    version = None

    def resolve(self, response_message):
        message_body = response_message[12:]
        self.status, = Unpack.get_unsigned_char_data(message_body[0:1])
        self.authenticator_ISMG = message_body[1:17]
        self.version, = Unpack.get_unsigned_char_data(message_body[17:18])

    def create(self, seq_id):
        pass


class TerminateResponseInstance(ResponseInstance):
    def resolve(self, response_message):
        pass

    def create(self, seq_id):
        pass


class SubmitResponseInstance(ResponseInstance):
    msg_id = None
    status = -1

    def resolve(self, response_message):
        message_body = response_message[12:]
        self.msg_id, = Unpack.get_unsigned_long_long_data(message_body[0:8])
        self.status, = Unpack.get_unsigned_char_data(message_body[8:9])

    def create(self, seq_id):
        pass


class ActiveTestResponseInstance(ResponseInstance):
    command_id = CMPP_ACTIVE_TEST_RESP
    length = 13
    reverse = b'0x00'

    def create(self, seq_id):
        return Pack.get_unsigned_long_data(self.length) + Pack.get_unsigned_long_data(
            self.command_id) + Pack.get_unsigned_long_data(seq_id) + self.reverse

    def resolve(self, response_message):
        pass
