"""Recusas e consulta da trilha sem guardar headers de autenticação."""
import json,urllib.request,urllib.error
from pathlib import Path
p=Path('/evidencias');casos=json.loads((p/'resultados-e2e.json').read_text());dados=json.loads((p/'cenarios.json').read_text());result=[]
def chamar(nome,method,path,permissao,scope='cefor',data=None,esperado=403):
 req=urllib.request.Request('http://127.0.0.1:8000'+path,method=method,headers={'Authorization':f'Bearer sujeito.sintetico|{scope}|{permissao}','Content-Type':'application/json','If-Match':'"3"','Idempotency-Key':'negativa-seguranca-adicional-002'},data=json.dumps(data).encode() if data is not None else None)
 try:r=urllib.request.urlopen(req)
 except urllib.error.HTTPError as e:r=e
 body=r.read().decode();result.append({'nome':nome,'path':path,'status':r.status,'expected':esperado,'response':json.loads(body)})
 assert r.status==esperado,(nome,r.status,body)
i=next(c for c in casos if c['id']=='E2E-03');d=next(c for c in casos if c['id']=='E2E-04')
pub={'signatory':{'authorityId':dados['autoridade']}}
chamar('publicar-fora-do-escopo','POST',f'/api/v1/admin/retificacoes/{i["rid"]}/publicacoes','retificacao:publicar',scope='outra-unidade',data=pub,esperado=404)
chamar('publicar-rascunho','POST',f'/api/v1/admin/retificacoes/{d["rid"]}/publicacoes','retificacao:publicar',data=pub,esperado=409)
chamar('auditoria-sem-permissao','GET','/api/v1/admin/auditoria','retificacao:publicar')
chamar('auditoria-autorizada','GET',f'/api/v1/admin/auditoria?aggregateId={i["rid"]}','auditoria:consultar',esperado=200)
(p/'seguranca-adicional.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('4 verificações aprovadas')
