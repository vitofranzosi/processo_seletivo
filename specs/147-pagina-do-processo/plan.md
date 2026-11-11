# Implementation Plan: A página do Processo Seletivo

**Branch**: `claude/gps-processo-seletivo-ui-ux-a59d79` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

## Summary

Reescrever o template de `interface:processo-detalhe` na forma da alternativa B, com os seis ajustes,
sobre um módulo de composição puro que só reagrupa o que a view já lê. A rota, a view de entrada, as
permissões, os atos e as telas de destino não mudam. Uma folha própria, `telas/processo.css`. Os
testes que ancoravam a forma antiga (`078`, `058`, `038`) são revistos junto com as specs de origem,
que recebem a marca de substituição.

## Technical Context

**Language/Version**: Python 3.13, Django 5 — templates, sem JavaScript novo
**Primary Dependencies**: as de hoje
**Storage**: nenhuma escrita; PostgreSQL só leitura
**Testing**: pytest (`make test-pg`), Playwright no grupo `navegador` para a jornada
**Target Platform**: gestão (`/gestao/`), navegador
**Performance Goals**: no máximo +3 consultas por papel em relação à página de hoje (SC-1663)
**Constraints**: CSP sem estilo nem script em linha; classe citada exige regra na folha; página sem
rolagem lateral
**Scale/Scope**: Processos de 1 a ~30 Editais

## Constitution Check

- **Negar por padrão**: nenhuma porta nova; cada oferta usa a mesma decisão de hoje — `pode_gerir_comissao`,
  `auditoria:consultar`, `edital:criar`, `atos_processo.disponiveis`, o alcance da Supervisão.
- **Publicação imutável / nada é excluído**: a feature não escreve.
- **Uma verdade só**: nenhum número calculado pela página (FR-5322); o recorte da faixa e a contagem
  por situação são reagrupamento.
- **Rastreabilidade**: matriz em [rastreabilidade.md](rastreabilidade.md); requisitos substituídos
  marcados nas specs de origem (FR-5323).

## O desenho

### O módulo `interface/pagina_do_processo.py`

Puro, sem consulta própria além das de leitura que hoje já se fazem em outro lugar:

- `compor(processo, ator, editais, pulso, sinais, atos, pendentes, alcance)` devolve um objeto com:
  `onde` (frase e detalhe, FR-5301); `linhas` (uma `LinhaDoEdital` por Edital, com pulso, sinais,
  Retificações e ações da pessoa); `grupos` (FR-5310, FR-5311); `faixa` (FR-5303, sem o Edital do
  próximo passo); `marcos` e `marcos_demais` (FR-5319); `com_sinal` e `total_de_sinais` (FR-5317);
  `com_inscricoes_abertas` (FR-5320); `administracao` (cada ato com `impedido`, FR-5307).
- As Retificações em curso vêm de `atos_retificacao.em_curso_por_edital` — uma consulta — e entram na
  faixa pelo argumento `em_curso`, para não serem lidas duas vezes.
- A faixa vem de `trabalho.do_ator`; o recorte das avaliações (FR-5309) é um parâmetro novo e
  opcional, `processo=`, em `trabalho.do_ator` e em `_das_avaliacoes`, que filtra as atribuições de
  `minhas_etapas` **antes** de `carga_nas_etapas`. A Lista não passa o parâmetro e não muda.

### A view

`views.processo_detalhe` continua lendo o que lê hoje; `aguardando_elaboracao` ganha a condição de
`FR-5304` (`pode_criar_edital` ou `pode_gerir_comissao`); o contexto recebe o resultado de `compor`.
O gancho do protótipo (`?prototipo=`) e os arquivos dele saem.

### O template

`interface/processo_detalhe.html`, reescrito na ordem de `UX-440`, reaproveitando: as classes de
cabeçalho do Centro (`cc-onde`, `cc-estados`, `cc-grade`, `cc-administracao`, `cc-terminais`), os
parciais `_item_de_trabalho.html`, `_sinal.html` e `_serie_de_inscricoes.html`, e as classes da faixa
(`itens-de-trabalho`) e da marca de Retificação da Lista. Ids de região: `acoes-processo` (O que fazer
agora), `atencao-titulo`, `editais-titulo`, `serie-titulo`, `administracao-titulo`. O pulso agregado
vai para o topo (FR-5321).

### A folha `telas/processo.css`

As regras do protótipo, sem o prefixo de protótipo, e mais as que os guardiões pedem. O
`centro.css` e o `lista.css` continuam carregados pela página, e não são alterados; o que deles é
usado fica listado no comentário de abertura da folha nova. A ordem de "Precisa de atenção" antes
dos marcos no estreito (UX-440) sai de a grade pôr os marcos numa seção própria da coluna esquerda,
reordenada por `order` no estreito.

## Guardiões que vão reprovar, e devem

- `test_telas_de_quem_elabora.py` (078): ordem das regiões e a tabela de Editais.
- `test_polish_da_058.py` (058): os atos em "O que fazer agora".
- `test_supervisao.py` e `acceptance/test_supervisao_do_processo.py` (038, 045): a região
  `conducao-titulo`.
- `test_processo.py`, `test_hardening_pos_auditoria.py`, `test_oferta_da_comissao.py` e os demais da
  lista do inventário: textos e destinos.
- `test_acessibilidade` e o guardião de classe sem regra: classes novas na folha.

Cada um é revisto para a regra nova, citando o requisito da 147, e nenhum é apagado sem que a
garantia dele continue coberta por outro.

## Riscos

- **Teste que ancora o texto antigo sem razão funcional** — reescrever o caso, e não contorná-lo.
- **A faixa da 104 na Lista** — o parâmetro novo é opcional e a Lista não o passa; o teste da Lista
  continua o mesmo.
- **Custo do avaliador** — coberto por teste de orçamento (SC-1663).

## Verificação

`cd backend && make lint check test-pg`, mais a jornada no navegador a 1366 e 390 px, e as capturas
do banco `ps_ux_147` comparadas às da rodada 1.
