# Auditoria Exploratória End-to-End

> **Situação em 02/09/2026, depois desta auditoria.** O pacote A da §14 foi executado nos commits
> seguintes a este documento. Estão **corrigidos**: E2E-001 e E2E-002 (a devolução, no Edital e na
> Retificação), E2E-003 (paginação, busca, filtros e contadores na lista de inscrições), E2E-006
> (o rascunho local que se contradizia), E2E-007 (o resumo de congelamento incompleto) e E2E-015
> (a matriz de recusa dos POSTs da 012). Todo o restante do inventário permanece como registrado.
>
> Um achado novo surgiu ao corrigir a devolução, e está no fim da §10 como **E2E-021**.
>
> **Situação em 04/09/2026.** **E2E-021 está implementado** — `CANCELAVEL` estreitou para a
> elaboração, `retificacao:cancelar` passou a pertencer ao Gestor, e o ato ficou alcançável. A
> implementação foi maior do que esta auditoria previu: ver a nota ao fim da seção do achado.
>
> **E2E-004 está implementado na metade da edição.** A tela de Retificação passou a alcançar
> `documentRequirements`: os campos publicados de cada Documento Exigido são editáveis, e a
> aplicabilidade é escolhida entre Perfis e Modalidades do conteúdo. **Acrescentar e remover
> continuam fora**, por decisão registrada na seção do achado — não por incompletude.

**Data:** 02/09/2026 · **Base:** `main` em `ec67d52` (012 — Mesa de Avaliação fechada) · **Método:** leitura do código, das 12 specs e da suíte (~1.891 testes) + percurso completo no navegador com sete identidades distintas (gestor, elaboradora, homologador, publicadora, dois candidatos, presidente, dois avaliadores), num banco novo (`ps_audit_e2e`), do `Novo Processo Seletivo` até avaliações concluídas na Mesa — mais uma Retificação publicada com o aviso de versão conferido na área do candidato.

Convenções deste relatório: **[FATO]** = observado no navegador ou no código citado; **[INFERÊNCIA]** = conclusão derivada; **[RECOMENDAÇÃO]** = sugestão. Ressalva de método: os três documentos exigidos do Edital de teste ficaram `required=false` por falha da automação do percurso (cliques em coordenadas obsoletas), não do sistema — a obrigatoriedade de documento não foi exercitada no navegador (a suíte a cobre em `tests/integration/inscricoes/test_submissao.py`).

---

## 1. Executive summary

O produto é **coerente e surpreendentemente operável de ponta a ponta**: criei Processo e Edital, elaborei Perfis/Cronograma/Etapas/documentos, submeti, homologuei, publiquei, me inscrevi como dois candidatos (com código por e-mail, upload e comprovante), constituí comissão, aloquei, distribuí 120 atribuições entre dois avaliadores com proposta automática equilibrada, avaliei e concluí — tudo pela interface, sem shell, sem Drive e sem planilha. As jornadas mais fortes são **candidato** (enxuta, mobile ok, zero redigitação, aviso de versão após Retificação) e **presidente/avaliador** (a distribuição da 012 é a tela mais madura do sistema; o loop concluir→próxima pendente é excelente).

Os maiores riscos não estão onde o sistema é novo, mas onde ele é antigo: (1) **um Edital submetido não tem caminho de volta** — erro visto na revisão obriga a cancelar (queimando o número) ou publicar o erro e retificar; a devolução de Retificação existe no domínio e na API, mas não tem botão; (2) a **lista administrativa de inscrições não pagina nem filtra** — com 60 já é longa, com 1.500 é a primeira planilha paralela; (3) a **Retificação pela UI não alcança** documentos exigidos nem os campos da 012 — um documento exigido publicado errado só se corrige por API.

Nada disso torna imprudente especificar a 013 — a fronteira (avaliações → Resultado da Etapa) está de pé e os nove itens do gate da 012 estão demonstrados. Recomendo, porém, **um pacote pequeno de correções antes** (seção 14), porque os três itens acima atingem a primeira seleção real independentemente da 013.

## 2. Mapa atual da jornada

```
CONFIGURAÇÃO
  Gestor          → cria Processo + 1º Edital ................. (001/002)
  Elaborador      → compõe em 7 passos, prévia, submete ....... (006/007)
  Homologador     → homologa com fundamento ................... (001/002)
  Publicador      → publica com autoridade signatária ......... (007/008)
        │  (handoff por contador na home + "Aguardando quem…" no detalhe)
PUBLICAÇÃO → vitrine pública imediata, PDF institucional ...... (008/009)
        │  (handoff automático: Edital publicado aparece em /selecoes/)
CANDIDATO
  entra sem senha (e-mail+código) → nome/CPF uma vez
  → tela única (modalidade decide documentos) → revisão
  → protocolo + comprovante → acompanhamento com aviso de versão (009/010)
        │  (handoff: inscrições aparecem em "Inscrições recebidas")
COMISSÃO
  Gestor          → constitui comissão (um a um ou em lote) ... (011)
  Presidente      → aloca por Etapa, matriz com contadores .... (011)
  Presidente      → distribui inscrições (proposta equilibrada) (012)
        │  (handoff: alocação vira "Minhas Etapas" do membro)
AVALIAÇÃO
  Avaliador       → Mesa → documentos embutidos → nota/parecer
                  → concluir → cai na próxima pendente ........ (012)
        │  (fronteira atual: avaliações concluídas, sem consequência)
[013 — consolidação → Resultado da Etapa: NÃO EXISTE]
```

Transições sem sinal ativo (dependem de combinação informal): elaborador→homologador→publicador (só contadores), publicação→constituição da comissão (nenhum CTA), etapa concluída→presidente (precisa ir olhar). Registrado, não é pedido de notificação (E2E-016).

## 3. Jornada do elaborador/publicador

**Caminho observado** (3 identidades, ~12 telas): Home → Novo Processo Seletivo (1 tela cria Processo+Edital) → Edital → Compor (Identificação → Perfis → Cronograma → Etapas → Inscrição → Conteúdo → Revisão) → Prévia → Submeter → [troca p/ homologador] Home → Homologar → [troca p/ publicador] Home → Publicar (autoridade signatária) → vitrine no ar.

**Pontos fortes [FATO]:**
- Stepper com estado derivado dos dados (concluída/pendente), não de cliques; título/descrição pré-preenchidos; datas do Evento nunca redigitadas ("nada é digitado duas vezes" — e é verdade).
- Validação viva com `IMPEDE`/`AVISO` **antes** do POST; a página do ato lista os impedimentos e não oferece o botão quando impedida — não existe "recusa só depois do POST" neste fluxo.
- Cada ato tem página de consequências ("O que este ato provoca", "Este ato não pode ser desfeito") + "Aguardando quem homologa/publica" no detalhe; "Quem atuou" com autoria e instantes.
- Aviso honesto quando nenhum Evento é período de inscrições: "será publicado, mas não receberá inscrições pelo sistema".

**Achados:** E2E-001 (sem devolução — o mais grave da jornada), E2E-006 (banner de rascunho local contraditório, reproduzido 3×), E2E-007 (resumo de congelamento omite os campos da 012), E2E-010 (decimais canônicos `20.0000%`/`1.0000` na Revisão), G17 (texto institucional genérico aceito por omissão — "revise antes de submeter" é o único guarda).

## 4. Jornada do candidato

**Descoberta [FATO]:** vitrine pública limpa, com prazo, contagem regressiva ("Faltam 10 dias"), vagas e CTA único; detalhe da seleção com requisitos, "N documentos que serão pedidos", PDF do Edital e `Inscrever-se nesta vaga`. Em 375 px, impecável.

**Inscrição [FATO]** (~8 telas do primeiro clique ao protocolo): Inscrever → e-mail → código de 6 dígitos → nome+CPF ("Pedimos uma única vez") → **o convite sobrevive ao login** ("Você pode continuar a inscrição que começou") → tela única com dados herdados, telefone opcional, modalidade que **decide e recarrega** os documentos ("Escolha guardada"), upload por requisito com substituir/remover → revisão com Editar por bloco + 2 declarações → protocolo + comprovante. Nenhum campo digitado duas vezes; "você pode sair e voltar quantas vezes precisar" é verdadeiro (rascunho de servidor).

**Retorno/acompanhamento [FATO]:** Minhas inscrições → Acompanhar separa "Sua participação" do "Cronograma do processo"; após a Retificação publicada, apareceu **"Este Edital foi atualizado após sua inscrição. Sua inscrição continua valendo sob a versão que você aceitou"** com link ao vigente. Vitrine para o inscrito vira "✓ Inscrição enviada · Ver comprovante".

**Risco de abandono [INFERÊNCIA]:** baixo por desenho. Os riscos reais de conversão são de infraestrutura e não de tela: entrega do código por e-mail é ponto único de falha (spam/atraso; reenvio só após 60 s) — E2E-020/G1; upload grande em rede lenta segue **não verificado** (como já registrava a 009). Polimentos: comprovante denso de SHA-256 e instruções `shasum`/`certutil` (E2E-011), "3 documentos" contando o de outra modalidade (E2E-012).

**Privacidade [FATO]:** candidato B recebeu 404 indistinguível na inscrição, no arquivo e no comprovante de A.

## 5. Jornada do presidente da comissão

**Caminho [FATO]:** o seletor de identidades (dev) lista "quem tem trabalho de comissão"; a presidente entra e **aterrissa em Minhas Etapas** com "Gerir comissão" e "Alocação por Etapa" e a explicação de que presidir não atribui avaliação. Constituição (pelo gestor ou por ela): formulário individual com **conferência antes de gravar** e aviso duro de que o identificador não é verificado; inclusão **em lote** colada "de uma portaria, de uma planilha", conferida inteira. Alocação: matriz pessoa×Etapa com contadores de lacuna ("1 Etapa sem ninguém", "1 de 3 sem nenhuma Etapa"), busca, atalhos Todos/Nenhum.

**Estado operacional [FATO]:** a tela de distribuição responde "quem falta" sem planilha: `60 sem nenhum avaliador / sem avaliador suficiente / com avaliação pendente`, carga por avaliador (atribuídas/concluídas), **proposta automática equilibrada com prévia** ("120 atribuições… nada foi gravado ainda" → "Ana +60, Breno +60"), atribuição manual paginada com filtros de cobertura, Impedimentos, Trilha e Conclusões preservadas (com reabertura por motivo).

**Achados:** E2E-009 (impedimento/filtragem digitando protocolo exato), E2E-019/E2E-010 (UUID de versão e caminhos técnicos em telas administrativas), E2E-017 (novas inscrições após uma distribuição exigem voltar e redistribuir — os contadores denunciam, mas ninguém avisa), E2E-013 (nada, após a publicação, diz "constitua a comissão").

## 6. Jornada do avaliador

**[FATO]:** Minhas Etapas mostra o cartão com "60 pendentes · 0% · 0 de 60 concluídas". A Mesa tem contadores (total/não iniciadas/rascunho/concluídas) e lista paginada (25). A inscrição aberta traz candidato (CPF mascarado), documentos **embutidos ao lado do formulário** (iframe da mesma origem — sem download, sem pasta local), com "N de 3 abertos por você" e cursor posicionado; pontuação com máxima/mínima publicadas **no lugar da decisão**; parecer com a explicação de para que serve; aviso não-bloqueante de registro fora do período. **Concluir leva direto à próxima pendente** com confirmação do que acabou de acontecer.

**Throughput [INFERÊNCIA]:** ~3–4 interações por candidato sem retorno manual à fila — ×500 candidatos, é o desenho certo. A recusa de conclusão com nota abaixo da mínima sem parecer é imediata e ensina o porquê **[FATO]**.

**Achados:** E2E-008 — a lista da Mesa só mostra protocolo+situação (sem nome) e os contadores não filtram; com 500, achar "as 3 em rascunho" é paginação manual. Etapa não alocada → 404 **[FATO]**.

## 7. Handoffs entre atores

| De | Para | Gatilho | O sistema deixa claro? | Lacuna |
|---|---|---|---|---|
| Gestor | Elaborador | Processo+Edital criados | Parcial — elaborador vê "Elaborar o Edital" na home | Nenhum sinal ativo; elaborador sem `processo:criar` não é informado de quem pode criar |
| Elaborador | Homologador | Submissão | Sim — "Aguardando quem homologa" + contador "Em revisão" + ação na home | Sem notificação; descoberta por varredura |
| Homologador | Elaborador | Discordância | **Não** — não existe devolução de Edital (E2E-001); a de Retificação existe só na API (E2E-002) | Beco: o texto da UI promete "devolvida ou homologada" |
| Homologador | Publicador | Homologação | Sim — "Aguardando quem publica" | Sem notificação |
| Publicador | Candidato | Publicação | Sim — vitrine imediata, sem ato extra | Pós-publicação sem link "ver na vitrine" |
| Publicador | Gestor/Presidente | Publicação | **Não** — nada sugere constituir comissão (E2E-013) | Combinação informal obrigatória |
| Gestor | Presidente | Designação | Sim — aviso "comissão ainda não tem presidente" bloqueando alocação com explicação | — |
| Presidente | Avaliador | Distribuição | Sim — Minhas Etapas + contadores | Sem notificação |
| Avaliador | Presidente | Conclusões | Parcial — contadores na distribuição | Nenhum sinal "Etapa completa"; presidente precisa ir olhar |
| Candidato | Comissão | Novas inscrições pós-distribuição | Parcial — contadores de cobertura sobem | Ninguém é avisado (E2E-017) |

## 8. Autorização, privacidade e auditoria

**[FATO] observado no navegador:** IDOR de candidato bloqueado com 404 indistinguível em três canais; avaliador em Etapa vizinha → 404; capacidades derivadas de papel/vínculo governam cada botão ("O que posso fazer"). **[FATO] da suíte:** 117 testes de autorização com a regra 403 (permissão sistêmica ausente) vs 404 (objeto/vínculo/escopo) documentada e verificada por "recusa indistinguível da inexistente".

**Lacunas de teste** (da análise da suíte, não observadas como falhas): nenhuma rota de **escrita** da avaliação (`mesa-avaliacao-gravar/concluir`) é exercitada por ator não autorizado via HTTP; `distribuicao-remover` e `impedimentos` sem testes de recusa; bloco `compor`/`retificar`/`previa-documento` quase sem matriz de recusa por escopo/objeto; `fragmento-retificacao-perfil/evento` com **zero** referências na suíte; sem rate-limit no canal institucional (E2E-015).

**Privacidade/LGPD:** CPF mascarado nas telas da equipe; abertura de documento registrada sob a Atribuição que a autorizou (além do que a spec pedia — G23); trilha não guarda nome de arquivo do candidato. Pendências conhecidas seguem: retenção/descarte (G2), rascunhos com dados pessoais visíveis à gestão (G22), provedor de identidade real (G3/G1 — o seletor permite a qualquer um marcar Gestor, por desenho, e produção recusa subir assim).

**Auditoria como resposta:** a trilha do Edital responde quem criou/alterou/submeteu/homologou/publicou, com fundamento e transições, em linguagem humana **[FATO]**. O inverso (auditoria demais na UX): comprovante do candidato com hashes e instruções de terminal (E2E-011), UUID de versão em Conclusões preservadas, caminho `/profiles/id=…` no detalhe da Retificação (E2E-019) — integridade competindo com a tarefa em três lugares, todos remediáveis por progressive disclosure.

## 9. Escala e eficiência operacional

Com 60 inscrições **[FATO]**: distribuição e Mesa paginadas (25/página) com contadores — operáveis em 1.500 (a suíte de performance cobre 500 atribuições com custo constante). O gargalo é **`Inscrições recebidas`: 60 linhas numa página só, sem paginação, busca, filtro ou contadores por Perfil/modalidade** (verificado no DOM: 60 `<tr>`, zero paginação) — em 1.500, o operador que precisar de "quantos por modalidade" ou "quem falta documento X" abre o Excel no primeiro dia (E2E-003). O aviso "⚠ CPF repetido neste Perfil" apareceu sozinho no meu seed — bom sinal de integridade.

Onde o incentivo a Drive/planilha ainda mora: (1) essa lista; (2) conferência documental em massa (sem visão "documentos por requisito através de candidatos" — aceitável, a Mesa é por inscrição); (3) qualquer consolidação de notas — **fronteira da 013, correta**. Exportação continua deliberadamente ausente; nada aqui a justifica como default.

## 10. Inventário completo de achados

| ID | Sev. | Natureza | Ator | Tela/fluxo | Problema | Impacto | Evidência | Recomendação | Quando |
|---|---|---|---|---|---|---|---|---|---|
| E2E-001 | **ALTO ATRITO** | FLUXO/MODELO | Elab./Homol. | Edital em revisão | Não existe transição de volta à elaboração; erro visto na revisão → cancelar (queima `(escopo, número, ano)`) ou publicar o erro e retificar | Beco no coração do fluxo de aprovação | [FATO] tela Homologar sem recusa; `interface/atos.py` sem devolver; `publish_edital.py:288`; `draft.py:180` | Ato "Devolver à elaboração" (EM_REVISAO→EM_ELABORACAO), espelhando a Retificação | **Corrigir agora** |
| E2E-002 | **ALTO ATRITO** | FLUXO | Homologador | Retificação em revisão | `devolver` existe no domínio/API (`retificacoes.py:313`) e a UI o promete ("até ser devolvida"), mas não há botão; `cancelar` exige `retificacao:cancelar`, que nenhum papel concede (`atos_retificacao.py:70`, `identidade.py:20-50`) | Discordância sem saída na UI | [FATO] tela só oferece Homologar | Expor devolver (com motivo) e decidir dono de cancelar | **Corrigir agora** |
| E2E-003 | **ALTO ATRITO** | UX/PERF | Gestor | Inscrições recebidas | Lista única sem paginação/busca/filtro/contadores | Inviável a 1.500; nasce a planilha paralela | [FATO] 60 `<tr>`, sem nav | Paginar + filtrar (perfil, modalidade, situação, busca) + contadores | **Corrigir agora** |
| E2E-004 | **ALTO ATRITO** | FLUXO | Elaborador | Retificar | UI não alcança documentos exigidos, pontuação máxima, avaliações por inscrição, marca de período; só acrescenta Perfis/Eventos | Documento exigido errado publicado → só API | [FATO] tela; domínio alcança (`colecoes.py:28`) | Cobrir as coleções retificáveis restantes | Próxima leva (não é 013) |
| E2E-005 | MELHORIA | MODELO | Gestor | Processo | "Ativo" só habilita Encerrar (`finalizacao.py:14,69`); tudo funciona "Em elaboração"; rótulo convive com Edital publicado e inscrições abertas | Estado sem significado operacional; badge confunde; Encerrar exige Ativar antes | [FATO] PS-AUDIT e PS-DEMO-B publicados com Processo "Em elaboração" | Inferir ativação na 1ª publicação, ou dar consequência real ao estado | Próxima leva |
| E2E-006 | MELHORIA | BUG/UX | Elaborador | Compor (todas as etapas) | Após "Rascunho salvo", banner "Há preenchimento não enviado neste navegador" com Restaurar/Descartar | Mina a confiança ("salvou ou não?") | [FATO] reproduzido 3× (Perfis, Cronograma, Etapas) | Limpar o rascunho local no save bem-sucedido | **Corrigir agora** |
| E2E-007 | MELHORIA | UX | Elaborador | Compor/Revisão | Resumo de congelamento omite pontuação máxima e avaliações por inscrição (o PDF as mostra — `pdf.py:1288-1293`) | Elaborador congela o que não conferiu | [FATO] tela vs banco | Incluir os dois campos no resumo | **Corrigir agora** |
| E2E-008 | MELHORIA | UX | Avaliador | Mesa | Lista só protocolo+situação; contadores não filtram; sem nome | A 500, achar pendências específicas = paginação manual | [FATO] | Contadores clicáveis como filtros; nome na linha | Próxima leva |
| E2E-009 | MELHORIA | UX | Presidente | Impedimentos/Conclusões | Inscrição indicada digitando protocolo exato | Erro de digitação vira recusa; cópia manual entre telas | [FATO] | Picker/autocomplete de inscrição | Apenas registrar |
| E2E-010 | POLIMENTO | UX | Equipe | Revisão, Conclusões | Forma canônica vaza: `20.0000%`, `1.0000`, UUID de versão | Ruído; contrasta com o cuidado da 007 no documento | [FATO] | Humanizar via mesmo helper do compositor | Apenas registrar |
| E2E-011 | POLIMENTO | UX | Candidato | Comprovante | SHA-256 + instruções `shasum`/`certutil` em bloco aberto | Integridade competindo com a tarefa | [FATO] | Progressive disclosure ("verificar integridade") | Apenas registrar |
| E2E-012 | POLIMENTO | UX | Candidato | Detalhe da seleção | "3 documentos que serão pedidos" ignora modalidade (AC recebe 2) | Expectativa levemente errada | [FATO] | "2 a 3 documentos, conforme a concorrência" | Apenas registrar |
| E2E-013 | MELHORIA | FLUXO | Publicador/Gestor | Pós-publicação | Confirmação não leva à vitrine; nada sugere constituir comissão | Próximo passo do fluxo inteiro fica na cabeça das pessoas | [FATO] "Nenhum ato disponível…" | CTA pós-publicação: ver na vitrine; painel do Processo apontando comissão/alocação pendentes | Próxima leva |
| E2E-014 | POLIMENTO | UX | Equipe | Identificar-se | "Ou entre por outro nome" sem lista acima em ambiente sem vínculos | Só superfície de demonstração | [FATO] | Esconder o "Ou" quando a lista está vazia | Apenas registrar |
| E2E-015 | MELHORIA | DÍVIDA TÉCNICA | — | Suíte | Escrita da Mesa, `distribuicao-remover`, `impedimentos`, `compor`/`retificar` cross-escopo sem teste de recusa HTTP; fragmentos de retificação sem teste algum | O eixo mais sensível da 012 sem contrato negativo no canal real | análise da suíte (`tests/authorization/`) | Fechar a matriz de recusa dos POSTs | **Corrigir agora** (só testes) |
| E2E-016 | — | FEATURE FUTURA | Todos | Handoffs | Sem notificação em nenhuma passagem de bastão | Combinação informal (e-mail/corredor) permanece | seção 7 | Registrar; não implementar por ora | Feature futura |
| E2E-017 | MELHORIA | FLUXO | Presidente | Distribuição | Inscrições chegadas após a distribuição ficam sem avaliador até alguém voltar à tela | Cauda de inscritos de última hora esquecida | [FATO] contadores sobem sem aviso | Registrar; contadores já denunciam | Apenas registrar |
| E2E-018 | POLIMENTO | UX | Retificação | Detalhe | Handoff sem texto: falta "Aguardando quem homologa" (o Edital tem) | Assimetria de orientação | [FATO] | Reusar o padrão do Edital | Apenas registrar |
| E2E-019 | POLIMENTO | PRIVACIDADE | Equipe | Home da gestão | Toda identidade institucional vê todos os Processos/Editais do escopo (sem ações) | Metadados apenas; provável decisão | [FATO] avaliadora vê PS-DEMO-B | Confirmar como decisão consciente | Apenas registrar |
| E2E-020 | MELHORIA | UX (conversão) | Candidato | Acesso | Código por e-mail é ponto único de falha; reenvio só após 60 s | Abandono por spam/atraso — dependente do SMTP real (G1) | [FATO] fluxo | Registrar; monitorar quando houver e-mail real | Feature futura |

| E2E-021 | MELHORIA | AUTORIZAÇÃO/UX | Elaborador | Retificação | `retificacao:cancelar` não pertence a papel nenhum (`identidade.py:20-50`): o ato "Cancelar Retificação" existe no domínio e na tabela de atos, e é inalcançável pela interface | Retificação aberta por engano não tem como ser abandonada pela tela; a devolução a leva de volta à elaboração, e ela fica lá | [FATO] descoberto ao expor a devolução (E2E-002); confirmado por varredura: duas ocorrências, nenhuma num papel | Decidir de quem é o ato — o espelho do Edital diria Gestor, que detém `edital:cancelar` — e conceder a permissão. É decisão de governança, não de implementação: não foi tomada aqui | Próxima leva |

Positivos que merecem registro: recusas pré-POST no fluxo de atos; convite por vaga sobrevivendo ao login; aviso de versão pós-Retificação; alerta "CPF repetido neste Perfil"; iframe de documento sem download; loop concluir→próxima; conferência antes de gravar na comissão; proposta de distribuição com prévia.

## 11. Top 10 oportunidades (impacto ÷ custo)

1. **Devolver à elaboração** (Edital e Retificação) — destrava os dois becos centrais do fluxo de aprovação (E2E-001/002).
2. **Paginar+filtrar Inscrições recebidas** com contadores por Perfil/modalidade (E2E-003).
3. **Retificação alcançando documentos exigidos e campos da 012** (E2E-004).
4. **Limpar rascunho local após save** (E2E-006) — pequeno, alto ganho de confiança.
5. **Resumo de congelamento completo** (E2E-007) — trivial.
6. **CTA pós-publicação** (vitrine + "constitua a comissão" no painel do Processo) (E2E-013).
7. **Contadores da Mesa como filtros + nome do candidato na lista** (E2E-008).
8. **Estado Ativo inferido na 1ª publicação** (ou consequência real) (E2E-005).
9. **Picker de inscrição em Impedimentos/Conclusões** (E2E-009).
10. **Humanizar decimais/paths/UUIDs nas telas administrativas** (E2E-010/018).

## 12. O que NÃO corrigir agora

- **Notificações/e-mail de handoff** — lacuna real, mas o canal de e-mail é limitado por decisão da 010; registrar apenas (E2E-016).
- **Exportar Excel/CSV** da lista de inscrições — a resposta certa é filtro+contador dentro do sistema, não exportação.
- **Reabrir a 008** (composição do PDF) — nenhuma regressão observada; a rubrica visual de 18 itens não foi re-executada nesta auditoria (registrado como não verificado, não como defeito).
- **Estruturar barema, avaliação cega, distribuição automática por regra** — vedados pela própria 012; nada visto muda isso.
- **Retirada de inscrição, reabertura pós-013** (EC-006/EC-010) — continuam esperando a feature que criar o estado.
- **Autenticação real, retenção/descarte, provedor de identidade, SMTP** — gates de produção conhecidos (G1–G4), não escopo de feature.
- **Redação institucional das seções e do catálogo de autoridades** — trabalho editorial (G17).

## 13. Gate antes da 013

**A. Há defeito que torna imprudente iniciar a 013?** **NÃO.** Nenhum achado toca a integridade da cadeia atribuição→avaliação→conclusão que a 013 consome (`avaliacoes_elegiveis` e os nove itens do gate da 012 estão demonstrados — inclusive observei autoria, versão-que-governou, reabertura com motivo e conclusão preservada nas telas). Os ALTO ATRITO desta auditoria vivem no fluxo de aprovação e na consulta administrativa, fora da fronteira da 013.

**B. Melhorias úteis, não bloqueantes:** E2E-005, E2E-008, E2E-009, E2E-010/011/012/013/014/018, E2E-017 — e o par E2E-015 (testes) que pode andar junto de qualquer leva.

**C. A fronteira da 013 continua sendo avaliações individuais → Resultado da Etapa?** **SIM.** As duas fontes (011 §4, 012 §21/§27) convergem, o contrato técnico (`avaliacoes_elegiveis`) existe e nada observado sugere fronteira melhor. Duas perguntas registradas devem entrar na spec da 013 como decisões explícitas, não como escopo: o tratamento da **reabertura de avaliação já consumida** (EC-010) e a definição de **quórum/déficit** quando "avaliações por inscrição" não foi atingido (a Mesa já mostra o déficit; a 013 decide o que ele significa).

## 14. Recomendação de próxima ação

**A — corrigir um pacote pequeno antes da 013**, com este conteúdo e nada mais:

1. Devolver à elaboração (Edital) + expor devolver de Retificação na UI (E2E-001/002);
2. Paginação/filtros/contadores em Inscrições recebidas (E2E-003);
3. Limpeza do rascunho local pós-save + resumo de congelamento completo (E2E-006/007);
4. Matriz de recusa HTTP dos POSTs da 012 na suíte (E2E-015).

Justificativa: nenhum desses itens depende da 013 nem a adianta, mas todos atingem a primeira seleção real — o beco da aprovação e a lista de inscrições são exatamente os pontos onde a equipe voltaria para e-mail e planilha. É um pacote de dias, não de semanas; a especificação da 013 pode começar em paralelo assim que ele estiver acordado.

---

## Régua final

> Se esse Processo Seletivo começasse amanhã, quais são as três coisas que mais provavelmente fariam candidato ou equipe abandonarem o fluxo do sistema?

1. **A equipe abre planilha na primeira semana por causa da lista de inscrições** — 1.500 linhas numa página, sem filtro nem contagem por modalidade ([FATO] 60 linhas sem paginação/busca; E2E-003).
2. **Um erro descoberto depois da submissão faz o fluxo de aprovação sair do sistema** — sem devolução, a correção vira reunião, cancelamento com número queimado, ou "publica e retifica"; e se o erro for num documento exigido, nem Retificação pela UI alcança ([FATO] telas de Homologar sem recusa + Retificar sem documentos; E2E-001/002/004).
3. **O candidato que não recebe o código no e-mail desiste** — é o único degrau da jornada dele que depende de infraestrutura ainda não real (SMTP/G1), e o único sem alternativa ([FATO] fluxo de acesso; E2E-020). Todo o resto da jornada do candidato joga a favor da conversão.

---

## Pendências registradas ao fechar a auditoria

Registradas aqui, e **fora da 013**, porque nenhuma delas toca a cadeia
Atribuição → Avaliação → Conclusão → Consolidação que a próxima feature consome. Puxá-las para a
spec da 013 interromperia o arco funcional para resolver capacidade lateral.

### E2E-004 — Retificar não alcança documentos exigidos (ALTO ATRITO)

A tela de Retificação alcança Perfis, Modalidades, Eventos, Etapas e Seções, e **não** alcança
`documentRequirements`, `maximumScore`, `evaluationsPerRegistration` nem a marca de período de
inscrições. O domínio alcança as coleções (`publicacoes/domain/colecoes.py`); é a interface que
para na metade. Consequência: um documento exigido publicado errado só se corrige pela API.

**Implementado em 04/09/2026 — a metade da edição, e o custo não era o previsto.** A metade das
Etapas caiu junto com a revisão do contrato de conclusão: `maximumScore` e
`evaluationsPerRegistration` entraram em `CAMPOS_ETAPA` com os campos da forma. A metade dos
documentos exigia outra coisa.

O laço do grupo é mecânico, como o das Etapas. Mas **dois dos campos publicados do Documento
Exigido não tinham tipo na tela**: `profileId` e `modalityId` referenciam entidades do próprio
conteúdo, `null` neles significa "sem restrição", e todos os tipos existentes eram escalares
digitados ou marcados. E são justamente esses dois que `documentos.aplicaveis` lê para decidir
quem precisa enviar o quê — oferecê-los como texto livre deixaria um erro de digitação mudar em
silêncio a obrigação documental de um grupo de candidatos.

Entrou um tipo de campo novo, `REFERENCIA`, com três consequências: as opções vêm do **conteúdo
publicado** e não de `edital.perfis`, porque uma Retificação anterior pode ter criado Perfil que
não existe na linha de elaboração; o POST confere a escolha contra o que foi oferecido, porque a
verificação de publicação confere a forma do UUID e não se ele endereça algo; e o resumo mostra o
rótulo, porque conferir identificador de cor é o mesmo que não conferir.

**Acrescentar e remover ficaram fora, e a razão é normativa.** Acrescentar Documento Exigido
obrigatório depois de publicado torna incompleta a inscrição de quem já enviou tudo o que se
pedia. O que fazer com essas pessoas é decisão do domínio, não da tela, e enquanto ela não existir
o grupo dos documentos não é removível.

**Classificação original:** P0 antes da primeira seleção real; **não** é pré-requisito da 013. Se um certame
for aberto antes de a 013 ficar pronta, esta correção passa à frente — é o último ponto por onde a
equipe sai do sistema no meio do certame.

### E2E-021 — quem cancela uma Retificação (decisão tomada)

**Decisão de governança, tomada em 02/09/2026:** cancelar uma Retificação **em elaboração** é ato
do **Gestor**, pelo mesmo padrão do Edital, onde `edital:cancelar` já pertence a ele. A separação
que a sustenta:

| Situação da Retificação | Ato | Quem |
|---|---|---|
| Em elaboração | Cancelar | Gestor |
| Em revisão · Homologada | Devolver para elaboração | Homologador |

Cancelar um ato administrativo **em preparação** não é a mesma coisa que devolver um ato já
submetido: quem elabora não ganha, por elaborar, o poder de eliminar o ato.

**Decisão fechada — o alcance do cancelamento.** `CANCELAVEL = {EM_ELABORACAO}`, e
`retificacao:cancelar` pertence ao **Gestor**. Uma Retificação em revisão ou homologada precisa ser
**devolvida antes** de poder ser cancelada:

```
EM_REVISAO ──devolver──▶ EM_ELABORACAO ──cancelar──▶ CANCELADA
HOMOLOGADA ──devolver──▶ EM_ELABORACAO ──cancelar──▶ CANCELADA
```

A alternativa — deixar o Gestor cancelar atravessando os estados de aprovação — foi recusada, e a
razão é a mesma que separa os dois atos: **devolver desfaz o avanço no fluxo de aprovação; cancelar
abandona um ato que está em elaboração**. Exigir dois atos para abandonar uma Retificação
homologada não é atrito acidental — é mais auditável, porque alguém desfaz a aprovação e alguém
abandona o rascunho, e a trilha guarda os dois.

~~Hoje `atos_retificacao.CANCELAVEL` admite as três situações, e a permissão segue sem dono em
`identidade.py::PAPEIS` — por isso o ato continua inalcançável pela interface. Implementar é
estreitar o conjunto e conceder a permissão ao Gestor: **próxima leva corretiva, fora da 013**.~~

**Implementado em 04/09/2026 — e a receita acima estava incompleta.** Estreitar `CANCELAVEL` e
conceder a permissão eram duas das três mudanças necessárias. A terceira, que esta auditoria não
viu, é a que importava:

```
TRANSITIONS["cancelar"] = (None, CANCELADA)   ← "qualquer estado não final"
```

O **domínio** admitia cancelar de qualquer situação não final, e a única guarda era uma recusa
explícita de `PUBLICADA` e `CANCELADA`. Estreitar apenas a constante da interface teria deixado a
API aceitando o que a decisão recusa — o que o Princípio IV proíbe, porque validação de tela não é
fronteira de segurança nem autoridade final.

A transição passou a declarar `(EM_ELABORACAO,)`, e a recusa ganhou o caminho de volta em vez da
mensagem genérica: quem tenta cancelar o que está em revisão ou homologado lê que precisa devolver
antes; quem tenta cancelar o que é final lê que não há volta. A semântica `None` deixou de existir
em `TRANSITIONS`, porque `cancelar` era a única a usá-la.

**Lição para as próximas correções:** um achado descrito pela tela pode ter metade da causa no
domínio. A verificação antes de implementar custou uma leitura e mudou o tamanho da mudança.
