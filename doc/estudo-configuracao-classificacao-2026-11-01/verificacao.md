# Método, execução e limites de verificação

## Ambiente e proteção dos dados

- Árvore investigada: `4d9e97a9597937f8812fed7c9a00f2197815e0d9`, em 01/11/2026.
- Django nativo, PostgreSQL 16 do Homebrew, `LC_ALL=pt_BR.UTF-8`, fuso institucional `America/Sao_Paulo`.
- Banco exclusivo `ps_ux_classificacao_20261101`; papéis novos `ps_uxclass_migracao` e `ps_uxclass_runtime`.
- Preparação em ordem: provisionamento, migrations com papel de migração, segundo provisionamento, unidades e semente. A segunda passada protegeu **46 de 46** tabelas append-only. `migrate --check` passou antes das navegações.
- Servidor investigado em `http://localhost:8113`, como runtime sem privilégios de alteração/exclusão dos históricos. Seletor de identidade habilitado apenas no desenvolvimento.
- Dois Processos criados com `seed_demo`: `UX-CLASS-20261101` e `UX-CLASS-HORA-20261101`. Todos os candidatos são fictícios da semente; nenhuma base pré-existente foi escrita.
- Senha aleatória e estados de sessão do navegador ficaram em arquivos locais temporários, fora do repositório. Não estão nos artefatos. Os scripts de registro da sessão têm identificadores sintéticos, não credenciais.
- Preparação do caso temporal por comandos oficiais de Retificação, com autoria e publicação preservadas. Não se desabilitou gatilho, privilégio ou autorização. Alterações do rascunho e atos de sorteio registrados nas capturas foram feitos na interface.

O banco e os atos sintéticos permanecem como registro da investigação. Não houve limpeza por exclusão normativa. O servidor do GPS foi utilizado somente para a auditoria; os protótipos são arquivos independentes.

## Verificações executadas

| Verificação | Resultado | Evidência / limite |
|---|---|---|
| `make lint check` em `backend` | Passou: Ruff check, Ruff format, Django check e migrations sem mudança | 1741 arquivos já formatados; nenhuma issue de sistema ou migration nova |
| Testes selecionados contra PostgreSQL, 4 workers / worksteal | **417 passaram em 13,73 s** | [log](verificacao-dominio.log), [comando exato](comando-verificacao.txt); banco de teste com nome exclusivo; não é execução da suíte completa |
| Casos numéricos da dupla dos protótipos | Passou com funções oficiais `combinar` e `ordenar_com_trajetoria` | [exemplos-oficiais.json](exemplos-oficiais.json), [script](scripts/conferir_exemplos.py); maquete só exibe esses resultados preparados |
| Sintaxe JavaScript | `node --check prototipos/prototipos.js` passou | Nenhuma instalação ou dependência frontend nova |
| Interações das duas maquetes em Chromium | Passaram: incompleta → corrigida; marca retirada → restaurada; destino circular → corrigido; exemplo; revisão; tempo; outro Perfil | [verificacao-prototipos.json](verificacao-prototipos.json), [script](scripts/verificar_prototipos.py); nenhum erro JavaScript observado |
| Foco e teclado parcial | Correções mantêm foco em elemento existente; restauração com Enter funciona | Não é percurso completo com tecnologia assistiva ou auditoria WCAG |
| Layout móvel | 390 × 844, sem overflow horizontal da página | Capturas móveis de A/E; relações ficam recolhidas no estreito e inspeção de seleção recebe foco contextual |
| Screenshots | **22 capturas da aplicação + 20 das maquetes**, além da apresentação | Arquivos em `capturas/`; as capturas da aplicação não foram alteradas |
| Arquivos e links locais | Destinos conferidos por script | [verificacao-arquivos.json](verificacao-arquivos.json); não verifica disponibilidade futura das referências web |
| Scripts do estudo | Ruff check e format conferidos; arquivos Python compiláveis | Fora do backend de produção; scripts de sessão não constituem uma suíte genérica de produto |
| Escopo da árvore | Apenas a pasta deste estudo foi acrescentada | Aplicação, specs, Constituição e os dois estudos preexistentes mantidos |

Os testes selecionados cobrem etapas e marcos, combinação, universo, desempate e corte, prévias e equivalência por recorte, viabilidade do sorteio, constituição, fonte só com data, congelamento após inscrições, interface das prévias e citações de requisitos. Não houve implementação de produto que justificasse rodar toda a suíte; o subconjunto dá evidência técnica da reconstrução sem alegar ausência geral de regressões.

## Cobertura das interações solicitadas

| Requisito de demonstração | A · Mapa | E · Caderno |
|---|---|---|
| Visão global | Etapas e relações do Perfil; troca para TEC-LAB | Conferir compromissos e Revisão completa |
| Configurar uma etapa | Títulos: marca e peso no inspetor | Onde a etapa é usada: marca e peso na frase |
| Dependências | Entradas → marco ⇢ destino; consumidores em dois perfis | Origem e alcance de cada compromisso; antes/depois |
| Marca conforme semântica real | Retirar não elimina; três referências ficam incompatíveis | Mesma decisão e seus compromissos afetados |
| Regra que afeta outra etapa | POS-TIT alimenta documental | “Quem segue?” escolhe destino de POS-TIT |
| Detectar inconsistência | Marca retirada, peso ausente e destino circular | Mesmas causas apresentadas por decisão |
| Resolver | Restaurar marca, declarar peso, alimentar documental | Ações diretas de reconciliação |
| Revisar conjunto | Tabela dos quatro marcos nos dois perfis | Conferência por compromisso e revisão comum |
| Configuração e simulação | Exemplo abre por solicitação com duas versões preparadas | Caso concreto a partir da decisão; retorno à edição |
| Prontidão | Eixos configuração/atos e hipótese operacional | Mesma distinção; confirmação só da leitura na página |

Configuração de novas entidades, edição de todas as combinações e valores livres não estão implementadas nas maquetes. As ações disponíveis são o recorte suficiente para comparar modelos de compreensão. Valores não editáveis são identificados como parte do cenário; não se promete um configurador funcional completo.

## Reproduzir o material

Para as maquetes, basta abrir os HTML ou servir a pasta por HTTP. Para repetir as capturas automáticas, com Playwright já instalado no ambiente de desenvolvimento:

```bash
python3 -m http.server 8768 --bind 127.0.0.1 --directory doc/estudo-configuracao-classificacao-2026-11-01
```

Em outro terminal, na raiz:

```bash
backend/.venv/bin/python doc/estudo-configuracao-classificacao-2026-11-01/scripts/verificar_prototipos.py
PYTHONPATH=backend backend/.venv/bin/python doc/estudo-configuracao-classificacao-2026-11-01/scripts/conferir_exemplos.py
python3 doc/estudo-configuracao-classificacao-2026-11-01/scripts/verificar_arquivos.py
```

Os scripts de auditoria real são **registros desta sessão**, com seus IDs e ordem de estados, não uma fixture idempotente. `preparar_ambiente.py` cria o banco exclusivo uma única vez e gera credencial aleatória fora da árvore. Um novo banco recebe novos IDs; para reproduzir os gestos, resolver os IDs no ambiente novo e adaptar os scripts ou seguir o roteiro de jornadas. Não repetir cegamente scripts de publicação/Retificação sobre registros já criados: são atos imutáveis. O contraste direto usa um segundo `seed_demo --codigo UX-CLASS-HORA-20261101 --numero 02`.

A navegação inicial usou `localhost` porque o `ALLOWED_HOSTS` do projeto o exige; o servidor de arquivos das maquetes aceita `127.0.0.1`. Não foi alterada configuração de segurança do produto para acomodar a auditoria.

## Limitações da conclusão

Não houve entrevistas, teste de compreensão com operadores, medição de tempo/erros, avaliação com leitor de tela ou teste de escala com dezenas de etapas. As capturas mostram quatro etapas e marcos existentes/sintéticos; não representam todo edital possível. A evolução proposta é uma hipótese fundamentada a ser escolhida e especificada depois, não uma solução validada ou integrada.
