:: for Windows
:: GitHub repository installation of Starfish PDK files for KLayout

:: Assumes that 
:: - Starfish-* repositories are in the user's profile directory, under OneDrive/Documents/GitHub
:: - KLAYOUT_HOME is in the user's profile directory, as KLayout

mklink /d %userprofile%\KLayout\tech\Starfish %userprofile%\OneDrive\Documents\Github\PDK_Starfish\klayout_PDK\tech\

