"""Compara os modelos fora do escopo com HEAD e verifica lint do conteúdo original."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parents[3]
files=['backend/processo_seletivo/processos/models.py','backend/processo_seletivo/comissoes/models.py','backend/processo_seletivo/editais/models/perfis.py']
result=[]
for f in files:
 original=subprocess.check_output(['git','show','HEAD:'+f],cwd=root)
 current=(root/f).read_text(encoding='utf-8')
 original_text=original.decode('utf-8')
 igual=original_text.splitlines()==current.splitlines()
 lint=subprocess.run([str(root/'backend/.venv/Scripts/ruff.exe'),'check','--no-cache','--stdin-filename',f,'-'],input=original,cwd=root,capture_output=True)
 fmt=subprocess.run([str(root/'backend/.venv/Scripts/ruff.exe'),'format','--check','--no-cache','--stdin-filename',f,'-'],input=original,cwd=root,capture_output=True)
 result.append({'arquivo':f,'igual_ao_HEAD':igual,'hash_HEAD':hashlib.sha256(original).hexdigest(),'lint_HEAD_exit':lint.returncode,'lint_HEAD':(lint.stdout+lint.stderr).decode(errors='replace'),'format_HEAD_exit':fmt.returncode,'format_HEAD':(fmt.stdout+fmt.stderr).decode(errors='replace')})
(Path(__file__).parent/'baseline-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(r['igual_ao_HEAD'] for r in result)
print([(r['arquivo'],r['lint_HEAD_exit'],r['format_HEAD_exit']) for r in result])
