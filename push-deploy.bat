@echo off
cd /d "%~dp0"

echo Clearing any stale git locks...
if exist ".git\index.lock" del /f ".git\index.lock"
if exist ".git\HEAD.lock" del /f ".git\HEAD.lock"

echo Committing all SEO/AEO audit changes...
git add -A
git commit -m "Full SEO/AEO audit pass: meta/titles, internal links, HowTo/ItemList/Speakable schema, dateModified

- Meta descriptions: trimmed 9 oversized pages (index.html was 291 chars), expanded 1 short page
- Title tags: fixed 4 pages over 60 chars; insights/index now keyword-rich
- Internal links: 3 contextual links per insight article + related reading sections
- Schema: HowTo on traction-stack, ItemList on insights/index, Speakable on FAQ + all insight articles
- dateModified updated to 2026-06-10 on all 3 insight articles
- aeo-audit.html title now includes Australia geo qualifier
- robots.txt: removed non-standard LLMs: directive"

echo.
echo Pushing to GitHub...
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS -- changes live on Cloudflare Pages.
) else (
    echo FAILED -- check your GitHub credentials.
)
pause
