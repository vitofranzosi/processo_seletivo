# Migração e reversão (110)

Como o registro de Unidades passa do arquivo ao banco **sem perder dado, sem interromper a
homologação e sem duas fontes de verdade**.

## O ponto de partida

Em toda instalação existente, o banco já tem a linha de cada unidade do arquivo: a sincronização
rodou no último preparo, na última subida do contêiner ou no último `ps-migrar`. Todo leitor já lê o
banco — `exigir_unidade`, a identificação da `109`, o contexto do ato da `060`. **Não há dado a
migrar.** O que a transição muda é quem escreve.

## A ordem de entrada

| # | Passo | Pré-condição | O que garante |
|---|---|---|---|
Os três incrementos entram separados (D-019). **A** e **B** não mudam o registro nem os papéis: A
cria o gatilho de escopo, que só recusa o que nenhum caminho da aplicação faz; B é código de teste.
A transição propriamente dita é a de **C**:

| # | Passo | Pré-condição | O que garante |
|---|---|---|---|
| 0 | a `108` e a `109` na `main` | — | **feito em 31/10/2026** (`cf048007`, `81ce6e94`) |
| 1 | a release de C **não** traz mudança no `unidades.json` | revisão do PR | nada de valor novo chega pelo arquivo na última vez em que ele seria lido |
| 2 | deploy da release: `ps-migrar` (provisionar, migrar, provisionar, `semear_unidades`) | — | a semente encontra o registro preenchido e não grava. **Nenhum privilégio muda**: o papel do registro nasce sem ninguém |
| 3 | conferir a linha `Unidades: registro com N unidades; a semente não se aplica.` | — | a semente não se aplicou, como devia |
| 4 | conferir `Modelos de aviso: 0 criados.` | — | nenhuma unidade sem modelos |
| 5 | conceder o papel do registro pela implantação, a quem o usuário designar, com o ato no motivo | a P-5 respondida | o poder de mudar o registro chega por ato, e não pelo deploy (D-002) |
| 6 | a partir daqui, toda mudança de unidade é pela tela | a pessoa do passo 5 **consegue entrar**: a entrada institucional precisa de provedor, e na VM de homologação e em produção isso é o SSO (D-017) | uma fonte |

Entre os passos 2 e 6, em produção e na VM de homologação, ninguém cadastra unidade — e ninguém
poderia usá-la, porque a gestão responde 503 sem SSO (D-019). Em desenvolvimento e no compose, a tela
está disponível pela entrada de homologação desde o passo 2.

**Um `ps-migrar` instalado de cópia antiga** chama `sincronizar_unidades`, que agora é o apelido da
semente: ela roda, a subida termina, e o aviso do nome anterior fica no *log* (D-003, EC-17).
Reinstala-se o roteiro quando for conveniente; o apelido sai quando nenhum *log* de implantação
tiver mais o aviso.

**Se a sincronização tiver de aplicar alguma coisa antes**, ela roda na release anterior, e não
nesta: a regra 2 existe para que nunca haja dúvida sobre qual foi a última escrita do arquivo.

### Ambientes

| Ambiente | Como a semente chega | Efeito |
|---|---|---|
| desenvolvimento nativo | `make preparar` | banco existente: nada; banco novo: o Cefor |
| compose (homologação local) | `scripts/docker/entrypoint.sh`, a cada subida | idem; a subida nunca falha por unidade fora do arquivo |
| instância controlada de validação | `make preparar`, num banco próprio | banco novo: o Cefor; as unidades da validação entram pela tela, pela entrada de homologação (roteiro G) |
| suíte | a fixture `autouse` registra o Cefor sem passar pela semente | nada muda; os testes da semente a chamam explicitamente |
| `seed_demo` | chama a semente | banco de demonstração novo: o Cefor; existente: nada |
| produção | `ps-migrar` | ver a tabela acima |

**A homologação não para.** O seletor de demonstração, o `seed_demo` e o Cefor continuam como estão
(FR-3338). A tela nova é da entrada institucional: a prova automatizada é a jornada no navegador
(`make test-navegador`), e a validação por pessoas é a da instância controlada, com a entrada de
homologação (D-017, D-018).

## A reversão

Três situações, da mais simples para a mais delicada.

### R-1 — Antes de qualquer ato pela tela

Voltar à release anterior a C. A sincronização volta a rodar, encontra o banco igual ao arquivo e
não grava nada. O gatilho de escopo é de A, e fica: a release anterior a C já o conhece. Os vínculos
do papel do registro, se o passo 5 já tiver ocorrido, ficam no banco sem efeito — a release anterior
ignora papel que não conhece.

### R-2 — Depois de cadastrar ou editar pela tela

A release anterior recusaria subir (`unidade_retirada`) se houver unidade cadastrada pela tela, e
reverteria toda edição para o valor do arquivo, com evento de `implantacao`. Por isso:

1. `manage.py semear_unidades --exportar > unidades.json` na release **atual**;
2. numa branch de reversão a partir do commit de destino, substituir `unidades/unidades.json` por
   esse arquivo e fazer commit — a release tem de corresponder a um commit, e não ser editada no
   servidor. É a única vez em que o arquivo recebe valor do banco, e é para que a sincronização
   encontre o que já está lá. O formato inclui `ativa` e omite o canal vazio (D-016), que é o que a
   validação da release de destino aceita;
3. implantar a release dessa branch e rodar o `ps-migrar` dela; conferir `0 criadas, 0 alteradas`.

Se a release de destino for anterior também a A, `migrate processos 0004` antes de trocar o código,
como na R-3.

Os eventos gravados pela tela ficam na trilha: são história, e a `108` da release de destino os lê
como lia.

### R-3 — Reverter A, o gatilho de escopo

`migrate processos 0004`, **antes** de trocar o código por uma release que não conheça a `0005`.
Independente do resto: nada nesta feature depende do gatilho para funcionar; ele só recusa o que
nenhum caminho da aplicação faz.

### R-4 — Reverter B

Tirar o adaptador da configuração da instância de validação. Não há dado nem esquema a desfazer.

### O que **não** se reverte

- a permissão e o papel: não são dado, são catálogo; saem com o código. Os vínculos do papel ficam,
  sem efeito;
- os eventos da trilha: append-only, por desenho;
- uma unidade cadastrada: não se exclui (gatilho da `060`); na reversão, ela passa ao arquivo (R-2).

## O que se confere depois da entrada

| Conferência | Como | Esperado |
|---|---|---|
| a semente não aplicou | a saída do `ps-migrar` | `registro com N unidades` |
| o gatilho existe | `\dS+ processos_edital` no `psql` | `edital_escopo_imutavel` |
| o registro não mudou | `semear_unidades --exportar` antes e depois, `diff` | idêntico |
| ninguém ganhou privilégio no deploy | a lista de vínculos vigentes no escopo institucional, antes e depois do passo 2 | idêntica |
| quem administra unidade é quem o usuário designou | os vínculos `administrador-de-unidades` vigentes, depois do passo 5 | as pessoas designadas, com o ato no motivo |
