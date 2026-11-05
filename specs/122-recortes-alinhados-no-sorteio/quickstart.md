# Quickstart: validar os recortes alinhados

## Passo 0 — Levantamento do acervo na instalação (antes de implementar)

**Só de leitura.** Era exigido pela 13ª decisão do usuário; **o usuário o dispensou em 05/11/2026**
(*"esquece a VM"*), e a implementação seguiu sem ele. O roteiro fica para quem quiser medir depois. Roda quem tem acesso à VM, no `manage.py shell` do serviço, com as
variáveis de ambiente do serviço carregadas.

O roteiro abre uma transação, a declara só de leitura antes de qualquer consulta e a desfaz no fim.
Nenhuma escrita é possível dentro dela, nem por engano.

```python
from django.db import connection, transaction

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio


def apontada(conteudo, perfil_id):
    for perfil in conteudo.get("profiles") or []:
        if str(perfil.get("id")) == str(perfil_id):
            valor = perfil.get("generalCompetitionModalityId")
            return str(valor) if valor else None
    return None


ESPECIES = (
    ("relacoes", RelacaoDeHabilitados.objects.select_related("versao"), lambda r: r.versao),
    ("sorteios", Sorteio.objects.select_related("relacao__versao"), lambda r: r.relacao.versao),
    ("atos", AtoDeOrdenacao.objects.select_related("versao"), lambda r: r.versao),
    ("publicacoes", PublicacaoResultado.objects.select_related("ato__versao"), lambda r: r.ato.versao),
)

with transaction.atomic():
    connection.cursor().execute("SET TRANSACTION READ ONLY")
    for edital in Edital.objects.order_by("id"):
        try:
            vigente = effective_version(edital_id=edital.id).content
        except Exception:
            continue
        linhas = {}
        for especie, consulta, versao_de in ESPECIES:
            for registro in consulta.filter(edital=edital, lista_id__isnull=False):
                if str(registro.lista_id) != apontada(vigente, registro.perfil_id):
                    continue
                nascido = apontada(versao_de(registro).content, registro.perfil_id) == str(
                    registro.lista_id
                )
                chave = (str(registro.marco_id), "nascido" if nascido else "tornado")
                linhas.setdefault(chave, {}).setdefault(especie, 0)
                linhas[chave][especie] += 1
        for (marco, origem), contagem in sorted(linhas.items()):
            print(edital.id, marco, origem, contagem)
    transaction.set_rollback(True)
```

**O que fazer com a saída:**

- **Nenhuma linha**: não há acervo excedente, e a seção de histórico só servirá a Editais futuros com
  Retificação (T1, T3, T5).
- **Linhas sem `publicacoes`**: há acervo, nenhum divulgado. A implementação segue como está.
- **Alguma linha com `publicacoes`**: **pare e apresente os números ao usuário** (Edital, marco,
  origem, quantas publicações). A explicação no portal é decisão dele, e não entra no escopo por si
  (FR-3915).

## Passo 1 — Suíte

```bash
cd backend && make lint check test-pg
```

Os testes que esta feature acrescenta, isolados:

```bash
cd backend && PYTEST_ADDOPTS="-k recorte_excedente or recortes_alinhados" make test-pg PYTEST_WORKERS=0
```

## Passo 2 — A jornada da SC-1165, no navegador

Pré-requisito: um Edital de demonstração com um Perfil que declara AC, PPI e PcD, AC apontada como a
ampla, um marco por sorteio, e **acervo excedente** gravado pelo helper dos testes da feature (um ato
de AC sorteado sob a regra antiga). O passo a passo da montagem fica no `verificacao.md` da
implementação.

1. Com a presidência, abrir a tela do sorteio. **Esperado**: três recortes; a frase da FR-3895; a
   seção de histórico com o registro de AC e a frase de **nascido**; nenhum botão nela.
2. Congelar e sortear os três recortes. **Esperado**: nenhuma pendência de AC.
3. Com o Publicador puro (`paula.publicadora`, papel `publicador`), abrir a página do Edital.
   **Esperado**: um *divulgar o resultado* por marco.
4. Segui-lo. **Esperado**: o quadro com três recortes; cada célula de divulgação leva à prévia.
5. Divulgar os três. **Esperado**: as três células como *feito*.
6. Abrir a Supervisão com os dois atores. **Esperado**: nenhum sinal daquele marco.
7. Abrir a prévia do ato de AC pelo endereço antigo. **Esperado**: a frase no lugar do botão.
8. Abrir o relatório do Edital. **Esperado**: três linhas de lista e o marco como definitivo, se as três
   forem definitivas.

## Passo 3 — A matriz temporal

Os casos T1 a T7 de [research.md](research.md), R-11, são testes de integração. Conferir na matriz de
rastreabilidade que cada um tem teste, e que cada caso-limite da spec também tem.
