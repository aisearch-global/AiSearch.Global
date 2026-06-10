@echo off
cd /d "%~dp0"
echo Pushing SEO/AEO audit fixes to GitHub...
git push origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS — changes deployed to Cloudflare Pages.
) else (
    echo FAILED — check your GitHub credentials.
)
pause
