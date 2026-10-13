# Jornada pública — quem chega, o que decide e onde tropeça

**Data:** 2026-10-12 · Parte da [auditoria de UX e conversão](../auditoria-ux-conversao-2026-10-12.md).
Os achados `C-NN` estão descritos no [diagnóstico](diagnostico.md).

---

## 1. Perfis de visitante

| | **A — decidido** | **B — interessado ainda não decidido** |
|---|---|---|
| Chega por | endereço guardado, e-mail do sistema (066), busca pelo número do Edital | campanha, divulgação institucional, busca genérica, indicação |
| Sabe | qual seleção, às vezes qual vaga | que "o Ifes tem alguma coisa"; talvez o curso ou cargo do anúncio |
| Quer | achar, conferir requisito e prazo, inscrever-se ou acompanhar | descobrir se há algo para si, entender o que é, decidir se vale |
| Mede o sistema por | quantos passos até a ação | quanto entende sem ler o Edital |
| Hoje é atendido | **bem** no desktop; **razoavelmente** no celular | **mal** na vitrine do celular; **bem** na página da seleção, depois de rolar |

Há um terceiro, que a hipótese inicial não nomeia e que o sistema atende cada vez mais:

| | **C — quem acompanha** |
|---|---|
| Chega por | aviso por e-mail (066), divulgação de resultado, boca a boca |
| Quer | resultado, prazo de recurso, sorteio, convocação |
| Hoje é atendido | **bem** na página da seleção (resultados em destaque quando encerrada; "Entrar para ver minha situação"), **mal** na vitrine, onde a seleção dele aparece como "Encerrada" sem mais nada (C-03) |

**O objetivo da jornada pública, portanto, são três tarefas:** encontrar uma oportunidade, começar a
inscrição e acompanhar o certame. Uma vitrine otimizada só para converter visitante em inscrito
empurraria a terceira para baixo — e é na terceira que estão os prazos para exercer direitos (recurso)
e os atos que mudam a situação da pessoa (resultado, sorteio, convocação). As propostas e a
priorização tratam as três como objetivo, com o mesmo peso da conversão.

## 2. Jornadas

### 2.1 Perfil B no celular, acesso geral

| Passo | O que vê | Pergunta que tem | Responde? |
|---|---|---|---|
| 1. Abre `/selecoes/` | topo verde, "Processos seletivos", subtítulo, formulário de 5 controles | "Tem algo para mim aqui?" | **Não na 1ª tela** — o 1º cartão começa em 602 px (C-01) |
| 2. Rola | "INSCRIÇÕES ABERTAS", cartão com "Processo Seletivo Simplificado 2026" | "O que é isto?" | Em parte: a oportunidade está no subtítulo do cartão (C-02) |
| 3. Lê o cartão | Perfis, "3 vagas imediatas", período, "Faltam 19 dias" | "Onde? Para quem?" | Não diz onde (C-19); requisito só na página |
| 4. Toca o cartão | página da seleção, 1ª tela só cabeçalho | "Quantas vagas, e como me inscrevo?" | **Não na 1ª tela** — "Vagas" a 734 px, botão a 1.249 px (C-11) |
| 5. Rola até a vaga | requisito, documentos, vagas, botão | "Eu tenho o que pedem?" | **Sim** — é o melhor trecho da jornada |
| 6. Toca "Inscrever-se" | "Entrar — Sem senha: enviamos um código…" | "Estou me inscrevendo ou criando conta?" | Não diz a vaga (C-12) |
| 7–9. E-mail, código, dados | três telas curtas | "Por que o CPF?" | Não diz (C-13) |
| 10. Volta à vaga | a mesma página, rolada | "E agora?" | Sem mensagem; precisa tocar de novo (C-12) |
| 11. Rascunho | "Etapa 1 de 3", documentos, **Requerimento exigido** | "Isso eu não sabia" | Surpresa (C-14) |

### 2.2 Perfil B por campanha específica

O anúncio fala de um curso ou cargo. O destino recomendado é a **página da seleção**
(`/selecoes/<edital>/`), e, quando o anúncio fala de **uma** vaga de um Edital com várias, a âncora
da vaga (`/selecoes/<edital>/#vaga-<perfil>`) — que **já existe** no HTML, porque é por ela que a
autenticação devolve a pessoa. Não exige nada novo.

A vitrine não é necessária nesse fluxo, e a experiência hoje tem quatro atritos entre o clique e a
inscrição:

1. **A prévia do link** — sem `description` nem Open Graph, o anúncio orgânico ou o encaminhamento por
   mensagem mostra só o título (C-16);
2. **"← Voltar aos resultados"** para quem não buscou (C-10);
3. **a âncora sem destaque** — a página rola até a vaga e nada indica que é aquela (sem `:target`);
4. **a ação a duas telas** quando o destino é a página sem âncora (C-11).

Endereços que já servem de destino de campanha, sem mudança:

| Campanha sobre | Destino | Observação |
|---|---|---|
| Um Edital | `/selecoes/<edital_id>/` | estável, público, sem login, sobrevive ao encerramento |
| Uma vaga de um Edital | `/selecoes/<edital_id>/#vaga-<perfil_id>` | a âncora existe; falta o destaque |
| Um curso ou cargo em vários Editais | `/selecoes/?busca=<termo>` | funciona; `?perfil=` exige o nome exato do Perfil e é frágil |
| Um Processo com vários Editais | — | **não há página de Processo** (047 a deixou fora) |

**Coerência anúncio–destino.** O anúncio que diz "Curso técnico em Informática EaD, 40 vagas,
inscrições até…" leva a uma página cujo `h1` é o título do Edital, e não o do curso; a palavra do
anúncio está no cartão da vaga, a 700 px. Com a âncora e um resumo de vagas no cabeçalho, a palavra
aparece na primeira tela.

**Campanhas geradas por programa (Ifes Ads), no futuro.** O que o sistema já oferece é suficiente
para um gerador: identificadores estáveis, a API pública da versão vigente
(`/api/v1/public/editais/{id}/versao-vigente`) com Perfis, vagas e período, e a âncora por Perfil. O
que um gerador **não** tem: endereço legível, prévia de compartilhamento e qualquer retorno sobre o
que aconteceu depois do clique. **Nada disso deve ser implementado agora**; o registro serve para que
a próxima mudança de endereço ou de cabeçalho não feche essa porta.

### 2.3 Perfil A, decidido

Busca pelo número do Edital ou pelo nome do cargo, abre, rola até a vaga e se inscreve. No desktop é
direto. No celular, o formulário no alto **ajuda** este perfil — é a única coisa na primeira tela que
lhe serve —, e qualquer proposta que esconda a busca precisa manter o campo visível.

### 2.4 Perfil C, quem acompanha

Recebe o aviso do sistema com o link da seleção e cai direto nos resultados em destaque — bem
atendido. Se vier pela vitrine, procura a seleção entre as "Encerradas" sem nenhuma pista de que há
resultado novo ou prazo de recurso correndo (C-03).

## 3. Pontos de decisão

| # | Decisão do visitante | Onde acontece | O que precisa estar à vista | Hoje |
|---|---|---|---|---|
| D1 | "Vale olhar?" | vitrine, 1ª tela | que há seleção aberta, de quê, onde | no celular, nada (C-01) |
| D2 | "É para mim?" | cartão | oportunidade, lugar, prazo | oportunidade em 2º plano, lugar ausente (C-02, C-19) |
| D3 | "Eu cumpro?" | seleção, cartão da vaga | requisito, documentos, o que mais será pedido | requisito e documentos sim; Requerimento não (C-14) |
| D4 | "Dá tempo?" | cartão e seleção | prazo, tempo restante | **sim**, e bem |
| D5 | "Começo agora?" | botão da vaga | o que acontece ao tocar | "exige identificação por e-mail" — bom |
| D6 | "Continuo?" | acesso, código, dados | para onde isto me leva | não nomeia a vaga (C-12, C-13) |

## 4. Fricções, em ordem de percurso

1. Formulário antes de qualquer oportunidade, no celular (C-01, C-04).
2. Cartão que nomeia o Processo antes da oportunidade (C-02).
3. Metadados internos no lugar do lugar (C-19).
4. Página da seleção sem resumo nem atalho para as vagas, no celular (C-11).
5. "Voltar aos resultados" a quem não buscou (C-10).
6. Acesso sem contexto; "Entrar" como botão de quem queria se inscrever (C-12).
7. CPF sem finalidade dita (C-13).
8. Volta à vaga sem destaque e segundo clique sem explicação (C-12).
9. Requerimento descoberto dentro do rascunho (C-14).

## 5. Oportunidades de melhoria

Detalhadas e comparadas nas [propostas](propostas-redesenho.md). Em uma linha cada:

- **Mostrar oportunidade antes de filtro** no celular — busca visível, demais filtros recolhidos.
- **Inverter a hierarquia do cartão** para a da página da seleção: o Edital (ou os Perfis) no título,
  o Processo como metadado.
- **Dizer onde** — localidades dos Perfis no cartão.
- **Dar à encerrada os fatos que ela tem** — resultado publicado, recurso até, sorteio realizado —,
  como fatos datados, sem estado agregado.
- **Resumo de vagas com âncora** no cabeçalho da seleção.
- **Carregar a vaga pela identificação**: nomeá-la no acesso, destacá-la na volta, dizer por que o
  segundo clique existe.
- **Anunciar o Requerimento** quando o Edital o pede na inscrição.
- **Assinatura institucional mínima** — rodapé com atendimento, favicon, metas de compartilhamento —
  **depois** do escopo mínimo, conforme contribuição demonstrável.

## 6. Relação entre descoberta e inscrição

A descoberta e a inscrição estão bem separadas no sistema — a primeira é anônima e não grava nada; a
segunda começa num POST auditado. Essa separação é uma **virtude a preservar**: ninguém entrega dado
pessoal para olhar uma vaga, e nenhum endereço compartilhado cria inscrição.

O custo dela hoje é de **contexto**, não de passos. O número de telas até o rascunho (cinco, para
pessoa nova; três, para quem já tem conta) é compatível com o acesso sem senha e com a `009` (SC-UX-001
conta a partir do rascunho). O que a pessoa perde no caminho é a **memória do que escolheu**: a vaga
some do texto entre o passo 1 e o passo 6, e reaparece sem aviso.

## 7. Validação e mensuração da jornada

**A melhoria não depende de analytics.** O que este conjunto propõe se valida pelo que a `024` já
praticou — percurso conduzido —, agora com pessoas de fora do projeto. Medir a jornada em produção é
outra coisa, e é decisão própria (§7.3).

### 7.1 Validar sem registrar navegação: percursos conduzidos

Sessões curtas, com candidatas e candidatos reais ou representativos (inclusive quem nunca se
inscreveu num processo do Ifes), no próprio celular da pessoa, sobre o banco de demonstração. Nada é
gravado no sistema; quem conduz anota acerto, tempo aproximado e onde a pessoa hesitou.

| Tarefa | Pergunta que a pessoa recebe | Sucesso |
|---|---|---|
| Encontrar | "Há alguma seleção aberta para técnico? Onde é?" | aponta o cartão e o lugar sem abrir o Edital |
| Compreender | "Você poderia se inscrever? O que vai precisar ter em mãos?" | diz o requisito, os documentos e o Requerimento, quando houver |
| Começar | "Comece a inscrição nesta vaga." | chega ao rascunho da vaga certa sem voltar atrás |
| Acompanhar | "Você participou desta seleção. Saiu resultado? Ainda dá para recorrer?" | acha o resultado e o prazo **a partir da vitrine** |

Cinco a oito sessões por rodada, antes e depois da mudança, já mostram se o atrito descrito aqui
existe para pessoas reais. Não é medida de conversão; é a evidência de compreensão e de conclusão de
tarefa que falta a esta auditoria. O registro das sessões é anotação de quem conduz, sem dado pessoal
além do consentimento.

### 7.2 O que já se pode contar, sem coletar nada novo

| Evento conceitual | Medível? | Como |
|---|---|---|
| Visualização da vitrine | não, só no log do servidor web | — |
| Visualização de uma seleção | não, só no log do servidor web | — |
| Visualização de vagas | não | — |
| Clique em "Inscrever-se" | só para quem já tem sessão (vira rascunho) | — |
| Acesso iniciado e concluído | sim, sem vínculo com Edital | `DesafioDeAcesso.criado_em` × `consumido_em` |
| Inscrição iniciada | **sim**, por Edital e Perfil | `Inscricao.created_at`, ato `CRIAR` |
| Inscrição concluída | **sim**, por Edital e Perfil | `Inscricao.submitted_at`, ato `SUBMETER` |
| Abandono entre etapas internas | **sim**, aproximado | atos `GRAVAR` e `ANEXAR` entre `CRIAR` e `SUBMETER` |

**Indicadores já calculáveis**, agregados, sem dado pessoal na saída — e nenhum deles é conversão:
dizem o que acontece **depois** que alguém começou, e nada sobre quantos viram a oportunidade e não
começaram:

- **conclusão das inscrições iniciadas** por Edital e Perfil = enviadas ÷ rascunhos criados;
- **rascunhos não enviados ao fim do prazo**, por Perfil — o abandono que custa uma inscrição;
- **tempo entre rascunho e envio** (mediana) — sinaliza onde a preparação pesa;
- **etapa de parada**: rascunho sem `GRAVAR`, com `GRAVAR` sem `ANEXAR`, com anexos sem `SUBMETER`;
- **códigos pedidos × consumidos** — a perda no e-mail, que a auditoria de 02/09 apontou como o
  principal risco de conversão.

Um relatório desses é **consulta sobre registro que já existe** — não muda o que se coleta. Ainda
assim, cruzar trilha de auditoria com finalidade estatística é uso secundário, e merece a
avaliação de LGPD que a Constituição pede a toda spec.

### 7.3 O que exigiria instrumentação, e o limite

Visualizações, cliques em cartão, taxa de início e **origem de campanha** exigem registrar
navegação — o que a `024` vedou **naquele incremento** (D-008, SC-047), chamando-o de "decisão de
proteção de dados sob o Princípio III, e não subproduto de um incremento de tela". A vedação não é
perpétua: pede decisão própria. **Esta auditoria não recomenda revogar a
decisão como parte de uma melhoria visual.** Se o produto quiser medir a jornada pública, o caminho
proporcional seria, nesta ordem e cada passo como decisão própria:

1. **Contadores agregados no servidor**, por Edital e por dia: visualizações da seleção e POSTs de
   "Inscrever-se". Sem cookie, sem identificador, sem IP guardado, sem script de terceiro.
2. **Origem declarada só como contagem**: um parâmetro de campanha reconhecido (`?origem=`, de lista
   fechada) incrementa um contador e é descartado — nunca associado a sessão, identidade ou inscrição.
3. **Nada de ferramenta de marketing recebendo dado de candidato.** Conversão por campanha, se um dia
   existir, é razão de dois agregados (visitas de origem X, rascunhos no mesmo período), e não
   rastreamento individual.

Qualquer um desses passos é **decisão própria**, com avaliação de LGPD, e não cabe numa feature de
apresentação — nem precisa vir antes dela. Fica como questão para o produto (Q1 da
[priorização](priorizacao.md#5-questões-para-o-responsável-pelo-produto)).

## 8. Limites institucionais aplicados às propostas

- **Isonomia e impessoalidade:** nenhuma ordenação por perfil do visitante, nenhuma recomendação. A
  ordem continua sendo a da urgência real (prazo) ou a cronológica.
- **Sem urgência fabricada:** "Faltam N dias" e "Último dia" ficam; contagem regressiva em horas,
  "últimas vagas" ou "N pessoas vendo agora" não entram — vaga não se esgota por inscrição, e o número
  de inscritos não é público.
- **Sem promessa:** nenhum texto fala em aprovação, contratação, matrícula ou vaga garantida. As listas
  de vocabulário proibido da área do candidato (`test_acompanhamento_pela_situacao.py`,
  `test_vocabulario_da_convocacao.py`) são bom ponto de partida para estender à vitrine.
- **O Edital é a referência:** resumo na tela complementa; o botão do Edital continua presente e a
  frase "conteúdo vigente" continua ao lado dele.
- **Requisito antes da ação:** nenhuma proposta move o botão para antes do requisito no cartão da vaga
  — o que se propõe é um **atalho** até a vaga, não uma inscrição que pule a leitura.
