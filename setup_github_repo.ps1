Write-Host "Setting up GitHub repository connection..." -ForegroundColor Green
Write-Host ""

Write-Host "Please create a GitHub repository first:" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: ASD-Research-Papers" -ForegroundColor Cyan
Write-Host "3. Description: Multi-agent webscraping system for ASD research papers" -ForegroundColor Cyan
Write-Host "4. Make it Public" -ForegroundColor Cyan
Write-Host "5. Do NOT initialize with README (we already have files)" -ForegroundColor Cyan
Write-Host "6. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter when you've created the repository"

Write-Host "Adding remote repository..." -ForegroundColor Green
git remote add origin https://github.com/AtticusG3/ASD-Research-Papers.git

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host ""
Write-Host "Repository setup complete!" -ForegroundColor Green
Write-Host "Your project is now available at: https://github.com/AtticusG3/ASD-Research-Papers" -ForegroundColor Cyan
Read-Host "Press Enter to continue"
