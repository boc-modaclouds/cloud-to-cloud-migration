# Migration script for re-location of an ADONIS:cloud database
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

########################################################################################################################
$leftIp = $args[0]                                                    # IP address of the source database server
$rightIp = $args[1]                                                   # IP address of the target database server
$instance = $args[2]                                                  # SQL Server instance, empty for default instances
$sqlUsername = "sa"                                                   # SQL Server user authorized to backup databases
$sqlPassword = $args[3] | ConvertTo-SecureString -asPlainText -Force  # the SQL Server user's password
$dbs = $args[4]                                                       # database names, list of strings
$backupFolder = $args[5]                                              # the folder where the backup shall be stored
$fullBackup = $args[6]                                                # true if full backup shall be done
########################################################################################################################

$psUsername = "cloudml"
$psPassword = "sFEbkxKOpHRc22KSyhUC" | ConvertTo-SecureString -asPlainText -Force
$psCred = New-Object System.Management.Automation.PSCredential $psUsername, $psPassword

Write-Host "Connecting to $($leftIp) ..."
$leftPsSession = new-pssession $leftIp -credential $psCred
Write-Host "Performing backup on $($leftIp), full=$($fullBackup) ..."
Invoke-Command -Session $leftPsSession -Scriptblock {

    $instance = $args[0]
    $sqlUsername = $args[1]
    $sqlPassword = $args[2]
    $dbs = $args[3]
    $backupFolder = $args[4]
    $fullBackup = $args[5]

	Import-Module SqlPS -DisableNameChecking
	$sqlCred = New-Object System.Management.Automation.PSCredential $sqlUsername, $sqlPassword

	# path to our instance
	$serverInstance = "$env:computername"
	if ($instance) {
	  $serverInstance = "$($serverInstance)\$($instance)"
	}

    $suffix = "full"
    if (-not $fullBackup) {
      $suffix = "diff"
    }
    $backupFolderUnc = $backupFolder.Replace(":", "$")

	# backup the databases
	foreach ($db in $dbs) {
	  if ($fullBackup) {
		Backup-SqlDatabase -Initialize -ServerInstance $serverInstance -Database $db `
		  -BackupFile "$($backupFolder)\$($db)_$($suffix).bak" -Credential $sqlCred
	  } else {
		Backup-SqlDatabase -Incremental -ServerInstance $serverInstance -Database $db `
		  -BackupFile "$($backupFolder)\$($db)_$($suffix).bak" -Credential $sqlCred -Initialize
	  }
	}
  } -ArgumentList $instance, $sqlUsername, $sqlPassword, $dbs, $backupFolder, $fullBackup

  # copy the backup files to the new database server
  Write-Host "Copying backup files fromm $($leftIp) to $($rightIp) ..."
  $suffix = "full"
  if (-not $fullBackup) {
    $suffix = "diff"
  }
  $backupFolderUnc = $backupFolder.Replace(":", "$")
  foreach ($db in $dbs) {
    $source = "\\$($leftIp)\$($backupFolderUnc)\$($db)_$($suffix).bak"
    $destination = "\\$($rightIp)\$($backupFolderUnc)\$($db)_$($suffix).bak"
    Copy-Item -Path $source -Destination $destination
  }


# restore on right side
Write-Host "Connecting to $($rightIp) ..."
$rightPsSession = new-pssession $rightIp -credential $psCred
Write-Host "Restoring backup on $($rightIp), full=$($fullBackup) ..."
Invoke-Command -Session $rightPsSession -Scriptblock {

    $instance = $args[0]
    $sqlUsername = $args[1]
    $sqlPassword = $args[2]
    $dbs = $args[3]
    $backupFolder = $args[4]
    $fullBackup = $args[5]

	Import-Module SqlPS -DisableNameChecking
	$sqlCred = New-Object System.Management.Automation.PSCredential $sqlUsername, $sqlPassword

	# path to our instance
	$serverInstance = "$env:computername"
	if ($instance) {
	  $serverInstance = "$($serverInstance)\$($instance)"
	}

    $suffix = "full"
    if (-not $fullBackup) {
      $suffix = "diff"
    }

	# restore the databases
	foreach ($db in $dbs)
	{
	  if ($fullBackup) {
		Restore-SqlDatabase -NoRecovery -ServerInstance $serverInstance -Database $db `
		  -BackupFile "$($backupFolder)\$($db)_$($suffix).bak" -Credential $sqlCred
	  } else {
		Restore-SqlDatabase -ServerInstance $serverInstance -Database $db `
		  -BackupFile "$($backupFolder)\$($db)_$($suffix).bak" -Credential $sqlCred
	  }
	}

} -ArgumentList $instance, $sqlUsername, $sqlPassword, $dbs, $backupFolder, $fullBackup

Write-Host "Operation completed!"
