# Roadmap consolidado — proposta de evolução (15/10/2026)

**Entregável D** da [auditoria de consolidação](../auditoria-de-consolidacao-2026-10-15.md). Base:
`main` @ `db428b30`. Este roadmap é uma **proposta**: ele não muda o escopo institucional e não
decide nada que esteja em [decisões pendentes](decisoes-pendentes.md). Onde uma etapa depende de
decisão, ela diz qual. Os IDs remetem à [matriz](matriz-pendencias.md).

## Os três princípios que ordenam a proposta

1. **O sistema não está em produção.** Por isso nenhum item é crítico para a operação de hoje. O que
   é crítico é crítico **para a implantação**, e só começa a contar quando a DEC-01 der uma data. A
   proposta separa o que avança já, sem data, do que só faz sentido com data.
2. **O backlog deriva das jornadas** (princípio VI da Constituição). Os "fora de escopo" e as dívidas
   de cada spec são insumo de priorização, e não a priorização. Por isso a consolidação funcional
   começa pelo que um candidato ou um servidor encontra num certame real, e não pelo resíduo da spec
   anterior.
3. **Validar antes de construir mais.** Nenhum dos 172 itens está **implementado e validado**. A
   próxima informação de maior valor é como pessoas de fora usam o que já existe, e não mais uma
   funcionalidade.

---

## 1. Correções críticas — os P0 para a implantação

Nenhuma é código que se possa escrever hoje sem resposta de fora. Todas começam por uma conversa.

| Item | O que destrava | Depende de | Primeiro passo | Complexidade depois da resposta |
|---|---|---|---|---|
| GO-22 Pedido de produção à TI | GO-01, GO-19, GO-23, GO-24, GO-25 | DEC-01 | Gerar o pedido a partir do §26 do guia de implantação | — |
| GO-01 Autenticação institucional (com AV-01 e ED-05) | Toda a gestão; a segregação de funções real; a trilha com autoria verdadeira | DEC-02 | Perguntar à TI as três opções | Média: a fronteira já está isolada em `interface/identidade.py` |
| GO-19 Retenção e descarte (com CA-03 e AV-02) | O recebimento de dado real (decisão de 01/09) | DEC-03 | Levar ao encarregado uma tabela de prazos por categoria | Média: comandos de expurgo e timers versionados |
| GO-25 Correio (com AS-23 e CA-16) | O acesso do candidato | DEC-05 | Checklist §25 ao setor de correio | Baixa |
| ED-04 Autoridade e assinatura (com GO-11 e GO-12) | Publicar qualquer Edital | DEC-04 | Pergunta ao Cefor, com a lista de autoridades | Baixa: muda o fecho do PDF |
| ED-03 Frases da `069` (SC-517) | O primeiro Edital real no texto novo | o usuário; jurídico para o resumo | Percorrer `specs/069-edital-linguagem-simples/equivalencia.md` | Nenhuma: é aprovação |

**Recomendação de encaminhamento:** um único "pacote de prontidão institucional", com quatro
destinatários (TI, encarregado, Cefor e correio), disparado assim que a DEC-01 der a janela. Sem a
DEC-01, registrar em `doc/` os quatro pedidos já redigidos, para que a data, quando vier, não comece do
zero.

## 2. Consolidação funcional — o que falta para as jornadas fecharem bem

### 2.1 Já, sem decisão: correções diretas (um lote)

Itens com "Precisa de decisão humana? não" que corrigem defeito observado. Cada um é pequeno, e
juntos cabem num PR de correções, no padrão dos de 27/09.

| Item | Defeito | Quem sofre |
|---|---|---|
| ED-07 | A Revisão de um Edital publicado e retificado mostra a norma do dia da publicação | Equipe de seleção, presidência, homologador |
| ED-18 | Gravar a etapa Perfis apaga a descrição da Modalidade: o formulário lê `description` (`interface/forms.py:116`), mas `_modalidade.html` não desenha o campo | Elaborador (perda de dado) |
| ED-13 | `advertencias_do_ato` filtra impeditivos só pelo código (issue #117, aberta desde 15/09) | Publicador |
| PV-03 / PV-04 | Duas telas transbordam a 375 px: a verificação do sorteio e o detalhe do Edital | Cidadão no celular; equipe |
| PV-05 (a) | Linha "Protocolo" vazia no Requerimento | Candidato |
| GO-42 (com CA-36 e AS-21) | Contradições de documentação ainda não tratadas, em especial as do guia de implantação, depois do merge do #283 | Quem implanta |

### 2.2 Specs curtas que só dependem de uma decisão de produto

Na ordem do impacto sobre a jornada:

1. **O "Edital completo" depois de Retificação** (ED-06, com CA-08 e AS-05) e **as Retificações
   homônimas** (PV-05 b). Depende da DEC-06; a recomendação é a opção A, que só muda leitura.
2. **O texto do reenvio da convocação** (CA-23, com AV-24). Depende só da redação, em Bloco 3.
3. **Reabilitado por recurso antes do marco** (AV-04). Depende da DEC-08.
4. **Retificação de documento exigido** (ED-08). Depende da DEC-07.
5. **Sessão e saída** (GO-03, com CA-28): `flush()` nos dois "Sair", validade explícita e limpeza
   agendada. Depende só da validade escolhida.
6. **Proteções baratas de privacidade** (CA-06 e CA-05): `noindex` na publicação nominal e trava de
   inicialização para os avisos em produção. Não esperam o mérito da DEC-03.

### 2.3 Validação com pessoas (DEC-14)

Uma semana de validação, com o banco de demonstração do `seed_demo`:

- teste operacional da elaboração e da condução (GO-31, com ED-01 e AV-08);
- cinco pessoas na jornada pública e na jornada completa do candidato (CA-01 e CA-15);
- leitor de tela e ASES (CA-14);
- sorteio com a comissão e reprodução externa (AV-07);
- revisão do setor das respostas da `070` (AS-01);
- aprovação das frases da `069` (ED-03).

**Saída esperada:** uma lista de achados de uso real. É ela, e não esta matriz, que deve ordenar a
seção 4.

## 3. Melhorias operacionais

| Item | O que é | Depende de | Valor |
|---|---|---|---|
| GO-23 | Empacotamento de produção: extra `prod` no lock (servidor de aplicação), `STATIC_ROOT`, units e timers versionados | GO-22 | Implantação reproduzível |
| GO-24 | Ensaio do guia numa VM descartável, com restauração | VM disponível | Primeira implantação sem surpresa |
| GO-29 (com AV-32 e AS-25) | Base de CEP: timer mensal versionado; o runbook contradiz o `Makefile` (`--se-mudou`) | — | Requerimento com endereço reconhecido |
| AS-24 (com AV-27 e GO-33) | E2E da fonte do sorteio rodado antes de cada sorteio real, ou agendado | decisão de regularidade | Sorteio do piloto não falhar no dia |
| AV-11 | Exportação de inscritos e resultados em planilha; hoje só existe a de matrículas | — | Elimina redigitação nas rotinas que ainda vivem em planilha |
| AV-09 (com AS-26) | Conversa com o Registro Acadêmico e primeira importação real | agenda do RA | O arquivo de matrículas realmente importa |
| CA-17 (com AS-27) | Procedimento de atendimento: correção de CPF, perda de acesso, canal | DEC-03, DEC-05 | O primeiro certame sem improviso no balcão |
| GO-17 (com CA-27) | Lacunas da trilha: login do candidato, download do próprio documento, exportação de matrículas, eventos de credencial sem escopo | — | Investigação de incidente |
| GO-45 | Documentos de operação institucional ausentes: resposta a incidente com dado pessoal, concessão de papéis, contingência do certame | GO-05, DEC-03 | Operação defensável |
| GO-30 | Medir o SLO de carga com o harness que já existe (`backend/scripts/carga_publica.py`) | ambiente | Saber o teto antes do último dia de inscrição |

## 4. Refinamentos de UX/UI

Ordená-los antes da semana de validação seria adivinhar. Ficam listados para que nada se perca, e a
ordem vem do que a validação mostrar.

- **Candidato:**
  - PV-01, a data de nascimento pedida duas vezes;
  - PV-02, o comprovante em linguagem técnica;
  - CA-11, a legibilidade do resultado público;
  - CA-09, o texto do Edital só no PDF (junto com a DEC-10);
  - CA-24 e CA-12, resíduos da `072`.
- **Gestão:**
  - AV-31, as telas da condução que nunca passaram por auditoria de UX;
  - ED-17, mensagens que se contradizem na composição;
  - ED-20, o aviso que soterra o impeditivo na Revisão;
  - AV-14, a reavaliação por recurso sem orientação na tela;
  - AV-18, a prévia da divulgação;
  - AV-40 e AV-46, identificar a inscrição e filtrar por Perfil;
  - GO-08, remoção em cascata num clique.
- **Mesa:** AV-41, zoom e rotação. O painel lateral e a aba própria existem desde 07/10 (#258), com o
  visualizador do navegador. Falta medir com avaliador real antes de decidir se precisa de mais.

## 5. Evoluções futuras

Nenhuma destas deve entrar antes das seções 1 a 3, e várias dependem de decisão.

| Item | Natureza | Decisão necessária |
|---|---|---|
| ED-10 (com AV-05 e AV-35): barema estruturado, heteroidentificação, cascata de grupos, submodalidades | Famílias normativas | DEC-09 |
| ED-09 (com AV-13): alcance da Etapa por Perfil | Modelo normativo | DEC-09 |
| CA-19: nome social | Direito do candidato | DEC-11 (pode subir para correção crítica) |
| ED-11: ato oficial acessível em HTML | Acessibilidade | DEC-10 |
| AS-15, AS-13, AS-14, AS-16 e GO-46: o assistente aberto ao candidato (Fase C, `074`) | Assistente | Critérios de aceite do piloto (AS-08, DP-3), L4 (AS-07) e Bloco 1 inteiro |
| ED-35 e ED-36: validade, prorrogação, vagas remanescentes, taxa e isenção | Famílias de Edital | Demanda de Edital real |
| AV-38: segunda instância recursal | Recursos | Institucional |
| CA-35: reaproveitamento de documentos entre inscrições | Candidato | — |
| ED-44: Libras | **Estudo documental**, nada implementado nem aprovado | Se e quando fazer um experimento com profissionais de Libras e participantes surdos |
| Ifes Ads e captação de interessados | **Exploratório**: excluído do escopo do assistente em 12/10 | Nenhuma agora |

## Ondas sugeridas

| Onda | Quando | Conteúdo | Sai quando |
|---|---|---|---|
| **0 — Decidir e proteger** | Agora, sem código | DEC-01; Bloco 3 das decisões (chave OpenRouter, commit da `074`, vídeos, #283); pacotes institucionais redigidos | Há data, ou a decisão explícita de não ter |
| **1 — Corrigir o que se viu** | Em paralelo à onda 0 | Lote de correções diretas (2.1); DEC-06 a DEC-08 e as specs curtas (2.2) | Lote mergeado e specs curtas entregues |
| **2 — Validar com pessoas** | Assim que houver participantes | Semana de validação (2.3) | Relatório de uso real registrado em `doc/` |
| **3 — Preparar a implantação** | Com as respostas institucionais | GO-01, GO-19, GO-25, ED-04, GO-23, GO-24, CA-17, GO-45 | Ensaio em VM aprovado e primeiro usuário real autenticado |
| **4 — Evoluir** | Depois do piloto, ou do piloto-sombra | Seção 4 ordenada pela validação; seção 5 por decisão | — |

## Conflitos que precisam de aprovação

Pontos em que esta proposta contraria, ou reabre, algo já escrito. Nenhum é aplicado sem aprovação.

1. **Manual.** A arquitetura de 08/09 diz "não reduzir escopo por parecer grande". Esta proposta
   recomenda adiar a produção do manual até o piloto (DEC-13). Não reduz o escopo do manual; muda o
   momento e a base.
2. **Prioridade da Retificação de documento exigido.** Em 03/09 o usuário a chamou de P0; a matriz a
   põe em P1, porque o sistema não está implantado (ED-08). Se a régua for a de 03/09, ela sobe para a
   onda 1.
3. **O teste operacional deixou de ser porta** das specs 049–051 em 28/09, por urgência. Esta
   proposta o põe de volta como condição para a onda 4 (DEC-14).
4. **D-G2 (403 × 404).** Decidida em 28/09 para entrar "junto com a preparação para produção". Fica
   na onda 3, como decidido; não é proposta de mudança.
5. **Ordem das specs depois da `074`.** As sessões recentes vinham emendando o assistente (`070` a
   `074`). Esta proposta põe o assistente na seção 5 até haver critério de aceite do piloto, e
   prioriza o que um certame real encontra primeiro.

## A próxima etapa de desenvolvimento

**O lote de correções diretas (2.1) e a spec curta do Edital vigente (DEC-06, opção A)**, enquanto a
onda 0 corre fora do código. São as únicas frentes que melhoram jornada real sem esperar ninguém, e
nenhuma cria superfície nova que precise de validação própria.
