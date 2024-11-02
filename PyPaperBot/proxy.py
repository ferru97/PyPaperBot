import socket
import pyChainedProxy as socks

def proxy(pchain):

    chain = pchain

    socks.setdefaultproxy()
    for hop in chain:
        socks.adddefaultproxy(*socks.parseproxy(hop))

    rawsocket = socket.socket
    socket.socket = socks.socksocket
