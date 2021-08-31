from pycmpp import utils
from pycmpp.cmpp_defines import *
from pycmpp.utils import Pack, decode_headers

_global_sep_no = 1


class RequestInstance(object):
    command_id = None
    length = 0
    seq_id = -1

    def get_headers(self, body_length=0):
        return (
                Pack.get_unsigned_long_data(body_length + 12) +
                Pack.get_unsigned_long_data(self.command_id) +
                Pack.get_unsigned_long_data(utils.get_sequence_no())
        )

    def resolve(self, request_message):
        """
        解析消息
        :param request_message:
        :return:
        """
        raise NotImplementedError()

    def create(self, *args, **kwargs):
        """
        生成请求
        :param sp_id:
        :param sp_secret:
        :param message:
        :return:
        """
        raise NotImplementedError()


class ConnectRequestInstance(RequestInstance):
    auth_source = None
    command_id = CMPP_CONNECT_REQ

    def resolve(self, request_message):
        pass

    def create(self, sp_id, sp_secret):
        _version = Pack.get_unsigned_char_data(CMPP_VERSION)
        _sp_id = sp_id.encode('utf-8')
        _sp_secret = sp_secret.encode("utf-8")
        _time_str = utils.get_string_time()
        self.auth_source = utils.get_md5_digest(
            _sp_id + 9 * b'\x00' + _sp_secret + _time_str.encode("utf-8")
        )
        message_body = _sp_id + self.auth_source + _version + Pack.get_unsigned_long_data(int(_time_str))

        return self.get_headers(len(message_body)) + message_body


class TerminateRequestInstance(RequestInstance):
    command_id = CMPP_TERMINATE_REQ

    def create(self, sp_id=None, sp_secret=None, message=None):
        return self.get_headers()

    def resolve(self, request_message):
        pass


class SubmitRequestInstance(RequestInstance):
    command_id = CMPP_SUBMIT_REQ

    def create(self,
               msg_src,
               msg_content,
               dest_terminal_id,
               msg_head=None,
               src_id='',
               pk_total=1,
               pk_number=1,
               registered_delivery=0,
               msg_level=0,
               service_id='',
               fee_usertype=2,
               fee_terminal_id="",
               tp_pid=0,
               tp_udhi=0,
               msg_fmt=8,
               feetype='01',
               feecode='000000',
               valid_time=17 * '\x00',
               at_time=17 * '\x00',
               sep_no=None):

        if len(msg_content) >= 70:
            raise ValueError("msg_content more than 70 words")
        if len(dest_terminal_id) > 100:
            raise ValueError("single submit more than 100 phone numbers")
        if not dest_terminal_id:
            raise ValueError("phone number can not be null")

        _msg_id = 8 * b'\x00'
        _pk_total = Pack.get_unsigned_char_data(pk_total)
        _pk_number = Pack.get_unsigned_char_data(pk_number)
        _registered_delivery = Pack.get_unsigned_char_data(registered_delivery)
        _msg_level = Pack.get_unsigned_char_data(msg_level)
        _service_id = (service_id + (10 - len(service_id)) * '\x00').encode(
            'utf-8')
        _fee_usertype = Pack.get_unsigned_char_data(fee_usertype)
        _fee_terminal_id = (fee_terminal_id + (
                21 - len(fee_terminal_id)) * '\x00').encode('utf-8')
        _tp_pid = Pack.get_unsigned_char_data(tp_pid)
        _tp_udhi = Pack.get_unsigned_char_data(tp_udhi)
        _msg_fmt = Pack.get_unsigned_char_data(msg_fmt)
        _msg_src = msg_src.encode('utf-8')
        _feetype = feetype.encode('utf-8')
        _feecode = feecode.encode('utf-8')
        _valid_time = valid_time.encode('utf-8')
        _at_time = at_time.encode('utf-8')
        _src_id = (src_id + (21 - len(src_id)) * '\x00').encode('utf-8')
        _destusr_tl = Pack.get_unsigned_char_data(len(dest_terminal_id))
        _dest_terminal_id = b""
        for msisdn in dest_terminal_id:
            _dest_terminal_id += (msisdn + (21 - len(msisdn)) * '\x00').encode(
                'utf-8')

        if msg_head:
            _msg_content = msg_head + msg_content.encode('utf-16-be')
        else:
            _msg_content = msg_content.encode('utf-16-be')
        _msg_length = Pack.get_unsigned_char_data(len(_msg_content))
        _reserve = 8 * b'\x00'
        _message_body = _msg_id + _pk_total + _pk_number + \
                        _registered_delivery + _msg_level + _service_id + \
                        _fee_usertype + _fee_terminal_id + _tp_pid + _tp_udhi + _msg_fmt + _msg_src + _feetype \
                        + _feecode + _valid_time + _at_time + _src_id + \
                        _destusr_tl + _dest_terminal_id \
                        + _msg_length + _msg_content + _reserve

        return self.get_headers(len(_message_body)) + _message_body

    def resolve(self, request_message):
        pass


class ActiveTestRequestInstance(RequestInstance):
    command_id = CMPP_ACTIVE_TEST_REQ

    def create(self, sp_id=None, sp_secret=None):
        return self.get_headers()

    def resolve(self, request_message):
        self.length, self.command_id, self.seq_id = decode_headers(request_message)
