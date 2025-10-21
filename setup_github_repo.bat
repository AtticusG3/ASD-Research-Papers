@echo off
echo Setting up GitHub repository connection...
echo.

echo Please create a GitHub repository first:
echo 1. Go to https://github.com/new
echo 2. Repository name: ASD-Research-Papers
echo 3. Description: Multi-agent webscraping system for ASD research papers
echo 4. Make it Public
echo 5. Do NOT initialize with README (we already have files)
echo 6. Click "Create repository"
echo.

pause

echo Adding remote repository...
git remote add origin https://github.com/AtticusG3/ASD-Research-Papers.git

echo Pushing to GitHub...
git push -u origin main

echo.
echo Repository setup complete!
echo Your project is now available at: https://github.com/AtticusG3/ASD-Research-Papers
pause
