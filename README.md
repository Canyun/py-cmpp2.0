# PyCmpp

## 置顶

Forked From https://github.com/zhanghongchuang/py-cmpp2.0  
在这个项目的基础上改了不少代码，支持发送超长短信，只测试过cmpp2.0  
根据[CMPP协议](https://www.kannel.org/~tolj/specs/CMPP2/CMPP-2.0.pdf), 只实现了以下消息的交互:

| command_id | 说明 |
|---|---|
| 0x00000001  | 请求连接  |
| 0x80000001  | 请求连接应答  |
| 0x00000002  | 终止连接  |
| 0x80000002  | 终止连接应答  |
| 0x00000004  | 提交短信  |
| 0x80000004  | 提交短信应答  |
| 0x00000008  | 激活测试  |
| 0x80000008  | 激活测试应答  |

## 安装方法

```shell
pip install pycmpp
```