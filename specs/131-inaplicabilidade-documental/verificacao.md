# Verificação: A inaplicabilidade documental tem fundamento publicado (131)

**Data**: 2026-11-07, sobre a `main` com o PR #425 (merge `8ca4ce41`), na branch
`claude/nostalgic-gagarin-492fdc`.

## 1. A suíte

**Primeira rodada completa**, `make lint check test-pg`:

- `DB_NAME=ps131`, 4 workers, `worksteal`;
- sem o grupo `navegador`;
- com o `.venv` desta worktree.

O resultado foi lint e `check` verdes, e **1 falha, 17 230 passando e 21 pulados**, em 769s. A
falha era real:

- o teste `unit/publicacoes/test_pdf_grafia.py::test_todo_texto_impresso_passa_pela_validacao`
  acusou que o PDF passou a imprimir a condição e a regra do caractere sem grafia não a percorria;
- a condição entrou na lista de campos varridos (`editais/domain/validation.py`), com o rótulo
  *"na condição de exigência"*.

**Depois da correção**, e de dois ajustes de texto vistos na jornada (§2), foram reexecutados:

- `tests/unit/publicacoes/test_pdf_grafia.py`, `tests/integration/convocacao/test_inaplicabilidade.py`
  e `tests/unit/editais`: **1003 passando**;
- `tests/interface` e `tests/integration/convocacao`: **5163 passando, 1 pulado**.

A segunda rodada completa está no §4.

**Os 21 pulados** são os 14 da medição do `CLAUDE.md` com o grupo `assistente` e sem o `navegador`,
mais os da varredura de vocabulário e das jornadas no navegador que esta worktree não instala. Não
foram comparados lista a lista com a `main`: a 131 não acrescenta teste pulado, e nenhum caso novo
depende de grupo opcional.

## 2. A jornada pela interface

**O banco.** É o `ps131demo`, novo e migrado. O cenário foi montado pelas funções das fixtures, o
mesmo de `test_inaplicabilidade.py`:

- o Edital 31/2026, publicado com cinco documentos na convocação;
- o certificado de alistamento militar, com a condição *"no caso de candidatos do sexo masculino,
  maiores de 18 anos"*;
- a autodeclaração étnico-racial, por recorte PPI;
- a certidão e o histórico, incondicionais;
- dois titulares convocados num gesto só;
- a Candidata 601, PPI, com três arquivos enviados;
- o membro `joao`, alocado à conferência.

**O caminho.** O painel do navegador não manteve a sessão da demonstração: a navegação voltava a
`/gestao/identificar`. A jornada foi feita **pelas mesmas telas e formulários** por um cliente HTTP
com sessão própria por ator, que escolhe a identidade na tela de demonstração, abre a página, abre
cada arquivo e envia cada formulário como os botões o fazem. Não há capturas de tela.

| Passo | Ator | O que a tela respondeu |
|---|---|---|
| Página dos documentos | `joao` (só alocado) | A certidão, o histórico e a autodeclaração oferecem só *conforme* e *pendente*; o alistamento oferece também *"Não se aplica"*, com *"Condição publicada: no caso de candidatos do sexo masculino, maiores de 18 anos."* |
| *"Não se aplica"* com motivo `"."` | `joao` | *"Escreva o motivo com palavras: ele aparece para a pessoa convocada."* |
| *"Não se aplica"* com o fato | `joao` | A convocação fica *Pronta para decidir*; os selos dizem *Conforme; Conforme; Não se aplica após análise; Conforme* |
| Condução | `carlos` (gestor) | *"Pronta para decidir — 3 de 4 conformes · 1 não se aplica após análise"* |
| Bloco antes do botão | `carlos` | *"Certificado de alistamento militar ou de reservista — condição publicada: no caso de candidatos do sexo masculino, maiores de 18 anos. Motivo: Candidata do sexo feminino, conforme o documento de identidade. Registrado por joao em 07/11/2026 11:26."* |
| Aceite sem ciência | `carlos` | *"Não foi possível concluir: Para registrar este desfecho, confirme que viu os documentos obrigatórios considerados não aplicáveis."* Nada gravado (conferido no banco) |
| Aceite com ciência | `carlos` | Aceite registrado. A trilha termina em *"Com ciência de 1 inaplicabilidade(s): 8e3d81c8-…"*, sem o motivo |

**O que a jornada corrigiu antes de valer:**

- o bloco imprimia *"identidade.."* (o ponto do motivo mais o da frase): o template só acrescenta o
  ponto quando o motivo não termina nele;
- a nota do topo da página dos documentos dizia *"falta conferir como conforme ou não se aplica"*
  para qualquer item; passou a *"como conforme, ou como não se aplica quando o Edital publicou a
  condição"*.

## 3. O que não foi verificado

- **A SC-1378** é humana: um conferente que nunca viu a tela diz, sem ajuda, por que o *"não se
  aplica"* aparece num item e não nos outros. Pendente.
- **A composição pela tela**:
  - o campo *"Exigido somente quando"*;
  - a recusa no facultativo;
  - a Retificação da condição pelo formulário.

  Os três ficaram provados só por testes de domínio e de contrato, e não abertos no navegador.
- **O PDF** foi provado pela função que compõe o item, e não pela leitura de um PDF gerado.
- **A regularização com ciência**, a condição em documento aproveitado, a condição com recorte por
  modalidade e a nova chamada não têm teste próprio. A matriz diz qual regra os cobre.
- **O orçamento de consultas** (SC-1377) não tem medição nova. A condição sai do conteúdo que a
  leitura já trazia, e os orçamentos existentes passaram.
- **A P-3** (inferência pelo manifesto) continua pendente, sem aceitação implícita.

## 4. Segunda rodada completa

Registrada depois da correção, no commit que fecha a implementação.
