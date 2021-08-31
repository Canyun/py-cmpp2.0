# REQUEST_MAPPING = {
#     CMPP_ACTIVE_TEST_REQ: None,
#     CMPP_TERMINATE_REQ: None
# }
#
import logging

from pycmpp.request import *
from pycmpp.response import *

__all__ = [
    'CmppConnectRespHandler',
    'CmppActiveTestReqHandler',
    'CmppActiveTestRespHandler',
    'CmppSubmitRespHandler'
]

logger = logging.getLogger(__name__)


class BaseHandler(object):
    command_id = 0x0

    def __init__(self, cmpp, message, **kwargs):
        self.cmpp = cmpp
        self.message = message


class CmppConnectRespHandler(BaseHandler):
    command_id = CMPP_CONNECT_RESP

    def __call__(self, *args, **kwargs):
        resp = ConnectResponseInstance()
        resp.resolve(self.message)
        if resp.status == 0:
            logger.info("短信网关连接成功")
        else:
            logger.error(f"短信网关连接失败; status: {resp.status}")


class CmppActiveTestReqHandler(BaseHandler):
    command_id = CMPP_ACTIVE_TEST_REQ

    def __call__(self, *args, **kwargs):
        req = ActiveTestRequestInstance()
        req.resolve(self.message)
        resp = ActiveTestResponseInstance()
        self.cmpp.send(resp.create(req.seq_id))


class CmppActiveTestRespHandler(BaseHandler):
    command_id = CMPP_ACTIVE_TEST_RESP

    def __call__(self, *args, **kwargs):
        logger.info('heartbeat')


class CmppSubmitRespHandler(BaseHandler):
    command_id = CMPP_SUBMIT_RESP
    error_map = {
        1: "消息结构错",
        2: "命令字错",
        3: "消息序号重复",
        4: "消息长度错",
        5: "资费代码错",
        6: "超过最大信息长",
        7: "业务代码错",
        8: "流量控制错",
    }

    def __call__(self, *args, **kwargs):
        resp = SubmitResponseInstance()
        resp.resolve(self.message)
        if resp.status == 0:
            logger.info(f'发送成功; msg_id: {resp.msg_id}')
        else:
            error = self.error_map.get(resp.status, '其它错误')
            logger.info(f'发送失败; msg_id: {resp.msg_id}; error: {error}')
