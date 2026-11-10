# Entrega E — Plano de evolução incremental

Nenhuma spec foi aberta. Os grupos abaixo são a menor divisão em que cada um entrega uma melhoria
inteira, sem depender de outro para fazer sentido. A decisão de transformar algum em spec é do usuário.

## Os grupos

| # | Grupo | Melhorias | Onde mexe | O que reaproveita | Depende de |
|---|---|---|---|---|---|
| **G1** | **O bloco do próximo passo** | M-01 retorno ao Centro · M-07 "Ainda neste marco" com link · M-15 | `_proximo_nesta_lista.html` e `views._proximo_nesta_lista` | a derivação da 127 (`andamento.da_lista`), sem regra nova; a URL do Centro (136) | nada |
| **G2** | **A providência chega ao ato** | M-02 | a URL da célula em `interface/andamento.py`; um id por `article.recorte` em `sorteio.html` | os ids que as telas já têm (`#chamadas`, `#chamada-N`, `#titulo-recortes`) | nada. Toca o `andamento.py`, como a 135: quem mergear depois roda a suíte sobre o outro |
| **G3** | **Conferência antes do ato irreversível** | M-04 convocar · M-12 congelar; depois sortear, corte, admitir, julgar | `convocacao.html` e a condição de `conferencia_do_texto.exigir`; `sorteio.html`; `corte.html`; recurso | `marco_conferir.html` e a conferência de texto da 125 | nada para convocar e congelar. **Observar fica fora até a D-5** |
| **G4** | **A tela do sorteio na ordem da tarefa** | M-06 · M-03 (sorteio) · M-13 · M-21 | `sorteio.html`, `telas/sorteio.css` | o módulo de conceitos da 136, para os nomes; os blocos que a tela já tem | G2 (os ids dos recortes). As frases marcadas **D-5** só com a D-5 |
| **G5** | **Convocação e documentos** | M-05 · M-08 · M-09 · M-19 | `convocacao.html`, `convocacao_documentos.html`, `ocupacao.html` | os ids das seções; o gesto "Avisar" da 134 | G1 e G2 para os links do próximo |
| **G6** | **Textos do Centro** | M-10 · M-11 | o módulo de composição e de conceitos da 136 | a regra `e_sua`, que já conta "1 sua" | entra nos ajustes da **138** (D-3, D-7 e validação com operadores) |
| **G7** | **Transições entre papéis** | M-14 · M-16 · M-17 · M-18 | condução e conferência da publicação; Mesa; consolidação; recurso | as frases "peça a alguém…" (P-9) | nada |
| **G8** | **Portal** | M-20 | lista de inscrições e acompanhamento | o andamento da convocação, que já é bom (P-10) | nada |

## A sequência

```
agora ──► G1 + G2  (um incremento curto; o maior ganho por linha de código)
     └──► G3: convocar, depois congelar (o ato que sai do GPS primeiro)
                           │
                           ▼
          G4 (sorteio) ──► G5 (convocação e documentos)
                           │
          D-5 decidida ───►├── frases marcadas D-5 no G4; conferência de observar no G3
                           │
          138 ────────────►└── G6 (com a validação com operadores)

          G7 e G8: independentes, quando houver folga
```

- **G1 e G2 vêm primeiro** e podem ir juntos: são as duas pontas da mesma passagem (ida e volta), e somam
  poucas linhas. Melhoram as cinco jornadas de uma vez.
- **O G3 começa por convocar** porque é o único ato irreversível do percurso que sai do GPS, e porque a
  interface hoje promete uma conferência que não acontece. Congelar vem em seguida: ele é irreversível
  e, no sorteio, a conferência é onde se diz quais listas ainda faltam — informação, e não regra.
- **O G4 espera o G2** só pelos ids dos recortes. O resto dele é ordem de blocos e texto.

## O que não fazer

- **Um componente global de "jornada"** ou de "contexto persistente": o bloco do próximo passo (127) e
  o Centro (136) já são as duas pontas. Os grupos acima só os completam.
- **Um "próximo passo" escolhido por prioridade** nas telas operacionais: a escolha continua sendo a da
  derivação. O que muda é que o próximo fica alcançável.
- **Miniaturas do Centro nas telas**: o retorno é um link, e não um painel.
- **Corrigir F-1 a F-5 dentro destes grupos**: são achados funcionais, com investigação própria
  ([06](06-achados-funcionais.md)). O G4, em particular, não resolve o F-1; ele só deixa de empurrar a
  pessoa para o passo arriscado.

## Para a validação com operadores da 136

O plano de produção do Centro prevê uma rodada com 3 a 5 pessoas
([08](../estudo-centro-de-controle-2026-11-09/08-plano-de-producao.md), seção 5). Ela pode medir a
continuidade com duas tarefas a mais, sem custo de preparação, nos mesmos cenários:

| Tarefa | Cenário | O que se mede |
|---|---|---|
| "A partir do Centro, fixe os participantes das duas listas e volte ao Centro" | C06, rodada nova | onde a pessoa procura o ato; se ela observa a semente antes da segunda lista; quantos cliques até voltar |
| "Confira os documentos de um convocado e registre o desfecho" | C12, rodada nova | quanto tempo até achar os documentos; se ela acha o desfecho sem ajuda |

A primeira mede, com gente, o risco do F-1 e o peso da D-5. Uma mesma rodada com o "antes" e com o
protótipo do "depois" separa o que é tela do que é falta de treino.
