# Achado — identificadores de requisito definidos duas vezes (133 e 134)

Registrado em 13/11/2026, na auditoria de consolidação (item P2-6).

> **Não é escopo de nenhuma feature por estar escrito aqui.** Este registro diz o que existe, por que
> importa e quais são as saídas. Renumerar ou não é decisão de governança do usuário.

## O que existe

- **134.** As pastas `specs/134-aviso-de-pendencia-documental/` (23 FRs) e
  `specs/134-cenarios-de-treinamento/` (20 FRs) abrem, ambas, a faixa em **FR-4601**. Os
  identificadores de FR-4601 em diante estão definidos nas duas, com significados diferentes. Os SCs
  não colidem.
- **133.** `specs/133-guia-visual-conceitos/` define FR-001 a FR-009, os mesmos números da 001. Ela
  não segue a faixa global adotada desde a 024.

## Por que importa

- Uma citação "FR-4601" no código é ambígua entre o aviso de pendência e os cenários de
  treinamento. O código cita números dessa faixa em `config/settings/production.py`,
  `test_configuracao_producao.py`, `test_ambiente.py` e `test_situacoes_de_mensagem.py`.
- O guardião `tests/test_citacoes_de_requisito.py` une as definições num `set` e não acusa
  duplicata. A rastreabilidade, que o projeto verifica por teste, não pega este caso.

## Saídas possíveis

1. **Renumerar uma das faixas da 134**, provavelmente a da spec mergeada depois, e corrigir as
   citações no código. É uma mudança só de texto, mas toca código e testes.
2. **Um guardião de definição única** de FR-, SC-, UX- e D- entre specs, que impeça a próxima
   colisão. Ele reprovaria hoje, até que a saída 1 seja feita ou até que as duas colisões entrem numa
   lista de exceções nomeadas.
3. **Deixar como está, registrado.** A 133-guia é uma prova de conceito pedagógica, e a colisão dela
   é inofensiva na prática.
