import sys
import threading
from logging.config import dictConfig

from pycmpp.cmpp import Cmpp

log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}][{levelname}][{pathname}:{lineno:d}]: {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'pycmpp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

dictConfig(log_config)

if __name__ == '__main__':
    client = Cmpp(
        host="127.0.0.1",
        port=8855,
        sp_id='300250',
        sp_secret='300250',
        src_id='10658300250'
    )
    content = """[紧急告警]已经恢复:\n告警名称：程序数据包溢出\n发生时间：2021-08-31 13:20:00\n告警内容：溢出包数0\n告警对象：192.10.23.122,se-dos"""
    threading.Timer(3, client.submit, (content, ["15059171009"])).start()
    client.run()
