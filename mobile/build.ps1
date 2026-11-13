$ErrorActionPreference = 'Stop'
$mobile = $PSScriptRoot
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$java = if ($env:JAVA_HOME) { $env:JAVA_HOME } else { 'C:\Program Files\Android\Android Studio\jbr' }
$env:JAVA_HOME = $java
$toolRoot = Join-Path $sdk 'build-tools\36.0.0'
$androidJar = Join-Path $sdk 'platforms\android-37.0\android.jar'
$build = Join-Path $mobile 'build'
$classes = Join-Path $build 'classes'
$dex = Join-Path $build 'dex'
New-Item -ItemType Directory -Force $build, $classes, $dex | Out-Null
function Check-Exit { if ($LASTEXITCODE -ne 0) { throw "Build command failed (exit $LASTEXITCODE)" } }
& "$toolRoot\aapt2.exe" compile --dir "$mobile\app\src\main\res" -o "$build\res.zip"
Check-Exit
& "$toolRoot\aapt2.exe" link -I $androidJar -A "$mobile\..\assets" --manifest "$mobile\app\src\main\AndroidManifest.xml" --min-sdk-version 26 --target-sdk-version 35 --version-code 2 --version-name '0.2' -o "$build\unsigned.apk" "$build\res.zip"
Check-Exit
$sourceFiles = Get-ChildItem "$mobile\app\src\main\java" -Filter '*.java' -Recurse | ForEach-Object { $_.FullName }
& "$java\bin\javac.exe" --release 8 -classpath $androidJar -d $classes $sourceFiles
Check-Exit
$classFiles = Get-ChildItem $classes -Filter '*.class' -Recurse | ForEach-Object { $_.FullName }
& "$toolRoot\d8.bat" --min-api 26 --lib $androidJar --output $dex $classFiles
Check-Exit
Push-Location $dex
try { & "$toolRoot\aapt.exe" add "$build\unsigned.apk" 'classes.dex'; Check-Exit } finally { Pop-Location }
& "$toolRoot\zipalign.exe" -f 4 "$build\unsigned.apk" "$build\aligned.apk"
Check-Exit
$keystore = Join-Path $build 'debug.keystore'
if (!(Test-Path $keystore)) {
    & "$java\bin\keytool.exe" -genkeypair -keystore $keystore -storepass android -keypass android -alias caught -dname 'CN=CAUGHT Development' -keyalg RSA -keysize 2048 -validity 10000
    Check-Exit
}
& "$toolRoot\apksigner.bat" sign --ks $keystore --ks-key-alias caught --ks-pass pass:android --key-pass pass:android --out "$build\CAUGHT-companion.apk" "$build\aligned.apk"
Check-Exit
& "$toolRoot\apksigner.bat" verify --verbose "$build\CAUGHT-companion.apk"
Check-Exit
Write-Output "Built: $build\CAUGHT-companion.apk"
