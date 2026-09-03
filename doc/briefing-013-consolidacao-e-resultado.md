# Briefing — 013: Consolidação e Resultado da Etapa

Ponto de partida da próxima sessão. A 012 — Mesa de Avaliação está fechada e mergeada, e a
auditoria E2E posterior a ela concluiu que **não há bloqueio para iniciar a 013**
(`doc/auditoria-exploratoria-e2e-2026-09-02.md`, §13).

## Fronteira

A 012 produz **Avaliações individuais**. A 013 transforma essas Avaliações em um **Resultado da
Etapa**.

> A 013 transforma Avaliações concluídas em um Resultado da Etapa reproduzível a partir das
> avaliações e das regras então vigentes. Nada que dependa de combinar Etapas entre si,
> classificar globalmente candidatos ou tratar recurso pertence a esta feature.

## Duas decisões já fechadas — entram na spec como decisão, não como pergunta

### D-1 · Déficit de avaliações

Uma Inscrição só está pronta para consolidação quando possuir **todas** as avaliações exigidas e
elegíveis.

```
avaliações exigidas = 2

Maria: 2 concluídas → pronta para consolidação
João:  1 concluída  → aguardando avaliação
Ana:   0 concluídas → aguardando avaliação
```

Não existe, na V1: consolidação parcial, nota assumida, quórum reduzido, nem autorização
excepcional da presidência. **O déficit é estado operacional, não decisão de ninguém** — e é isso
que mantém a 013 determinística.

### D-2 · Reabertura de Avaliação já consumida

Uma Avaliação que já compõe um Resultado da Etapa válido **não pode ser reaberta**.

```
Avaliação concluída → Resultado consolidado → Avaliação protegida
```

O que a regra existe para impedir:

```
resultado = 73 → reabre avaliação → troca 72 por 52 → resultado continua 73
```

Isso destruiria a proveniência. A V1 recusa alto, com a mensagem dizendo o porquê: *esta avaliação
já compõe um Resultado da Etapa e não pode ser reaberta*. Anulação/reconsolidação só entra se
houver necessidade concreta, e como **ato explícito** — não como efeito colateral da reabertura.

## Antes do `/specify`: exploração do código real

Ler a implementação da 012 — spec, research, models, commands, guards, testes e contratos — e não
preservar nomes ou estruturas imaginadas se a 012 tiver implementado contratos diferentes.

Verificar especialmente:

- como a 012 determina `avaliacoes_elegiveis`;
- onde vive a quantidade de avaliações exigidas;
- como conclusão e reabertura funcionam;
- como a versão normativa que governou a Avaliação é preservada;
- como critérios, pontuação total, `minimum_score` e `weight` estão representados;
- quais permissões e vínculos podem operar a consolidação;
- como concorrência e revisão são tratadas;
- se Etapa ou Perfil introduz alguma restrição;
- quais regras normativas já existem para transformar N avaliações num resultado único.

## Fora de escopo

Classificação global, resultado final, desempate, recurso, publicação de resultado e notificação.

## O que **não** entra nesta feature, e está registrado à parte

- **E2E-004** — a Retificação pela interface não alcança documentos exigidos e alguns campos da
  012. P0 antes da primeira seleção real; não é pré-requisito da 013.
- **E2E-021** — quem cancela uma Retificação. Decisão de governança tomada (Gestor cancela a que
  está em elaboração); a implementação ainda precisa resolver as situações que a decisão não
  nomeia.

Os dois estão em `doc/auditoria-exploratoria-e2e-2026-09-02.md`, na seção "Pendências registradas
ao fechar a auditoria".
