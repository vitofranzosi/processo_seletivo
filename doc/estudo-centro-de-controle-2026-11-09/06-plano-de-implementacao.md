# Entrega 6 — Plano de implementação

**Premissas.**
- Nenhuma engine de workflow nova.
- Nenhuma coluna, tabela ou migration.
- Nenhuma regra de disponibilidade duplicada: tudo lê o `Andamento` da 127 e o `acoes.do_edital`.
- Cada spec é um incremento que entra sozinho e não quebra os anteriores.
- **O MVP são as specs C1 e C2.** As demais são melhorias.

As specs só se escrevem depois das decisões D-1 a D-8 do README. A numeração vem de `--number N`, como
sempre.

---

## C1 — Onde estamos: o detalhe do Edital reorganizado (MVP)

**Problema.** A-01, A-05, A-08, A-11 e H1–H3: o estado não é dito, o fim de ciclo compete com a
operação, e o histórico vem antes do andamento.

**Escopo.**
- Cabeçalho com a frase "Onde estamos" e os três estados rotulados.
- A trilha das oito macrofases, com a legenda recolhida.
- "O que fazer agora" com as regras de apresentação da Entrega 3:
  - destaque só com uma providência sua;
  - a fase de cada providência;
  - esperas e impedimentos numa seção própria.
- Administração e histórico ao fim; Encerrar e Cancelar recolhidos.
- Só depois da publicação: antes dela, o detalhe atual fica como está, porque conduz bem.

**O que se reutiliza.**
- `andamento.do_edital`, `providencias.Nivel1` / `Providencia`, `Alcance.de`;
- `acoes.do_edital` / `hierarquia`, `atos_retificacao.em_curso`;
- `_documentos_publicados`, `_providencia.html`, `andamento.css`, `terminais.css`.

**O que muda.**
- Um módulo `interface/centro.py`, com as macrofases, `agregar`, `juntar` e "onde estamos". É o
  `prototipo/centro.py` sem a parte pedagógica, que é da C4.
- `views.detalhe` passa a compor o centro.
- `detalhe.html` é reorganizado.
- Uma folha `interface/telas/centro.css`.

**Dependências.** Decisões D-1, D-2, D-3, D-4 e D-8 (esta só para a parte do Processo, que é a C5).

**Critérios de aceite.**
- Nos 15 cenários da 134, a frase "Onde estamos" e a trilha aparecem na primeira dobra a 1440 × 900.
- A macrofase está em "ação disponível" **se, e só se**, alguma célula dela está em `A_PRATICAR`
  para alguém. É o teste de coerência, no molde do SC-1230 da 127.
- Nenhuma providência do nível 1 deixa de aparecer. A soma das seções é igual ao `Nivel1.total`.
- Encerrar e cancelar não aparecem no cartão "O que fazer agora".
- A 375 px, nenhuma rolagem horizontal; a trilha empilha.

**Riscos de regressão.**
- Os testes de template do detalhe que leem a ordem das seções.
- `test_acessibilidade` (classe sem regra na folha).
- `test_estaticos`.
- A varredura de vocabulário (lista literal de telas).
- O orçamento de consultas do detalhe (FR-4120 da 127) **não pode** subir.
- As citações `FR-`/`D-` nos comentários.

**Testes.**
- Funções puras: `agregar` e `juntar` nas famílias S1–S3 e P1–P3 da 127, sem banco.
- Template: o detalhe dos cenários, por papel (presidência, Gestor, Publicador, avaliação).
- Orçamento de consulta igual ao de hoje.
- Uma jornada no navegador (grupo `navegador`): abrir o C06, ler "Onde estamos", seguir "Congelar a
  relação" até a tela do sorteio e voltar pelo caminho de navegação.

## C2 — O detalhe da fase e "onde cada lista está" (MVP)

**Problema.** A-12 e H3: o detalhe por lista fica recolhido e rola na horizontal; não há sequência por
fase.

**Escopo.**
- O painel de detalhe da fase (`?fase=`), com o roteiro numerado e a tabela lista × ponto.
- A tabela "Onde cada lista está", com "Agora nesta lista".
- A matriz completa da 127 continua, recolhida, como "Ver todos os pontos".
- Tudo restrito a `ve_a_matriz` (D-004 da 127, ou o que a D-6 decidir).

**O que se reutiliza.** `PerfilNoAndamento.pontos` / `linhas` / `destinos` e as classes da matriz.

**O que muda.** O template do detalhe e `centro.py` (roteiro, "agora nesta lista" e a fase escolhida
por padrão).

**Dependências.** C1 e D-6.

**Critérios de aceite.**
- Cada cartão da trilha abre o detalhe da fase **sem JavaScript**.
- A fase padrão segue a regra fixa: a sua primeiro, a paralela por último.
- Quem não `ve_a_matriz` não recebe tabela por lista: o teste confere a ausência no HTML, e não só
  na tela.

**Riscos.** O vazamento por agregação (inventário da supervisão); por isso o teste de ausência no HTML.

**Testes.** Template por papel; a regra da fase padrão, como função pura; e o navegador a 390 px.

## C3 — Correções da derivação reveladas pelo estudo

**Problema.** Os achados de derivação e de texto, que nenhuma reorganização resolve.

**Escopo.**
- **G-1 / A-09.** A célula da ordem leva a contagem da lista. A providência de lista vazia passa a
  dizer "Declarar que ninguém concorreu — PPP (lista sem inscritos)", e não entra no destaque.
- **G-3.** A `Celula` do resultado ganha o que foi divulgado (`preliminar`/`definitivo`), e a nota
  deixa de ser a única fonte.
- **A-08.** A razão da espera do definitivo não oferece publicar como preliminar quando o preliminar
  já existe.
- **G-7 / A-07.** A contagem de providências do Perfil e a do Edital somam o mesmo, ou dizem o seu
  escopo.

**O que se reutiliza.**
- `conducao_do_marco.indicador_do_marco` (que já sabe a lista vazia);
- `divulgacao_do_ato`;
- `publicabilidade.aferir`.

**Dependências.** Nenhuma. **Pode vir antes da C1**, e é a recomendação.

**Critérios de aceite.** Nos C08, C12 e C14, nenhuma providência "Emitir a ordem — PPP" sem a menção
à lista vazia, e nenhuma espera do definitivo oferecendo o preliminar já publicado.

**Riscos.** O teste `…nunca_diz_pendente_para_a_ordem_que_o_comando_recusa`, e as transições
"Próximo nesta lista", que leem a mesma célula.

**Testes.** As funções puras da 127 com a lista vazia e com o preliminar publicado; o template das
providências.

## C4 — Conceitos no lugar da decisão (melhoria)

**Problema.** A-06, mais a lacuna do estudo de 06/11 ("semente" e "relação" sem definição).

**Escopo.**
- Um módulo único de conceitos, por natureza do ato, com o que é, por que existe e o que acontece ao
  confirmar.
- O "Entenda" do Centro de Controle **e** os "Termos desta tela" das telas de ato leem dele.
- Acrescentar "congelar a relação" ao `gps-por-dentro`.

**Dependências.** D-7: quem aprova o texto. Validação com 3 a 5 operadores **antes** de ir para
produção, como o POC da 133 recomenda.

**Critérios de aceite.**
- Nenhum texto de conceito duplicado entre telas.
- Um guardião confere que toda natureza de providência tem conceito.

**Riscos.** O texto ensinar uma regra imprecisa. Por isso a revisão humana é critério.

## C5 — O Processo agregado ("Frente B" da 129) (melhoria)

**Problema.** A-02 e A-10.

**Escopo.**
- "Onde cada Edital está", com a frase, a mini-trilha e as contagens.
- Sai o "O que fazer agora" do Processo, ou ele passa a somar os Editais (D-8).
- Os atos do Processo vão para a administração.
- "Próximos marcos" cruza o cronograma com o andamento, ou diz que é o declarado.

**O que se reutiliza.** `andamento.do_edital` por Edital, `supervisao.pulso` / `sinais`, `pending_editais`.

**O que muda.** **Leitura em lote**: com N Editais, N vezes a derivação estoura o orçamento. É o desenho
pendente da 129.

**Dependências.** C1 e D-8.

**Riscos.** O orçamento de consulta da página do Processo e da Lista.

**Testes.** O orçamento com 1, 3 e 10 Editais; o template com um Processo de dois Editais (fixture
nova, porque **nenhum cenário tem**).

## C6 — Sorteio: observar antes de congelar (decisão de domínio)

**Problema.** A-03 / G-6. A tela oferece um ato de um clique que inviabiliza o anterior.

**Escopo.** Depende da D-5. As opções:
- (a) recusar no comando enquanto houver relação do marco não congelada;
- (b) confirmação em duas fases, dizendo quais relações ficam de fora — o P1 do guia do sorteio;
- (c) só alertar na tela.

**Riscos.** Mexe no rito do sorteio. Na (a), a observação parcial legítima — uma lista que nunca vai
congelar — precisa de saída.

---

## O MVP e o que fica para depois

| | Specs | O que entrega |
|---|---|---|
| **MVP** | C3 → C1 → C2 | O detalhe do Edital publicado responde "onde estamos, o que fazer, o que espera e onde cada lista está", sem dado novo, com as correções de texto e de lista vazia |
| Em seguida | C6 (com a D-5), C4 | O sorteio seguro, e os conceitos validados com operadores |
| Depois | C5 | O Processo agregado, com leitura em lote |
| **Futuro, fora deste plano** | — | Agenda ligada aos atos; efeito de uma Retificação por fase (G-5); recurso por lista (G-4); filtro por Perfil em Editais grandes; avisos proativos |

**O que não se recomenda.**
- Um motor de workflow.
- Persistir uma "fase atual".
- Uma página nova ao lado do detalhe.
- Percentual de conclusão.
- Um "próximo passo único" escolhido por prioridade.
