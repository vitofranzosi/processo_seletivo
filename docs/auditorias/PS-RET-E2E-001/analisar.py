"""Confronta artefatos capturados, sem acessar ou alterar a aplicação."""
import json,re,hashlib,urllib.request
from pathlib import Path
p=Path(__file__).parent
sql=json.loads((p/'postgresql.json').read_text(encoding='utf-8'))
final=json.loads((p/'postgresql-final.json').read_text(encoding='utf-8'))
cases=json.loads((p/'resultados-navegador.json').read_text(encoding='utf-8'))
net=json.loads((p/'rede-executar.json').read_text(encoding='utf-8'))
requests=[m['params']['request'] for m in net if m.get('method')=='Network.requestWillBeSent']
responses=[m['params']['response'] for m in net if m.get('method')=='Network.responseReceived']
checks=[]
def check(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})
for i,c in enumerate(cases[:3]):
 api=json.loads((p/f'c{i+1}-api.json').read_text())
 def content(x):return x.get('content',x.get('canonicalContent',{}))
 before=content(api['before']);after=content(api['after'])
 check(f'c{i+1}-api-alterou',before!=after if i==0 else before==after,{'before':before.get('schedule'),'after':after.get('schedule')})
for c in cases:
 original=[r for r in sql['publicacoes']['rows'] if r['edital_id']==c['eid'] and r['publication_order']==1][0]
 preserved=[r for r in final['publicacoes']['rows'] if r['id']==original['id']][0]
 check('original-preservado-'+c['eid'],original==preserved,original['content_hash'])
check('sem-duplicacao',len(sql['publicacoes']['rows'])==7,{'publicacoes':len(sql['publicacoes']['rows']),'esperadas':7})
check('append-only-runtime',all(not r['atualiza'] and not r['exclui'] for r in final['privilegios']['rows']),final['privilegios']['rows'])
base=json.loads((p/'base-futura.json').read_text());v=next(r for r in final['versoes']['rows'] if r['id']==base['base'])
check('base-futura-comprovada',v['valid_from'].startswith('2026-10-30'),{'base':base,'valid_from':v['valid_from']})
for i,c in enumerate(cases):
 req=urllib.request.Request(f'http://127.0.0.1:8017/selecoes/{c["eid"]}/')
 with urllib.request.urlopen(req) as r:
  body=r.read();(p/f'anonimo-c{i+1}.html').write_bytes(body)
  check('portal-sem-autorizacao-ou-cookie-'+str(i+1),r.status==200,{'requestHeaders':dict(req.header_items()),'status':r.status,'sha256':hashlib.sha256(body).hexdigest()})
summary={'checks':checks,'formRequests':[{'url':r['url'],'method':r['method'],'postData':r.get('postData')} for r in requests if r['method']=='POST'],'responses':[{'url':r['url'],'status':r['status']} for r in responses if '/gestao/' in r['url'] or '/selecoes/' in r['url']]}
(p/'verificacoes.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
