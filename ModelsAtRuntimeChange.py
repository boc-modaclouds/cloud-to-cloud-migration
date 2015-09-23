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

from Constants import Constants
import logging
from ModelsAtRuntimeClient import ModelsAtRuntimeClient


class ModelsAtRuntimeChange(object):
    """ This class takes care of enacting a deployment change through the M@R deployer
    """

    def __init__(self, step, config):
        self.__log = logging.getLogger(ModelsAtRuntimeChange.__name__)
        self.__step = step
        self.__config = config
        self.__client = ModelsAtRuntimeClient(self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_IP']],
                                              self.__config[Constants['MANIFEST_MODELS_AT_RUNTIME_PORT']],
                                              '- [step %d] ' % self.__step)

    def execute(self):
        fd = open(self.__config[Constants['DEPLOYMENT_MODEL']])
        deploymentModel = fd.read()
        fd.close()
        self.__log.info('- [step %d] enacting step %d deployment model ...' % (self.__step , self.__step))
        self.__client.deploy(deploymentModel)

    def done(self):
        if self.__client: self.__client.close()
        self.__client = None
