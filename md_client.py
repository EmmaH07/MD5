"""
Author: Emma Harel
Date: 5.10.24
Description: a client that gets a domain of numbers to check.
"""
import multiprocessing
import socket
import logging
import hashlib
import md_protocol


IP = '127.0.0.1'
PORT = 5732
MAX_RECV = 6

logging.basicConfig(filename='md_client.log', level=logging.DEBUG, filemode='w')


def brute_force(start, end, md5_str):
    """
    the func encrypts every number within the domain and checks if the encryption id similar to the md5 str.
    :param start: the starting number
    :param end: the ending number
    :param md5_str: the md5 to find
    :return: a protocol based messages that announce whether the client found the number.
    """
    print('Checking numbers between ' + str(start) + ' and ' + str(end) + '...')
    ret_str = 'NOT FOUND,'
    for i in range(start, end + 1):
        attempt_str = str(hashlib.md5(str(i).encode()).hexdigest())
        if md5_str == attempt_str:
            ret_str = 'FOUND,' + str(i)
            break
    if ret_str == 'NOT FOUND,':
        print('I did not find the number')

    else:
        print('I found the number!')

    return ret_str


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        msg = md_protocol.get_msg(my_socket)
        logging.debug('I got: ' + msg)
        if md_protocol.get_cmd(msg) != 'MD5':
            msg = md_protocol.get_msg(my_socket)
            logging.debug('I got: ' + msg)
        md5_to_dec = md_protocol.get_data(msg)
        cpu = multiprocessing.cpu_count()
        proto_msg = md_protocol.create_proto_msg('GET', str(cpu))
        my_socket.send(proto_msg.encode())
        logging.debug('I sent: ' + proto_msg)
        msg = md_protocol.get_msg(my_socket)
        logging.debug('I got: ' + msg)
        if md_protocol.get_cmd(msg) != 'JOB':
            msg = md_protocol.get_msg(my_socket)
            logging.debug('I got: ' + msg)
        data = md_protocol.get_data(msg)
        start = int(data.split(',')[0])
        end = int(data.split(',')[1])
        found = brute_force(start, end, md5_to_dec)
        proto_msg = md_protocol.create_proto_msg('ANS', found)
        my_socket.send(proto_msg.encode())
        logging.debug('I sent: ' + proto_msg)

    except socket.error as err:
        print('received socket error ' + str(err))
        logging.debug('received socket error ' + str(err))

    except KeyboardInterrupt as err:
        logging.debug('received exception - ' + str(err))

    finally:
        my_socket.close()


if __name__ == '__main__':
    main()
