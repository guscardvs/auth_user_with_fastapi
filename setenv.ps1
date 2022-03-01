$vars = Get-Content ./.env-dev

foreach ($var in $vars){
    $name, $value = $var -split "=";
    [Environment]::SetEnvironmentVariable($name, $value, "Process") | Out-Null
}
