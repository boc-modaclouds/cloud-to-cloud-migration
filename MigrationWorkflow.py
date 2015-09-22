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
import copy
from Constants import Constants
from DbMigration import DbMigration
from ModelsAtRuntimeChange import ModelsAtRuntimeChange
import socket


class MigrationWorkflow (object):
    """ Workflow class calling specialized task handlers
    """

    def __init__(self, config):
        self.__checkManifest(config)
        self.__config = config
        self.__checkIfModelsAtRuntimeIsOnline()
        step2Deployment = ModelsAtRuntimeChange(2, self.__deploymentChangeConfig(2))
        step2DbMigration = DbMigration (2, self.__dbMigrationConfig(True))
        step3Deployment = ModelsAtRuntimeChange(3, self.__deploymentChangeConfig(3))
        step3DbMigration = DbMigration (3, self.__dbMigrationConfig(False))
        step4Deployment = ModelsAtRuntimeChange(4, self.__deploymentChangeConfig(4))
        self.__workflowsSteps = [
            step2Deployment,
            step2DbMigration,
        #   step3Deployment,
            step3DbMigration,
        #   step4Deployment
        ]

    def execute(self):
        for step in self.__workflowsSteps:
            step.execute()

    def done(self):
        for step in self.__workflowsSteps:
            step.done()

    def __deploymentChangeConfig(self, step):
        if step not in (2,3,4): raise Exception('Invalid argument - only steps 2,3,4 are supported')
        config = {}
        key = 'MANIFEST_STEP%d_DEPLOYMENT_MODEL' % step
        config[Constants['DEPLOYMENT_MODEL']] = self.__config[Constants[key]]
        config[Constants['MANIFEST_MODELS_AT_RUNTIME_IP']] = self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_IP']]
        config[Constants['MANIFEST_MODELS_AT_RUNTIME_PORT']] = self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_PORT']]
        return config

    def __dbMigrationConfig(self, full):
        # here we copy the full manifest and add the information full vs. diff
        if full not in (True, False): raise Exception('Invalid argument - expected boolean')
        config = copy.deepcopy(self.__config)
        config[Constants['DB_MIGRATION_FULL']] = full
        return config

    def __checkManifest(self, manifest):
        # we only check if the mandatory properties are contained
        for k in Constants.keys():
            if k.startswith('MANIFEST_') and Constants[k] not in manifest:
                raise Exception('Missing manifest property %s' % Constants[k])

    def __checkIfModelsAtRuntimeIsOnline(self):
        host = self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_IP']]
        port = self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_PORT']]
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host, port))
            conn.close()
        except Exception, e:
            raise Exception('Cannot connect to Models@Runtime endpoint at %s:%d' % (host, port))