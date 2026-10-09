# Implementation Plan: Avisos complementares aos candidatos, vinculados a ato oficial

**Branch**: `claude/066-avisos-complementares` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/066-avisos-complementares/spec.md`

## Summary

Um app novo, `avisos` (`R-001`), deixa a seleção avisar por e-mail os candidatos que um ato já
publicado identifica. São dois tipos de ato: as publicações vigentes de resultado de um marco, e a
chamada comunicada por publicação. O aviso não tem efeito nenhum (`D-001`, `FR-1242`).

- **Os destinatários saem do ato.** No resultado, as `SituacaoDivulgada` deduplicadas por inscrição
  (`D-002`). Na chamada, o universo histórico da referência, com a elegibilidade atual separada dele
  (`D-003`).
- **O texto** é da seleção, com variáveis fechadas, partindo de modelos da unidade. Três modelos
  iniciais são criados uma vez por `sincronizar_unidades` (`R-012`).
- **Na confirmação**, o texto é congelado com os links resolvidos (`R-007`) e a lista é gravada.
  Nada é enviado nessa hora.
- **O envio** é de um comando, `despachar_avisos`, num timer do systemd a cada minuto (`R-005`).
  - O início da tentativa é gravado antes de chamar o servidor (`R-003`), e a resposta é
    classificada pela fase em que veio (`R-004`).
  - A concorrência é resolvida por trava consultiva, porque `FOR UPDATE` sobre tabela append-only é
    negado à role de runtime. Isso foi verificado em 09/10 (`R-002`).
- **Reenvio** é um aviso filho do anterior (`R-011`). **Interrupção** é registro próprio, conferido
  antes de cada tentativa (`D-006`).
- **`EMAIL_TIMEOUT`** entra em `base.py` e passa a valer para os quatro envios do sistema (`R-006`).
- **Uma chave**, `AVISOS_AOS_CANDIDATOS`, desligada em produção, segura a confirmação e o despacho até
  a validação da LGPD e do correio (`R-013`, aprovada). Uma **janela de despacho** de 24 horas faz a
  reativação, ou o timer que volta, não dispararem mensagem antiga (`R-016`, `D-009`).
- **Os links** são três variáveis distintas: publicação específica, página do processo seletivo e área
  do candidato (`R-008`).

Nenhuma dependência nova. Nenhuma tabela existente muda. Uma função de outro app muda de lugar:
`destinatario_de` sai de `convocacao` para `identidade`, sem mudar de comportamento (data-model §3).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2, templates renderizados no servidor, CSS à mão na
folha da gestão

**Primary Dependencies**: nenhuma nova. O envio usa `django.core.mail` (`get_connection`,
`EmailMessage`). A concorrência usa `pg_advisory_lock` e `pg_advisory_xact_lock` do PostgreSQL, que
o código já usa.

**Storage**: PostgreSQL. App `avisos`: seis tabelas append-only (gatilho e privilégio ausente) e uma
mutável sem exclusão ([data-model.md](data-model.md)). Uma migration, com gatilhos.

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio).

- **Unitários, sem banco**: composição da mensagem, validação de variáveis, classificação de
  resposta do servidor, derivação de estado do destinatário.
- **Integração**:
  - universo e elegibilidade por origem;
  - deduplicação;
  - prévia defasada;
  - idempotência;
  - despacho com backend que falha, que aceita e derruba, e que devolve 0;
  - duas execuções concorrentes, por thread e por trava;
  - interrupção sob concorrência;
  - modelos iniciais criados uma vez;
  - autorização por origem e escopo.
- **Guardiões a atualizar** estão em `R-015`.

**Target Platform**: Ubuntu com nginx, gunicorn, PostgreSQL e systemd
(`doc/implantacao-em-producao-ubuntu.md`). Telas a 1280 × 900 e 375 px.

**Project Type**: monólito web Django, área de gestão (`interface/`), mais um comando de manutenção
periódica

**Performance Goals**:

- A confirmação responde em menos de 2 s com 1.000 destinatários (SC-482). São inserções em lote e
  nenhum envio.
- O histórico do aviso tem consultas constantes no número de destinatários.
- 500 destinatários são despachados em até 15 min contra servidor simulado (SC-483).

**Constraints**:

- Nenhum envio dentro da requisição (`FR-1265`).
- Nenhum reenvio automático de indeterminada (`FR-1267`).
- Nenhuma tentativa depois da interrupção (`FR-1273`).
- Nenhum `FOR UPDATE` em tabela append-only (`R-002`).
- Nenhum teste contra servidor real (`FR-1281`).
- 375 px sem rolagem horizontal.

**Scale/Scope**:

- O app `avisos`: modelos, domínio, aplicação e um comando.
- Seis telas novas e dois pontos de entrada em telas existentes.
- Uma linha em `PAPEIS` e uma entrada em `sincronizar_unidades`.
- Um setting de timeout e cinco de despacho.
- Uma unidade systemd no runbook.
- A revisão do guardião da `FR-084`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o respeita | Situação |
|---|---|---|
| I. Integridade normativa e nada excluído | O aviso cita o ato e não o altera. Nada é excluído: as seis tabelas de envio são append-only. Modelos são mutáveis, mas nunca excluídos (`delete()` e gatilho). O universo da chamada é histórico (`D-003`). | ✓ |
| II. Publicação imutável e temporalidade | Nenhuma publicação muda. O aviso sobre retificação é ato novo que cita a sucessora (`D-002`). O texto é congelado com o instante da confirmação, e o fuso é o da instalação (`R-007`). | ✓ |
| III. Negar por padrão, escopo e LGPD | Capacidade própria `aviso:enviar`, que não concede outra (`FR-1275`). A autorização é pela origem (`D-004`), e o escopo é filtrado em toda consulta (`FR-1276`). Minimização: só o nome varia por pessoa, sem modalidade, posição ou motivo (`FR-1255`). O detalhe técnico vai sem endereço (`FR-1279`). A trilha não copia endereços (`FR-1278`). A validação institucional é precondição de produção, com chave proposta (`R-013`). | ✓, com pendência institucional declarada |
| IV. Regras explícitas, lote explícito, consistência | O universo e a elegibilidade são mostrados antes do ato irreversível, com origem e motivo (`FR-1259`, `UX-178`). A prévia é assinada (`R-010`), e a confirmação idempotente roda sob o lock do Processo (`R-009`). Envio fora da transação, com o início da tentativa gravado antes (`R-003`). | ✓ |
| V. Simplicidade e necessidade demonstrável | **Um processo periódico novo em produção.** Ver *Complexity Tracking*. Nenhuma fila, broker ou dependência: a "fila" são as linhas do banco, e o worker é o timer que a implantação já usa para quatro rotinas. | ✓, justificado |
| VI. Jornada demonstrável | Resultado, retificação, chamada, modelos e interrupção pela interface do ator, com o correio de desenvolvimento ([quickstart.md](quickstart.md)). | ✓ |

**Re-check depois do desenho:** o data-model não acrescenta coluna a tabela existente nem `UPDATE`
em tabela append-only. Os contratos não expõem dado além das variáveis da lista fechada. O despacho
não introduz dependência. ✓

## Project Structure

### Documentation (this feature)

```text
specs/066-avisos-complementares/
├── spec.md
├── plan.md                # este arquivo
├── research.md            # R-001 a R-016
├── data-model.md          # sete tabelas, estado derivado, universo por origem
├── quickstart.md          # roteiro de validação
├── contracts/
│   ├── telas.md           # rotas, portas, recusas, vocabulário
│   ├── despacho.md        # o comando, garantias, configuração, systemd
│   └── mensagem.md        # partes, rodapé, variáveis, os três modelos iniciais
├── checklists/
│   └── requirements.md
└── tasks.md               # /speckit-tasks — ainda não
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── avisos/                                   # novo (R-001)
│   ├── models.py                             # data-model §1
│   ├── migrations/0001_initial.py            # tabelas e gatilhos
│   ├── domain/
│   │   ├── nomes.py                          # códigos de recusa e estados
│   │   ├── variaveis.py                      # lista fechada, validação por origem
│   │   ├── mensagem.py                       # composição pura (contrato mensagem.md)
│   │   ├── estado.py                         # estado derivado do destinatário (data-model §2)
│   │   ├── resposta.py                       # classificação da resposta do servidor (R-004)
│   │   └── modelos_iniciais.py               # os três textos (D-008)
│   ├── application/
│   │   ├── comando.py                        # comando_de_aviso (R-009)
│   │   ├── destinatarios.py                  # universo e elegibilidade por origem
│   │   ├── previa.py                         # prévia e assinatura (R-010)
│   │   ├── confirmar.py                      # confirmação e reenvio (R-011)
│   │   ├── interromper.py
│   │   ├── modelos.py                        # CRUD auditado e garantir_modelos_iniciais (R-012)
│   │   ├── despacho.py                       # a 4ª situação da FR-084 (contrato despacho.md)
│   │   └── selectors.py                      # histórico, linha de estado, alerta de despacho parado
│   └── management/commands/despachar_avisos.py
├── identidade/application/endereco.py        # destinatario_de, movido de convocacao (data-model §3)
├── convocacao/application/comunicar.py       # passa a importar destinatario_de de identidade
├── unidades/application/sincronizacao.py     # chama garantir_modelos_iniciais
├── interface/
│   ├── identidade.py                         # aviso:enviar em publicador e gestor
│   ├── avisos.py                             # views novas (contrato telas.md)
│   ├── urls.py                               # rotas novas
│   └── templates/interface/
│       ├── aviso_previa.html, aviso.html, aviso_interromper.html
│       ├── avisos_do_edital.html, modelos_de_aviso.html, modelo_de_aviso.html
│       ├── publicacoes_do_marco.html         # ponto de entrada (UX-174, UX-175)
│       └── convocacao.html                   # ponto de entrada na chamada por publicação
├── seguranca/papeis.py                       # +6 em TABELAS_APPEND_ONLY
backend/config/settings/
├── base.py                                   # EMAIL_TIMEOUT, AVISOS_*
├── production.py                             # AVISOS_AOS_CANDIDATOS desligada por padrão
└── test.py                                   # AVISOS_AOS_CANDIDATOS ligada
backend/tests/
├── unit/avisos/                              # mensagem, variáveis, resposta, estado
├── integration/avisos/                       # destinatários, confirmação, despacho, concorrência
├── interface/test_avisos.py                  # telas, portas, escopo, vocabulário
└── test_situacoes_de_mensagem.py             # quatro situações (R-015)
doc/implantacao-em-producao-ubuntu.md         # ps-avisos.timer, EMAIL_TIMEOUT, gap I-4 resolvido
AGENTS.md                                     # 40 de 40; os números da suíte
```

**Structure Decision**: monólito existente. O app novo segue o desenho em camadas dos vizinhos
(`convocacao`, `divulgacao`): `domain` puro, `application` com transação e trilha, e `interface`
para as telas.

## Decisões arquiteturais para a revisão

As de maior consequência, com o argumento completo em [research.md](research.md):

1. **`R-002`, concorrência por trava consultiva.** O `FOR UPDATE` foi descartado por fato verificado,
   e não por preferência. Uma execução do despacho por vez, a trava por aviso para
   interrupção × tentativa, e o `UNIQUE` como última porta.
2. **`R-003` e `R-004`, a tentativa em duas gravações e a classificação pela fase SMTP.** É o
   contrato que o usuário pediu. Falha depois do aceite e antes do registro vira indeterminada, e
   nunca é reenviada sozinha. O código só classifica quando é resposta lida a um comando da
   mensagem; queda, timeout e resposta ilegível ficam indeterminados.
3. **`R-007`, o texto congelado na confirmação.** Elimina a configuração de URL-base e faz o
   registro dizer o que saiu.
4. **`R-011`, reenvio como aviso filho.** Nenhum estado "reaberto" e nenhuma tabela a mais.
5. **`R-012`, os modelos iniciais em `sincronizar_unidades`.** Criados uma vez, com trilha, e sem
   escrita em GET.
6. **`R-013` e `R-016`, a chave de habilitação e a janela de despacho (aprovadas).** O código pode
   ir a produção antes do parecer de LGPD, sem confirmação e sem envio. Religar não dispara o que
   ficou para trás.
7. **`R-008`, três variáveis de destino.** Nenhuma variável vale o que outra vale, e o link de
   publicação antigo continua levando à vigente.

## Riscos remanescentes

| Risco | Onde aparece | Mitigação no plano | Resíduo |
|---|---|---|---|
| A conta institucional de correio limita abaixo de 60/min, ou por dia | produção | parâmetro (`AVISOS_LIMITE_POR_MINUTO`); falha temporária retentada | **precisa do número do setor de correio antes da implantação** |
| O servidor aceita e a mensagem cai no spam | produção | SPF, DKIM e DMARC, que o runbook já exige (§16.2) | o sistema não observa; a tela nunca diz "entregue" |
| Uma tentativa vira indeterminada sem necessidade (timeout com servidor lento) | despacho | `EMAIL_TIMEOUT` de 20 s; a execução para na primeira indeterminada | exige decisão humana por destinatário; a tela mostra o caminho |
| O timer parado | produção | alerta no histórico (`FR-1272`); `OnFailure` só cobre falha de conexão | um timer **desabilitado** não alerta: o runbook precisa de conferência em `systemctl list-timers` |
| A presidência envia aviso de resultado sem ter publicado | regra | decisão recebida (2); a trilha registra o autor | nenhum: é a regra pedida |
| Texto livre com dado sensível digitado pela seleção | conteúdo | orientação fixa, modelos neutros, prévia com pessoa real (`D-007`) | **depende de quem escreve**; o sistema não varre texto, por decisão |
| A `065` (PR aberto) e a `066` disputam guardiões globais | integração | a faixa de identificadores tem folga; o `M` e as contagens de migration se medem na hora do merge | **integrar a 066 só depois de resolver a 065**, como o usuário pediu |
| A suíte de 15 a 18 min cresce mais | CI | casos transacionais só onde o banco é a garantia (concorrência, gatilho, privilégio); o resto é unitário | mais casos `transaction=True` |
| LGPD sem validação | produção | `R-013`: confirmação e despacho desligados até a ativação | **precondição institucional aberta** |
| Aviso confirmado pouco antes de a chave ser desligada e religado em menos de 24 h | produção | a janela de despacho | **sai ao religar**, porque ainda está dentro da janela. É o comportamento pretendido: não é mensagem antiga |

## Complexity Tracking

| Acréscimo | Por que é necessário | Alternativa mais simples, recusada porque |
|---|---|---|
| Um processo periódico novo em produção (`ps-avisos.timer`, a cada minuto) | O envio síncrono não cabe na requisição. Não há timeout hoje (gap I-4), o gunicorn corta em 120 s, e centenas de mensagens sequenciais encostam nesse teto. Além disso, a recuperação de queda exige alguém que **volte** depois: um despacho que só roda dentro de um clique não tem como marcar a tentativa órfã. | **Envio em fatias na requisição** ("Continuar o envio, faltam 80"): deixa o aviso pela metade quando a aba fecha, põe o operador em laço e não tem quem retente a falha temporária. **Celery ou RabbitMQ**: dependência e serviço novos, recusados pela decisão recebida (6) e pelo Princípio V. |
| Seis tabelas append-only (40 no total) | O contrato de envio exige, por destinatário, registrar o início antes do servidor e o resultado depois, sem `UPDATE` (`R-003`). O universo histórico e a interrupção são fatos com autor. | **Uma tabela com coluna de estado**: exigiria `UPDATE` e reabriria a mutação em registro de envio, que o sistema inteiro fechou. |
