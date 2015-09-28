#! /usr/bin/env python
#
# Migration scripts for re-location of an ADONIS:cloud service instance
# Author: stepan.seycek@boc-eu.com
#
# (c)2015 BOC Information Systems GmbH
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

import datetime
import logging
import re
import socket
import sys
import thread
import threading
import time
import websocket


class ModelsAtRuntimeClient(object):
    """ Class for connecting to models at runtime via websocket
    """

    def __init__(self, host, port, loggingPrefix):
        self.__log = logging.getLogger(ModelsAtRuntimeClient.__name__)
        self.__loggingPrefix = loggingPrefix
        ModelsAtRuntimeClient.__testConnection(host, port)
        self.__host = host
        self.__port = port
        self.__conn = None
        self.__inboundMessages = []
        self.__inboundMessageCounter = 0
        self.__mtx = threading.Lock()
        self.__connected = False

    @staticmethod
    def __testConnection(host, port):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
            conn.close()
        except:
            raise Exception('Connection to ModelsAtRuntime at %s:%d failed' % (host, port))

    def connect(self):
        self.__conn = websocket.WebSocketApp('ws://%s:%d/' % (self.__host, self.__port),
                                             on_message = self.messageHandler,
                                             on_error = self.errorHandler,
                                             on_open = self.openHandler,
                                             on_close = self.closeHandler)
        thread.start_new_thread(self.__conn.run_forever, ())
        self.__mtx.acquire()
        connected = self.__connected
        self.__mtx.release()
        while not connected:
            time.sleep(1)
            self.__mtx.acquire()
            connected = self.__connected
            self.__mtx.release()

    def close(self):
        if self.__conn: self.__conn.close()

    def getSnapshot(self, path = '/'):
        self.__write('!getSnapshot { path: %s }' % path)

    def deploy(self, model):
        # reformat JSON to be on the safe side
        self.__write('!extended { name : LoadDeployment }')
        additional = '!additional json-string:%s' % model
        # IMPORTANT: do not wait for a response here, you won't get it
        self.__write(additional, False)
        self.__write('!extended { name : Deploy }', expect = '.*!ack.*completed')
        self.__resetInbound()

    def __resetInbound(self):
        self.__mtx.acquire()
        try:
            self.__inboundMessageCounter = 0
            self.__inboundMessages = []
        finally:
            self.__mtx.release()

    def __write(self, message, wait_for_response = True, timeout = 3600, expect = ''):
        if not self.__conn: self.connect()
        #self.__purgeInboundMessages()
        expect_rgx = None
        if expect: expect_rgx = re.compile(expect, re.IGNORECASE)
        inboundMessageCounter = self.__getInboundMessageCounter()
        self.__conn.send(message)
        if wait_for_response:
            waiting = 0
            while waiting < timeout:
                done = False
                try:
                    self.__mtx.acquire()
                    while inboundMessageCounter < self.__inboundMessageCounter:
                        if not expect_rgx or expect_rgx.match(
                                self.__inboundMessages[len(self.__inboundMessages) - 1]['message']):
                            done = True
                            break
                        else:
                            inboundMessageCounter += 1
                finally:
                    self.__mtx.release()
                    if done: break
                time.sleep(1)
                waiting += 1
                if waiting == 5: self.__log.info('%swaiting for completion ...' % self.__loggingPrefix)
                if 0 == waiting % 20: sys.stdout.write('.')
            if 20 <= waiting: sys.stdout.write('\n')

    def __purgeInboundMessages(self):
        try:
            self.__mtx.acquire()
            self.__inboundMessages = []
        finally:
            self.__mtx.release()

    def messageHandler(self, ws, msg):
        try:
            self.__mtx.acquire()
            self.__inboundMessageCounter +=1
            self.__inboundMessages.append({
                'sequenceNumber': self.__inboundMessageCounter,
                'timestamp': datetime.datetime.now(),
                'message': msg})
            self.__log.debug('%sgot message from M@R: %s' % (self.__loggingPrefix, msg))
        finally:
            self.__mtx.release()

    def errorHandler(self, ws, err):
        self.__log.error('%swebsocket error: %s' % (self.__loggingPrefix, str(err)))

    def openHandler(self, ws):
        self.__log.debug("%sestablished websocket connection with M@R" % self.__loggingPrefix)
        self.__mtx.acquire()
        self.__connected = True
        self.__mtx.release()
        self.__write('!listenToAny', wait_for_response = False)

    def closeHandler(self, ws):
        self.__log.debug("%swebsocket connection with M@R has been closed" % self.__loggingPrefix)

    def __getInboundMessageCounter(self):
        try:
            self.__mtx.acquire()
            return self.__inboundMessageCounter
        finally:
            self.__mtx.release()
