# 3. Especificação funcional enxuta

*Proposta de estudo, e não spec do Spec Kit. Os identificadores daqui (`R-`, `E-`) são locais a este
documento e não entram na matriz de rastreabilidade. Quando o usuário decidir as pendências do
[diagnóstico](01-diagnostico.md#7-lacunas-e-dúvidas-normativas), cada parte vira uma pasta em `specs/`
pelo `/speckit-specify`, com `FR-` da faixa global.*

## 3.1 Duas camadas, e por que nessa ordem

A verificação por vídeo não existe sem a verificação. Hoje o GPS **não tem** heteroidentificação:
ela acontece fora do sistema, por videoconferência na RNP ou presencialmente, e todas as specs a
mandam para "spec própria" ([diagnóstico §2](01-diagnostico.md#2-o-que-o-gps-tem-hoje)). Um módulo
de vídeo construído antes seria a estrutura paralela que o pedido proíbe: guardaria pareceres que
nenhum Resultado de Etapa lê e decisões que nenhuma lista obedece.

| Camada | O que é | Precisa de autorização normativa nova? |
|---|---|---|
| **A. O procedimento no GPS** | Etapa de verificação, alcance por lista, pareceres, deliberação, consequência, recurso. O meio continua o de hoje: entrevista ao vivo, gravada fora do sistema | **Não.** É o rito da Res. CS 61/2019 e dos Editais 28, 35, 46 e 57, registrado no sistema |
| **B. O vídeo assíncrono** | Um meio a mais de colher a imagem, opcional para o candidato, só para confirmar | **Sim.** Nenhum Edital nem protocolo do Ifes o prevê hoje |

A camada B fica atrás de uma chave desligada por padrão e **recusada em produção**, e só se habilita
quando um protocolo aprovado existir e o Edital o citar.

## 3.2 Regras de negócio

### Camada A: o procedimento

- **R-1 · Alcance por lista.** A Etapa de verificação declara as Modalidades que alcança. Ela vale
  só para inscrições cuja Modalidade declarada está entre elas. Quem está só na ampla nunca é
  alcançado. Esta é a lacuna L-2, e o barema por curso precisa da mesma peça.
- **R-2 · Consequência por lista.** A Etapa declara o efeito do desfecho desfavorável:
  - **retirar da reserva**: a inscrição continua na ampla, como no 28/2026 (8.10) e no 46/2026;
  - ou **eliminar**, como na leitura de ausência do 57/2026 (8.11).

  É dado normativo do snapshot, com classificação de mutabilidade. Hoje `ELIMINADA` tira a pessoa de
  todas as listas, e é isso que a R-2 corrige.
- **R-3 · Critério só fenotípico.** O parecer não aceita documento pretérito, ascendência nem
  fotografia anterior como prova. O formulário não oferece campo para isso.
- **R-4 · Colegiado com regra declarada.** A Etapa declara o tamanho do painel
  (`evaluations_per_registration`: os entrevistadores, sem o acolhedor do Ato 15) e uma de três
  regras de combinação:
  - confirma por maioria (Ofício MEC 3/2025; IN 261);
  - confirma só por unanimidade (leitura literal da Res. 61, art. 15, III, b);
  - recusa só por unanimidade (leitura dos editais do Ifes).

  A escolha entre elas é a P-3. Cada membro registra o seu parecer **sem ver o dos outros** até
  registrar, como a avaliação "individual e independente" da IN 261, art. 23. A deliberação aplica a
  regra, e a presidência confirma, como na consolidação de hoje.
- **R-5 · Fundamentação.** O desfecho desfavorável exige motivo, por lista fechada mais texto livre.
  O motivo sai no Resultado da Etapa, para o candidato poder recorrer.
- **R-6 · Ausência.** O não comparecimento vira Ocorrência, que já existe. A consequência é a da R-2
  ou outra que o Edital declarar (P-6).
- **R-7 · Menor de idade.** Se o candidato tinha menos de 18 anos na data da verificação, a tela da
  comissão mostra a marca "menor". A deliberação exige registrar a presença do responsável, ou a do
  servidor indicado pela comissão (28/2026, 6.9.2 e 6.9.3).
- **R-8 · Recurso.** Cabe recurso contra o Resultado da Etapa, e por isso a Etapa precisa ser
  visível ao titular, ou seja, enumerada no marco. Julga quem tem `recurso:julgar` no escopo (a
  CPVA). Quem deu parecer nesta Etapa fica impedido, pela regra que já existe
  (`recursos/domain/elegibilidade.py`).
- **R-9 · Publicação mínima.** A lista pública traz o nome e o desfecho, e nunca imagem, motivo
  detalhado ou parecer individual. O motivo vai só ao titular.

### Camada B: o vídeo, se e quando autorizado

- **R-10 · Opção, nunca obrigação.** Quando a Etapa admite o vídeo, o candidato escolhe entre o
  vídeo e a entrevista síncrona, presencial ou por videoconferência, que é a forma do Ofício MEC
  3/2025, item 17. Não escolher equivale a "ao vivo". O vídeo nunca é o único caminho.
- **R-11 · O vídeo só confirma.** Pelo vídeo, a deliberação tem dois desfechos: **confirmada** ou
  **encaminhada à entrevista ao vivo**. A não confirmação só existe depois da entrevista ao vivo.
  - O parecer "não dá para confirmar pelo vídeo" não é voto contra.
  - Basta **um** desses pareceres para encaminhar, quando a regra é a unanimidade. Na maioria, o
    encaminhamento segue a mesma regra.

  É a regra que dá segurança jurídica ao experimento: ninguém perde a reserva sem ter sido visto
  ao vivo. É também o modelo da UFC (Edital 01/2026, itens 7.2.2 a 7.2.4 e 8.6), o único dos
  examinados que nega só no presencial.
- **R-12 · Não enviar não é ausência.** Quem escolheu o vídeo e não o enviou no período vai para a
  agenda da entrevista ao vivo. Não sofre a consequência da R-6.
- **R-13 · Gravação contínua, na página.** O vídeo nasce na página do GPS, por câmera e microfone,
  com permissão do navegador e em uma tomada só:
  - não há upload de arquivo da galeria;
  - não há corte, pausa nem edição;
  - "parar e recomeçar" descarta a tomada inteira.

  O guia de enquadramento é desenhado por cima da prévia e não entra na gravação.
- **R-14 · Roteiro versionado.** O roteiro (passos e falas) é texto da unidade, versionado. O vídeo
  guarda a versão exibida e os instantes em que o candidato passou de um passo a outro. Isso ajuda a
  comissão a achar o trecho, e não serve para julgar ritmo.
  - Não há tempo mínimo nem cronômetro por passo.
  - Há só um teto técnico generoso (por exemplo, 3 minutos), declarado antes de começar.
  - O roteiro de referência é o da UFC, que cabe em ~1 minuto: documento, perfil esquerdo, perfil
    direito e frente com a fala. O CPF não é falado (P-8).
- **R-15 · Revisão local.** Antes do envio, o candidato assiste ao vídeo e pode regravar quantas
  vezes quiser. **As tomadas não enviadas nunca saem do aparelho**: minimização (LGPD, art. 6º, III).
- **R-16 · Envio definitivo e comprovante.** O envio é autenticado pela sessão do portal e pela
  titularidade da inscrição, e acontece em partes retomáveis. O servidor:
  1. confere a assinatura do contêiner (WebM ou MP4), o tamanho e a duração;
  2. calcula o SHA-256;
  3. emite o comprovante com data, duração e resumo.

  Até a primeira abertura por um membro da comissão, o candidato pode pedir a troca. A troca nova
  substitui a anterior, e as duas ficam na trilha. Depois da primeira abertura, não há troca.
- **R-17 · Armazenamento privado.** O vídeo vai para `ArmazenamentoPrivado`, sob a raiz dos arquivos
  dos candidatos, sem URL pública. Fica associado a inscrição × Etapa, com hash. Nenhum serviço de
  terceiros o recebe, e não há transcodificação externa.
- **R-18 · Reprodução mediada e registrada.** Só abre o vídeo:
  - quem está alocado à Etapa e tem a Atribuição daquela inscrição;
  - ou quem julga um recurso dela, por ato de instrução.

  A entrega é mediada, com conferência do hash e suporte a `Range`. A trilha registra **uma**
  abertura por sessão de reprodução, e não cada pedaço. A tela não oferece baixar. Isso não impede a
  captura de tela, e o termo de sigilo da comissão cobre o resto (P-9).
- **R-19 · Nenhuma inferência automática.** O sistema não analisa o vídeo de nenhuma forma:
  - nada de detecção de rosto, de tom de pele ou de "qualidade";
  - nada de miniatura gerada;
  - nada de transcrição.

  Um teste guardião recusa dependência de visão computacional no grupo de produção. A única
  verificação automática é técnica: contêiner, duração e hash.
- **R-20 · Falha técnica.** Falha de câmera, de permissão ou de envio nunca vira ausência:
  - o envio retoma de onde parou;
  - depois de três tentativas sem sucesso, a página oferece "pedir entrevista ao vivo" e registra o
    relato;
  - o link "Não consigo usar a câmera" está em todas as telas.
- **R-21 · Acessibilidade.** Toda instrução existe em texto e é anunciada ao leitor de tela, e os
  passos avançam por toque ou teclado, e não por relógio. A fala pode ser substituída por:
  - cartão escrito;
  - Libras;
  - nenhuma fala, quando o protocolo permitir (P-8).

  Quem não pode usar o vídeo tem a entrevista ao vivo, e o atendimento presencial quando a unidade
  o oferecer.
- **R-22 · Menor de idade não grava.** A Res. 61 (art. 12 §§1º-2º) garante ao menor acompanhamento
  em tempo real, pelo responsável ou por um servidor, e um vídeo gravado em casa não reproduz isso.
  - Se o candidato tem menos de 18 anos no início do período, a opção do vídeo não aparece, e ele
    vai ao vivo.
  - Se um protocolo futuro admitir o vídeo para menores, ele precisará dizer como o responsável
    participa (P-7).
- **R-23 · Retenção.** O vídeo é evidência do ato, e não o ato: o ato é o Resultado da Etapa, que é
  append-only e nunca se apaga. Há duas formas possíveis de reter o vídeo (P-10):
  - **(a)** o arquivo é eliminado depois do prazo da tabela de temporalidade, contado do fim do
    certame ou do trânsito do último recurso, e ficam o hash, a duração e a trilha;
  - **(b)** ele é guardado pelo prazo integral do processo seletivo.

  O comando de eliminação seguiria o padrão de `excluir_registros_do_piloto`: argumento explícito,
  prazo conferido e evento na trilha.
- **R-24 · O titular vê o próprio vídeo.** Do acompanhamento, o candidato assiste ao vídeo que
  enviou, pela mesma entrega mediada (IN 261, art. 25, por analogia). Ele não vê os pareceres
  individuais, só o desfecho e o motivo.

## 3.3 Estados

### Da inscrição na Etapa de verificação (camada A)

```
não alcançada ── (Modalidade fora do alcance) ── fim
alcançada
  └─ aguardando procedimento ──► em análise ──► deliberada ──► resultado publicado
                     │                │             (confirmada | não confirmada)
                     └─ ausente (Ocorrência)        └─ recurso ─► julgado (mantida | reformada)
```

### Do meio, quando o vídeo existe (camada B)

| Estado | Quem vê | Sai para |
|---|---|---|
| `escolha pendente` | candidato | `vídeo escolhido` · `ao vivo escolhido` · (fim do período) `ao vivo` |
| `vídeo escolhido` | candidato | `vídeo recebido` · `falha relatada` · (fim do período) `ao vivo` |
| `vídeo recebido` | candidato, comissão | `em análise` (primeira abertura) · `vídeo recebido` (troca, antes da abertura) |
| `em análise` | comissão | `confirmada` (regra satisfeita) · `ao vivo` (encaminhada) |
| `falha relatada` | presidência | `ao vivo` |
| `ao vivo` | candidato, comissão | entra no fluxo da camada A como entrevista |

O meio nunca produz "não confirmada". Só `ao vivo` produz.

## 3.4 O que reaproveita e o que é novo

| Necessidade | Reaproveita | Novo |
|---|---|---|
| Etapa de verificação | `EtapaAvaliacao` forma `DECISORIA` com rótulos do Edital | alcance por Modalidade (R-1); efeito por lista (R-2) |
| Comissão (CLVA) | `MembroComissao` + `AlocacaoEtapa` | nada |
| Pareceres e deliberação | `Atribuicao`, `Avaliacao`, `ConclusaoAvaliacao`, consolidação | regra de combinação decisória (R-4); parecer às cegas |
| Ausência | `registrar_ocorrencia` | nada |
| Recurso e CPVA | `Recurso`, papel julgador, `Impedimento`, ato de instrução | nada na 1ª entrega; 2ª instância é pendência (P-5) |
| Próximo passo do candidato | `situacao_da_inscricao`, `Acao` | um degrau: verificação pendente / agendada / em análise |
| Pendências da gestão | `andamento.py`, `centro.py`, `atividades.py` | uma natureza: "verificação da autodeclaração" |
| Arquivo privado e leitura registrada | `ArmazenamentoPrivado`, `portal/arquivos.py`, `record_event` | aceitar vídeo; entrega com `Range`; envio em partes |
| Aviso por e-mail | avisos complementares (066) | origem nova: resultado e agenda da verificação |
| Chave de funcionalidade | padrão `_exigir` de `production.py` | `VERIFICACAO_POR_VIDEO` (recusada em produção até o protocolo) |
| Indígenas | `DocumentoExigido` com recorte por Modalidade + conferência (115) | **nada**: é análise documental, outra Etapa ou a própria conferência |

## 3.5 Fora do MVP, de propósito

- **Agenda individual da entrevista ao vivo**, com horário por pessoa e sala. Na primeira entrega
  ela fica como hoje: a comissão marca fora e registra o desfecho. Ela entra depois, porque serve a
  qualquer entrevista, e não só a esta (registro de 09/10).
- **Composição da comissão com validação de gênero e cor dos membros.** Seria tratar dado sensível
  de servidor. A presidência declara que a composição atende à norma, e o ato de designação fica
  fora do sistema.
- **Transcodificação, marca-d'água e player próprio.** Ficam o `<video>` do navegador e o contêiner
  original.
- **Reverificação "a qualquer tempo"** (28/2026, 6.8), por denúncia. É outro procedimento, com
  contraditório próprio.
