#! /usr/bin/env python
#
# Migration scripts for re-location of an ADONIS:cloud service instance
# Author: stepan.seycek@boc-eu.com
#
# (c)2015 BOC Informations Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#  1. Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the
#     following disclaimer.
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials
#     provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import socket
import websocket


class ModelsAtRuntimeClient(object):
    """ Class for connecting to models at runtime via websockets
    """

    def __init__(self, host, port, loggingPrefix):
        self.__log = logging.getLogger(ModelsAtRuntimeClient.__name__)
        self.__loggingPrefix = loggingPrefix
        ModelsAtRuntimeClient.__testConnection(host, port)
        self.__host = host
        self.__port = port
        self.__conn = None

    @staticmethod
    def __testConnection(host, port):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
            conn.close()
        except:
            raise Exception('Connection to ModelsAtRuntime at %s:%d failed' % (host, port))

    def connect(self):
        self.__conn = websocket.create_connection('ws://%s:%d/' % (self.__host, self.__port))

    def close(self):
        if self.__conn: self.__conn.close()

    def getSnapshot(self, path):
        self.__write('!getSnapshot { path: / }')

    def deploy(self, model):
        # reformat JSON to be on the safe side
        self.__write('!extended { name : LoadDeployment }')
        additional = '!additional json-string:%s' % model
        # IMPORTANT: do not wait for a response here, you won't get it
        self.__write(additional, False)
        self.__write('!extended { name : Deploy }')

    def __write(self, message, wait_for_response = True):
        if not self.__conn: self.connect()
        self.__conn.send(message)
        if wait_for_response:
            response = self.__conn.recv()
            #self.__log.debug('%sGot response from models@runtime: %s' % (self.__loggingPrefix,response))
