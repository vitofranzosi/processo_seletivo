# Achado — O PDF que a página chama de "Edital completo" pode não conter a versão vigente

*Registrado em 12/10/2026, sobre a `main` em `a79ce463`, durante a preparação da spec da Fase A do
assistente de dúvidas. É o `LAC-07` da
[auditoria do assistente](auditoria-assistente-de-duvidas-do-edital-2026-10-12.md), agora
**reproduzido**. Nada foi corrigido. Caminhos relativos a `backend/processo_seletivo/`.*

> **Registro, e não escopo.** Governança é do usuário (`CLAUDE.md`). A correção não entra na spec
> do assistente; lá ela figura só como dependência da abertura pública.

## O que acontece

A página pública da seleção oferece "Ler o Edital completo (PDF)"
(`portal/templates/portal/selecao.html:58`). O link aponta para o documento da **publicação de
origem da versão vigente**, `versao.source_publication_id` (`portal/views.py:151`).

Esse documento pode não conter uma Retificação que já está em vigor, por três razões que se somam.

1. **A versão vigente aplica todos os atos.** A versão consolidada é refeita a partir do original,
   com **todos** os atos publicados, na ordem de vigência (`publicacoes/application/retificacoes.py:786-823`,
   `_materialize_affected_versions`).
2. **O documento de uma Retificação aplica só ela.** O documento é composto sobre a versão-base dessa
   Retificação mais as alterações dela, e não sobre o conteúdo em vigor. O próprio código diz isso
   (`retificacoes.py:826-836`, `_consolidacao`), e a marca de consolidação do documento declara
   corretamente o que ele contém.
3. **A versão aponta para o último ato publicado.** Toda versão materializada durante a publicação de
   uma Retificação registra essa Retificação como `source_publication`, inclusive as versões de
   fronteiras de vigência que ela não criou (`retificacoes.py:807`).

O resultado é que a página pode mostrar o cronograma e as vagas da versão vigente — lidos do
consolidado — e oferecer, como "Edital completo", um documento que não traz uma das Retificações
aplicadas.

## Reprodução

Dois cenários, rodados em 12/10/2026 contra PostgreSQL, num banco de teste próprio. Foi usado um
teste temporário sobre os ajudantes de `backend/tests/fixtures/publicacao.py`, apagado depois da
execução; o roteiro está no fim. Nos dois:

- Edital publicado;
- duas Retificações elaboradas sobre a versão original, uma mudando a descrição e a outra o local
  do mesmo Evento;
- leitura da página com o relógio no instante indicado.

| Cenário | Atos | Versão vigente | Documento ligado pela página | Marca do ato que falta, nos bytes do PDF |
|---|---|---|---|---|
| 1 — vigência futura seguida de correção imediata | R1 com vigência em +10 dias, publicada; depois R2 com vigência imediata, base original (como o ajudante de testes documenta para esse caso) | descrição de R1 **e** local de R2 (lida em +11 dias) | o de R2: local de R2, **descrição original** | marca de R2 presente; **marca de R1 ausente** |
| 2 — duas Retificações elaboradas em paralelo | R1 e R2 sobre a versão original, publicadas nessa ordem | descrição de R1 **e** local de R2 | o de R2: local de R2, **descrição original** | marca de R2 presente; **marca de R1 ausente** |

Nos dois cenários o link para esse documento estava na página (`public-document/<id da publicação
de R2>`).

**O cenário 1 é operacional, e não exótico.** Basta uma prorrogação publicada com vigência futura e,
antes dela, uma correção imediata de outro campo. Durante a vigência da prorrogação, não existe
**nenhum** documento publicado que contenha as duas: o de R1 não tem R2, e o de R2 não tem R1.

## O que **não** se afirma

- **Não se afirma que algum PDF esteja errado.** Cada documento é fiel ao que declara conter, e a
  marca de consolidação diz quais Retificações ele incorpora.
- **Não se afirma que haja perda de dado.** O consolidado vigente está certo, e o "O que mudou" de
  cada ato também.
- O defeito está em **apresentar** um desses documentos como "o Edital completo" da versão vigente.
  A gestão já evita isso de propósito: `interface/views.py:3514-3522` (`_documentos_publicados`) não
  rotula documento nenhum como vigente.

## Alcance

- **Página pública da seleção.** Diretamente.
- **API pública: não alcançada.** `versao-vigente` não devolve a publicação de origem
  (`publicacoes/api/public_serializers.py:95-113`, `VersaoConsolidadaSerializer`). Ela devolve
  `appliedPublications` e, por caminho alterado, a publicação que o produziu (`provenance`, FR-030
  da `001`). É o vínculo certo: o documento do ato que fixou um valor sempre contém esse valor,
  porque é composto da base do ato mais as alterações dele.
- **Teste existente.** `backend/tests/integration/portal/test_documento_oficial.py` afirma que a
  página leva ao documento da `source_publication`. Ele confere o link, e não o conteúdo, e por isso
  continua verde.
- **Assistente de dúvidas.** Uma referência que levasse ao "Edital completo" poderia mostrar
  documento divergente do conteúdo que fundamentou a resposta. A spec da Fase A não usa esse link
  como referência.

## Opções de correção (não decididas)

| Opção | O que muda | Custo |
|---|---|---|
| A | A página diz quais atos o documento ligado contém e lista os demais documentos em vigor, sem chamá-lo de "completo" | Só leitura; não muda publicação |
| B | Recusar publicar Retificação cuja base não contenha todos os atos publicados que vigorarão junto com ela | Muda a regra de Retificação (`048` e anteriores); alcança o caso legítimo de vigência anterior |
| C | Compor um documento para cada versão consolidada, no momento em que ela é materializada | Documento novo, sem ato próprio; toca a decisão de que a versão consolidada não tem documento |
| D | Compor o documento da Retificação sobre o conteúdo que vigorará na data de vigência dela | Muda o que o ato publica; conflita com a marca de consolidação atual |

Qualquer uma é spec própria. A escolha é do usuário.

## Roteiro da reprodução

```python
original = VersaoConsolidada.objects.get(edital=edital)
evento = original.content["schedule"][0]["id"]
futuro = timezone.now() + timedelta(days=10)
r1 = create_retification(api_client, edital,
        [{"targetPath": f"/schedule/id={evento}/description", "operation": "REPLACE",
          "newValue": "R1-MARCA ..."}],
        effective_at=futuro.isoformat(), base=original, suffix="a")
publish_retification(api_client, r1, suffix="a")
r2 = create_retification(api_client, edital,
        [{"targetPath": f"/schedule/id={evento}/location", "operation": "REPLACE",
          "newValue": "R2-MARCA ..."}],
        base=original, suffix="b")
publish_retification(api_client, r2, suffix="b")

versao = effective_version(edital_id=edital.id, at=futuro + timedelta(days=1))
fonte = versao.source_publication                   # a publicação de R2
json.loads(bytes(fonte.canonical_content))          # sem a descrição de R1
b"R1-MARCA" in bytes(fonte.documento.bytes)         # False
b"R2-MARCA" in bytes(fonte.documento.bytes)         # True
```
