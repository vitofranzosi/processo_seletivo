"""Confronto dos registros SQL e capturas HTTP, sem mutações."""
import json,hashlib
from pathlib import Path
p=Path(__file__).parent
s=json.loads((p/'postgresql.json').read_text(encoding='utf-8'))
casos=json.loads((p/'resultados-e2e.json').read_text(encoding='utf-8'))
checks=[]
def verificar(nome,ok,detalhe):
 checks.append({'nome':nome,'aprovado':bool(ok),'detalhe':detalhe})
def linhas(chave):return s[chave]['rows']
for c in casos:
 r=next(r for r in linhas('retificacoes') if r['id']==c['rid'])
 esperado='EM_ELABORACAO' if c['id']=='E2E-04' else 'HOMOLOGADA' if c['id'] in ('E2E-03','E2E-06') else 'PUBLICADA'
 verificar(c['id']+'-estado',r['status']==esperado,{'estado':r['status'],'retificacao':r['id'],'publication_id':r['publication_id']})
 if c['id'] in ('E2E-03','E2E-06'):
  verificar(c['id']+'-sem-publicacao-parcial',r['publication_id'] is None and not any(a['aggregate_id']==r['id'] and a['operation']=='PUBLICAR' for a in linhas('auditoria')),r['id'])
for pub in linhas('publicacoes'):
 verificar('hash-'+pub['id'],hashlib.sha256(pub['canonical_content'].encode()).hexdigest()==pub['content_hash'],pub['content_hash'])
c=next(c for c in casos if c['id']=='E2E-05');r=next(r for r in linhas('retificacoes') if r['id']==c['rid']);pub=next(a for a in linhas('publicacoes') if a['id']==r['publication_id'])
futuras=[v for v in linhas('versoes') if v['edital_id']==c['eid'] and v['valid_from'].startswith('2026-10-30')]
verificar('historico-futuro-preservado',len(futuras)==2 and all(v['content']==json.loads(pub['canonical_content']) for v in futuras),[{'id':v['id'],'source':v['source_publication_id'],'hash':v['content_hash']} for v in futuras])
for c in casos:
 antes=c['antes']['content']['profiles'][0]['classificationMilestones'][0]
 depois=c['depois']['content']['profiles'][0]['classificationMilestones'][0]
 verificar(c['id']+'-semente-preservada',antes==depois,'Marco e método da ocorrência inalterados')
verificar('runtime-append-only',all(not r['atualiza'] and not r['exclui'] for r in linhas('privilegios')),linhas('privilegios'))
prep=json.loads((p/'preparacao-http.json').read_text(encoding='utf-8'))
for req in prep:
 if req['path'].endswith('/publicacoes') and req['status']==201:
  response=json.loads(req['response']);pub=next(p for p in linhas('publicacoes') if p['id']==response['id'])
  verificar('original-preservado-'+pub['id'],pub['content_hash']==response['contentHash'],pub['content_hash'])
(p/'integridade-verificada.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(checks),'verificações;',sum(not c['aprovado'] for c in checks),'reprovações')
assert all(c['aprovado'] for c in checks)
