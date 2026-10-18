param([switch]$SinNavegador)
$ErrorActionPreference='Stop'
$projectPath=$PSScriptRoot
Set-Location -LiteralPath $projectPath
$localPath=Join-Path $projectPath '.local'
New-Item -ItemType Directory -Force -Path $localPath,(Join-Path $localPath 'temp') | Out-Null
$env:TEMP=Join-Path $localPath 'temp'
$env:TMP=$env:TEMP

# Rutas de ejecución; no cambian la instalación ni las variables permanentes del equipo.
$javaExe=$null
if($env:JAVA_HOME -and (Test-Path -LiteralPath (Join-Path $env:JAVA_HOME 'bin/java.exe'))){$javaExe=Join-Path $env:JAVA_HOME 'bin/java.exe'}
if(-not $javaExe){$jdk=Get-ChildItem -LiteralPath "$env:ProgramFiles/Java" -Directory -ErrorAction SilentlyContinue | Where-Object {$_.Name -like 'jdk*'} | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if($jdk){$javaExe=Join-Path $jdk.FullName 'bin/java.exe'}}
if(-not $javaExe){$command=Get-Command java.exe -ErrorAction SilentlyContinue; if($command){$javaExe=$command.Source}}
if(-not $javaExe){throw 'Se necesita Java 17 o posterior para ejecutar la aplicación.'}
$mysqlBin=Join-Path $env:ProgramFiles 'MySQL/MySQL Server 8.0/bin'
if(-not (Test-Path -LiteralPath (Join-Path $mysqlBin 'mysqld.exe'))){$mysqlExe=Get-Command mysqld.exe -ErrorAction SilentlyContinue; if($mysqlExe){$mysqlBin=Split-Path -Parent $mysqlExe.Source}else{throw 'No se encontró MySQL Server 8.0. Indica su carpeta en este script.'}}
$pythonExe=$null
$bundledPython=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if(Test-Path -LiteralPath $bundledPython){$pythonExe=$bundledPython}
if(-not $pythonExe){$pythonCmd=Get-Command python.exe -ErrorAction SilentlyContinue; if($pythonCmd -and $pythonCmd.Source -notlike '*WindowsApps*'){$pythonExe=$pythonCmd.Source}}
if(-not $pythonExe){$py=Get-Command py.exe -ErrorAction SilentlyContinue;if($py){$pythonExe=(& $py.Source -3 -c 'import sys;print(sys.executable)')}}
if(-not $pythonExe){throw 'Se necesita Python 3.11 o 3.12. Instálalo desde python.org.'}
$env:PYTHONUTF8='1'
$env:PYTHONPATH=Join-Path $localPath 'python'
$pythonCheck=Join-Path $localPath 'python/fastapi/__init__.py'
if(-not (Test-Path -LiteralPath $pythonCheck)){
 Write-Host 'Preparando dependencias de Python. La primera ejecución necesita Internet...'
 & $pythonExe -m pip install --target (Join-Path $localPath 'python') -r (Join-Path $projectPath 'python-service/requirements-lock.txt') --disable-pip-version-check --no-warn-script-location --no-cache-dir
 if($LASTEXITCODE -ne 0){throw 'No se completó la instalación de dependencias.'}
}
$launchArgs=@((Join-Path $projectPath 'scripts/launch.py'),'--java',$javaExe,'--mysql-bin',$mysqlBin)
if($SinNavegador){$launchArgs+='--no-browser'}
& $pythonExe @launchArgs
if($LASTEXITCODE -ne 0){throw 'No se completó el inicio. Revisa el mensaje anterior.'}
