# Quickstart: verificar os templates por família e formato

O roteiro de verificação de cada incremento. Os comandos seguem o `CLAUDE.md` (suíte contra
PostgreSQL, banco de teste próprio por worktree).

## Pré-requisitos

- o ambiente da `111` funcionando, com `resvg-py` instalado e a chave da peça ligada;
- o incremento C da `111` (pacote e galeria), na `main` desde o #377;
- `INTERFACE_SELETOR_IDENTIDADE=true` no runserver local, e um ator com o papel de comunicação.

## Incremento 1 — motor generalizado

```bash
cd backend && uv run pytest tests/unit/kit -q
```

Esperado: os testes de referência da `111` passam sem regravar nenhum SVG em
`tests/fixtures/kit_referencias/` (`git status` limpo nessa pasta). SC-1133.

## Incremento 2 — Pós Lato Sensu

1. Publique um Edital com Perfis de carga horária declarada pela interface de elaboração e
   publicação. (O `seed_demo` ou o helper `levar_a_publicacao` dos testes servem de atalho de
   preparação, mas não são a jornada.) Daqui em diante, tudo é pela tela, como a comunicação faria.
2. Abra o kit do Edital, escolha "Pós Lato Sensu" e uma imagem. Confira:
   - as três prévias, cada uma com o texto alternativo;
   - "Inscrições até DD/MM/AAAA" com ano, hora e início no mesmo bloco;
   - nenhum texto nas faixas reservadas do story;
   - "Acesse o edital" só no banner, e a busca nos três.
3. Exporte o PNG do story e o ZIP. A trilha do Edital mostra as duas exportações com família, formato,
   template e imagem.
4. Altere o canal de atendimento da unidade pela tela "Unidades" e reabra o kit: a faixa diz
   "contato: antes → agora".
5. Gere a galeria:

```bash
cd backend && uv run python scripts/galeria_do_kit.py --familia pos-lato-sensu
```

Esperado: cada formato da família em todos os cenários de referência, com a recusa e o motivo onde
não couber, e o identificador, a versão e o resumo curto do template em cada peça. É o material da
aprovação (SC-1135): registre-a em `verificacao.md` com os três dados e a data (FR-3834).

6. Libere só a versão aprovada no ambiente, por exemplo
   `KIT_DE_DIVULGACAO_TEMPLATES=pos-lato-sensu/post@1,pos-lato-sensu/story@1`, e confirme que o
   banner aparece indisponível. Suba a versão de um template numa cópia descartável: ele passa a
   "versão nova em aprovação" até a configuração nomeá-la (FR-3835).
7. Baixe o ZIP e abra o `manifesto.json`: uma entrada por formato em `pecas`, com template, versão,
   resumo e arquivos, e o banner com o motivo `nao_liberado`.

## Incrementos 3a–3f — uma família por PR

Os mesmos passos 2 a 5 com a família do PR. Antes de abrir o PR: o arquivo de origem da família tem
todo ativo com licença e resumo, e o teste de origem passa.

## Verificação completa

```bash
cd backend && make lint check test-pg
```
