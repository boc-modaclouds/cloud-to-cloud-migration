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


import json
import logging
from MigrationWorkflow import MigrationWorkflow
import sys
import time


def usage():
    print 'Usage: %s <migration-manifest-file>' % sys.argv[0]
    sys.exit(1)


def main():
    __log = logging.getLogger()
    fd = None
    config = None
    if len(sys.argv) < 2:
        usage()
    try:
        fd = open(sys.argv[1])
    except:
        __log.critical('Cannot open %s for reading')
        sys.exit(1)
    try:
        __log.info('loading migration manifest ...')
        config = json.load(fd)
        fd.close()
    except Exception, e:
        __log.critical('Failed loading manifest - Exception: %s' % str(e))
        sys.exit(1)
    wfl = MigrationWorkflow(config)
    __log.info('migration manifest OK')
    try:
        wfl.execute()
        time.sleep(60)
    finally:
        wfl.done()
        __log.info("Finished")

if __name__ == '__main__':
    #logging.basicConfig(format='%(asctime)s %(message)s [%(filename)s:%(lineno)d]', level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s ', level=logging.INFO)
    main()
