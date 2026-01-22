:: for Windows
:: GitHub repository installation of Starfish PDK files for KLayout

:: Assumes that 
:: - Qfounbdry-* repositories are in the user's profile directory, under OneDrive/Documents/GitHub
:: - KLAYOUT_HOME is in the user's profile directory, as KLayout

Check if the github directory exists
if not exist "%userprofile%\Documents\Github" (
    echo GitHub directory not found in %userprofile%\Documents\Github
    echo Please clone the Qfoundry repositories from GitHub into this directory first.
    pause
    exit /b 1
)
mklink /d %userprofile%\KLayout\tech\Qfoundry %userprofile%\Documents\Github\PDK_Qfoundry\klayout_PDK\tech\

