# A.5 — Plano de regularização da integridade e dos controles

Data: 19/10/2026.

**A.5 DOCUMENTAL CONCLUÍDA**  
**INTEGRIDADE OPERACIONAL BLOQUEADA**  
**CONSULTA OPERACIONAL NÃO EXECUTADA**  
**FASE 5B.2-A INTEGRAL NÃO CONCLUÍDA**

Branch inicial/final: `001-decisoes-pendentes`. HEAD inicial/final: `550f5bb8983bcdbf32eff210622449a0c959d12d`. Nenhum arquivo preexistente modificado. Criados somente os sete arquivos autorizados desta pasta.

## Entrega e resultados

| Arquivo novo | Finalidade |
|---|---|
| [README.md](README.md) | Relatório executivo |
| [matriz-integridade.md](matriz-integridade.md) | Onze caminhos únicos, referências, hashes e sobreposições |
| [estrategia-integridade.md](estrategia-integridade.md) | Comparação das três alternativas e política proposta |
| [controles-executor.md](controles-executor.md) | Especificação documental dos controles e níveis de prova |
| [plano-implementacao.md](plano-implementacao.md) | Seis incrementos pequenos, dependências, aceite e rollback |
| [gates-autorizacao.md](gates-autorizacao.md) | G1–G6, evidências e decisões humanas |
| [manifesto-a5.json](manifesto-a5.json) | Hashes dos seis documentos e evidências de preservação |

Reconfirmadas 63 comparações históricas, com 11 caminhos divergentes únicos. As duas falhas operacionais já pertencem ao conjunto histórico; não são somadas novamente. Em todos os divergentes, CRLF calculado apenas em memória recupera o hash esperado. A origem por normalização Git é provável; evento e autoria continuam indeterminados.

Recomenda-se **alternativa 1: preservar bytes atuais e aprovar uma nova baseline**, vinculada às referências anteriores. Isso não libera o operador antigo nem resolve automaticamente controles ausentes. Nenhuma alternativa foi implementada.

Controles a preparar: identidade/caminho/hash do binário e runtime, endpoint exato/local, autorização de tentativa única, timeout, contenção/encerramento de descendentes, interrupção segura, limites e sanitização de saída, recibo exclusivo e custódia. Os controles parciais identificados na A.4 precisam complementação; os três comprovados estaticamente precisam continuar presentes na revisão sucessora.

## Verificações e preservação

Constituição v1.2.0 e instruções de governança consultadas; proposta respeita história, negação por padrão e rastreabilidade. A especificação técnica está restrita a estes documentos, sem editar specs funcionais. Validado o hash publicado do manifesto A.4 e os cinco documentos nele referidos. Hashes dos 117 arquivos anteriores da área foram inventariados antes/depois: preservados. O working tree começou com oito arquivos não rastreados anteriores (dois controles e seis documentos A.4), mantidos intactos; nenhuma alteração rastreada foi introduzida.

Realizadas somente leitura de arquivos, comparação SHA-256/CRLF em memória e consultas Git de leitura. Nenhum teste de executor, script operacional, serviço, Docker ou banco foi executado. Não houve consulta de credenciais, instalações, normalização ou modificação de configuração Git. A conferência documental não valida endpoint, binário ou isolamento operacional.

O manifesto A.5 inclui hashes brutos dos seis Markdown, inventário anterior/posterior e comparações; exclui o próprio hash para evitar autorreferência. Seu hash é entregue externamente na resposta final. Não substitui o manifesto operacional.

## Ordem e próxima autorização mínima

I1 (baseline documental) → I2 (guardas) → I3 (processos) e I4 (custódia) → I5 (integração) → I6 (preparação humana/host). A preparação de I4 pode ocorrer em paralelo ao desenho I2; testes com processos ou arquivos persistentes têm autorização própria. G1–G6 permanecem pendentes/não executados: **nenhum gate aprovado nesta etapa**.

Próxima autorização mínima proposta: escolher a alternativa 1 e autorizar apenas I1, criando baseline-integridade.json e procedencia.md no novo caminho proposto no plano. Revisão do plano não equivale a essa autorização. Não iniciar código ou consulta antes de novos aceites.

Riscos remanescentes: integridade operacional divergente, executável e endpoint desconhecidos, ausência de timeout/contenção/custódia no operador atual, confiança não demonstrada no runtime, TOCTOU e efeitos indiretos do host. Permanecem pendentes pessoas, janela, destino, ACL, retenção e aprovação dos limites propostos.

Aguardam-se análise humana e autorização expressa. Nenhum incremento será iniciado automaticamente.

