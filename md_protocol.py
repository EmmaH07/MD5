"""
Name: Emma Harel
Date: 5.10.24
Description: The protocol for the server-client communication.
"""
MAX_RECV = 7
CMD_LST = ['MD5', 'GET', 'JOB', 'ANS']


def get_msg(my_socket):
    """
    the func gets a message.
    :param my_socket: my socket
    :return: the message received.
    """
    msg = my_socket.recv(MAX_RECV).decode()
    data_len = msg.split('@')[1]
    data_len = data_len.split('!')[0]
    data_msg = my_socket.recv(1).decode()
    while int(data_len) > len(data_msg):
        data_msg += my_socket.recv(1).decode()
    msg += data_msg
    return msg


def get_cmd(proto_msg):
    """
    The func checks if the param is a message created by protocol. If it is, the func extracts the command.
    :param proto_msg: a message written by protocol
    :return: the command
    """
    if '@' not in proto_msg or '!' not in proto_msg:
        return_msg = create_err_msg()
    else:
        return_msg = proto_msg.split('@')[0]

    return return_msg


def get_data(proto_msg):
    """
    The func checks if the param is a message created by protocol. If it is, the func extracts the data.
    :param proto_msg: a message written by protocol
    :return: the data
    """
    if '@' not in proto_msg or '!' not in proto_msg:
        return_msg = create_err_msg()

    else:
        return_msg = proto_msg.split('!')[1]

    return return_msg


def create_err_msg():
    """
    the func creates an error message by protocol.
    :return: a protocol based messages announcing an error.
    """
    return 'ERR@0!'


def create_proto_msg(cmd, data):
    """
    The func creates a message by protocol.
    :param cmd: the wanted command
    :param data: the data to include
    :return: a protocol based message
    """
    ok = False
    for i in range(len(CMD_LST)):
        if CMD_LST[i] == cmd:
            ok = True

    if ok:
        if len(data) < 10:
            return_msg = cmd + '@0' + str(len(data)) + '!' + data
        else:
            return_msg = cmd + '@' + str(len(data)) + '!' + data

    else:
        return_msg = create_err_msg()

    return return_msg
