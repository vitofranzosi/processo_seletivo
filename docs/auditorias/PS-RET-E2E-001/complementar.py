"""Cenários adicionais de integração HTTP e extração SQL final."""
source=open('/evidencias/verificar.py').read()
exec(source.split('pub={')[0].replace("'integracao-http.json'","'integracao-complementar.json'"))
c=cases[0];base=VersaoConsolidada.objects.filter(edital_id=c['eid']).latest('materialized_at');event=base.content['schedule'][0]
def create(name,new):
 return request(name,'POST',f'/api/v1/admin/editais/{c["eid"]}/retificacoes',{'baseSnapshotId':str(base.id),'justification':name,'changes':[{'targetPath':f'/schedule/id={event["id"]}/endAt','operation':'REPLACE','newValue':new,'expectedPreviousHash':hashlib.sha256(json.dumps(event['endAt'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}]},'retificacao:elaborar',expected=422)
create('sem-alteracao-efetiva',event['endAt'])
invalid=create('cronograma-invertido','2020-01-01T12:00:00-03:00')
if invalid['status']==201:
 rid=json.loads(invalid['response'])['id']
 for action,permission,who in [('submissoes','retificacao:submeter','submetente.extra'),('homologacoes','retificacao:homologar','homologador.extra')]:
  r=Retificacao.objects.get(pk=rid);request(action,'POST',f'/api/v1/admin/retificacoes/{rid}/{action}',{'reason':'Teste de cronograma'},permission,who,rev=r.revision,expected=200)
 r=Retificacao.objects.get(pk=rid);request('publicar-cronograma-invertido','POST',f'/api/v1/admin/retificacoes/{rid}/publicacoes',{'signatory':{'authorityId':authority}},'retificacao:publicar','publicador.extra',rev=r.revision,expected=422)
for i,c in enumerate(cases):
 request('portal-anonimo-'+str(i),'GET',f'/selecoes/{c["eid"]}/',expected=200)
request('retificacao-inexistente-publica','GET','/api/v1/public/retificacoes/00000000-0000-0000-0000-000000000099',expected=404)
exec(source[source.index('snapshot={}'):].replace("'postgresql.json'","'postgresql-final.json'"))
