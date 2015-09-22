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



Constants = {
    'MANIFEST_SOURCE_DB_IP': 'sourceDbIP',
    'MANIFEST_SOURCE_PS_USER': 'sourcePsUser',
    'MANIFEST_SOURCE_PS_PASSWORD': 'sourcePsPassword',
    'MANIFEST_SOURCE_DB_INSTANCE': 'sourceDbInstance',
    'MANIFEST_SOURCE_SA_PASSWORD': 'sourceSaPassword',
    'MANIFEST_TARGET_DB_IP': 'targetDbIP',
    'MANIFEST_TARGET_PS_USER': 'targetPsUser',
    'MANIFEST_TARGET_PS_PASSWORD': 'targetPsPassword',
    'MANIFEST_TARGET_DB_INSTANCE': 'targetDbInstance',
    'MANIFEST_TARGET_SA_PASSWORD': 'targetSaPassword',
    'MANIFEST_BACKUP_FOLDER': 'backupFolder',
    'MANIFEST_DB_NAME': 'dbName',
    'MANIFEST_STEP2_DEPLOYMENT_MODEL': 'step2DeploymentModel',
    'MANIFEST_STEP3_DEPLOYMENT_MODEL': 'step3DeploymentModel',
    'MANIFEST_STEP4_DEPLOYMENT_MODEL': 'step4DeploymentModel',
    'MANIFEST_MODELS_AT_RUNTIME_IP': 'modelsAtRuntimeIp',
    'MANIFEST_MODELS_AT_RUNTIME_PORT': 'modelsAtRuntimePort',
    'DB_MIGRATION_FULL': 'dbMigrationFull',
    'DEPLOYMENT_MODEL': 'deploymentModel'
}
