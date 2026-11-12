# Achado — os documentos da convocação saem sem forma no PDF do Edital

Encontrado em 12/11/2026, numa revisão do PDF pedida pelo usuário ("a lista de convocação das
modalidades está sem qualquer formatação; talvez devesse ser uma tabela").

> **Não vira escopo por estar escrito aqui.** O que se registra é o que o documento imprime hoje, por
> que confunde e as saídas possíveis. Priorizar e escolher é do usuário. O PDF é o ato oficial no
> piloto: defeito nele não é polimento.

## Como se viu

Pelo compositor da `main` em `07226c45`, em modo prévia, sobre:

- o SIM03/2026 publicado no banco `ps_demo_157` (um Perfil, `PPP` reservada, documentos da inscrição e
  da convocação);
- os cenários A e B da auditoria de 08/10, por `tests/unit/publicacoes/cenarios_da_auditoria.por_perguntas`.

**As modalidades já saem em tabela**, com borda e cabeçalho: "Vagas por Perfil e lista de
concorrência" e "Reserva de vagas" (Lista, Percentual, Fundamento). O trecho sem forma é outro: os
**documentos exigidos na convocação, agrupados por recorte**. No SIM03, a seção 5 imprime:

```text
5. Quais documentos enviar?

De todos os candidatos:                                         ← negrito
   a) Documento de identificação com foto — frente e verso em arquivo único.

Documentos exigidos na convocação                               ← negrito, mesmo corpo
Estes documentos são pedidos só a quem for convocado, e são apresentados na área do candidato
dentro do prazo da convocação.

Também, de quem concorre ao Perfil DOC-INFO — Professor de Informática:
   a) Diploma de graduação — diploma ou certidão de conclusão, com histórico.

De todos os candidatos:
   a) Comprovante de residência — emitido nos últimos três meses.

Também, de quem concorre às vagas para pessoas pretas, pardas e indígenas (PPP):
   a) Autodeclaração étnico-racial — conforme o modelo do Anexo do Edital.
```

## Os três defeitos

1. **Não há seção própria.** O FR-3569 da `115` pede *"uma seção própria e neutra"*. O compositor
   (`_documentos_exigidos`, em `publicacoes/infrastructure/pdf.py`) escreve o título como uma linha
   em negrito dentro da seção de documentos, no mesmo corpo e fonte dos cabeçalhos de grupo ("De
   todos os candidatos:"). Nada marca, para o leitor, onde terminam os documentos da inscrição e
   começam os da convocação. O teste que prende a forma atual é
   `test_os_da_convocacao_saem_sob_titulo_proprio_depois_dos_da_inscricao`, em
   `tests/unit/publicacoes/test_secao_da_convocacao.py`: ele confere a ordem e o título, não o
   nível.

2. **Os grupos saem na ordem de cadastro, e o "também" fica sem referência.** `_grupos_de_documentos`
   agrupa pela ordem do primeiro documento de cada recorte (`order`). Quando quem elaborou cadastrou
   primeiro o documento de um Perfil, "Também, de quem concorre ao Perfil…" sai **antes** de "De
   todos os candidatos:", e "também" pressupõe o que ainda não foi dito. O mesmo pode acontecer na
   lista da inscrição: o defeito não é só da convocação, mas é ali que ele apareceu.

3. **"De todos os candidatos" diz mais do que é.** Sob a convocação, o documento é pedido só a quem
   for convocado. O título do grupo é o da inscrição (`_titulo_do_grupo_2`), reaproveitado.

Com mais listas reservadas, como num Edital da Lei de Cotas (L1, L2, L5, L6… e PcD), cada lista
ganha o seu grupo "também", e o candidato precisa somar os grupos de cabeça para saber o que entrega.

## Tabela ou alíneas

A sugestão do usuário foi tabela. O que se observou:

- **Como forma principal, a tabela perde.** Cada documento leva uma instrução de uma ou duas linhas
  ("frente e verso em arquivo único", "conforme o modelo do Anexo"). Numa coluna, ela vira várias
  linhas estreitas. O compositor registra essa escolha: *"Alíneas, e não tabela: é lista normativa
  curta"*.
- **Como resumo, a tabela ganha quando há várias listas.** Um quadro documento × lista, com ✓ onde
  o documento é exigido, deixa o candidato achar a própria coluna sem compor os grupos "também". O
  compositor já tem como decidir se a matriz cabe na largura (`_cabe_lado_a_lado`, da `068`) e
  como cair para a forma longa quando não cabe. Com uma lista reservada só, como no SIM03, o quadro
  não acrescenta nada.

## Saídas possíveis, sem decisão

- **A. Consertar o que está errado, e só.** Uma subseção numerada para cada momento ("5.1 Na
  inscrição", "5.2 Na convocação"), como as de "Como será a seleção?". Os grupos em ordem fixa
  (todos → Perfil → lista → Perfil e lista), com a ordem declarada dentro de cada grupo. "De todos
  os convocados" sob a convocação. Isso cumpre o FR-3569 ao pé da letra.
- **B. A + o quadro-resumo**, só quando houver duas ou mais listas reservadas com documento
  próprio, antes das alíneas.
- **C. Mover os da convocação para "Como será a convocação?"** (seção 15 do catálogo da `069`), que
  é onde o convocado procura o que fazer. Fica longe dos documentos da inscrição, e é preciso
  conferir se a remissão do aproveitamento ("Quem enviou … na inscrição não precisa enviá-lo de
  novo") continua clara a essa distância.

Qualquer saída muda o texto do PDF publicado, e por isso pede spec: a fixture de bytes do documento
publicado (`tests/contract/test_documento_publicado.py`) e os testes da `115` mudam junto. **Edital
já publicado não se regenera**: a mudança só alcança os publicados depois dela.

## Para reproduzir

Com o Python do `.venv` do checkout principal, de dentro de `backend/` da worktree (o diretório do
`manage.py` vence o pacote instalado):

```python
import json, subprocess
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes import cenarios_da_auditoria as c

conteudo = json.loads(subprocess.check_output(
    ["psql", "-At", "-d", "ps_demo_157", "-c",
     "select content from publicacoes_revisaoedital "
     "where id='1527c149-d1b0-4a98-b534-a32b2bd28788'"]))
open("sim03.pdf", "wb").write(
    pdf.render_edital_pdf(conteudo, "", pdf.MODO_PREVIA, unidade=c.UNIDADE))
```

A página 2 mostra o trecho (`pdftoppm -f 2 -l 2 -r 80 -png sim03.pdf sim03`).
