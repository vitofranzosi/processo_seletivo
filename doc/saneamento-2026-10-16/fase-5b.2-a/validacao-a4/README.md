# A.4 — Saneamento de integridade e controles operacionais

Data: 19/10/2026.

**A.4 DOCUMENTAL CONCLUÍDA**  
**INTEGRIDADE OPERACIONAL BLOQUEADA**  
**CONSULTA OPERACIONAL NÃO EXECUTADA**  
**FASE 5B.2-A INTEGRAL NÃO CONCLUÍDA**

## Resultado executivo

Branch inicial/final: `001-decisoes-pendentes`. HEAD inicial/final: `550f5bb8983bcdbf32eff210622449a0c959d12d`. Criados exclusivamente os seis documentos desta pasta; zero arquivos preexistentes modificados. O working tree começou sem alterações rastreadas e com os dois controles da etapa anterior não rastreados; eles permanecem intactos. Nenhum commit, troca de branch ou operação de infraestrutura.

O manifesto operacional tem dez hashes concordantes e dois divergentes. Os dois scripts estão em LF; os hashes da representação CRLF calculada só em memória coincidem com os registros históricos. Os dois inventários A.2 somam nove caminhos divergentes distintos, incluindo o par; todos coincidem com a representação CRLF. Normalização pelo Git é causa provável; equivalência de representação é confirmada, mas autoria/instante da conversão permanecem indeterminados.

Três controles estão comprovados estaticamente, cinco são parciais, quatro ausentes e um depende de observação operacional. Faltam caminho/hash confiável do binário, timeout obrigatório, tratamento de processos bloqueados e recibo/custódia da consulta. Endpoint e interrupção segura também não estão demonstrados. Não se recomenda autorizar a consulta atual.

A conferência das 15 cópias históricas A.1 identificou outras duas divergências de representação. Somando os inventários A.1/A.2, há 11 caminhos divergentes distintos, incluindo os dois scripts, sem diferença adicional identificada além de EOL nas comparações criptográficas.

## Documentos criados

- [Integridade](integridade.md): hashes, diferenças adicionais, blobs Git e classificação causal.
- [Controles operacionais](controles-operacionais.md): 13 controles, fluxo indireto e verificações propostas.
- [Alternativas](alternativas-saneamento.md): consequências, riscos, reversibilidade e autorizações.
- [Proposta de autorização](proposta-autorizacao.md): comando de referência bloqueado e campos pendentes.
- [Manifesto A.4](manifesto-a4.json): hashes dos cinco Markdown, inventário dos 111 arquivos anteriores, comparações e verificações; exclui o próprio hash para evitar autorreferência.
- Este README.

## Verificações e limites

Foram feitas leituras binárias/JSON/código e consultas Git de status, HEAD, histórico, atributos/configuração e blobs. Hashes e conversões foram calculados em memória. Nenhum teste operacional ou teste de serviço foi executado; não se repetiram os testes históricos como se fossem evidência nova. Nenhum módulo local do operador foi importado. Foram consultados a Constituição v1.2.0, as instruções de governança e os contratos aplicáveis, preservando negação por padrão e rastreabilidade.

Os 111 arquivos anteriores desta área foram comparados antes/depois por SHA-256 e permanecem idênticos. Esse controle local não revalida retroativamente hashes históricos divergentes nem cobre arquivos secretos, que não foram lidos. Os arquivos de controle anteriores continuam sem autorização operacional; nenhum dado real, chave ou perfil institucional foi acessado.

## Critérios documentais

| Critério | Resultado |
|---|---|
| Hashes atuais/históricos e método reproduzível | Atendido; integridade.md e manifesto |
| Diferenças além de EOL e causa classificadas | Atendido para os inventários comparados; causalidade histórica limitada expressamente |
| Treze controles examinados | Atendido; aprovação operacional permanece bloqueada |
| Pendências, alternativas e proposta futura | Atendido; nenhum campo humano presumido |
| Preservação de arquivos anteriores | Atendido; 111 hashes antes/depois no manifesto |
| Nenhuma execução operacional | Atendido; somente leitura estática e novos documentos A.4 |
| Integridade operacional | Bloqueada, não é critério de aprovação desta documentação |
| Consulta e fase 5B.2-A integral | Não executada / não concluída |

## Próxima decisão humana

Avaliar os achados e escolher a alternativa de saneamento. Recomenda-se preservar o estado e autorizar separadamente uma nova revisão dos artefatos exclusivos de homologação, com novo manifesto e controles ausentes. Revisão de código/controles, preenchimento humano e consulta futura são autorizações distintas. A A.4 encerra-se nesta entrega; aguarda-se avaliação, sem execução automática.

