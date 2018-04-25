from mysmb import MYSMB
from impacket import smb, smbconnection, nt_errors
from impacket.uuid import uuidtup_to_bin
from impacket.dcerpc.v5.rpcrt import DCERPCException
from struct import pack
import sys
from socket import *
from kivy.logger import Logger

'''
Script for
- check target if MS17-010 is patched or not.
- find accessible named pipe
'''

USERNAME = ''
PASSWORD = ''

NDR64Syntax = ('71710533-BEBA-4937-8319-B5DBEF9CCC36', '1.0')

MSRPC_UUID_BROWSER = uuidtup_to_bin(('6BFFD098-A112-3610-9833-012892020162', '0.0'))
MSRPC_UUID_SPOOLSS = uuidtup_to_bin(('12345678-1234-ABCD-EF00-0123456789AB', '1.0'))
MSRPC_UUID_NETLOGON = uuidtup_to_bin(('12345678-1234-ABCD-EF00-01234567CFFB', '1.0'))
MSRPC_UUID_LSARPC = uuidtup_to_bin(('12345778-1234-ABCD-EF00-0123456789AB', '0.0'))
MSRPC_UUID_SAMR = uuidtup_to_bin(('12345778-1234-ABCD-EF00-0123456789AC', '1.0'))

pipes = {
    'browser': MSRPC_UUID_BROWSER,
    'spoolss': MSRPC_UUID_SPOOLSS,
    'netlogon': MSRPC_UUID_NETLOGON,
    'lsarpc': MSRPC_UUID_LSARPC,
    'samr': MSRPC_UUID_SAMR,
}


def is_vulnerable(target):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(3)
    result = s.connect_ex((target, 445))
    is_succ = False
    os = ''

    if (result == 0):
        conn = MYSMB(target)
        try:
            conn.login(USERNAME, PASSWORD)
        except smb.SessionError as e:
            Logger.warn('Login failed: ' + nt_errors.ERROR_MESSAGES[e.error_code][0])
        finally:
            Logger.info('Target OS: ' + conn.get_server_os())

        tid = conn.tree_connect_andx('\\\\' + target + '\\' + 'IPC$')
        conn.set_default_tid(tid)

        # test if target is vulnerable
        TRANS_PEEK_NMPIPE = 0x23
        recvPkt = conn.send_trans(pack('<H', TRANS_PEEK_NMPIPE), maxParameterCount=0xffff, maxDataCount=0x800)
        status = recvPkt.getNTStatus()
        if status == 0xC0000205:  # STATUS_INSUFF_SERVER_RESOURCES
            Logger.info('The target is not patched')
        else:
            Logger.info('The target is patched')

        for pipe_name, pipe_uuid in pipes.items():
            try:
                dce = conn.get_dce_rpc(pipe_name)
                dce.connect()
                try:
                    dce.bind(pipe_uuid, transfer_syntax=NDR64Syntax)
                    Logger.info('{}: Ok (64 bit)'.format(pipe_name))
                    is_succ = True
                except DCERPCException as e:
                    if 'transfer_syntaxes_not_supported' in str(e):
                        Logger.info('{}: Ok (32 bit)'.format(pipe_name))
                        is_succ = True
                    else:
                        Logger.info('{}: Ok ({})'.format(pipe_name, str(e)))
                        is_succ = True
                dce.disconnect()
            except smb.SessionError as e:
                Logger.warn('{}: {}'.format(pipe_name, nt_errors.ERROR_MESSAGES[e.error_code][0]))
            except smbconnection.SessionError as e:
                Logger.warn('{}: {}'.format(pipe_name, nt_errors.ERROR_MESSAGES[e.error][0]))
        os = conn.get_server_os()
        conn.disconnect_tree(tid)
        conn.logoff()
        conn.get_socket().close()
    s.close()
    return {'OS': os, 'Result': is_succ}
