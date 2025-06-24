@echo off
REM Script to automate the update of RNC data in Windows
REM Usage: update_rnc_data.bat [DOWNLOAD_URL]

setlocal enabledelayedexpansion

REM Configuración
set "SCRIPT_DIR=%~dp0"
set "MODULE_DIR=%SCRIPT_DIR%.."
set "DATA_DIR=%MODULE_DIR%\data"
set "TOOLS_DIR=%SCRIPT_DIR%"
set "TEMP_ZIP=DGII_RNC_TEMP.zip"
set "TEMP_FILE=DGII_RNC_TEMP.TXT"

REM Default URL (can be overridden as a parameter)
set "DEFAULT_URL=https://www.dgii.gov.do/app/WebApps/Consultas/RNC/DGII_RNC.zip"
set "DOWNLOAD_URL=%1"
if "%DOWNLOAD_URL%"=="" set "DOWNLOAD_URL=%DEFAULT_URL%"

echo Starting RNC data update...
echo Download URL: %DOWNLOAD_URL%

REM Verify that we are in the correct directory
if not exist "%MODULE_DIR%\__manifest__.py" (
    echo Error: __manifest__.py file not found
    echo Make sure to run this script from the module directory
    exit /b 1
)

REM Create directories if they don't exist
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

REM Download ZIP file
echo Downloading RNC (ZIP) file...
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%'"
if errorlevel 1 (
    echo Error downloading file
    exit /b 1
)
echo ZIP file downloaded successfully

REM Verify that the ZIP file was downloaded correctly
if not exist "%TEMP_ZIP%" (
    echo Error: ZIP file not downloaded
    exit /b 1
)

REM Extract ZIP file
echo Extracting ZIP file...
powershell -Command "Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '.' -Force"
if errorlevel 1 (
    echo Error extracting ZIP file
    del "%TEMP_ZIP%" 2>nul
    exit /b 1
)

REM Search for TXT file in TMP folder
echo Searching for TXT file in TMP folder...
if exist "TMP\*.txt" (
    for %%f in (TMP\*.txt) do (
        echo Copying file: %%f
        copy "%%f" "%TEMP_FILE%" >nul
        goto :found_txt
    )
) else (
    echo Error: TXT file not found in TMP folder
    del "%TEMP_ZIP%" 2>nul
    rmdir /s /q "TMP" 2>nul
    exit /b 1
)

:found_txt
if not exist "%TEMP_FILE%" (
    echo Error: TXT file not copied
    del "%TEMP_ZIP%" 2>nul
    rmdir /s /q "TMP" 2>nul
    exit /b 1
)
echo TXT file extracted successfully

REM Convert file
echo Converting file to compressed JSON...
python "%TOOLS_DIR%\convert_rnc_data.py" "%TEMP_FILE%" "%DATA_DIR%"
if errorlevel 1 (
    echo Error in conversion
    del "%TEMP_FILE%" 2>nul
    del "%TEMP_ZIP%" 2>nul
    rmdir /s /q "TMP" 2>nul
    exit /b 1
)
echo Conversion completed

REM Clean temporary files
del "%TEMP_FILE%" 2>nul
del "%TEMP_ZIP%" 2>nul
rmdir /s /q "TMP" 2>nul

REM Show statistics of the generated file
if exist "%DATA_DIR%\rnc_data.json.gz" (
    for %%A in ("%DATA_DIR%\rnc_data.json.gz") do set "FILE_SIZE=%%~zA"
    set /a "FILE_SIZE_MB=%FILE_SIZE%/1024/1024"
    echo Generated file: %DATA_DIR%\rnc_data.json.gz (%FILE_SIZE_MB% MB)
    echo Process completed successfully
) else (
    echo Error: Data file not generated
    exit /b 1
)

echo RNC data update completed!
echo Remember to update the module in the clients: -u l10n_do_rnc

endlocal 