$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)
Set-Location ..

python -m unittest discover -s tests
python -c "import ast; ast.parse(open('contracts/GreenTrace.py', encoding='utf-8').read())"
genlayer lint contracts/GreenTrace.py
genlayer deploy contracts/GreenTrace.py --name GreenTrace
