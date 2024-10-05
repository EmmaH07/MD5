"""
Author: Emma Harel
Date: 5.10.24
Description: a server that distributes 'jobs' to different clients in order to find the encrypted MD5 number.
"""
import threading
from threading import Thread
import socket
import logging
import md_protocol

IP = '0.0.0.0'
PORT = 5732
QUEUE_SIZE = 10
MD_TO_DEC = 'ec9c0f7edcc18a98b1f31853b1813301'
JOB_PER_CPU = 15000000
LOCK = threading.Lock()

# Shared data
JOB_LEFT = 8999999999
START_NUM = 1000000000

logging.basicConfig(filename='md_server.log', level=logging.DEBUG, filemode='w')


def handle_thread(client_socket, client_address, my_index):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :param my_index: the index of the client
    :return: None
    """
    try:
        global JOB_LEFT
        global START_NUM
        proto_msg = md_protocol.create_proto_msg('MD5', MD_TO_DEC)
        client_socket.send(proto_msg.encode())
        logging.debug('I sent: ' + proto_msg)
        msg = md_protocol.get_msg(client_socket)
        logging.debug('I got: ' + msg)
        if md_protocol.get_cmd(msg) != 'GET':
            msg = md_protocol.get_msg(client_socket)
            logging.debug('I got: ' + msg)
        cpu = int(md_protocol.get_data(msg)) * JOB_PER_CPU
        LOCK.acquire()
        start = START_NUM
        end = START_NUM + cpu
        if end > 9999999999:
            end = 9999999999
        JOB_LEFT = JOB_LEFT - cpu
        START_NUM = START_NUM + cpu + 1
        if JOB_LEFT <= 0 or START_NUM > 9999999999:
            JOB_LEFT = 0
        data_str = str(start) + ',' + str(end)
        proto_msg = md_protocol.create_proto_msg('JOB', data_str)
        client_socket.send(proto_msg.encode())
        logging.debug('I sent: ' + proto_msg)
        print('SOCK ' + str(client_address) + 'is checking numbers between ' + str(start) + ' and ' + str(end))
        LOCK.release()
        msg = md_protocol.get_msg(client_socket)
        logging.debug('I got: ' + msg)
        if md_protocol.get_cmd(msg) != 'ANS':
            msg = md_protocol.get_msg(client_socket)
            logging.debug('I got: ' + msg)
        data = md_protocol.get_data(msg)
        found = data.split(',')[0]
        if found == 'FOUND':
            print('I found the number! \r\nThe number is: ' + data.split(',')[1])
            LOCK.acquire()
            JOB_LEFT = 0
            LOCK.release()
        else:
            print('SOCK ' + str(client_address) + ' did not find the number :(')

    except socket.error as err:
        logging.debug('Thread' + str(my_index) + ' received socket exception - ' + str(err))

    except KeyboardInterrupt as err:
        logging.debug('Thread' + str(my_index) + ' received exception - ' + str(err))

    finally:
        logging.debug('Thread' + str(my_index) + ' disconnected from client')
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        global JOB_LEFT
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        sock_list = []
        while JOB_LEFT > 0:
            client_socket, client_address = server_socket.accept()
            print('connected')
            logging.debug('connected to: ' + str(client_address))
            sock_list.append(client_socket)
            thread = Thread(target=handle_thread,
                            args=(client_socket, client_address, len(sock_list) - 1))
            thread.start()

    except socket.error as err:
        print('received socket exception - ' + str(err))
        logging.debug('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
