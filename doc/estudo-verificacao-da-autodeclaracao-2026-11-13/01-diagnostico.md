# 1. Diagnóstico técnico e normativo

## 1. Resumo

- **O GPS não tem heteroidentificação.** Nenhuma ocorrência funcional no código. Todas as specs que a
  tocam (012, 014, 015, 016, 018, 019, 021, 066, 067) a mandam para "spec própria", e a Visão do
  Sistema diz que ela "é conduzida fora dele". Hoje a autodeclaração é só um documento exigido na
  convocação.
- **As peças existem quase todas.** O que falta:
  - a Etapa aplicável só a quem declarou uma Modalidade (a lacuna L-2);
  - a consequência por lista ("sai da reserva, fica na ampla");
  - a regra de combinação de pareceres decisórios.

  O vídeo, sozinho, pede pouco de novo: aceitar o formato, a entrega com `Range` e o envio em partes.
- **A gravação assíncrona não está autorizada no Ifes.**
  - A Res. CS 61/2019 prevê entrevista **presencial**, gravada.
  - O Ato 12/2020 abriu a **videoconferência**, em caráter excepcional e enquanto durasse a
    suspensão das aulas presenciais.
  - O Ofício Circular MEC nº 3/2025 pede, fora do presencial, entrevista on-line **síncrona**.

  O vídeo gravado pelo candidato exigiria, no mínimo, alteração da Resolução pelo Conselho
  Superior, protocolo da CPVA e previsão no Edital.
- **Consequência para o desenho.** O que dá para fazer já é pôr no GPS o rito que o Ifes pratica
  (camada A). O vídeo é uma camada B experimental, desligada e recusada em produção, desenhada para a
  única forma que tem precedente defensável: **o vídeo só confirma** (modelo UFC), e a não
  confirmação só existe depois da entrevista síncrona.

## 2. O que o GPS tem hoje

Caminhos relativos a `backend/processo_seletivo/`.

| Necessidade do rito | Onde está | Situação |
|---|---|---|
| Etapa decisória (aceitar/recusar) | `EtapaAvaliacao.forma = DECISORIA`, rótulos do Edital (`editais/models/etapas.py:50-54`) | **existe** |
| Etapa só para quem declarou PPI | `EtapaAvaliacao` é do Edital e vale para todos (`etapas.py:11-17`) | **falta (L-2)**, precondição registrada em `doc/avaliacao-de-capacidade-editais-2026-09-11.md:140` |
| Modalidade da inscrição | `Inscricao.modality_id`, imutável após o envio (`inscricoes/models.py:34,113-136`); `ModalidadeConcorrencia` por Perfil, `code` livre (`editais/models/perfis.py:118`) | existe; não há marcador semântico de "cota racial" (039 em Draft) |
| Comissão local (CLVA) | `MembroComissao` por Processo (`comissoes/models.py:31`), `AlocacaoEtapa` membro × Etapa (`:76`) | **existe**: a CLVA é a alocação à Etapa |
| Parecer por membro | `Atribuicao`, `Avaliacao` (sentido, parecer), `ConclusaoAvaliacao` (`avaliacoes/models.py:36,77,186`) | **existe** |
| Deliberação colegiada | mais de uma avaliação por inscrição dá `REGRA_DE_COMBINACAO_AUSENTE` (`resultados/domain/regra.py:71-76`) | **falta** a regra (unanimidade/maioria) |
| Consequência "fica na ampla" | `ResultadoEtapa.ELIMINADA` tira de todas as listas (`resultados/domain/progressao.py:12-20`); QC4 aberta (`doc/estudo-concorrencia-concomitante-2026-11-07.md:431`); 158 em Draft | **falta** |
| Ausência | `registrar_ocorrencia` (`resultados/application/ocorrencia.py:129`) | **existe** |
| Recurso e instância distinta | `Recurso`, papel julgador `recurso:julgar` (`interface/identidade.py:111`), impedimento de quem concluiu (`recursos/domain/elegibilidade.py:42`), ato de instrução (`recursos/application/instruir.py`) | existe; julgamento singular, sem colegiado e sem 2ª instância (018) |
| Visibilidade e recorribilidade | Etapa fora de marco não é visível nem recorrível (`resultados/application/selectors.py:191`; `doc/estudo-orientacao-da-jornada-2026-11-06/mapa-das-etapas.md:272-284`) | atenção: a Etapa precisa entrar no marco |
| Convocar para a Etapa | `Convocacao` é só para vaga; convocar para etapa "não é ato" (`doc/registro-convocacao-para-etapas-2026-10-09.md`) | **falta**; não é precondição do vídeo, mas da agenda ao vivo |
| Próximo passo do candidato | `portal/situacao.py:213` (`situacao_da_inscricao`, 7 degraus), `Acao` (`:158`) | existe; ganha um degrau |
| Pendências da gestão | `interface/andamento.py` (naturezas), `interface/centro.py:48`, `interface/atividades.py:451` | existe; ganha uma natureza |
| Arquivo privado | `ArmazenamentoPrivado` (`inscricoes/storage.py`), raiz fora da árvore (`production.py:139-146`) | existe |
| Entrega mediada e leitura registrada | `portal/arquivos.py` (`copia_verificada`, `entregar_e_registrar_ao_fim`); eventos `CONSULTAR_DOCUMENTO`, `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` | existe, só para PDF e sem `Range` |
| Validação de upload | `shared/arquivos.py:56` (`aceitar`: só PDF, por assinatura); limite de 10 MiB (`config/settings/base.py:432`); nginx 12 MB; gunicorn sync 120 s | **falta** vídeo |
| CSP | `shared/politica_de_conteudo.py:39-50`, sem `media-src` e sem `Permissions-Policy` | **falta** a exceção da página de gravação |
| Trilha | `RegistroAuditoria` append-only em três camadas; registra leitura, nunca conteúdo | existe |
| Chave desligada e recusada em produção | `_exigir` em `config/settings/production.py:66-68` (por exemplo, `ASSISTENTE_NA_PAGINA_DO_EDITAL`, `:242`) | existe; padrão a seguir |
| Retenção e eliminação programada | só `duvidas/management/commands/excluir_registros_do_piloto.py`; retenção é *gate* de implantação (009 FR-076, 115 QI-4) | **falta**, e é decisão |
| Menores de idade | nada no código nem nas specs | **falta** |
| Vídeo, câmera, `MediaRecorder` | nada; a 021 (FR-065) proíbe gravar vídeo **no sorteio** | não existe |

## 3. Base normativa

### 3.1 Do Ifes

| Norma | O que importa aqui | Fonte |
|---|---|---|
| **Res. CS 61/2019** (13/12/2019) | Institui a CPVA. A verificação é obrigatória, está prevista no Edital e ocorre antes da matrícula (art. 4º). Negros: **entrevista presencial** (arts. 11, I; 12), **gravada em áudio e vídeo** (art. 14 §1º), só fenótipo (art. 14 §2º). Indígenas: análise documental (art. 11, II). Indeferimento (art. 15), incluindo a recusa a ser filmado e o "não constatada, de maneira unânime" (III, b). Falsidade elimina, com contraditório (art. 16). Recurso à CPVA (art. 17). Menor acompanhado pelo responsável ou por servidor (art. 12 §§1º-2º). Não aceita imagem pretérita (art. 19). Impedimento pela Lei 9.784 (art. 20). **Não fixa guarda das gravações.** | [PDF](https://www.ifes.edu.br/images/stories/Res_CS_61_2019_-__Comiss%C3%A3o_Permanente_de_Verifica%C3%A7%C3%A3o_Autodeclara%C3%A7%C3%A3o_CPVA.pdf) |
| **Ato 12/2020** (30/09/2020) | Suspende o presencial **enquanto durar a suspensão das aulas presenciais** e autoriza **videoconferência**, em caráter excepcional. Falha de conexão do candidato após 3 tentativas = ausência. Vale "até aprovação pelo CS"; a homologação não foi localizada | [PDF](https://www.ifes.edu.br/images/stories/Ato_12_-_Suspende_Efeitos_de_Dispositivos_Resolu%C3%A7%C3%A3o_CS_61_2019.pdf) |
| **Ato 15/2021** (25/11/2021), "a alteração de 2021" | Altera só o art. 10: CLVA com **no mínimo 4** membros (1 do Neabi); um membro **acolhedor** orienta; os demais entrevistam, com diversidade. **Não trata de remoto** | [PDF](https://ifes.edu.br/images/stories/Ato_15_-_Altera_Resolução_CS_61_2021.pdf) |
| Parecer CPVA 01/2020 | Entrevista presencial e análise documental são "fundamentais e insubstituíveis" | [PDF](https://www.ifes.edu.br/images/stories/-publicacoes/conselhos-comissoes/cpva/parecer_01_cpva_heteroidentificacao_ps_2020.pdf) |
| Parecer CPVA 02/2020 | Origem das regras da videoconferência. Gravação e arquivamento da entrevista **individual**. A falta de tecnologia não pode eliminar, e o campus oferece outra estratégia | [PDF](https://www.ifes.edu.br/images/stories/-publicacoes/conselhos-comissoes/cpva/parecer_02_2020_cpva_heteroidentificacao.pdf) |
| Relatório CPVA 2020 | Registra a "fragilidade da ferramenta virtual" para o fenótipo. Compromisso de normatizar a etapa telepresencial do EaD e de definir **com a TI onde arquivar os vídeos** | [PDF](https://www.ifes.edu.br/images/stories/-publicacoes/conselhos-comissoes/cpva/relatorio_anual_cpva_2020.pdf) |
| Protocolo II CPVA (13/11/2020) | Para estudante **já matriculado**: entrevista presencial ou telepresencial gravada, arquivada no processo. Para menores, comunicação via responsáveis. Foto da matrícula só como último recurso | [PDF](https://www.ifes.edu.br/images/stories/-publicacoes/conselhos-comissoes/cpva/protocolo_ii_orientacoes_de_heteroidentificacao_de_estudantes.pdf) |
| Editais do Cefor 28/2026, 35/2026, 09/2026; Ifes 46/2026 (presencial), SiSU 156/2025 | Na prática: videoconferência **síncrona** na RNP, gravada (Cefor) ou presencial (46/2026). Indeferido por fenótipo **fica na ampla** (28/2026, 6.9.15 e 8.10). Recurso à CPVA. O 28/2026, 6.5, ainda justifica a videoconferência pela pandemia | `~/Downloads`; [SiSU 156/2025](https://www.ifes.edu.br/images/stories/-publicacoes/processos-seletivos/alunos/2025/2025-156-sisu/Orientacoes_para_heteroidentificacao.pdf) |

O pedido cita "a alteração de 2021". Ela é o Ato 15, e **não trata de remoto**. O que trata de
remoto é o Ato 12, de 2020.

### 3.2 Federal

| Norma | O que importa aqui |
|---|---|
| **Ofício Circular nº 3/2025/GAB/SESU** (Sesu e Setec, abr/2025), [cópia](https://portal.unila.edu.br/secafe/organizacao-de-bancas/SESU.pdf) | Orientação, e não norma vinculante. Ressalva a autonomia. Pede comissão plural, capacitada, **ímpar, mínimo de 3**; critério fenotípico. **Preferencialmente presencial; senão, on-line síncrono** (item 17). **Maioria simples** com parecer fundamentado (21). Recurso por **novo grupo**, síncrono (22-23). Indígenas e quilombolas **não** passam pela heteroidentificação (25-28). Silente sobre vídeo enviado, foto, IA e guarda |
| Lei 12.711/2012 (red. 14.723/2023) | Fala em "autodeclarados", sem comissão. O cotista concorre primeiro na ampla |
| Lei 15.142/2025 | Só concursos e seletivos **de pessoal**, e não discentes. Não confirmado segue na ampla; eliminação só por fraude |
| Portaria MPOG 4/2018 → IN MGI 23/2023 → **IN Conjunta 261/2025** | Concursos, e não discente; a Res. 61 remete à Portaria 4, hoje revogada. A IN 261 traz: presencial ou, excepcional e motivadamente, telepresencial (art. 18); **filmagem obrigatória** (22); maioria, com avaliação **individual e independente, sem interação** (23); o candidato pode ver a própria gravação (25); recursal distinta (29-31); **prevalece a autodeclaração** se as duas instâncias divergirem sem unanimidade (32) |
| ADC 41 (STF) e Tema 1.420 | Heteroidentificação legítima com dignidade, contraditório e ampla defesa; ato sujeito a controle judicial (fonte secundária) |
| LGPD | Origem racial e dado biométrico são **sensíveis** (art. 5º, II). Bases sem consentimento: obrigação legal e política pública (art. 11, II, a-b). Menores pelo melhor interesse (art. 14). Revisão de decisão automatizada (art. 20). Eliminação ao fim do tratamento, salvo obrigação legal (arts. 15-16) |
| Tabela de temporalidade CONARQ/IFES (Port. AN 92/2011) | **Sem código para heteroidentificação, imagem ou vídeo.** Analogias: inscrições eliminam; resultados e recursos com guarda permanente; matrícula enquanto houver vínculo + 5 anos; com ação judicial, aguarda-se o término |
| PL 2338/2023 (no Senado, pendente na Câmara) | IA como fator determinante na seleção de estudantes é **alto risco** (art. 14, II). **Não há vedação explícita em vigor** à inferência racial por IA. A proibição deste estudo (R-19) é escolha institucional, mais rígida que a lei |

## 4. Pretos e pardos × indígenas

| | Pretos e pardos | Indígenas |
|---|---|---|
| O que se verifica | **fenótipo** no momento do procedimento | **pertencimento étnico**, que não é fenotípico |
| Como | entrevista gravada, com comissão diversa | **análise documental**: declaração do cacique ou vice e mais 2 lideranças, com contato; Funai ou comprovante de residência (Res. 61, art. 3º §2º); Ofício MEC: memorial, ACI e DPE |
| No GPS | Etapa decisória nova (camada A) | **nada novo**: `DocumentoExigido` com recorte por Modalidade e a conferência da 115 já fazem isso |
| Vídeo cabe? | só como meio de colher a imagem (camada B) | **não**: vídeo de indígena seria inferência fenotípica de algo que não é fenotípico |

A separação vale também para a tela. A Etapa de vídeo nunca alcança a lista de indígenas, e a
composição da Etapa diz isso por extenso ([wireframes, aba 3](wireframes.html)).

## 5. O que pede norma e o que é infraestrutura

| Pede autorização normativa (CS, CPVA, Edital) | É infraestrutura que o GPS pode ter sem ela |
|---|---|
| Adotar o vídeo assíncrono como meio, mesmo opcional | Etapa por Modalidade, deliberação, consequência por lista |
| Confirmar com base só no vídeo | Registrar pareceres, desfecho, ausência e recurso do rito atual |
| A regra de deliberação (unanimidade × maioria) | Oferecer as regras como opção do Edital |
| Roteiro: o que dizer, mostrar o documento, duração | Roteiro como texto versionado, configurável |
| Vídeo de menor de idade | Bloquear o vídeo para menor por padrão |
| Prazo de guarda e eliminação do vídeo | Comando de eliminação com prazo como argumento |
| Quem julga o recurso e como (colegiado, síncrono) | Julgador, impedimento e ato de instrução, como hoje |
| Composição da CLVA (≥ 4 com acolhedor × ímpar) | Alocação de membros à Etapa |
| Termo de uso de imagem ou aviso de privacidade específico | Tela de acolhimento com o aviso que a norma aprovar |

Na coluna da direita, **tudo pode ser construído e testado com dados sintéticos** sem tocar
Edital publicado. A coluna da esquerda é do usuário e das instâncias do Ifes.

## 6. Modelos de vídeo: UFC e IFPE, e o Ifes de hoje

| | **Ifes hoje** (28/2026) | **UFC** (Edital 01/2026, SiSU) | **IFPE** (Edital 21/2025; PartiuIF 2026) |
|---|---|---|---|
| Meio | videoconferência síncrona RNP, gravada | vídeo assíncrono, como **triagem** | vídeo assíncrono, como **decisão** |
| Roteiro | entrevista | documento frente/verso (~5 s cada), perfil esquerdo, perfil direito, frente dizendo nome, CPF, "preto(a)/pardo(a)" e data | 3 s de frente, documento e frase padronizada |
| Duração e arquivo | — | ≤ 60 s, contínuo; MP4 ≤ 20 MB; câmera horizontal | contínuo; MP4/MOV ≤ 10 MB; Libras permitida |
| Proibições | estampas, boné, maquiagem | maquiagem, óculos, chapéu, turbante, **filtros, IA, deepfake** (elimina) | acessórios, maquiagem, filtro, edição |
| Envio | — | Portal do Candidato; sem reenvio | Área do Candidato; **autorização de imagem obrigatória** |
| Decisão | CLVA (≥ 4; "unânime", ambíguo) | **o vídeo só confirma**; a comissão encaminha ao presencial; não enviar também encaminha; **indeferir só no presencial** | comissão de 3 decide pelo arquivo, por maioria |
| Recurso | CPVA | Coordenação do SiSU, irrecorrível | escrito, **sem novo vídeo**, à comissão recursal distinta |
| Aderência ao Ofício MEC 3/2025 | síncrono: adere | parcial: nega só no presencial | baixa: decide e julga só pelo arquivo |

**Leitura.** O modelo UFC é o único que reduz a carga das entrevistas sem tirar do candidato o
direito de ser visto ao vivo antes de perder a reserva, e é o que este estudo adota (R-11). Do IFPE,
vale a Libras e o limite de arquivo baixo. A decisão só pelo arquivo, sem nova oitiva no recurso,
não deve ser copiada.

## 7. Lacunas e dúvidas normativas

São do usuário e das instâncias do Ifes. O estudo não presume nenhuma resposta. O "Recomendação"
é a opção que deixa menos risco, e não uma decisão.

| # | Pergunta | Fatos | Recomendação |
|---|---|---|---|
| **P-0** | O vídeo assíncrono pode ser adotado? Por qual ato? | Res. 61 manda presencial; Ato 12 abriu só a videoconferência, excepcional; Ofício MEC pede síncrono | Proposta à CPVA para alterar a Res. 61 pelo CS, com o modelo "só confirma". Até lá, a camada B fica só em desenvolvimento |
| **P-1** | Aceitar a L-2 (Etapa por Modalidade)? | DP-10 deixou "decidir por família, quando houver intenção de operá-la" | **Decidida em 13/11: sim.** A Etapa declara as Modalidades que alcança |
| **P-2** | Consequência do "não confirmada": fica na ampla ou elimina? | Res. 61, art. 16: falsidade elimina; 28/2026: fica na ampla; 57/2026, 8.11: ausência elimina; Lei 15.142 e IN 261: ampla | **Decidida em 13/11:** o Edital declara (R-2), com "sai da reserva e fica na ampla" como padrão |
| **P-3** | Regra de deliberação | Res. 61, art. 15, III, b, é ambígua; editais do Ifes leem "recusa só por unanimidade"; MEC: maioria; IN 261: maioria, com prevalência da autodeclaração se as instâncias divergirem | **Decidida em 13/11:** o GPS oferece as três, e o Edital escolhe. Qual delas os Editais do Ifes usarão continua sendo pergunta à CPVA |
| **P-4** | Composição: ≥ 4 com acolhedor (Ato 15) × ímpar (MEC) | 3 entrevistadores + 1 acolhedor satisfaz os dois | Painel de 3 que dão parecer; acolhedor fora da contagem. No vídeo, a tela de acolhimento não substitui o acolhedor: na entrevista ao vivo ele continua |
| **P-5** | Recurso: a CPVA julga em colegiado? Nova entrevista síncrona? | GPS: julgamento singular; MEC: novo grupo, síncrono | A 1ª entrega usa o julgador do 018 e a gravação; colegiado e oitiva são spec posterior |
| **P-6** | Ausência ao ao vivo: elimina ou fica na ampla? | Ato 12: ausência após 3 falhas; Parecer 02: falta de tecnologia não elimina | Ocorrência com a consequência do Edital; falha técnica nunca é ausência |
| **P-7** | Vídeo de menor de idade | Res. 61 exige acompanhamento em tempo real; vídeo em casa não reproduz isso | **Indisponível para menor** no MVP; menor vai ao vivo |
| **P-8** | Roteiro: mostrar documento no vídeo? fala obrigatória? duração? | UFC e IFPE mostram o documento; minimização (LGPD, art. 6º, III) | Documento sim (identidade), CPF não falado; Libras ou cartão; teto técnico, sem cronômetro |
| **P-9** | Sigilo e acesso | IN 261, art. 25: o candidato vê a própria gravação | Termo de sigilo da comissão; o titular assiste ao próprio vídeo (R-24) |
| **P-10** | Guarda do vídeo | sem código na tabela do CONARQ; CPVA (2020) sem local definido; Protocolo II: "arquivada no processo" | Consulta ao arquivo institucional e ao encarregado de dados. O GPS guarda o hash e a trilha para sempre; o arquivo, conforme a resposta |
| **P-11** | Lista pública por Modalidade expõe a autodeclaração | governança aberta desde a 063; o Ifes já publica por modalidade | Publicar só nome e desfecho (R-9) |
| **P-12** | A videoconferência atual tem base vigente? | Ato 12 condicionado à suspensão das aulas; homologação não localizada; o 28/2026 ainda cita a pandemia | **Achado, e não escopo**: registrar para a CPVA. Afeta a camada A tanto quanto a B |

Não foram lidos: o Protocolo I da CPVA, a Res. CONSUP/IFPE 106/2021, o acórdão integral da ADC 41
e o desfecho do caso UFOB no TRF1. Ficaram sem verificação: a homologação dos Atos 12 e 15 e uma
tabela de temporalidade mais nova da Rede Federal.

## 8. Restrições técnicas que o vídeo encontra

- **Formato.** O `MediaRecorder` produz WebM no Chrome e no Firefox, e MP4 no Safari. Os dois são
  aceitáveis por assinatura (EBML `1A45DFA3`; `ftyp`), e não se transcodifica. Se o WebM toca no
  navegador da comissão é pergunta da POC.
- **Tamanho e tempo.** Com o roteiro da UFC (~1 min) a ~1 Mbit/s, o vídeo fica em ~8 MB. Com folga
  para 3 min, ~25 MB. Isso não cabe no limite de 10 MiB, nos 12 MB do nginx nem no gunicorn
  síncrono: o envio vai em partes.
- **CSP e permissões.** `media-src 'self' blob:` e `Permissions-Policy: camera=(self),
  microphone=(self)` só na página de gravação. Sem isso, a prévia some em silêncio.
- **"Sem filtro" não é garantível no navegador.** Câmera virtual e embelezamento do sistema
  operacional escapam à página. A garantia é processual: a R-11 encaminha a dúvida ao ao vivo.
- **Reprodução.** `<video>` com entrega mediada e `Range`; uma abertura registrada por reprodução.
