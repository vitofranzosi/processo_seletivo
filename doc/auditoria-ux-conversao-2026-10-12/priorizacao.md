# Priorização — o que fazer primeiro, o que depende de decisão

**Data:** 2026-10-12 · Parte da [auditoria de UX e conversão](../auditoria-ux-conversao-2026-10-12.md).
Evidência de cada item no [diagnóstico](diagnostico.md); desenho nas [propostas](propostas-redesenho.md).

> **Nenhuma linha aqui é escopo aprovado.** A sequência proposta é recomendação; o roadmap não foi
> alterado.

> **Revisão de 12/10/2026.** A primeira versão punha o fato da encerrada (C-03) num lote posterior e
> rodapé e favicon no escopo mínimo — e a síntese prometia resolver os cinco problemas principais com
> um escopo que deixava um deles de fora. Esta versão inverte: o prazo para exercer um direito entra
> no escopo mínimo, e a assinatura visual vai para depois, conforme contribuição demonstrável.

---

## 1. Matriz de problemas

**Severidade:** Crítico (impede a tarefa) · Alto (a tarefa acontece com perda provável de quem não
insiste, ou um direito pode deixar de ser exercido) · Médio (atrito ou dúvida) · Baixo (acabamento).
Não há Crítico: nenhuma tarefa ficou impossível.

**Tarefa:** E = encontrar · I = começar a inscrição · A = acompanhar o certame.

**Tipo:** T = só texto · TC = template/CSS · CE = componente existente · CI = comportamento de
interface · NF = nova funcionalidade · AD = alteração de domínio.

| ID | Problema | Sev. | Tarefa | Dimensão | Compl. | Tipo | Impacto esperado (hipótese, a validar) |
|---|---|---|---|---|---|---|---|
| C-03 | Encerrada não diz resultado, recurso, sorteio | Alto | A | Compreensão | Média | CE + seletor em lote | quem acompanha acha resultado e prazo de recurso pela vitrine |
| C-01 | No celular, formulário antes da oportunidade; convite fora da 1ª tela | Alto | E | Descoberta | Baixa | TC | mais visitantes chegam a ver um cartão |
| C-02 | Cartão titulado pelo Processo; oportunidade em 2º plano | Alto | E | Compreensão | Baixa | TC | cartões distinguíveis sem leitura |
| C-11 | Ação a ~1,9 tela no celular, sem resumo de vagas | Alto | I | Conversão | Baixa | TC | menos desistência entre abrir a seleção e achar a vaga |
| C-12 | Identificação sem contexto; volta sem destaque nem mensagem | Alto | I | Conversão | Baixa | T + TC + CI | menos abandono entre código e rascunho |
| C-14 | Requerimento exigido na inscrição não anunciado antes | Médio | I | Decisão | Baixa | TC (dado existe) | menos surpresa dentro do rascunho |
| C-04 | Filtros desproporcionais ao catálogo | Médio | E | Descoberta | Baixa | TC | (resolvido junto com C-01) |
| C-19 | Código interno no lugar do "onde" | Médio | E | Decisão | Baixa | TC (dado existe) | "é perto de mim?" respondido no cartão |
| C-07 | Grupos sem hierarquia; encerradas com o peso das abertas | Médio | E, A | Consistência visual | Baixa | TC | abertas em destaque sem esconder o resto |
| C-10 | "Voltar aos resultados" a quem não buscou | Médio | E | Navegação | Baixa | T | menos estranhamento de quem chega por link direto |
| C-13 | CPF pedido sem finalidade nem contexto | Médio | I | Decisão | Baixa | T | mais confiança no ponto da coleta |
| C-15 | Sem rodapé, atendimento, favicon, assinatura; fonte não carregada | Baixo · Médio (atendimento) | — | Consistência visual | Baixa (rodapé) · Alta (identidade) | TC · decisão | não demonstrado |
| C-16 | Sem prévia de compartilhamento | Baixo | E | Descoberta | Baixa | TC | não demonstrado; relevante se houver campanha |
| C-05 | `<title>` × `h1` × subtítulo desalinhados | Baixo | E | Compreensão | Baixa | T | — |
| C-08 | Linha de Perfis sem teto; soma de vagas entre Perfis | Baixo | E | Compreensão | Baixa | TC | — |
| C-17 | Contorno de campo 1,48:1 (1.4.11, a confirmar) | Baixo | — | Acessibilidade | Baixa | TC (token compartilhado) | — |
| C-18 | Estado vazio repetido e sem caminho | Baixo | E | Navegação | Baixa | T | — |
| C-09 | Rótulos de trabalho num Perfil de curso, no exemplo do seed | a avaliar | E | Compreensão | a avaliar | estudo antes | — |

## 2. Alto impacto, baixo custo

```
            impacto esperado
               alto │ C-01  C-02  C-11  C-12   │  C-03
                    │ C-14  C-19                │
             médio  │ C-10  C-13  C-07  C-04    │
                    │                           │
             baixo  │ C-05  C-08  C-17  C-18    │  C-15 (identidade)
                    │ C-15 (rodapé)  C-16       │  C-09 (a estudar)
                    └───────────────────────────┴──────────────────────
                         baixa complexidade        média / alta
```

O escopo mínimo (§4, lote 1) é o quadrante de cima à esquerda **mais C-03**: é o único item de
complexidade média que entra, porque protege o exercício de um direito.

## 3. Reaproveitamento

| Peça existente | Serve a |
|---|---|
| `historico_publico_do_edital`, `janela_da_publicacao_divulgada`, `sorteios_do_edital` | C-03 — as mesmas leituras da página, feitas em lote |
| `_consulta.html` e a regra `.consulta` | C-01, C-04 — o formulário fica, muda o invólucro (`<details>`) |
| `_cartao_da_selecao.html`, `_selecao_da_vitrine` | C-02, C-08, C-19 — os dados já estão no dicionário do cartão, salvo localidades |
| `id="vaga-<perfil>"` e `_de_volta_a_vaga` | C-11, C-12 — a âncora já existe e já é o destino da volta |
| `_rota_do_destino` | C-12 — já resolve a vaga do destino |
| `_mensagens.html` | C-12 — a mensagem da volta |
| `Edital.requerimento_momento` | C-14 |
| `unidades.json` (`sigla`, `nome`, `local`) | C-19, título da vitrine |
| `PORTAL_ATENDIMENTO`, `_atendimento.html` | C-15 — rodapé, quando vier |
| Listas de vocabulário proibido da área do candidato | estender à vitrine, para que texto novo não prometa |

## 4. Sequência proposta

### Lote 1 — escopo mínimo: a jornada nas três tarefas

| Tarefa | Itens |
|---|---|
| Encontrar | C-01 e C-04 (busca visível, demais filtros recolhidos no celular), C-02 (Edital no título, Processo como metadado), C-19 (lugar), C-08, C-07 |
| Começar | C-11 (atalho para as vagas, `:target`), C-12 (contexto no acesso e no código, volta explicada), C-13, C-14 |
| Acompanhar | **C-03** (fato datado na encerrada, "recurso até…", convite "Ver resultado") |
| Texto que acompanha | C-05, C-10, C-18 |

**Dependências:**
- **seletor em lote para C-03**, com teste de orçamento de consultas — a vitrine faz hoje duas
  consultas para todos os cartões e não pode passar a fazer uma por cartão;
- **releitura das decisões que os testes localizam** — `test_vitrine.py`, `test_detalhe_selecao.py`,
  `test_consulta_da_vitrine.py`, `test_acessibilidade_do_portal.py`, `test_porta_de_entrada.py`,
  `test_peso_da_vitrine.py`. Cada asserção aponta uma decisão da 009, 024, 047 ou 062; a spec diz qual
  mantém e qual revê — entre elas, **o achado da `024` sobre títulos repetidos** (linha 539), que esta
  auditoria revisa (diagnóstico, C-02);
- **o texto de "Seus dados"** validado com quem responde por LGPD;
- **medição antes e depois** com [`medir-primeira-tela.js`](medir-primeira-tela.js) no mesmo banco, e
  **percurso conduzido com pessoas reais** ([jornada](jornada-publica.md), §7.1) antes e depois.

### Lote 2 — conforme contribuição demonstrável

C-15 (rodapé com atendimento, favicon), C-16 (prévia de compartilhamento), C-17 (contorno de campo —
token compartilhado com a gestão, exige olhar as duas bases). Entram quando houver motivo concreto: o
rodapé, se o percurso conduzido mostrar gente travada sem saber a quem recorrer; a prévia, quando
houver campanha.

### Lote 3 — só com decisão do produto

Identidade visual completa, tipo da seleção (depois do estudo de Q4), instrumentação (Q1),
alternativa B, endereço legível, página de Processo, aviso de novas seleções.

## 5. Questões para o responsável pelo produto

| # | Questão | Por que importa | Opções |
|---|---|---|---|
| Q1 | **Instrumentar a jornada pública?** | A 024 vedou naquele incremento (D-008, SC-047) e pediu decisão própria. **Não bloqueia o lote 1**, que se valida por percurso conduzido. Contar rascunhos e envios não mede conversão | (a) não; validar só por percurso; (b) relatório agregado dos registros que já existem (conclusão do iniciado); (c) + contadores agregados no servidor, sem cookie nem identificador; (d) + origem declarada como contagem. De (b) em diante, avaliação de LGPD |
| Q2 | **Reabrir a identidade visual?** | Fora de escopo na 024 e na 047; a 060 deixou a marca pendente; não há manual no repositório | (a) só rodapé, favicon, fonte carregada; (b) assinatura do Ifes conforme manual a fornecer; (c) adotar um design system público (gov.br DS) |
| Q3 | **Encerradas na vitrine principal: até quando?** | Hoje ficam para sempre; com o tempo empurram as abertas para baixo | (a) como hoje; (b) "Anteriores" recolhido após N dias do último ato; (c) página de arquivo |
| Q4 | **Curso, cargo e bolsa precisam de tratamento diferente?** | O único exemplo é do seed. Não está provado que haja diferença de rótulo, de campo ou de comportamento | Estudar Editais reais de cada tipo (a amostra local tem vários) e listar as diferenças de **comportamento** — só então decidir entre nada, rótulo condicional ou dado novo |
| Q5 | **Destino padrão de campanha** | Define o que precisa ficar estável | (a) página da seleção; (b) âncora da vaga; (c) vitrine filtrada; (d) endereço legível novo |
| Q6 | **"Vaga" nomeia o Perfil e a quantidade** | "2 vagas" pode ser dois Perfis ou duas vagas | (a) manter "vaga" para o Perfil e dizer a quantidade sempre por extenso; (b) outro termo para o Perfil na tela pública |
| Q7 | **Renomear "Entrar" no topo?** | A 024 manteve por decisão; para quem nunca se inscreveu, "Entrar" sugere conta | (a) manter; (b) "Minhas inscrições" também sem sessão, levando ao acesso |
| Q8 | **Vagas por modalidade com número na página pública** | Pendente desde 13/09; afeta quem concorre por cota | (a) com o lote 1; (b) depois |
| Q9 | **Lote 1 como a próxima spec?** | Recomendação desta auditoria | (a) sim; (b) reduzir; (c) B direto |

## 6. Ganhos esperados e riscos

**Ganhos esperados — hipóteses, nenhuma medida:** mais visitantes do celular chegam a um cartão;
menos aberturas de seleção que não servem; menos desistência entre a página e a vaga e entre o código
e o rascunho; menos surpresa dentro do rascunho; quem acompanha acha resultado e prazo de recurso pela
vitrine. O percurso conduzido verifica compreensão e conclusão de tarefa; aumento de conversão, só com
Q1 — e, mesmo então, como razão de agregados.

**Riscos:**

- **Reabrir defeito já corrigido** ao mudar texto sem reler a decisão que o originou — o "Voltar aos
  resultados" nasceu da FR-144; o "Inscrever-se exige identificação por e-mail", da FR-137.
- **Orçamento de consultas** em C-03.
- **Texto que promete** — o vocabulário novo passa pelo mesmo crivo da área do candidato.
- **Perda do Perfil A** se a busca for recolhida junto com os filtros — a busca fica visível.
- **Conclusão sem gente de fora** — sem o percurso conduzido, o efeito continua hipótese.
