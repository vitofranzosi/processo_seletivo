# Contrato: os cenários de aceite e regressão

**Feature**: [../spec.md](../spec.md)

São os treze cenários mínimos do pedido do usuário (07/11/2026), na numeração dele, com o lugar do
teste e o que ele prova.

**Fixtures:** as da `115` (`tests/fixtures/documentos_da_convocacao.py`), com duas chaves novas:

- `ALISTAMENTO`: obrigatório na convocação, `requiredWhen` = *"no caso de candidatos do sexo
  masculino, maiores de 18 anos"*;
- `LAUDO`: obrigatório na convocação, recorte por modalidade PcD, sem condição.

**Siglas dos arquivos de teste:**

- `ic`: `tests/integration/convocacao/test_inaplicabilidade.py` (novo);
- `dd`: `tests/unit/convocacao/test_documentos_dominio.py` (novo);
- `ia`: `tests/interface/test_aceite_com_inaplicabilidade.py` (novo);
- `fc`: `tests/unit/formalizacao/test_conjunto.py` (existente);
- `cp`: `tests/integration/editais/test_condicao_de_exigencia.py` (novo).

| # | Cenário | Dado | Quando | Então | Teste | Requisitos |
|---|---|---|---|---|---|---|
| 1 | Incondicional não se afasta | certidão sem condição | o alocado envia *"não se aplica"* com motivo bom | `nao_se_aplica_sem_condicao`, nada gravado; a tela não oferece a opção | `ic`, `ia` | FR-4457, SC-1371 |
| 2 | Condicional legitimamente não aplicável | `ALISTAMENTO` da Ana, sem arquivo | *"não se aplica"* com *"Candidata do sexo feminino…"* | *não se aplica*; atende com ciência | `ic` | FR-4457, FR-4458, FR-4470 |
| 3 | Obrigatório conforme | certidão com arquivo aberto | *conforme* | *conforme*; atende sem ciência | `ic` (regressão da `115`) | FR-3585 da `115`, FR-4470 |
| 4 | Obrigatório pendente | histórico | *pendente* com motivo | *pendente*; aceite recusado | `ic` (regressão da `115`) | FR-3592 da `115` |
| 5 | Sem fundamento válido | `ALISTAMENTO` | *"não se aplica"* sem motivo | `motivo_da_conferencia_obrigatorio` | `ic` | FR-4458 |
| 6 | Justificativa `"."` | `ALISTAMENTO` | motivo `"."`, `"-"`, `"..."`, `"   "` | `motivo_sem_conteudo`, nada gravado; o mesmo no *pendente* | `dd`, `ic` | FR-4458 |
| 7 | Recebido, mas não aplicável | `ALISTAMENTO` com arquivo | *"não se aplica"* sem abrir; depois, abrindo | `nao_se_aplica_sem_abertura`; depois, aceito, com versão e hash | `ic` | FR-4460 |
| 8 | Alocado nos casos permitidos | membro só alocado | *"não se aplica"* no `ALISTAMENTO`; e no `LAUDO` | aceito; recusado | `ic` | FR-4465, FR-4457 |
| 9 | Gestor vê e confirma | Ana com 1 *"não se aplica"* | abre o desfecho; registra sem ciência, com ciência superada, com ciência | bloco com condição, motivo, autor e instante; recusa; recusa; aceito, com a trilha citando os `id` | `ia`, `ic` | FR-4467, FR-4468, FR-4469, SC-1372 |
| 10 | Três obrigatórios sem condição | certidão, histórico e `LAUDO` | *"não se aplica"* nos três | três recusas; aceite recusado por falta | `ic` | FR-4457, SC-1371 |
| 11 | Fora do recorte | `LAUDO` da Bia (ampla) | conferência de qualquer resultado; abertura | inexistente (404), nada gravado | `ic` | FR-4464, SC-1373 |
| 12 | Retificação e nova chamada | condição retificada depois da convocação; nova chamada da mesma inscrição | ler a chamada aberta; ler a nova | a aberta lê a condição da versão dela; a nova, a da vigente; o *"não se aplica"* anterior não viaja | `ic`, `cp` | FR-4456, D-013 |
| 13 | Formalização | Ana aceita com `ALISTAMENTO` *"não se aplica"*; Bia com o `LAUDO` fora do recorte | verificar e exportar | *"não se aplica após análise"* com instante × *"não se aplica"*; sem motivo no manifesto | `fc` | FR-4473, SC-1374 |

## Os cenários da composição e da transição

| Cenário | Teste | Requisitos |
|---|---|---|
| Condição em facultativo ou documento da inscrição impede a publicação | `cp` | FR-4453 |
| Condição chega ao PDF depois de vírgula; documento sem condição sai byte a byte igual | `cp`, `tests/contract/test_documento_publicado.py` | FR-4454, SC-1375 |
| Reaproveitamento (`023`) leva a condição | `cp` | FR-4455 |
| Versão publicada antes da feature eleva com `requiredWhen: null` | `tests/integration/publicacoes/test_elevacao_de_versao.py` | FR-4455, FR-4477 |
| *"Não se aplica"* gravado antes em item incondicional: decidida continua decidida; aberta segue a P-1 | `ic` | FR-4470, FR-4476, FR-4478 |
| Substituição envolvendo *"não se aplica"* sem arquivo exige motivo | `ic` | FR-4462 |
| Nova versão depois do *"não se aplica"* recusada | `ic` | FR-4463 |
| Orçamento de consultas da condução e da página | `tests/interface/` (orçamento existente da `115`) | SC-1377 |
