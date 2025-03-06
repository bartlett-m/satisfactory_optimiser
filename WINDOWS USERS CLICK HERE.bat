@echo off
rem If you are a Linux user and looking for the equivalent file, just mark
rem main.py as executable and run it directly.  It works fine there.
setlocal
    rem The script is still capable of turning off hash randomisation itself
    rem on Windows, but its not as great at it, so we give it a helping hand
    rem while we are already busy working around an issue with pyw.exe.
    set "PYTHONHASHSEED=0" && start pythonw main.py
endlocal
@echo on