# Quickstart — verificar a 060

Os cenários que provam a feature de ponta a ponta. Os contratos estão em
[contracts/](contracts/); o modelo, em [data-model.md](data-model.md).

## 1. A suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_060
```

**Esperado**: verde. Os pulados podem subir, com os testes de gatilho e de trava da 060, que só o
PostgreSQL verifica; as falhas do modo SQLite não podem mudar de causa (CLAUDE.md).

**A fixture de bytes** (`tests/contract/test_documento_publicado.py`) passa **sem**
`documento_publicado_v1.pdf` refeito — é a prova de que o Cefor não mudou (`SC-430`).

## 2. A preparação do banco

Num banco próprio:

```bash
cd backend && make preparar DB_NAME=ps_060_demo
```

**Esperado**: o provisionamento diz `34 de 34` na segunda passada — as tabelas da 060 não são
append-only (research R-006) — e `sincronizar_unidades` diz `Unidades: 1 criadas, 0 alteradas,
0 sem mudança.` Rodar de novo: `0 criadas, 0 alteradas, 1 sem mudança.`

## 3. Duas unidades, dois documentos

No mesmo banco:

1. Acrescentar ao `unidades.json`, **só nesta cópia de trabalho e sem commit**, uma segunda Unidade
   (`"serra"`, *Campus Serra*, cabeçalho `["Campus Serra"]`, local `"Serra (ES)"`) e rodar
   `sincronizar_unidades`.
2. Pela camada de aplicação, num shell (o seletor de identidade só oferece o escopo padrão —
   research R-016), com um Gestor e um Publicador de cada escopo:
   - cadastrar uma autoridade em cada Unidade;
   - levar um Edital de cada Unidade até a publicação, cada um com a sua autoridade.
3. Extrair os dois `DocumentoPublicado.bytes` e lê-los com `pdftotext -layout`.

**Esperado**: o do Campus Serra abre com *Ministério da Educação · Instituto Federal do Espírito
Santo · Campus Serra* e fecha com *Serra (ES), <data>.*, sem nenhuma ocorrência de *Cefor*,
*Centro de Referência* ou *Vitória* (`SC-429`); o do Cefor, como hoje.

4. Tentar publicar o Edital do Campus Serra com a autoridade do Cefor.

**Esperado**: `422 autoridade_indisponivel`, e nenhuma Publicação nova (`SC-431`).

## 4. Trocar a autoridade sem mudar o sistema

Pela interface (preview, `INTERFACE_SELETOR_IDENTIDADE=true`), como Gestor do Cefor:

1. Lista de Editais → *Autoridades da unidade*. Cadastrar *"Diretora-Geral"*, nome fictício,
   portaria fictícia, início hoje. Cronometrar.
2. Como Publicador, publicar um Edital homologado escolhendo essa autoridade.
3. Como Gestor, tentar corrigir o nome dela. **Esperado**: recusa com a orientação de encerrar e
   cadastrar outra.
4. Encerrar com fim hoje; cadastrar outra com início amanhã. Conferir os três grupos da lista
   (UX-149).
5. Abrir a consulta pública da Publicação do passo 2 e o documento dela.

**Esperado**: cadastrar leva menos de três minutos (`SC-432`); a Publicação, a consulta e o documento
continuam dizendo a primeira autoridade (`SC-433`); a trilha de auditoria mostra *Cadastrou
autoridade* e *Encerrou autoridade* com os valores.

## 5. Sem autoridade vigente

Num banco de trabalho, encerrar pela tela todas as autoridades do Cefor com fim hoje e, **no dia
seguinte**, abrir a publicação de um Edital homologado. A tela recusa fim de ontem
(`encerramento_retroativo`, FR-1120), e é por isso que o cenário precisa da virada do dia — ou, para
não esperar, gravar o fim de ontem direto pelo `manage.py shell`, que não passa pelo comando. Isso só
funciona com autoridade **nunca usada** ou usada antes de ontem: para a usada hoje, o banco recusa fim
anterior ao dia do primeiro uso (`autoridade_usada_imutavel`, research R-006), e esse é o
comportamento esperado.

**Esperado**: a frase de FR-1127 no lugar do seletor e o botão desabilitado; um POST forjado com o
identificador de uma encerrada volta `autoridade_fora_de_vigencia`.

## 6. Nada se exclui

```bash
cd backend && uv run python manage.py dbshell -- -c "DELETE FROM unidades_autoridadehabilitada;"
```

**Esperado**: o gatilho recusa (`SC-434`). O mesmo para `unidades_unidade`, e para retirar uma
Unidade do `unidades.json` e sincronizar (`unidade_retirada`).

## 7. Implantação

Antes da primeira operação real, como Gestor do Cefor, cadastrar pela tela as três autoridades que o
catálogo tinha — Reitora, Pró-Reitor de Ensino e Diretora-Geral do Cefor —, só com o cargo enquanto
o Cefor não fornecer nome e portaria (FR-1124, research R-013).
