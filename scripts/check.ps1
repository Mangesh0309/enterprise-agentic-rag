$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot/../backend"
python -m pytest
Pop-Location

Push-Location "$PSScriptRoot/../frontend"
npm run build
Pop-Location
