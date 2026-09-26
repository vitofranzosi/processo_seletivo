# Percursos — o gate da publicação, pela tela

**Tudo pela interface.** Shell e banco preparam o ambiente e diagnosticam; **não atravessam passo
que deveria estar disponível à pessoa**. Não havendo caminho, registre a lacuna e siga — protocolo da
`034`.

## Ambiente

- Banco próprio da worktree (`DB_NAME`), `migrate`, a preparação dos papéis **duas vezes** — a saída
  deve dizer `34 de 34` — e `seed_demo`.
- `INTERFACE_SELETOR_IDENTIDADE=true`. Abra sempre por `http://localhost:<porta>`.
- As identidades: **Elaborador** (compõe e submete), **Homologador**, **Publicador**, **Auditor**. A
  segregação de funções exige três pessoas distintas até a publicação.
- **Não use o Edital do `seed_demo` para os percursos 1 e 2**: ele já está publicado. Crie um Processo
  novo pela tela e componha.

---

## 1 — A Etapa que o fluxo exige e que não se consolida (`SC-275`, `FR-746` a `FR-750`)

1. Como **Elaborador**, componha um Edital com um Perfil, um Evento, e duas Etapas: *Análise
   documental* (decisória, eliminatória) e *Prova de títulos* (pontuada, eliminatória, nota mínima
   60, **Avaliações por inscrição = 2**). Um marco enumerando *Prova de títulos*, com regra de corte.
2. Abra a *Revisão*.

**Esperado**: *"Impede"*, na etapa *Etapas*, nomeando *Prova de títulos*, dizendo que o Edital não
declara como combinar as avaliações e que ninguém é eliminado por ela nem posicionado pelo marco.
Hoje: nada.

3. Tente submeter. **Esperado**: recusa com a mesma frase.
4. Abra *Como preencher estes campos*, na etapa *Etapas*. **Esperado**: a explicação de que mais de
   uma avaliação exige regra de combinação que o sistema não publica (`FR-750`). O cartão da Etapa não
   ganhou texto.
5. Troque para **1** avaliação e submeta. **Esperado**: passa (Cenário B).
6. **Contraprova do aviso**: acrescente uma terceira Etapa, *Entrevista*, decisória e **não**
   eliminatória, fora de todo marco. **Esperado**: *"Aviso"*, e a submissão passa. Enumere-a no marco:
   **Esperado**: *"Impede"*.

## 2 — O Perfil que não convoca ninguém (`SC-277`, `FR-752`, `FR-753`)

1. Num Edital em elaboração com um Perfil e **um** marco, escolha *"Este marco não corta"*.
2. Abra a *Revisão*. **Esperado**: *"Impede"*, na *Classificação*, nomeando o Perfil — e **nenhum**
   aviso por marco junto. Hoje: um aviso.
3. Acrescente um segundo marco, com regra de corte completa. **Esperado**: o impeditivo some; o
   primeiro marco recebe **um** aviso (o da `032`).
4. Troque o segundo marco para uma regra que *"Não governa Etapa alguma"*. **Esperado**: nada muda.

## 3 — O Edital publicado não se julga como se fosse publicar (`SC-278`, `FR-755`)

1. Leve até a publicação, com as três identidades, um Edital cujo Evento de inscrições é o período
   designado e **termina em poucos minutos** (memória *mesa pelo navegador com prazo de minutos*).
2. Depois do término, como **Auditor**, abra a tela do Edital.

**Esperado**: nenhuma seção *"Validação do conteúdo"*. Hoje: *"Impede — O período de inscrições
encerrou… corrija… antes de publicar"*.

3. Abra cada etapa do assistente pelo link da composição. **Esperado**: nenhuma pendência.
4. Como alguém com a permissão de retificar, inicie uma Retificação e vá à confirmação.
   **Esperado**: as advertências do ato de Retificação continuam lá, como hoje.

## 4 — A fonte de demonstração (`SC-279`, `FR-757` a `FR-759`)

Este percurso **não** é pela tela de produção, que não existe aqui. Ele é o teste de configuração, e a
contraprova é a tela de desenvolvimento.

1. `make test-pg` — os testes de `tests/test_configuracao_producao.py` e o do vocabulário sob
   configuração de produção passam.
2. Em desenvolvimento, `seed_demo` roda sem rede, e a tela do sorteio do Edital da demonstração
   observa a ocorrência e sorteia — como hoje.
3. Na composição de um marco de sorteio, em desenvolvimento, o seletor de fonte oferece as duas
   fontes.

## 5 — A regressão

`make lint check test-pg`. **Esperado**: verde, com o total de passados **maior** que o de antes, os
**11** pulados de sempre, e o `make preparar` em `34 de 34`.
