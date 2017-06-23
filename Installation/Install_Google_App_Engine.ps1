$GitSCMURL = "https://github.com/git-for-windows/git/releases/download/v2.10.2.windows.1/Git-2.10.2-64-bit.exe"
$PythonURL = "https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi"
$GoogleCloudSDKURL = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"

$output = "$PSScriptRoot\GoogleAppEngine-1.9.40.msi"
$start_time = Get-Date

Import-Module BitsTransfer
Start-BitsTransfer -Source $url -Destination $output
#OR
#Start-BitsTransfer -Source $url -Destination $output -Asynchronous

Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"

msiexec /i /a $output /qn /l*v .\install_GoogleAppEngine_SDK.txt