# Verificação — 071 · O piloto interno do assistente conversacional do Edital

*13/10/2026, na worktree `stoic-tharp-c938a1`, na branch `claude/piloto-assistente-do-edital`,
empilhada sobre a da `070` (`ceadb141`, PR #274), sem commit próprio. Verificado pelo agente da
sessão de implementação, por suíte, comandos e navegador; nada aqui foi visto por uma pessoa do
setor, e nada falou com um modelo real.*

## 1. A suíte (T066)

`make lint check test-pg DB_NAME=ps_071`, com `LC_ALL` exportado e nenhum arquivo editado durante a
suíte. Sobre o estado final desta feature, depois da emenda de 14/10 ao `FR-1507`: **11177 passando
e 12 pulados**, nenhuma falha, em 1270s; `ruff check`, `ruff format --check`, `manage.py check` e
`makemigrations --check` limpos.

Os pulados, agrupados por arquivo e motivo com `-rs`, são os onze do `AGENTS.md` — nove pares
*termo × template* da varredura de vocabulário, a recusa por vendor e o E2E da fonte do sorteio —
mais **um** da `071`: `unit/duvidas/test_tokens.py`, a contagem real do tokenizer, que pula sem a
biblioteca `tokenizers`, do grupo opcional `assistente`. O `AGENTS.md` foi atualizado com a medição.

As medições anteriores: 11176 com a US6 e a US7, e 11180 depois do Polish, em 13/10. Dos quatro
casos a mais do Polish, três são os da exclusão (T061); o quarto não foi identificado, porque a lista
da suíte anterior não foi guardada. A emenda de 14/10 tirou sete casos — quatro dos orçamentos da
aplicação e três do `--max-chamadas` e do total da avaliação — e pôs quatro: a aplicação que não
conta chamadas externas, a rodada que para na recusa pelo limite de gasto e a verificação no
OpenRouter com e sem limite na chave; de 11180, 11177.

**Depois de atualizar com a `main`** (`55889d11`, que traz a `070` mergeada e a `072`): **11263 passando
e 12 pulados**, os mesmos doze, nenhuma falha, em 1311s, com lint e `check` limpos. Os 86 casos a
mais são da `072`. O único conflito do merge foi a tabela de incrementos do README, onde as linhas
da `071` e da `072` caíram no mesmo lugar; as duas ficaram.

## 2. A tela, pelo navegador (MVP, US1)

**Ambiente.** Banco próprio da sessão, com o 91/2026 do corpus publicado pelo fluxo real, o seletor
de identidade e um serviço **falso**, fora do repositório, que respondia pelo contrato da saída —
nunca um modelo. Identidade com o papel do setor e o "Participante do piloto do assistente".

| O que se fez | O que se viu |
|---|---|
| Página do Edital → "Conversar com o assistente (piloto)" | A faixa do piloto interno, a orientação sobre dado pessoal e a versão vigente no topo |
| Uma pergunta que as fontes respondem | Resposta "Respondida pelas fontes", com os trechos rotulados em palavras e as fontes citadas no `<details>`, cada uma com o ato e o link do documento |
| Uma saída que a conferência recusava | No lugar da resposta, "não se sustentou nas fontes do Edital", as fontes para consulta e o canal |
| Uma pergunta que o Edital não responde | "O Edital não informa", com a citação literal e o canal |
| 375 px de largura | Sem rolagem horizontal |

Os casos da tela que não precisam de navegador — os estados, as negativas, o escape, o POST que
redireciona e o recarregar que não chama de novo — estão na suíte (`TT`, na
[rastreabilidade](rastreabilidade.md)).

**As duas abas.** O teste de duas gravações concorrentes na mesma conversa
(`test_duas_abas_gravam_em_ordens_distintas`) foi rodado **sem** a trava da conversa: reprovou nas
três vezes. Com a trava, que dura só a gravação e não a chamada, passa.

## 3. O corpus e a matriz num banco da equipe (T048, T049)

Num banco descartável, `ps_071_corpus`, preparado do zero com o superusuário (para não mexer nos
papéis do cluster com outra suíte rodando):

1. `scripts/publicar_corpus_do_piloto.py` publicou os sete Editais — 01, 91 e 92/2026 com as
   Retificações do corpus, e 901 a 904 — e imprimiu "Deslocamento: 4 dias". A primeira tentativa
   recusou com `autoridade_indisponivel`: o banco não tinha a autoridade signatária dos ajudantes da
   suíte, e o script passou a registrá-la.
2. Uma **rodada seca** da matriz inteira, `--repeticoes 1 --deslocamento-dias 4`, sem serviço e sem
   tokenizer: 93 casos, 88 rodados, 95 trocas, todas `SEM_TOKENIZER`, **zero chamadas**. Os cinco não
   rodados são os quatro que a suíte cobre e o `CB-11`, que só roda no serviço externo. Nenhum caso
   caiu em "sem versão vigente".
3. As fronteiras de versão caíram onde a matriz pede: `CA-02`, `CA-18` e `CB-03` passam de v1 a v2;
   `CA-19` e `CB-04` atravessam a vigência futura do 01/2026 (v2 → v3, em 30/10 deslocado); o `CA-17`
   fica na v2, antes dela.

O banco ficou na máquina, com o corpus publicado e as 95 trocas da rodada seca.

## 4. Os comandos do serviço local, sem L4 (T055, T057)

- `verificar_servico_de_inferencia`: só pela suíte (`UV`), com `urlopen` respondendo como o Ollama
  — a saída impressa, e o código 1 para modelo não instalado, quantização diferente ou não
  configurada, modelo em parte na CPU, acréscimo por mensagem subestimado e contexto menor que o
  configurado.
- `scripts/carga_do_assistente.py`: contra uma porta local fechada (`127.0.0.1:9`), sem rede. Os
  níveis saem com `INDISPONIVEL`; com `--carga-publica`, a API sem e com carga lado a lado, e o aviso
  de quando a carga pública passa do fim do nível. Com `ASSISTENTE_SERVICO=openrouter`, o script
  recusa.

## 5. Os critérios de conclusão do piloto, um a um

| Critério | Situação |
|---|---|
| 1. Os `SC-545` a `SC-550` passam na suíte | **Cumprido** — §1 e a [rastreabilidade](rastreabilidade.md) |
| 2. A verificação de conexão rodou contra a L4, sem divergência | **Aberto** — T058, bloqueada pelo acesso à L4 |
| 3. Uma rodada completa da matriz no Ollama da L4, revisada por humanos | **Aberto** — T059, depois da T058 |
| 4. As medições do `FR-1517` no relatório datado, e o teto configurado é o medido | **Aberto** — T060, depois da T058 |
| 5. O setor usou o piloto em sessões acompanhadas | **Aberto** — T065: pede um serviço real, o OpenRouter com limite de gasto na chave, como ensaio, ou a L4, que é a sessão que conta |
| 6. O relatório final diz, para cada `SC-551` a `SC-558`, se passou | **Aberto** — depois dos critérios da DP-3, que se aprovam antes de qualquer resultado ser declarado aceito |

**Nenhuma chamada externa aconteceu.** Depois da emenda de 14/10 ao `FR-1507`, a única barreira de
gasto no OpenRouter é o limite da própria chave: sem ele, a verificação acusa divergência e não manda
a conversa sintética. A primeira chamada externa espera o pedido do usuário.

## 6. Achados e emendas da implementação

| Achado | O que mudou |
|---|---|
| As fontes, montadas só das respostas da `070`, deixavam de fora as seções que nenhuma das doze perguntas mostra — cinco no 91/2026, quatro no 92/2026, entre elas as Disposições Finais —, contra o `FR-1472` | Toda seção textual preenchida entra inteira (`R-002`); um teste confere cada seção do corpus |
| O inventário de negativas da `033` só cobra `Http404`, e a tela recusa pelo `DomainError` do domínio | Nenhuma linha nova no inventário (T023) |
| O presente como instante dos casos mudava a impressão das fontes a cada minuto | O `instante_padrao` da matriz (contracts/comandos.md §1) |
| A unicidade de número e ano não deixa cópia do 91/2026 no mesmo banco | Os Editais de teste da matriz são 901 a 904, com identificadores remapeados (T048) |
| O custo não é gravado por troca (`FR-1510`), e o `resumo.md` precisa do total | O comando o lê da linha de log da troca, durante a rodada |
| A API do Ollama não diz se aceita `truncate` e `shift`, e uma sonda seria a segunda chamada que o `FR-1520` não permite | Eles vão à lista "a confirmar com a infraestrutura" (`R-017`) |
| A verificação não tinha quantização esperada com que comparar (US7, cenário 2) | `ASSISTENTE_QUANTIZACAO`, vazia por padrão, e vazia é divergência (`R-009`) |
| As doze perguntas da `070` "para cada Edital e parâmetro" dariam centenas de casos | Um Perfil por Edital, e a `P-05` com cada lista dele; a amostra está declarada na matriz |
