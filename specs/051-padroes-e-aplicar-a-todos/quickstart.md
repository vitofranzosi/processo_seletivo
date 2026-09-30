# Quickstart — 051

## Suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_051
```

## Percurso no preview — a estrutura do 28/2026

Banco próprio, servidor com `INTERFACE_SELETOR_IDENTIDADE=true`. Edital em elaboração com 7 polos
idênticos (40 vagas: ampla 28, PPI 10, PcD 2), uma Etapa decisória (análise documental) e o Evento
*"Sorteio eletrônico"* no Cronograma.

1. **Perfis.** Compor o polo 1 com as três Modalidades, declarando o arredondamento *"a fração vira
   vaga"*; *Preencher pelo percentual* → 10 e 2. Duplicar seis vezes. No controle do Edital, forma de
   convocação *"por mensagem individual"* → prévia *"7 mudam"* → confirmar.
2. **Etapas.** Acrescentar a Etapa decisória: ela vem eliminatória.
3. **Classificação.** Método comum: escolher o Evento do sorteio; escolher as duas regras sem digitar a
   prosa. No polo 1, *Acrescentar marco*, *"Por sorteio"*: o corte vem declarado e o empate não é
   perguntado; responder a faixa seguinte e o recurso. *Aplicar aos demais Perfis (6)* → prévia *"6
   nascem"* → confirmar.
4. **Revisão.** Conferir: o grupo dos 7 marcos com a origem *"aplicado a partir do Perfil …"*; o corte
   com *"padrão do sistema"*; o instante com o Evento; a prosa *"gerada da regra"*; o bloco dos campos
   que não se corrigem depois de publicados.
5. Editar à mão o marco de um polo e reabrir a Revisão: ele deixa de ser atribuído ao gesto.

**A contagem.** Contar as interações da etapa Classificação (e da forma de convocação) antes, na
`main`, e depois, neste branch, pelo mesmo roteiro — cada clique, escolha ou campo digitado.

## Percurso no preview — a Retificação em lote (P2)

Banco próprio (`ps_051p2`) e servidor com `INTERFACE_SELETOR_IDENTIDADE=true`, num host próprio
(`lote.localhost`) para não herdar sessão de outro servidor local. Um Edital **publicado** de 7 polos,
cada um com o marco do Edital máximo — prazo recursal de 2 dias, corte de quantidade fixa, convocação
por publicação —, menos o POLO07, que corta pelo quadro.

1. **Retificar.** No POLO01: *Forma de comunicar a convocação* → mensagem individual; *Prazo em dias*
   → 3.
2. *Aplicar a janela recursal aos demais Perfis (6)* → a conferência mostra o gesto: *"6 mudam"*,
   `Prazo em dias: 2 → 3` em cada polo.
3. No cartão do Perfil POLO01, *Aplicar a forma de convocação aos demais Perfis (6)* → segundo bloco,
   *"6 mudam"*; o título conta 14 Alterações.
4. **O destino fora.** Suplentes do POLO01 → 2; *Aplicar a regra de corte aos demais Perfis (6)* →
   *"5 mudam, 1 fica fora do alcance"*: o POLO07, com a espécie do alvo nomeada, a razão do contrato e
   os dois valores. *Desfazer este gesto* e suplentes de volta a 1.
5. Justificativa → *Criar Retificação (14 Alterações)* → uma Retificação, 14 Alterações; submeter,
   homologar e publicar → uma versão nova, um documento, os 7 polos com 3 dias e mensagem individual.

**A contagem**, pelo mesmo critério da P1 — cada clique, escolha ou campo preenchido: antes, os 7
prazos e as 7 formas à mão; depois, o POLO01 e os dois gestos.
