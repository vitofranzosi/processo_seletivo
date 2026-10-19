# Próximas atividades e revisão da entrega

Data: 16/10/2026. A execução documental não autoriza operações de preservação ou implementação.

## Plano por grupos

| Grupo | Próxima atividade recomendada | Dependências / paralelismo | Encerramento |
|---|---|---|---|
| Riscos imediatos | Titular comprovar GO-09; localizar vídeos; confirmar destino e preservar Git/mídia/bancos | GO-09 e localização podem seguir independentemente; bundle aguarda destino; bancos aguardam inventário e autorização | Evidências sanitizadas, hashes e restauração/reprodução verificadas; localização sem backup não encerra GO-47 |
| Produto | Deliberar DEC-01, 06–13 e CA-23; DEC-15 por linha | DEC-09 depende do edital piloto; DEC-12 requer encarregado; CA-23 pode ser deliberada separadamente | Registro expresso com autor, data e alternativa; implementação continua em estado próprio |
| Institucional | Revisar e encaminhar minutas por responsável humano | TI, encarregado, Cefor, correio e jurídico podem responder em paralelo; não há envio autorizado ao agente | Respostas dos setores competentes, condições e responsáveis registrados |
| Correções técnicas | Revisar mudanças exclusivas da main; avaliar lote já integrado; preparar specs somente quando aprovadas | Sem integração automática; execução funcional fora desta fase | Autorização específica, rastreabilidade, regressões e revisão; merge humano |
| Homologação | Nomear participantes, ambiente sintético e agenda DEC-14 | Pode avançar enquanto chegam respostas institucionais, sem dados reais/chamadas pagas por presunção | Evidências das jornadas, achados, responsáveis e aceite humano |
| Implantação | Planejar identidade, correio, autoridade, retenção, operação e restauração | Piloto/janela e decisões institucionais; validação 073/TI/L4 permanece própria | Ensaio e restauração aprovados, condições institucionais cumpridas e autorização de entrada |

## Primeira próxima execução sugerida

1. Usuário revisar a matriz e a pauta DEC-15 e designar responsáveis nominais.
2. Titular entregar comprovação sanitizada de GO-09.
3. Confirmar máquina/raízes dos vídeos, destino externo do bundle e destino das mídias; autorizar
   operações delimitadas. Confirmar separadamente inventário/backup dos bancos.
4. Revisar minutas; encaminhamento por pessoa autorizada, sem envio automático pelo agente.
5. Deliberar CA-23, DEC-06 e DEC-08 sem iniciar suas implementações nesta rodada documental.
6. Autorizar, se desejado, commit exclusivamente dos documentos após inspeção do diff.

## Revisão de consistência desta fase

- Documentos históricos não foram sobrescritos; todos os artefatos novos ficam nesta pasta.
- Implementação, integração, teste automatizado e homologação são distinguidos no adendo.
- DEC-01 a DEC-16 têm alternativas, recomendação, evidência anterior, responsável, dependências,
  estado, critério de aceite e prova necessária; DEC-16 possui cinco subdecisões.
- Pauta DEC-15 desdobra as seis reclassificações da 026; registra a discrepância entre as cinco
  citadas no documento de mutabilidade e as seis da ED-47, sem resolver por inferência.
- Minutas são propostas não enviadas; não fornecem parecer jurídico nem institucional.
- CA-23 preserva vencimento e explicita disponibilidade do instante do primeiro sucesso sem
  inventar registro de envio; nenhum código foi alterado.
- Roteiro de mídia não copia nem exclui; manifesto/hash/cópia/restauração não foram executados
  sobre evidências reais. Cobertura de mídia é explícita e não equivale a inventário de todos os projetos.
- Constituição, specs, arquivos funcionais, refs e bancos permanecem sem alteração desta fase.

## Verificações executadas

| Verificação | Resultado | Limite |
|---|---|---|
| Parser PowerShell de `preservar-videos.ps1` | Sem erros de sintaxe | Não executado sobre mídia; não prova integridade de cópia |
| Links Markdown locais dos 13 documentos | Todos os destinos de arquivo existem | Não verifica âncoras nem disponibilidade de URLs externas |
| Cobertura da matriz | DEC-01 a DEC-16 presentes, com cinco subdecisões da DEC-16 revisadas | Nenhuma deliberação aprovada |
| Espaços finais nos 14 arquivos novos e `git diff --check` | Sem problemas detectados | Conferência dos novos arquivos feita separadamente, pois ainda não rastreados |
| `backend/.venv/Scripts/python.exe -m pytest tests/test_citacoes_de_requisito.py -q -p no:cacheprovider` | **6 passando em 27,47 s** | Teste de rastreabilidade sem banco; não é suíte PostgreSQL, homologação ou validação de produto |
| `git diff --name-only` e status final | Nenhum arquivo rastreado modificado; somente os 14 arquivos novos desta pasta | Sem commit, staging ou atualização de refs |

Não foram executados lint/suíte funcional completa: não houve alteração funcional ou de specs.
Não foi usado SQLite como evidência de produto. O teste de citações lê os artefatos existentes e
não demonstra sozinho a qualidade dos documentos novos; esta foi conferida por revisão de
campos, fontes, links, estados, escopo e consistência entre os entregáveis.

**FASE 1 DOCUMENTAL CONCLUÍDA — AGUARDANDO RATIFICAÇÕES E AUTORIZAÇÕES OPERACIONAIS.**
