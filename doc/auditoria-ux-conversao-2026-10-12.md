# Auditoria de UX e conversão da jornada pública

**Data:** 2026-10-12 · **Commit:** `b4a1abf4` · **Natureza:** diagnóstica e propositiva — nada foi
implementado, nenhuma feature foi aberta, o roadmap não foi alterado.

> **Não vira escopo por estar escrito aqui.** Aprovar, recortar e ordenar é do responsável pelo
> produto. Esta auditoria para aqui e aguarda autorização antes de qualquer especificação.

> **Revisada no mesmo dia** contra o código e as specs: medições reproduzíveis com altura de tela,
> script e resultado versionados; objetivo ampliado para três tarefas (encontrar, começar,
> acompanhar); o prazo de recurso dentro do escopo mínimo; a revisão do achado da `024` sobre títulos
> repetidos explicitada; o tipo da seleção rebaixado a questão a estudar; validação separada de
> instrumentação.

| Documento | Conteúdo |
|---|---|
| [Diagnóstico](auditoria-ux-conversao-2026-10-12/diagnostico.md) | escopo, método e reprodução, estado atual, estados do domínio, pontos positivos, achados `C-01` a `C-19`, heurísticas, limitações |
| [Jornada pública](auditoria-ux-conversao-2026-10-12/jornada-publica.md) | perfis, as três tarefas, jornadas, pontos de decisão, campanhas, validação por percurso conduzido, o que já se pode contar |
| [Propostas de redesenho](auditoria-ux-conversao-2026-10-12/propostas-redesenho.md) | alternativas A e B, wireframes, cartões, microcopy, responsivo, recomendação |
| [Priorização](auditoria-ux-conversao-2026-10-12/priorizacao.md) | matriz, sequência em lotes, reaproveitamento, questões ao produto |
| [`medir-primeira-tela.js`](auditoria-ux-conversao-2026-10-12/medir-primeira-tela.js) · [`medicoes.json`](auditoria-ux-conversao-2026-10-12/medicoes.json) | o script das medidas e o resultado bruto, com navegador, commit e Edital |
| [Capturas](auditoria-ux-conversao-2026-10-12/capturas/) | primeira tela da vitrine e da seleção em 375 × 667, 1280 × 900 e 1440 × 900; acesso sem contexto |

Banco de demonstração: `ps_ux_conversao` (`make preparar` + `seed_demo`), mantido para medir o depois
nas mesmas condições. O passo a passo para reproduzir está no [diagnóstico, §3](auditoria-ux-conversao-2026-10-12/diagnostico.md#3-metodologia).

---

## Síntese

### 1. Diagnóstico

A hipótese se confirma **em parte**. A página da seleção já é orientada à decisão — título do Edital,
situação como marca, requisito antes do botão, documentos anunciados antes da identificação,
cadastro reserva como oferta, prazo honesto. **A vitrine ainda é catálogo**, sobretudo no celular, e
**o início da inscrição perde o contexto** da vaga escolhida.

A vitrine serve a **três tarefas**: encontrar uma oportunidade, começar a inscrição e acompanhar o
certame. O Perfil A (decidido) é bem atendido no desktop; o Perfil B (indeciso) tropeça na primeira
tela do celular; e quem acompanha resultado encontra a própria seleção como "Encerrada" sem mais nada
— inclusive quando há prazo de recurso correndo.

### 2. Os cinco problemas mais relevantes

1. **C-03 — acompanhar:** a encerrada não diz o que tem. O Edital 51 tem resultado preliminar e recurso
   aberto até 17/10, e o cartão diz só "Inscrições encerradas em 02/09/2026". É prazo para exercer um
   direito.
2. **C-01 — encontrar:** no celular, o formulário ocupa de 203 a 537 px e o primeiro cartão começa em
   602 px. Em telas baixas (375 × 667, 320 × 568) nenhuma oportunidade aparece antes da rolagem; em
   telas altas (até 390 × 844) aparece o título, mas o convite do cartão não, em nenhuma.
3. **C-02 — encontrar:** o título do cartão é o do Processo ("Processo Seletivo Simplificado 2026", igual
   nos três cartões); a oportunidade vem abaixo, em corpo menor — a hierarquia oposta à da seleção.
4. **C-11 — começar:** no celular, o primeiro "Inscrever-se nesta vaga" fica entre 1.223 e 1.350 px,
   fora da primeira tela em todos os celulares medidos, sem resumo de vagas nem atalho.
5. **C-12 — começar:** "Inscrever-se" leva a uma tela "Entrar" que não nomeia a vaga; a volta à vaga
   não tem destaque nem mensagem e exige o segundo clique sem explicá-lo.

### 3. O que deve ser preservado

Consulta no endereço e sem JavaScript; um link por cartão; situação por cor **e** palavra no mesmo
lugar; "Faltam N dias" arredondado para baixo e sem urgência fabricada; cadastro reserva como oferta;
documentos e teto antes da identificação; Cronograma e histórico de Retificações públicos; acesso sem
senha; **o segundo clique** — o POST que impede link compartilhado de criar inscrição
(`portal/views.py`, `_de_volta_a_vaga`); ausência nunca dita como "não informado"; nenhum dado de
navegação coletado; nenhuma rolagem lateral de 320 a 1.440 px.

### 4. Principais oportunidades

O fato datado na encerrada ("recurso até…", "Ver resultado"); oportunidade antes do filtro no celular,
com a busca visível; o Edital no título do cartão e o Processo como metadado; o lugar no cartão; atalho
para as vagas no alto da seleção; a vaga nomeada no acesso e a volta explicada; o Requerimento
anunciado antes.

### 5. Conservadora × substantiva

**A** reordena, reescreve e traz para a vitrine fatos que o sistema já sabe, sem revogar decisão — revê
um único diagnóstico registrado, o da `024` sobre títulos repetidos, sem tocar conteúdo normativo.
Complexidade baixa a média. **B** troca a lista de Editais por oportunidades agrupadas por Edital, cria
as faixas "Acompanhe" e "Anteriores", põe barra fixa no celular e assinatura institucional — e revoga
escolhas da 024 (quatro grupos, um link por cartão) e o fora de escopo de identidade da 024 e da 047.
Complexidade média a alta, dependente de decisões ainda não tomadas.

### 6. Recomendação de direção

**A, com foco na jornada:** hierarquia dos cartões, filtros recolhidos no celular com a busca acessível,
contexto durante o acesso, retorno explicado à vaga e informação acionável sobre resultados e recursos.
**Rodapé, favicon e prévia de compartilhamento entram depois**, conforme contribuição demonstrável. A
aparência administrativa vem de **hierarquia** — estrutura dominando conteúdo —, e não de falta de
enfeite. B fica para depois de A, se o percurso conduzido mostrar que A não basta.

### 7. Mudanças possíveis sem alterar o domínio

Todos os achados do escopo mínimo: texto (C-05, C-10, C-13, C-18, parte de C-12), template e CSS (C-01,
C-02, C-04, C-07, C-08, C-11, C-19), dado que já existe e não é mostrado (C-14 pelo
`requerimento_momento`, C-19 pela localidade dos Perfis e pelo registro de Unidades) e um seletor em
lote sobre leituras que já existem (C-03). Se curso, cargo e bolsa precisam de tratamento diferente é
pergunta em aberto (Q4) — o único exemplo da auditoria é do seed.

### 8. Dependências e riscos

Seletor em lote para C-03, com teste de orçamento de consultas. Releitura das decisões que seis
arquivos de teste localizam — os testes apontam compromissos, não tornam texto intocável; a spec diz o
que mantém e o que revê. Texto novo que prometa resultado — estender à vitrine o vocabulário proibido
da área do candidato. Recolher a busca junto com os filtros perderia o Perfil A. E a limitação maior:
**ninguém de fora usou a interface**, e a jornada de uma candidata nova não foi percorrida de ponta a
ponta.

### 9. Escopo mínimo para a futura feature

O [lote 1](auditoria-ux-conversao-2026-10-12/priorizacao.md#4-sequência-proposta), organizado pelas
três tarefas. **Encontrar:** busca visível e filtros recolhidos no celular; Edital no título, Processo
como metadado, vagas por Perfil, lugar; encerradas compactas. **Começar:** atalho para as vagas com
`:target`; vaga nomeada no acesso e no código; finalidade em "Seus dados"; volta explicada;
Requerimento anunciado. **Acompanhar:** o fato datado da encerrada, com "recurso até…" e "Ver
resultado". Validado por medição antes e depois no mesmo banco e por percurso conduzido com pessoas
reais — sem instrumentação.

### 10. Questões que dependem do responsável pelo produto

Nove, com opções, na [priorização](auditoria-ux-conversao-2026-10-12/priorizacao.md#5-questões-para-o-responsável-pelo-produto):
instrumentar a jornada (não bloqueia o lote 1)? · reabrir a identidade visual, e com qual manual? ·
até quando as encerradas ficam na vitrine? · curso, cargo e bolsa precisam de tratamento diferente —
a estudar em Editais reais? · destino padrão de campanha? · "vaga" como Perfil e como quantidade? ·
renomear "Entrar"? · número de vagas por modalidade na página pública? · o lote 1 é a próxima spec?
