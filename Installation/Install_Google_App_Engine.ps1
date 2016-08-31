$url = "https://storage.googleapis.com/appengine-sdks/featured/GoogleAppEngine-1.9.40.msi"
$output = "$PSScriptRoot\GoogleAppEngine-1.9.40.msi"
$start_time = Get-Date

Import-Module BitsTransfer
Start-BitsTransfer -Source $url -Destination $output
#OR
#Start-BitsTransfer -Source $url -Destination $output -Asynchronous

Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"

msiexec /i /a $output /qn /l*v .\install_GoogleAppEngine_SDK.txt