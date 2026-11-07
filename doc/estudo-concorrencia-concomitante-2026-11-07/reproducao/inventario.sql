-- Pessoas com convocação vigente em mais de um recorte do mesmo Edital, Perfil e marco, e o
-- desfecho raiz vigente de cada uma. Só leitura.
with vig as (
  select c.* from convocacao_convocacao c
  where not exists (select 1 from convocacao_convocacao s where s.convocacao_anterior_id = c.id)
), d as (
  select v.edital_id, v.perfil_id, v.marco_id, v.inscricao_id, v.lista_id, v.especie,
         (select x.especie from convocacao_desfechodaconvocacao x
           where x.convocacao_id = v.id order by x.registrado_em desc limit 1) as desfecho
  from vig v
)
select e.number || '/' || e.year as edital, d.inscricao_id,
       count(distinct coalesce(d.lista_id::text, 'AMPLA')) as recortes,
       string_agg(coalesce(left(d.lista_id::text, 8), 'AMPLA') || ':' || d.especie || '->' ||
                  coalesce(d.desfecho, '—'), ' | ' order by d.lista_id nulls first) as percurso
from d join processos_edital e on e.id = d.edital_id
group by 1, 2 having count(distinct coalesce(d.lista_id::text, 'AMPLA')) > 1;
