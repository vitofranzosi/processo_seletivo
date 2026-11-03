"""Integração HTTP e SQL de leitura; nenhuma transição é escrita diretamente no banco."""
import sys,json,uuid,urllib.request,urllib.error,hashlib
from pathlib import Path
sys.path.insert(0,'/app/backend')
import django
django.setup()
from django.db import connection
from processo_seletivo.publicacoes.models_retificacao import Retificacao,VersaoConsolidada
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.auditoria.models import RegistroAuditoria
root=Path('/evidencias');cases=json.loads((root/'resultados-navegador.json').read_text());authority=json.loads((root/'cenarios.json').read_text())['autoridade'];results=[]
def request(name,method,path,data=None,perms='',subject='teste.http',scope='cefor',rev=None,key=None,expected=None):
 headers={'Authorization':f'Bearer {subject}|{scope}|{perms}','Content-Type':'application/json','Idempotency-Key':key or str(uuid.uuid4())}
 if rev is not None:headers['If-Match']=f'"{rev}"'
 req=urllib.request.Request('http://127.0.0.1:8000'+path,method=method,headers=headers,data=json.dumps(data).encode() if data is not None else None)
 try:r=urllib.request.urlopen(req)
 except urllib.error.HTTPError as e:r=e
 body=r.read();record={'name':name,'method':method,'path':path,'request':data,'subject':subject,'permissions':perms,'scope':scope,'ifMatch':rev,'key':headers['Idempotency-Key'],'status':r.status,'expected':expected,'response':body.decode(errors='replace') if 'pdf' not in r.headers.get('Content-Type','') else {'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}}
 record['passed']=r.status in expected if isinstance(expected,list) else r.status==expected if expected else None;results.append(record);(root/'integracao-http.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));return record
def item(i):return Retificacao.objects.get(pk=cases[i]['rid'])
def trans(i,action,perms,subject='teste.http',scope='cefor',rev=None,expected=403,data=None,key=None):
 r=item(i);return request(action,'POST',f'/api/v1/admin/retificacoes/{r.id}/{action}',data if data is not None else {'reason':'Fundamento sintético'},perms,subject,scope,r.revision if rev is None else rev,key,expected)
pub={'signatory':{'authorityId':authority}}
trans(2,'publicacoes','retificacao:elaborar',data=pub)
trans(3,'homologacoes','retificacao:publicar')
trans(3,'submissoes','retificacao:submeter',scope='outra-unidade',expected=404)
trans(3,'publicacoes','retificacao:publicar',expected=409,data=pub)
trans(2,'publicacoes','retificacao:publicar',expected=422,data={'signatory':{'authorityId':str(uuid.uuid4())}})
# A vigência vencida precede a autoridade neste cenário: testar autoridade no rascunho devolvido após homologação.
r=item(3);change=r.alteracoes.first();changes=[{'targetPath':a.target_path,'operation':a.operation,'newValue':a.new_value,'expectedPreviousHash':a.expected_previous_hash} for a in r.alteracoes.all()]
payload={'justification':'Edição pela API após devolução','changes':changes}
request('homologador-editar','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:homologar',rev=r.revision,expected=403)
old=r.revision
request('editar-valido','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:elaborar',rev=old,expected=200)
request('editar-obsoleto','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:elaborar',rev=old,expected=412)
trans(3,'submissoes','retificacao:submeter',subject='unico.sintetico',expected=200)
trans(3,'homologacoes','retificacao:homologar',subject='unico.sintetico',expected=200)
trans(3,'publicacoes','retificacao:publicar',subject='unico.sintetico',data=pub,expected=403)
trans(3,'publicacoes','retificacao:publicar',subject='outro.publicador',data={'signatory':{'authorityId':str(uuid.uuid4())}},expected=422)
trans(3,'publicacoes','retificacao:publicar',subject='outro.publicador',data={},expected=422)
key=str(uuid.uuid4());revision=item(3).revision
trans(3,'publicacoes','retificacao:publicar',subject='outro.publicador',data=pub,expected=201,key=key)
trans(3,'publicacoes','retificacao:publicar',subject='outro.publicador',data=pub,expected=201,key=key,rev=revision)
trans(3,'publicacoes','retificacao:publicar',subject='outro.publicador',data=pub,expected=409)
request('inexistente','GET',f'/gestao/retificacoes/{uuid.uuid4()}/',expected=200)
for i,c in enumerate(cases):
 request('publica-retificacao-'+str(i),'GET',f'/api/v1/public/retificacoes/{c["rid"]}',expected=404 if i==2 else 200)
 for p in Publicacao.objects.filter(edital_id=c['eid']):request('documento-'+str(p.id),'GET',f'/api/v1/public/publicacoes/{p.id}/documento',expected=200)
snapshot={}
queries={
 'retificacoes':'SELECT id,edital_id,status,revision,created_by,created_at,prepared_by,submitted_at,homologated_by,homologated_at,homologation_reason,justification,effective_at,publication_id,base_snapshot_id FROM publicacoes_retificacao ORDER BY created_at',
 'alteracoes':'SELECT * FROM publicacoes_alteracaonormativa ORDER BY retificacao_id,"order"',
 'publicacoes':'SELECT id,edital_id,publication_order,published_at,effective_at,published_by,content_hash,signatory_name FROM publicacoes_publicacao ORDER BY edital_id,publication_order',
 'versoes':'SELECT id,edital_id,valid_from,materialized_at,source_publication_id,content_hash,content FROM publicacoes_versaoconsolidada ORDER BY edital_id,valid_from,materialized_at',
 'auditoria':'SELECT * FROM auditoria_registroauditoria ORDER BY occurred_at',
 'processos':'SELECT id,status,institution_scope FROM processos_processoseletivo',
 'privilegios':"SELECT tablename,has_table_privilege('auditoria_runtime',quote_ident(schemaname)||'.'||quote_ident(tablename),'UPDATE') AS atualiza,has_table_privilege('auditoria_runtime',quote_ident(schemaname)||'.'||quote_ident(tablename),'DELETE') AS exclui FROM pg_tables WHERE schemaname='public' AND tablename IN ('publicacoes_publicacao','publicacoes_versaoconsolidada','auditoria_registroauditoria')"
}
for name,sql in queries.items():
 try:
  with connection.cursor() as cur:cur.execute(sql);snapshot[name]={'sql':sql,'rows':[dict(zip([d[0] for d in cur.description],r)) for r in cur.fetchall()]}
 except Exception as e:snapshot[name]={'sql':sql,'error':str(e)}
(root/'postgresql.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2,default=str))
print(json.dumps([{'name':r['name'],'status':r['status'],'passed':r['passed']} for r in results],indent=2));print('SQL',[(k,len(v.get('rows',[])),v.get('error')) for k,v in snapshot.items()])
