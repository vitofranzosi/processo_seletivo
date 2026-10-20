# Quickstart: validar a fatia 2

## Hoje — o protótipo de cálculo

De dentro de `backend/`:

```bash
uv run python ../specs/095-previa-cotas-e-vagas/prototipo/reproducao.py
```

Confira, contra a R-001 de [research.md](research.md):

1. **Concomitância, alvo do quadro**: a PPI tem faixa 3, duas posições dela de quem ocupa pela ampla,
   um autodeclarado além, e 3/3/1/2.
2. **Reversão por saldo**: a PPI cederia 2, a PcD 1, e a próxima apuração da ampla leria 13.
3. **Reversão por esgotamento**: "há quem ocupar: sim", e nada é cedido — inclusive na PcD toda
   ocupando pela ampla.
4. **Alvo fixo 10**: a faixa da PPI é de 4, todos os autodeclarados.
5. **Empate na última vaga da ampla**: a ampla para, e as reservadas aparecem como dependentes dela.
6. **Reserva sem autodeclarados, esgotamento**: ordem vazia, e as 2 vagas seriam cedidas.

## Depois — a feature

Pré-requisitos: a interface da `094` implementada; banco preparado (`make preparar`); runserver com
`INTERFACE_SELETOR_IDENTIDADE=true`.

1. Num rascunho, no passo Perfis, declare as Modalidades "PPI" e "PcD", o quadro com 10, 3 e 2, e a
   reversão *"A quantidade que ficou sem preencher"*. Grave.
2. Na etapa Classificação, num marco por pontuação com alvo do quadro, aperte "Simular
   classificação". A jornada mostra o resumo por recorte no marco, a união na Etapa alimentada e o
   bloco da ocupação depois do marco (US1, US4).
3. Abra o detalhe e troque o recorte para a PPI: posição na ampla em cada linha, a marca "ocuparia pela
   ampla", a frase da faixa tomada pela ampla (US2).
4. Leia o bloco da ocupação: quatro quantidades por recorte, as hipóteses, a quantidade cedida e as
   efetivas que a próxima apuração da ampla leria (US2, US3).
5. Volte ao passo Perfis, troque a reversão para *"Só quando a lista reservada esgota"*, grave, e
   recalcule: nada cedido, com a frase do comportamento atual (US3, DP-2). Retire a declaração: "não
   reverte".
6. Troque o alvo para fixo 10 no cartão, sem gravar: a faixa da PcD passa a 10 posições, e o painel diz
   os dois números (US5, FR-2307).
7. Nada foi gravado: rascunho, atos, apurações, movimentos e trilha iguais (FR-2341).

Verificação automática:

```bash
cd backend && make lint check test-pg
```
