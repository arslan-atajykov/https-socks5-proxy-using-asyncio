import socket
import logging
import asyncio
import struct
import argparse
import sys
import traceback
import os
import ipaddress


class MyError(Exception):
    pass


SOCKS_VERSION = b'\x05'   #5
IPV4=b'\x01'
DOMAIN = b'\x03'
IPV6 = b'\x04'
logging.basicConfig(level=logging.INFO)



async def close_writer(writer):
    if not writer:
        await asyncio.sleep(0.001)
        return
    add=writer.get_extra_info('peername')
    logging.info(f'disconnect   {add}')

    try:

            writer.close()
            await writer.wait_closed()
    except Exception as err:
        logging.error(err)


async def write_data(writer,buf):
    try:
        writer.write(buf)
        await writer.drain()
    except ConnectionAbortedError as err:
        logging.error(err)



async def exchnge(reader, writer):
    try:
        while True:
            buf = await read_data(reader,65500)

            await write_data(writer,buf)
    except Exception as err:
        logging.error(err)

    await close_writer(writer)

async def read_data(reader,len):
    buff=None
    try:
        buff = await reader.read(len)
    except Exception as err:
        logging.error(err)
    if not buff:
        raise MyError(f'recvEOF')
    return buff


#doclient
async def handle_client_connection(reader, writer):
    version=None
    try:
        address = writer.get_extra_info('peername')
        logging.info('Accepted connection from {}'.format(address))
        hdr = await reader.read(1)
        if hdr==SOCKS_VERSION:
            p_type=555
            #print("father")
            numMethods = await reader.read(1)

            await reader.read(numMethods[0])

            writer.write(struct.pack("!BB",5,0))

            version,cmd,_,address_type = struct.unpack("!BBBB",await reader.read(4))

            try:

                if address_type == 1:   #ipv4
                    host_add = socket.inet_ntop(socket.AF_INET,await reader.read(4))

                elif address_type == 3:    #domain
                    domain_length = (await reader.read(1))[0]
                    host_add = await reader.read(domain_length)
                    host_add = host_add.decode("UTF-8")
                elif address_type == 4:    #ipv6
                    host_add = socket.inet_ntop(socket.AF_INET,await reader.read(16))

                else:
                    #print("error address_type")
                    writer.close()
            except Exception as err:
                logging.error(err)
            #print("mother")
            host_port = struct.unpack('!H', await reader.read(2))[0]
        else:
            #print("yoooo{}".format(hdr))
            L= await reader.readline()
            #print("noooo")
            L=hdr + L
            L = L.decode()
            method,uri,proto,*_ = L.split()
            if method.lower() == 'connect':
                print("Http")

                host_add,host_port,*_ = uri.split(':')
                data = await reader.readuntil(b'\r\n\r\n')
            else:
                print("error http")

        logging.info(f'connection start = {host_add} port = {host_port}')


        remote_reader,remote_writer = await asyncio.open_connection(args.remoteHost, args.remotePort)

        await write_data (remote_writer,f'{host_add} {host_port}\r\n'.encode())

        f_line = await remote_reader.readline()
        con_host, con_port, *_ = f_line.decode().rstrip().split()
        logging.info(f'Connect bind={con_host} port={con_port}')


        if version==5:
            try:

                add_type=ipaddress.ip_address(con_host)
                if add_type.version == 4:
                    address_type = IPV4
                    hostData = struct.pack('!L',int(add_type))
                else:
                    address_type = IPV6
                    hostData = struct.pack('!16s',ipaddress.v6_int_to_packed(int(add_type)))
            except Exception:
                hostData = struct.pack(f'!B{len(con_host)}s', len(con_host), con_host)

            data = struct.pack(f'!ssss{len(hostData)}sH', b'\x05', b'\x00', b'\x00', address_type, hostData, int(con_port))
            await write_data(writer, data)
        else:

            await write_data(writer, f'{proto} 200 OK\r\n\r\n'.encode())

        await asyncio.wait({
            asyncio.create_task(exchnge(reader, remote_writer)),
            asyncio.create_task(exchnge(remote_reader, writer))
        })

    except Exception as exc:
        logging.error(exc)
        await close_writer(writer)
        print("failll")




async def handle_local_connection(reader, writer):

    try:
        host_loc, port_loc, *_ = writer.get_extra_info('peername')

        f_line = await reader.readline()

        host_add, host_port = f_line.decode().rstrip().split()

        logging.info(f'started>> {host_loc} {port_loc}')

        srv_reader, srv_writer = await asyncio.open_connection(host_add, host_port)
        con_host, con_port, *_ = srv_writer.get_extra_info('sockname')
        logging.info(f'succesfully connected>> {con_host} {con_port}')

        await write_data(writer, f'{con_host} {con_port}\r\n'.encode())

        await asyncio.wait({
            asyncio.create_task(exchnge(reader, srv_writer)),
            asyncio.create_task(exchnge(srv_reader, writer))
        })

    except MyError as exc:
        logging.info(exc)
        await close_writer(writer)
        await close_writer(srv_writer)








async def main():
    if args.remoteHost:
        server = await asyncio.start_server(
            handle_client_connection, host=args.listenHost,port=args.listenPort)
        addrList = list([s.getsockname() for s in server.sockets])
        print('listening at {}'.format(addrList))
        async with server:
            await server.serve_forever()
    else :
        server = await asyncio.start_server(
                handle_local_connection, host=args.listenHost,port=args.listenPort)
        addrList = list([s.getsockname() for s in server.sockets])
        print('listening at {}'.format(addrList))
        async with server:
            await server.serve_forever()
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='socks5 http')
    parser.add_argument('--host', dest='listenHost', metavar='listen_host', help='proxy listen host default listen all interfaces')
    parser.add_argument('--port', dest='listenPort', metavar='listen_port', required=True)
    parser.add_argument('remoteHost', nargs='?', default=None)
    parser.add_argument('remotePort', nargs='?', default=None)
    args= parser.parse_args()

    asyncio.run(main())
