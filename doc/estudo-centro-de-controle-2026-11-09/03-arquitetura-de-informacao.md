# Entrega 3 — Arquitetura de informação do Centro de Controle

## A decisão de fundo: transformar o detalhe do Edital, sem criar outra página

O Centro de Controle proposto **é o detalhe do Edital publicado, reorganizado**. Não é uma página nova
ao lado dele. Três razões:

1. O detalhe já é o destino de todos os caminhos: lista de Processos, Agenda, "Próximo nesta lista" e
   o caminho de navegação de cada tela de ato. Uma segunda página dividiria o destino, e a pergunta
   "qual das duas?" voltaria.
2. A 104 (D-001) recusou uma página nova por duplicar a Visão Geral e a Agenda. A convergência de 07/11
   manteve o critério: "nenhuma entrega cria página nova".
3. Voltar do detalhe operacional ao Centro de Controle (tarefa T9 do pedido) passa a ser gratuito: o
   caminho de navegação de toda tela de ato já aponta para o detalhe do Edital.

O protótipo mora em outra URL (`/gestao/prototipo-centro/…`) **só** para permitir a comparação lado a
lado. Ver a decisão D-2.

## As quatro camadas, nesta ordem

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Edital SIM12/2026  Conferência documental (treinamento)                      │
│ [ONDE ESTAMOS] A seleção avança em 4 frentes: classificação, resultado …     │
│ Situação administrativa: Publicado · Processo ativo │ Inscrições: … │ Papel  │
├──────────────────────────────────────────────────────────────────────────────┤
│ A  ✓Edital ✓Inscrições ✓Avaliação ●Classificação ◷Resultado ◐Vagas ●Conv. ·Fim│
├───────────────────────────────┬──────────────────────────────────────────────┤
│ B  O que fazer agora          │  Detalhe da fase escolhida                   │
│    Sua próxima ação (se 1)    │  ① Relação ② Semente ③ Sorteio  (roteiro)    │
│    Suas ações (sem ranking)   │  lista × ponto: situação, ato, razão, link   │
│    Esperando prazo/correção   │  Entenda: … (opcional)                       │
│    Com outros papéis          │                                              │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ C  Onde cada lista está: lista × macrofase + "agora nesta lista"             │
│    Ver todos os pontos (matriz da 127) · Telas do marco                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ D  Administração e histórico: documentos, consultas, quem atuou, validação   │
│    ▸ Encerrar ou cancelar o Edital (recolhido, ao fim)                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Cabeçalho — onde estamos
- **Uma frase** derivada das macrofases em curso: *"A seleção avança em 4 frentes ao mesmo tempo:
  classificação, resultado e recursos, vagas e convocação."* Concluída a seleção: *"Seleção
  concluída. Nada em aberto."*
- **Três estados separados**, cada um com rótulo: a situação administrativa (selo do Edital, mais o
  Processo), as inscrições (a linha da 127) e o seu papel aqui (lido do `Alcance` da 127: "Você conduz
  a seleção", "Você publica resultados", "Você acompanha este Edital sem ato a praticar nele").

### Camada A — a jornada
- **Oito cartões**, um por macrofase, com sinal, nome, situação em palavras e um resumo curto ("1 de 2
  listas concluídas", "preliminar publicado em 1 lista", "◷ espera até 14/11", "2 providências").
- **Sem percentual nem barra contínua.** Várias fases podem estar acesas ao mesmo tempo. A situação
  nunca é só cor: há sinal e palavra (WCAG 1.4.1).
- Cada cartão é um link (`?fase=…`) que abre o detalhe da fase. Funciona sem JavaScript, por causa da
  CSP.
- "Como ler a jornada" fica recolhido, com a legenda das sete situações de apresentação.

### Camada B — o que fazer agora
A mesma derivação do nível 1 da 127, com quatro regras de apresentação:

1. **Uma ação em destaque só quando é seguro identificá-la**: a pessoa tem **exatamente uma**
   providência sua. Com várias, aparece *"O GPS não as ordena por importância"*, e cada uma traz a fase
   a que pertence. Nada de prioridade artificial.
2. **Cada providência diz em que fase está**, e, quando a derivação o sabe, que é **paralela**
   ("Independente do sorteio: a relação, a semente e o sorteio não leem o resultado desta Etapa").
3. **Esperas e impedimentos juntos, numa seção própria**, com data, razão e, no impedimento, quem
   resolve e o caminho (Retificar). A espera recomendada leva a marca "recomendação" (133).
4. **"Entenda"**, recolhido, com três frases fixas: o que é, por que existe e o que acontece ao
   confirmar.

### Detalhe da fase
- **O roteiro**: os atos da fase, na ordem da jornada, numerados, com a situação agregada e "N de M
  listas". O que vale para todas as listas (a semente, a Etapa) diz isso.
- **A tabela lista × ponto** com situação, ato, razão, nota e o link para a tela real.
- O histórico vem por "ver o ato" nas células feitas.
- A fase aberta por padrão segue uma regra fixa: a primeira com ato **seu**, com a frente paralela por
  último; senão, a primeira em curso; senão, a última concluída.

### Camada C — onde cada lista está
- Uma tabela por Perfil: linhas = listas, colunas = as cinco macrofases por lista, mais **"Agora nesta
  lista"** (os atos a praticar, um por fase; ou a primeira espera).
- A matriz completa da 127 continua acessível ("Ver todos os pontos"), assim como os links das telas do
  marco.

### Camada D — administração e histórico
- Documentos publicados e Retificações, consultas (relatório, formalização, avisos, inscrições,
  recursos — as que `acoes.do_edital` oferece), quem atuou e a validação do conteúdo.
- **Encerrar e cancelar ficam recolhidos ao fim**, com a frase "atos de fim de ciclo, irreversíveis".
  A tela de cada ato continua mostrando antes o que está em aberto (130).

## Critérios de exibição

| O quê | Quando aparece | Regra de origem |
|---|---|---|
| Ação em destaque | Exatamente uma providência **sua** | Nova, de apresentação (decisão D-4) |
| Providência com link | Sua, e a pessoa abre a tela | `Providencia.da_celula` (127): `url` só se `sua` |
| Espera | `AGUARDA`, com `ate` quando houver | 127 |
| Recomendação | `recomendacao=True` | 133, R2 |
| Impedimento | `IMPEDIDO`, mais `quem_resolve` e `url_da_saida` | 127 |
| Jornada e "onde estamos" | Todos que abrem o Edital publicado | O mesmo nível de informação das providências do nível 1 (D3c do estudo de 06/11) |
| Detalhe da fase por lista e camada C | Só `ve_a_matriz` (quem conduz ou audita) | D-004 da 127. O protótipo **errou** isso na primeira versão (avaliação e Publicador viam a tabela) e corrigiu; ver `proposta-c06-avaliacao1.png` |
| Encerrar e cancelar | Quem os tem em `acoes.do_edital`, recolhido | `acoes.hierarquia().terminais` |

## Segurança: o que a representação não faz
- **Não autoriza nada.** Todo botão leva à tela real do ato, que decide e recusa. A previsão vem das
  mesmas funções (`Alcance.de`, `pode_gerir_comissao`, `pode_conferir_documentos`, `acoes.do_edital`).
- **Não guarda estado.** Nenhuma coluna, tabela ou migration. A macrofase é rótulo de apresentação.
- **Não é derivação nova**, salvo duas regras de agregação puras (`agregar` e `juntar`), que se provam
  por teste como as sete situações da 127.

## A página do Processo
- **Onde cada Edital está**: um item por Edital, com a frase "onde estamos", a mini-trilha das oito
  fases e "N providências em aberto · M suas · K aguardando", levando ao Centro de Controle.
- Sai o "O que fazer agora" que diz "nenhum ato" ao lado de Editais com providências (A-02). Os atos do
  Processo (comissão, alocação, supervisão) vão para "Administração do Processo"; encerrar e cancelar,
  recolhidos.
- Com vários Editais, a lista é a mesma, um item por Edital. **Não visto com dado real**: nenhum
  cenário tem dois Editais.

## Pedagogia integrada (Etapa 5 do pedido)
- **Fonte única de conceitos.** No protótipo é o dicionário `CONCEITOS`, por natureza do ato. Na
  implementação, **um** módulo lido pelo Centro de Controle **e** pelos "Termos desta tela" das telas
  de ato. Dois textos divergiriam na primeira mudança, a lição da 103 e da 104.
- **Curtos e opcionais**: três frases, sempre recolhidas, exceto o "o que é" da ação em destaque.
- **Conteúdo** conferido com o guia da jornada do sorteio (congelamento, semente, a Caixa) e com o
  `gps-por-dentro` (corte, faixa, apuração). O guia aponta uma lacuna: **congelar a relação não está
  entre os 17 conceitos** do `gps-por-dentro`.
- **Os guias completos continuam em `doc/`.** Ligá-los ao produto pede versioná-los com o código, e
  o próprio POC recomenda não integrá-los sem teste com operadores (decisão D-7).
