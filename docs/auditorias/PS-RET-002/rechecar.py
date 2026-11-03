"""Repete arquivos afetados com fixtures completas e cache Python separado."""
import json,sys,pytest
from pathlib import Path
files=json.loads(Path('/evidencias/arquivos-rechecagem.json').read_text())
files=[f for f in files if Path(f).name.startswith('test_')]
sys.exit(pytest.main(['-p','no:cacheprovider','-n','4','--dist','worksteal','-q','-ra',*files]))
