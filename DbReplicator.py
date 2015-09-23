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

from Constants import Constants
import logging
import os
import socket
import subprocess


class DbReplicator(object):
    """ This class executes PowerShell Scripts
    """
    def __init__(self, config, loggingPrefix):
        self.__loggingPrefix = loggingPrefix
        self.__log = logging.getLogger(DbReplicator.__name__)
        self.__full = config[Constants['DB_MIGRATION_FULL']]
        self.__sourceDbIp = config[Constants['MANIFEST_SOURCE_DB_IP']]
        self.__sourcePsUser = config[Constants['MANIFEST_SOURCE_PS_USER']]
        self.__sourcePsUserPassword = config[Constants['MANIFEST_SOURCE_PS_PASSWORD']]
        self.__sourceDbInstance = config[Constants['MANIFEST_SOURCE_DB_INSTANCE']]
        self.__sourceSaPassword = config[Constants['MANIFEST_SOURCE_SA_PASSWORD']]
        self.__targetDbIp = config[Constants['MANIFEST_TARGET_DB_IP']]
        self.__targetPsUser = config[Constants['MANIFEST_TARGET_PS_USER']]
        self.__targetPsUserPassword = config[Constants['MANIFEST_TARGET_PS_PASSWORD']]
        self.__targetDbInstance = config[Constants['MANIFEST_TARGET_DB_INSTANCE']]
        self.__targetSaPassword = config[Constants['MANIFEST_TARGET_SA_PASSWORD']]
        self.__dbName = config[Constants['MANIFEST_DB_NAME']]
        self.__backupFolder = config[Constants['MANIFEST_BACKUP_FOLDER']]
        # sanity checks
        if self.__sourceDbInstance != self.__targetDbInstance:
            raise Exception('Currently only equal instance names are supported')
        if self.__sourceSaPassword != self.__targetSaPassword:
            raise Exception('Currently only equal sa passwords are supported')

    @staticmethod
    def __testPsConnections(ip):
        try:
            conn = socket.socket()
            conn.connect((ip, 5985))
            conn.close()
            return True
        except Exception, e:
            return False

    def execute(self):
        if not DbReplicator.__testPsConnections(self.__sourceDbIp):
            raise Exception('Connection to %s on WinRM port failed' % self.__sourceDbIp)
        if not DbReplicator.__testPsConnections(self.__targetDbIp):
            raise Exception('Connection to %s on WinRM port failed' % self.__targetDbIp)
        proc = subprocess.Popen([r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe',
                                 '-ExecutionPolicy',
                                 'Unrestricted',
                                 './migrate_db.ps1',
                                 self.__sourceDbIp,
                                 self.__targetDbIp,
                                 self.__sourceDbInstance,
                                 self.__sourceSaPassword,
                                 self.__dbName,
                                 self.__backupFolder,
                                 '1' if self.__full else '0'],
                                cwd = os.getcwd(),
                                stderr = subprocess.PIPE,
                                stdout = subprocess.PIPE)
        self.__log.debug('%sSTDOUT: ' % self.__loggingPrefix)
        while True:
            line = proc.stdout.readline()
            if not line: break
            else: self.__log.debug('%s  %s'  % (self.__loggingPrefix, line.rstrip()))
        result = proc.wait()
        self.__log.debug('%sPowerShell script finished with exit code %d' % (self.__loggingPrefix, result))
        stderr = proc.stderr.read()
        if stderr:
            raise Exception('database replication failed: %s' % stderr)
