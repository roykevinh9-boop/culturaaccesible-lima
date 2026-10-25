param([switch]$SinFallos)
$ErrorActionPreference='Stop'
$projectPath=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectPath
$pythonExe=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if(-not(Test-Path -LiteralPath $pythonExe)){$pythonExe=(Get-Command python.exe -ErrorAction Stop).Source}
$env:PYTHONPATH=(Join-Path $projectPath '.local/python')
$env:PYTHONUTF8='1'
& $pythonExe 'scripts/verify_structure.py'
if($LASTEXITCODE -ne 0){throw 'La separación entre Java y SQL no cumple la estructura del proyecto.'}
$nodeExe=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if(-not(Test-Path -LiteralPath $nodeExe)){$nodeExe=(Get-Command node.exe -ErrorAction Stop).Source}
& $nodeExe --test 'scripts/test_catalog_model.mjs' 'scripts/test_support_preferences.mjs'
if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de consultas y preferencias del navegador.'}
& $pythonExe -m pytest 'python-service' -q
if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de Python.'}
& $pythonExe 'scripts/integration_tests.py'
if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de integración. Verifica que la aplicación esté iniciada.'}
& $pythonExe 'scripts/migration_tests.py'
if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de migración o instalación de la base.'}
& $pythonExe 'scripts/procedure_tests.py'
if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de procedimientos almacenados.'}
if(-not $SinFallos){
 & $pythonExe 'scripts/fault_tests.py'
 if($LASTEXITCODE -ne 0){throw 'Fallaron las pruebas de fallos controlados.'}
}
