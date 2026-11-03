"""Preparação sintética e chamadas HTTP reais; executado só no container da auditoria."""
import os,sys,json,uuid,urllib.request,urllib.error
from pathlib import Path
from datetime import timedelta
sys.path.insert(0,'/app/backend')
import django
django.setup()
from django.utils import timezone
from django.core.management import call_command
from django.db import connection
assert connection.settings_dict['HOST']=='ps-ret-002-db'
assert connection.settings_dict['NAME']=='auditoria_ret_002'
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.application.autoridades import cadastrar
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import complete_draft
call_command('sincronizar_unidades')
a=cadastrar(actor=Actor('gestor.sintetico','cefor',frozenset({'autoridade:gerir'})),cargo='Diretora de testes',nome='Autoridade sintética',inicio_vigencia=timezone.localdate(),ato_de_nomeacao='PS-RET-002',idempotency_key='autoridade-sintetica-001',correlation_id='PS-RET-002')
if isinstance(a,tuple):a=a[0]
log=[]
def http(method,path,data=None,permissions='',subject='gestor.sintetico',rev=None):
 headers={'Authorization':f'Bearer {subject}|cefor|{permissions}','Content-Type':'application/json','Idempotency-Key':str(uuid.uuid4()),'X-Correlation-ID':'PS-RET-002'}
 if rev is not None:headers['If-Match']=f'"{rev}"'
 req=urllib.request.Request('http://127.0.0.1:8000'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
 try:r=urllib.request.urlopen(req)
 except urllib.error.HTTPError as e:r=e
 raw=r.read().decode();log.append({'method':method,'path':path,'request':data,'status':r.status,'response':raw});Path('/evidencias/preparacao-http.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
 assert r.status<400,(r.status,raw)
 return json.loads(raw) if raw else {}
now=timezone.now();ids=[]
for n in range(1,5):
 existing=Edital.objects.filter(processo__institutional_code=f'PS-RET-002-{n}').first()
 if existing:
  ids.append({'edital':str(existing.id),'processo':str(existing.processo_id)})
  continue
 p=http('POST','/api/v1/admin/processos',{'institutionalCode':f'PS-RET-002-{n}','title':f'Auditoria sintética {n}','firstEdital':{'number':f'AUD-{n}','year':2026,'title':f'Edital sintético {n}'}},'processo:criar,processo:ativar,edital:criar')
 e=Edital.objects.get(processo_id=p['id']);d=complete_draft(seed=800+n)
 d['schedule'][0].update(startAt=(now-timedelta(days=1)).isoformat(),endAt=(now+timedelta(days=10)).isoformat(),isRegistrationPeriod=True)
 d['schedule'].append({'id':str(uuid.uuid4()),'type':'SORTEIO','description':'Sorteio programado sintético','startAt':(now+timedelta(days=12)).isoformat(),'order':2})
 path=f'/api/v1/admin/editais/{e.id}'
 http('PUT',path+'/rascunho',d,'edital:elaborar',rev=e.revision);e.refresh_from_db()
 http('POST',path+'/submissoes',{},'edital:submeter',subject='elaborador.original',rev=e.revision);e.refresh_from_db()
 http('POST',path+'/homologacoes',{'reason':'Conferência sintética'},'edital:homologar',subject='homologador.original',rev=e.revision);e.refresh_from_db()
 http('POST',path+'/publicacoes',{'signatory':{'authorityId':str(a.id)}},'edital:publicar',subject='publicador.original',rev=e.revision)
 ids.append({'edital':str(e.id),'processo':p['id'],'draft':d})
Path('/evidencias/cenarios.json').write_text(json.dumps({'autoridade':str(a.id),'cenarios':ids},ensure_ascii=False,indent=2))
print('Cenários sintéticos preparados',len(ids))
