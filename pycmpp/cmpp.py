import logging
import socket
import threading
import time
from queue import Queue

from pycmpp import handlers
from pycmpp.cmpp_defines import *
from pycmpp.request import (
    ConnectRequestInstance,
    TerminateRequestInstance,
    SubmitRequestInstance,
    ActiveTestRequestInstance
)
from pycmpp.utils import Unpack, split_message, Pack

TIMEOUT_CONNECT_TIMES = 3

logger = logging.getLogger(__name__)


class Cmpp(object):
    def __init__(self,
                 host: str,
                 port: int,
                 sp_id: str,
                 sp_secret: str,
                 src_id: str,
                 delivery: str = 0,
                 client_heartbeat=True):
        """
        :param host: Gateway IP
        :param port: Gateway port
        :param sp_id: Service provider id
        :param sp_secret: Service provider secret
        :param src_id: src_id
        :param delivery: delivery
        :param client_heartbeat: client_heartbeat
        """
        self.host = host
        self.port = port
        self.sp_id = sp_id
        self.sp_secret = sp_secret
        self.src_id = src_id
        self.delivery = delivery
        self.client_heartbeat = client_heartbeat
        self.so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._thread_receive = None
        self._thread_heartbeat = None
        self.send_queue = Queue(maxsize=999)
        self.handlers = self.load_handlers()

    @staticmethod
    def load_handlers():
        _handlers = {}
        for c in handlers.__all__:
            handler_cls = getattr(handlers, c, None)
            _handlers[handler_cls.command_id] = handler_cls
        return _handlers

    def submit(self, content, phone_list):
        """
        超长短信需要携带6个字节的协议头 05 00 03 XX MM NN；这6个字节占用短信内容长度；
        byte 1 : 05, 表示剩余协议头的长度
        byte 2 : 00, 这个值在GSM 03.40规范9.2.3.24.1中规定，表示随后的这批超长短信的标识位长度为1（格式中的XX值）。
        byte 3 : 03, 这个值表示剩下短信标识的长度
        byte 4 : XX，这批短信的唯一标志，事实上，SME(手机或者SP)把消息合并完之后，就重新记录，所以这个标志是否唯一并不是很重要。
        byte 5 : MM, 这批短信的数量。如果一个超长短信总共5条，这里的值就是5。
        byte 6 : NN, 这批短信的数量。如果当前短信是这批短信中的第一条的值是1，第二条的值是2。

        :param content:
        :param phone_list:
        :return:
        """
        if len(content) < 70:
            req = SubmitRequestInstance()
            msg = req.create(
                msg_src=self.sp_id,
                msg_content=content,
                dest_terminal_id=phone_list,
                registered_delivery=self.delivery
            )
            logger.info(f'发送短信; msg: {msg}')
            self.send(msg)
        else:
            messages = split_message(content)
            for i, message in enumerate(messages):
                message_head = (
                        Pack.get_unsigned_char_data(5) +
                        Pack.get_unsigned_char_data(0) +
                        Pack.get_unsigned_char_data(3) +
                        Pack.get_unsigned_char_data(0) +
                        Pack.get_unsigned_char_data(len(messages)) +
                        Pack.get_unsigned_char_data(i + 1)
                )

                req = SubmitRequestInstance()
                msg = req.create(
                    msg_src=self.sp_id,
                    msg_content=message,
                    msg_head=message_head,
                    dest_terminal_id=phone_list,
                    pk_total=len(messages),
                    pk_number=i + 1,
                    registered_delivery=self.delivery,
                    tp_pid=1,
                    tp_udhi=1
                )
                logger.info(f'发送超长短信; total: {len(messages)}; number: {i}; msg: {msg}')
                self.send(msg)

    # def send_message(self):
    #     while True:
    #         targets, message = self.send_queue.get()
    #         print(message)
    #         self.submit(message, targets)

    def auth(self):
        req = ConnectRequestInstance()
        message = req.create(self.sp_id, self.sp_secret)
        self.send(message)
        logger.debug(f'认证请求; sp_id: {self.sp_id}; password: {self.sp_secret}; request: {message}')

    def terminate(self):
        self.send(TerminateRequestInstance().create())

    def connect(self):
        self.so.connect((self.host, self.port))

    def send(self, message):
        self.so.send(message)

    def receive(self):
        while True:
            # 先接收12字节的消息头
            header = self.so.recv(12)
            if header:
                try:
                    msg_length, = Unpack.get_unsigned_long_data(header[0:4])
                    command_id, = Unpack.get_unsigned_long_data(header[4:8])
                    hex_command_id = hex(command_id)
                    seq_id, = Unpack.get_unsigned_long_data(header[8:12])
                except Exception as e:
                    logger.error(f'无法识别的消息头; msg: {header}; error: {str(e)}')
                    continue

                message = header + self.so.recv(msg_length - 12)
                logger.info(f'接收消息; command: {hex_command_id}; seq_id: {seq_id}; length: {msg_length}; msg: {message}')
                if command_id not in ALL_MESSAGES:
                    logger.error(f'未知的消息类型; command: {hex_command_id}; seq_id: {seq_id}')
                    continue

                handler_cls = self.handlers.get(command_id)
                if handler_cls is None:
                    logger.error(f'未找到Handler; command: {hex_command_id}; seq_id: {seq_id}')
                    continue
                try:
                    handler = handler_cls(self, message)
                    handler()
                    logger.info(f'消息处理完成; command: {hex_command_id}; seq_id: {seq_id}')
                except Exception as e:
                    logger.error(f'消息处理失败; command: {hex_command_id}; seq_id: {seq_id}; error: {str(e)}')

    def close(self):
        self.so.close()

    def heartbeat(self):
        times = 0
        while True:
            try:
                self.send(ActiveTestRequestInstance().create())
            except Exception as e:
                logger.error(str(e))
                if times >= TIMEOUT_CONNECT_TIMES:
                    times = 0
                    self.reconnect()
                    logger.debug('重新连接服务器')
            finally:
                times += 1
                time.sleep(60)

    def reconnect(self):
        self.close()
        self.connect()
        self.auth()

    def disconnect(self):
        self.terminate()
        self.close()

    def _start_thread_heartbeat(self):
        t = threading.Thread(target=self.heartbeat)
        t.start()

    def run(self):
        self.connect()
        self.auth()
        if self.client_heartbeat:
            self._start_thread_heartbeat()
        self.receive()
