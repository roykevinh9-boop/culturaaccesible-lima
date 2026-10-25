$ErrorActionPreference='Stop'
$projectPath=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectPath
$mavenCmd=Get-Command mvn.cmd -ErrorAction SilentlyContinue
if($mavenCmd){$mavenExe=$mavenCmd.Source}else{
 $idea=Get-ChildItem -LiteralPath "$env:ProgramFiles/JetBrains" -Directory -ErrorAction SilentlyContinue | Where-Object {$_.Name -like 'IntelliJ*'} | Sort-Object LastWriteTime -Descending | Select-Object -First 1
 if($idea){$mavenExe=Join-Path $idea.FullName 'plugins/maven/lib/maven3/bin/mvn.cmd'}
}
if(-not $mavenExe -or -not(Test-Path -LiteralPath $mavenExe)){throw 'Configura Maven 3.9+ o abre backend/pom.xml con IntelliJ IDEA.'}
if(-not $env:JAVA_HOME){$jdk=Get-ChildItem -LiteralPath "$env:ProgramFiles/Java" -Directory -ErrorAction SilentlyContinue | Where-Object {$_.Name -like 'jdk*'} | Sort-Object LastWriteTime -Descending | Select-Object -First 1;if($jdk){$env:JAVA_HOME=$jdk.FullName}}
New-Item -ItemType Directory -Force -Path '.local/temp','.local/maven-repository','app' | Out-Null
$env:TEMP=(Resolve-Path '.local/temp').Path;$env:TMP=$env:TEMP
$env:MAVEN_OPTS="-Djava.io.tmpdir=$env:TEMP --enable-native-access=ALL-UNNAMED"
& $mavenExe -B --no-transfer-progress -f 'backend/pom.xml' "-Dmaven.repo.local=$projectPath/.local/maven-repository" -DforkCount=0 test package
if($LASTEXITCODE -ne 0){throw 'La compilación o las pruebas fallaron.'}
Copy-Item -LiteralPath 'backend/target/culturaaccesible-1.0.0.jar' -Destination 'app/culturaaccesible.jar' -Force
Write-Host 'Compilación terminada. Ejecuta Abrir-demo.cmd.'
