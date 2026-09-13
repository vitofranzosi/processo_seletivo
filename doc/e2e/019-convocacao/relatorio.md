# Percurso conduzido — SPEC 019 · Convocação, Chamada e Suplência

**Data:** 13/09/2026 · **Branch:** `claude/pr-110-merge-ready-f91335` · **Base:** commit `b172404`
**Ambiente:** banco isolado `ps_demo_019`, papéis provisionados pelo superusuário local (**31 de 31**
tabelas append-only sem `UPDATE` nem `DELETE` para o runtime — as cinco novas desta feature entram
aí), `INTERFACE_SELETOR_IDENTIDADE=true` e `PORTAL_IDENTIDADE_DEMO=true`, servidor em
<http://localhost:8019> (entrada `convocacao-019` **acrescentada** ao `.claude/launch.json`, sem
reescrevê-lo).

**Escopo:** o percurso do [quickstart](../../../specs/019-convocacao-chamada-suplencia/quickstart.md)
pela interface administrativa contra servidor real — ler o recorte, convocar, comunicar, registrar
desfecho, ver a apuração ficar obsoleta, emiti-la de novo e ver o número se mover, convocar para
regularizar e fechar o ciclo.

## Sobre as evidências

**Não há PNGs em `screenshots/`, e é limitação da sessão, não esquecimento** — o mesmo registrado
pelos percursos da `014`, da `016`, da `020` e da `025`. O painel de navegador desta ferramenta
devolve as capturas para a conversa e não as grava em disco; com o painel oculto, ele devolve imagem
em branco. Cada observação abaixo traz, no lugar da imagem, a **URL, o controle e o texto literal
lido da página**.

**O que foi montado fora da tela, e por quê.** O Edital publicado com quadro e regra de corte, as
quatro inscrições, as avaliações da Prova de títulos, a consolidação, o ato de ordenação, o corte,
os Resultados da Etapa governada e a primeira apuração da `016` foram criados por um script que
chama os **mesmos commands da aplicação** que a suíte usa — nada entrou por SQL direto, de modo que
autoria, segregação e auditoria ficam verdadeiras. São jornadas da `009`, da `012`, da `013`, da
`014`, da `015` e da `016`.

**O que a `019` entrega foi percorrido pela interface, sem exceção**: a leitura do recorte, a
convocação, a emissão da comunicação, o registro do desfecho, a obsolescência declarada, a
convocação para regularizar e o desfecho de regularização.

## O certame do percurso

Duas vagas de ampla concorrência, faixa alcançando três, quatro inscritas:

| Inscrição | Situação na Etapa governada | Papel no percurso |
|---|---|---|
| `INS-2026-0601` — Candidata 601 | habilitada | titular convocada, que desiste |
| `INS-2026-0602` — Candidata 602 | habilitada | titular, permanece na fila |
| `INS-2026-0603` — Candidata 603 | **indeferida** | convocada para regularizar, e regulariza |
| `INS-2026-0604` — Candidata 604 | sem avaliação | fora da faixa |

---

## 1. Veredito

**A feature está entregue pelo canal do ator, e o ciclo que a `SC-085` mede fecha pela interface.**
Ler o recorte, convocar com fundamento, emitir a comunicação, registrar a desistência, ver a
apuração ficar obsoleta com a causa nomeada, emitir a seguinte e **ver o número cair de 2 para 1** —
tudo aconteceu pela tela, sem shell e sem banco. A regularização devolveu o número a 2 pelo
mecanismo da `018`, sem reabrir a ordem.

**O defeito da `§1.0` foi observado corrigido em servidor real.** Com o cálculo antigo, a linha do
passo 5 abaixo continuaria dizendo `2 ocupadas · 0 a ocupar`.

## 2. O ciclo, passo a passo

| # | Ato, pela tela | O que a tela disse |
|---|---|---|
| 1 | abrir `/gestao/editais/…/marcos/…/convocacao` | `Publicadas 2 · Efetivas 2 · Ocupadas 2 · A ocupar 0`, `Convocadas 0`, `Responderam 0` |
| 2 | convocar `INS-2026-0601` para vaga inicial | *"Convocação praticada. O ato é imutável; corrigi-lo é sucedê-lo com motivo, e a anterior continua legível."* |
| 3 | ler a chamada praticada | *"Convocado, prazo não iniciado — a comunicação ainda não foi enviada com sucesso"* |
| 4 | emitir a comunicação | *"Comunicação enviada. O prazo desta convocação corre a partir do envio."* |
| 5 | registrar **desistência expressa** | *"Desfecho registrado. A apuração vigente passa a aparecer obsoleta, e o número novo sai na apuração seguinte."* |
| 6 | reler o recorte | *"A apuração deste recorte está obsoleta… um desfecho de convocação mudou quem ocupa vaga neste recorte depois dela"* — **e os números continuam os apurados** (`FR-278a`) |
| 7 | emitir a apuração seguinte, em `/…/ocupacao` | `Publicadas 2 · Efetivas 2 · **Ocupadas 1** · **A ocupar 1**` |
| 8 | convocar `INS-2026-0603` **para regularizar** | *"Convocação praticada"*; `Convocadas 2` |
| 9 | registrar **regularização** | *"Desfecho registrado…"*, e a apuração fica obsoleta de novo |
| 10 | emitir a apuração seguinte | `Publicadas 2 · Efetivas 2 · **Ocupadas 2** · **A ocupar 0**` |

**O passo 7 é a feature inteira.** É a linha em que o número antigo não se movia.

## 3. O que a tela da ocupação passou a dizer

A quinta causa de obsolescência aparece na tela da `016` **sem nomear convocação**:

> *um efeito registrado depois dela mudou o conjunto de ocupantes deste recorte*

A frase é deliberada, e a varredura de vocabulário a exige: a `016` não conhece convocação
(`UX-034`). Quem dá sentido ao fundamento é quem o escreveu — e é a tela da `019` que o diz com
todas as letras.

## 4. Achados

### 4.1 — A tela identificava as pessoas por UUID · **corrigido**

**O que apareceu.** A fila de chamada, os dois seletores de inscrição, o título de cada chamada
praticada e a coluna do histórico saíam assim:

> `959e770d-a766-42c8-b806-ec460ce0d341 — próxima da fila`

**Por que importa.** Quem vai convocar confere a fila contra a lista publicada, e a lista publicada
tem protocolo e nome. Um identificador sorteado é indistinguível de ruído — é a mesma lição que a
fixture de inscrição da `009` registra ao gerar `INS-<ano>-NNNN` em vez de quatro dígitos nus. A
tela estava tecnicamente exata e operacionalmente inútil.

**Correção.** `leitura_do_recorte` passou a resolver as inscrições para `{protocolo, nome}` numa
consulta só, e as telas passaram a exibi-los. O identificador continua sendo o valor que o
formulário envia e a âncora que a auditoria usa. Prendido por
`tests/interface/test_convocacao.py::test_a_tela_identifica_a_pessoa_por_protocolo_e_nome_e_nao_por_uuid`.

Depois da correção:

> `INS-2026-0601 — Candidata 601 · próxima da fila`

### 4.2 — A entrada no portal esbarra na reconciliação da `010` · **registrado, não corrigido**

**O que aconteceu.** Entrar em `/selecoes/acesso` com o e-mail da inscrição funciona, e o código de
seis dígitos sai no terminal do `runserver`, como esperado. A conta criada, porém, não está vinculada
à inscrição: a tela oferece *"Vincular participação anterior"*, e o fluxo de reconciliação volta a
pedir o código sem chegar à confirmação de CPF.

**Por que não foi corrigido aqui.** É caminho da `010`, e não desta feature — a `019` não toca
identidade, credencial nem reconciliação. A tela da convocação no portal foi verificada por
`tests/interface/test_portal_convocacao.py` (14 casos) contra a **view e o template reais**,
incluindo as duas ausências distintas, o *"enviada em"*, a ausência de *"recebido em"* e a leitura
que não move o relógio.

**Fica como achado da `010`**, e não como escopo da seguinte — a regra de governança deste
repositório.

## 5. O que o percurso não alcançou, e por quê

**A suplência não foi exercitada pela tela.** O elenco montado tem duas habilitadas e a faixa
alcança três; a terceira está indeferida, de propósito, para o cenário da regularização. Não sobrou
suplente habilitada para chamar depois da desistência. O ciclo completo da suplência — desistência,
chamada do próximo, número voltando — está medido em
`tests/integration/convocacao/test_ciclo_do_77.py` e, numa **lista reservada**, em
`tests/integration/convocacao/test_suplencia.py`.

**Os cenários 4 (prazo vencido), 5 (atestado e inércia) e 7 (imutabilidade pelo shell) não foram
percorridos na tela**, e a razão é a mesma em todos: dependem de relógio, de fato externo ou de
conexão com privilégio distinto, e os três estão medidos na suíte —
`tests/integration/convocacao/test_comunicacao.py`, `tests/integration/convocacao/test_inercia.py` e
`tests/unit/convocacao/test_append_only.py` mais
`tests/integration/test_database_permissions.py`.

## 6. O que mudou depois deste percurso

**Uma revisão de código posterior encontrou oito achados bloqueantes**, e três deles mudam o que
este percurso observou:

- **a janela de titulares foi recortada de novo.** Naquele momento ela era recortada depois de
  filtrar as habilitadas, e três eliminados dentro do alvo promoviam os três seguintes sem ato — a
  promoção silenciosa que a feature existe para eliminar, sobrevivendo do outro lado. Os números do
  percurso não mudam (o cenário não tinha eliminados dentro do alvo), mas a regra sim;
- **a emissão por publicação passou a exigir onde se publicou.** O passo 4 deste percurso usou a
  forma **individual**, e não foi alcançado pela mudança;
- **a `US5` deixou de ser impossível**: o desfecho passou a suceder o desfecho, e o cancelamento por
  inércia alcança quem havia aceitado.

A lista completa está em
[`rastreabilidade.md`](../../../specs/019-convocacao-chamada-suplencia/rastreabilidade.md), com o
teste que prende cada uma.

## 7. Verificação final

```
cd backend && make lint check test-pg
```

`ruff check` e `ruff format --check` limpos; `manage.py check` sem problemas; `makemigrations
--check` sem mudanças pendentes. A suíte contra PostgreSQL fecha em **5397 passando e 2 pulados** —
os dois deliberados de sempre.
