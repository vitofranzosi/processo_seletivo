# Diagnóstico e alternativas — Entrega documental controlada

**Data**: 2026-11-04, revisto no mesmo dia. **Base**: `main` em `83cd5863`, mais a implementação da
`115` no PR vitofranzosi/processo_seletivo#369 (branch `claude/115-documentos-na-convocacao`, em
`a8e1f68b` em 04/11, conferido na consolidação), **aberto e sem merge**. Os caminhos são relativos a `backend/processo_seletivo/`. Quando o
código citado só existe no PR #369, a referência diz **[#369]**.

Este documento não repete a auditoria de matrícula e dossiê nem o complemento dela, de 03/11. Ele
parte da §10.4 do complemento, que já registrou esta lacuna, e responde só ao que a spec `117`
precisa decidir.

> **Revisão de 04/11.** A primeira versão propunha três coisas, todas revistas a pedido do usuário:
>
> - uma marca no Documento Exigido da convocação, publicada no PDF e retificável;
> - um papel com designação feita pela presidência;
> - um pacote "do Edital".
>
> As §4.2, §4.3 e §4.4 registram o que mudou e por quê. A §5 dá a base do limite de tamanho.
>
> **Consolidação de 04/11.** As decisões D-009 a D-013, D-016, D-019 a D-021 foram aprovadas pelo
> usuário. A §5 foi reescrita: a versão anterior presumia que o buffer do nginx liberaria o worker,
> e isso não foi verificado.

---

## 1. Estado da base

| Fato | Evidência |
|---|---|
| A spec da `115` está na `main` | PR #368 mergeado; `specs/115-documentos-na-convocacao/spec.md` |
| A implementação da `115` **não** está na `main` | PR #369 aberto, conferido em 04/11; a `main` não tem `ItemDaListaDaConvocacao`, `ApresentacaoDeDocumento` nem `ConferenciaDeDocumento` |
| Na `main`, documento só existe na inscrição | `inscricoes/models.py:329-384` (`DocumentoSubmetido`) |
| A spec `116` (Loteria Federal), também aberta, reserva até o requisito três mil seiscentos e cinquenta e dois e o critério mil e cem | PR #370 |

**Consequência:** a `117` depende do merge do PR #369. A sessão de implementação começa conferindo
esse merge.

## 2. Respostas às dez perguntas

### 2.1 Como os documentos são armazenados e recuperados

- **Raiz privada única**, fora da árvore estática e sem URL: `ArmazenamentoPrivado`, com
  `base_url=None`. Sem raiz configurada, falha na subida (`inscricoes/storage.py:28-39`; raiz em
  `config/settings/base.py:361`).
- **Nome físico opaco**: `inscricoes/{inscricao}/{uuid}.pdf` (`storage.py:64-72`) e
  `convocacoes/{chamada}/{uuid}.pdf` [#369]. O nome enviado fica só como metadado (`nome_original`).
- **Hash SHA-256 gravado no envio** (`DocumentoSubmetido.content_hash`;
  `ApresentacaoDeDocumento.content_hash` [#369]). O documento da inscrição é imutável depois do envio
  (FR-054 da `009`, `inscricoes/models.py:369-384`).
- **A entrega reconfere o hash sobre a cópia que serve**: `copia_verificada` (`portal/arquivos.py:54-69`)
  copia para `SpooledTemporaryFile` (em memória até 2 MB, `:24`) e calcula o resumo na mesma passagem.
  É a FR-053a da `009`, estendida à convocação pela FR-3605 da `115`.
- **Aproveitamento por referência, sem cópia** [#369]: a apresentação é arquivo **ou** referência, e a
  referência nunca aponta outra referência (FR-3619 da `115`). `fonte_do_arquivo` ([#369]
  `convocacao/application/documentos.py:390`) devolve o arquivo em um passo.

### 2.2 Como identificar os aptos para formalização

- `DESFECHOS_QUE_INCLUEM = (ACEITE, REGULARIZACAO)` (`convocacao/domain/nomes.py:100`).
- **Vigência é derivada**: vigente é a convocação e o desfecho que ninguém sucedeu
  (`convocacao/models.py:7`, `:132-135`, `:288-310`; FR-273 da `019`).
- A condução da `115` já marca *"Apto para formalização"* [#369] (`interface/views.py:8311`).
- **Não existe seletor "aptos do Edital".** A população da `031` (`matriculas/application/populacao.py:203-229`)
  inclui quem ainda não respondeu e não serve.

### 2.3 O que determina o conjunto documental

- [#369] A raiz de cada chamada congela a lista da convocação, com a versão que a fundamentou
  (FR-3573 da `115`). A conferência vigente do item aponta a apresentação julgada e **copia o hash
  conferido**.
- A inscrição enviada tem um `DocumentoSubmetido` por requisito atendido.
- **Nada diz para que serve cada documento**, isto é, se é prova para a comissão ou necessário à
  formalização. O momento ([#369] `editais/models/documentos.py`) diz **quando** se pede, e não
  **para quem** vai. O recorte por modalidade (`forma_do_recorte`, `modalidade_id`) sugere documento
  de reserva de vagas, mas não o define.

### 2.4 Como o GPS exporta hoje

Uma exportação só, a da `031` (`interface/views.py:5660-5753`; `matriculas/application/exportar.py:187-302`):

- população escolhida, sem padrão (FR-433 da `031`);
- prévia que não grava, com assinatura;
- POST que recompõe e recusa se mudou (409 `export_preview_stale`);
- planilha em memória, entregue como `attachment` e **não guardada** (FR-456 da `031`);
- registro append-only `GeracaoDeArquivo` (`matriculas/models.py:27-70`), **sem hash do arquivo e sem
  histórico visível**.

Não há ZIP nem exportação de documento em lugar nenhum.

### 2.5 O que da `031` se reaproveita

| Controle | Reaproveita? |
|---|---|
| Capacidade própria, **não concedida por padrão**, separada de `inscricao:consultar` (FR-455 da `031`; papel `exportador`, `interface/identidade.py:113-127`) | **Sim**, é o molde |
| Prévia sem gravação, assinatura, recomposição na confirmação | **Sim** |
| Arquivo não guardado (FR-456 da `031`) | **Sim**, num temporário sem nome, porque o pacote não cabe em memória |
| Registro append-only com ids, sem dado pessoal | **Sim**, com o que falta à `031`: hash do pacote, resultado e histórico visível |
| A geração fora da trilha (`matriculas/domain/nomes.py:80-89`) | **Não**: aqui o ato precisa estar na trilha |

### 2.6 Permissões por unidade, Processo e Perfil

- **O único eixo sistêmico é a unidade.** O `Vinculo` da `107` é pessoa × unidade × papel, sem
  Processo nem Perfil (`seguranca/models.py:61-82`).
- Papel operacional é concedido por quem tem `acesso:gerir` na unidade, com motivo, sem
  autoconcessão, com revogação append-only (`seguranca/application/acessos.py:163-263`). As permissões
  são recalculadas dos vínculos a cada requisição (`interface/identidade.py:207-210`).
- **Por Edital e Perfil**, só a alocação à conferência da `115` [#369], que é de **membro da
  comissão** e dá competência de conferir (FR-3595 da `115`).
- **Recusas**: sem capacidade, 403; escopo alheio ou inexistente, 404 filtrado na consulta
  (`seguranca/application/authorization.py:117-146`). Todo 404 novo entra no inventário da `033`.
- **A barra não consulta o banco** (`interface/navegacao.py:9`). Item novo depende de capacidade que
  já venha dos vínculos.
- **Perfil não tem unidade ofertante** (`editais/models/perfis.py:26`).

### 2.7 Como registrar sem duplicar

O registro guarda **identificadores e hashes**, nunca bytes. O arquivo de origem continua único. O
pacote é montado num temporário sem nome e descartado.

### 2.8 O que a FR-069 da `009` proíbe, e por quê

> *"Cada documento DEVE poder ser aberto pela interface, exibido no navegador quando o formato
> permitir; baixar DEVE existir apenas como ação secundária individual. NÃO DEVE existir download em
> lote, exportação, planilha nem painel."*

**Origem.** A `009` tirava a seleção de um circuito:

> *"a equipe baixa arquivo por arquivo depois do encerramento, reorganiza em armazenamento local ou
> Drive, e passa a controlar candidatos, documentos e avaliações em planilhas"*
> (`specs/009-inscricao-simples-documentos/spec.md:31-33`).

O lote recriaria a pasta de rede dentro da seleção, com todos os inscritos. Acompanham a proibição:

- a SC-016 da `009`;
- a lista do que fica fora (`spec.md:780`);
- a docstring da view (`interface/views.py:5774-5775`).

A FR-3606 da `115` reafirmou a proibição na convocação.

| Risco | Tela de inscrições (`009`) | Exportação aos aptos (`117`) |
|---|---|---|
| População | todos os inscritos | só aptos, e só os que o destinatário seleciona dentro do alcance dele |
| Conteúdo | tudo o que veio | só os documentos definidos para a formalização |
| Finalidade | nenhuma: a seleção avalia na tela | custódia pelo setor competente, que exige cópia |
| Quem baixa | quem conduz a seleção | o setor, sem competência de seleção, com acesso concedido pela gestão de acessos |
| Cópia fora do GPS | presente | **continua**: é inerente à finalidade e dependência institucional (§10.6 do complemento) |
| Concentração num arquivo | presente | **continua**, menor; exige limite, registro e nenhuma guarda |

**Conclusão:** a exceção estreita se justifica, e a revogação não. A redação proposta está na D-016 da
spec.

### 2.9 Consulta sem download e comportamento nas falhas (conferido no código)

| Situação | Inscrição (`main`) | Convocação [#369] |
|---|---|---|
| Visualizar | `inline`, `no-store`, evento `CONSULTAR_DOCUMENTO` | idem, `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` |
| Baixar (`?baixar=1`) | **mesmo evento**: a trilha não distingue (`views.py:5795-5815`) | razão ganha *", baixado"* (`views.py:8686`) |
| Nome do arquivo baixado | `nome_original`, escolhido pelo candidato (`portal/arquivos.py:48`) | idem |
| Hash divergente | `INTEGRIDADE` gravado, 409, nada servido (`views.py:5818-5834`) | idem (`views.py:8662-8692`) |
| **Arquivo ausente** | **`FileNotFoundError` em `arquivo.open` (`portal/arquivos.py:64`) → 500, sem evento** | **idem**: `copia_verificada(fonte)` antes de qualquer tratamento (`views.py:8660`) |

Nenhum caminho de produção trata `FileNotFoundError` ou `OSError`.

### 2.10 O esforço real

Cenário A: 40 aptos com 5 documentos de formalização cada.

| Caminho | Acesso legítimo do setor? | Gestos |
|---|---|---|
| `main` | não há documento de convocação | — |
| PR #369, pelo predicado da `115` | só alocando o servidor à conferência (ganha conferir) ou dando-lhe o papel Gestor (ganha a unidade) | ≈ 680: 40 páginas, 200 aberturas, 200 downloads, 200 renomeações, 40 pastas |
| Página restrita (B) | sim | ≈ 240: 200 downloads com nome do sistema e 40 pastas |
| Exportação por pessoa (C) | sim | ≈ 41 |
| Exportação do recorte (C) | sim | 4: selecionar, verificar, ler o resultado, baixar |

## 3. Alternativas

**A — Consulta individual existente.** Sem infraestrutura nova. Mas **o setor não tem acesso
legítimo**, e dar-lhe o predicado da `115` é dar competência de conferir. Insuficiente.

**B — Página restrita ao setor.** Aptos do alcance, documentos de formalização, visualização como
padrão e download individual registrado com nome do sistema. **Resolve a separação e a minimização.**
Basta para processos pequenos (bolsista). No Cenário A, sobram 200 downloads.

**C — Exportação controlada.** ZIP com manifesto, por pessoa, por seleção ou por recorte autorizado.
Tem verificação com o resultado antes do download, temporário sem nome e registro com hash. **Resolve o esforço.** O risco é a
concentração num arquivo, mitigada pelo alcance, pelo limite e pelo registro. Depende de revisar a
FR-069 da `009` e a FR-3606 da `115`.

**D — Encaminhamento ou integração externa.** Nada no repositório demonstra que o SIGAA, o SIPAC ou
outro sistema receba documento. A auditoria cita o SIGAA só como destino da planilha da `031`. A
decisão 7 da §10.1 do complemento põe a integração obrigatória fora do escopo. **Evolução futura,
condicionada** a capacidade demonstrada pela TI.

| Critério | A | B | C | D |
|---|---|---|---|---|
| Valor operacional | baixo | médio | **alto** | alto, se existir |
| Redução de esforço (Cenário A) | nenhuma | ~65% | **~99%** | ~100% |
| Segurança e privacidade | ruim | **boa** | boa, com controles | depende do externo |
| Complexidade | nenhuma | baixa | média | alta, desconhecida |
| Implantação e manutenção | — | baixa | baixa-média | alta |
| Compatível com a arquitetura | sim | sim | sim, molde da `031` | não demonstrado |
| Facilidade de uso | ruim | boa | **boa** | transparente |
| Dependências | — | conceder acesso | conceder acesso; aprovar a exceção | TI, sistema externo |

**Recomendação: B + C numa página só; D como evolução; A não é alternativa.**

## 4. Fronteira da entrega

### 4.1 População

| Caso | Entra? |
|---|---|
| Aceite ou regularização vigente | sim |
| Desfecho que incluía e foi sucedido por outro | **não**: vale o vigente |
| Convocação sucedida (correção de vencimento ou fundamento) | lê a vigente da chamada |
| Convocações múltiplas da mesma inscrição | vale a **chamada mais recente** |
| Reclassificação por Resultado sucessor sem novo desfecho | segue o desfecho vigente; o GPS não reinterpreta a `018`/`019` aqui |
| Sem resposta, não atendimento, desistência, inércia, indeferimento | não |
| Perfil fora do alcance do destinatário | não aparece; 404 na URL direta |

### 4.2 Documentos: a revisão

**O que a primeira versão propunha.** Uma marca no Documento Exigido **da convocação**, publicada no
PDF e retificável. **Por que não serve**, nos quatro cenários do pedido de revisão:

| Cenário | Marca na convocação | Definição interna por Edital (proposta revista) |
|---|---|---|
| **A** — documento da inscrição aproveitado na convocação | funciona, pelo item da convocação | funciona; o mesmo arquivo sai **uma vez** |
| **B** — documento só da inscrição, necessário ao setor | **falha**: obrigaria a criar um documento da convocação com aproveitamento, ou seja, a **duplicar a exigência**, e a fazer a comissão conferir de novo. Em Edital publicado nem isso dá, porque o aproveitamento não é retificável (decisão da `115` sobre momento e aproveitamento) | funciona: o requisito da inscrição entra na definição |
| **C** — documento só da seleção (classificação, reserva) | funciona, se não marcado | funciona, se não incluído. O recorte por modalidade gera **aviso** na definição |
| **D** — documento da convocação que o setor não precisa | funciona | funciona |

E há o problema de fundo, que é a diretriz do pedido. **A marca misturava a obrigação do candidato com
uma decisão interna de encaminhamento.**

- A obrigação (o que apresentar, quando, sob que regra) é conteúdo normativo. Vai no Edital
  publicado, e muda só por Retificação.
- O encaminhamento (qual setor recebe qual documento já coletado) não muda o que o candidato deve
  fazer. Pô-lo no Edital obrigaria a uma Retificação para corrigir uma escolha de rota. E,
  como a marca se lia na versão do item, uma correção de minimização não alcançaria quem já foi
  convocado: **o erro de incluir um laudo não poderia ser desfeito para as chamadas existentes.**

**Proposta revista: a "definição dos documentos para a formalização".**

- É por Edital: um conjunto de requisitos do próprio Edital, **de qualquer momento**, vazio por
  padrão.
- É registrada pela condução do processo, que conhece a finalidade de cada documento que pediu. O
  destinatário não escolhe o que recebe.
- É append-only e versionada, com motivo.
- **Fica fora do conteúdo publicado**: não entra no snapshot, no hash nem no PDF, e não exige
  Retificação.

Respostas às perguntas do pedido:

| Pergunta | Resposta |
|---|---|
| Só na convocação ou no catálogo comum? | Sobre **todos** os requisitos do Edital. Não há catálogo institucional (a QI-3 decidiu que cada Edital declara os seus), e o "catálogo comum" é o Documento Exigido do Edital |
| Identifica a finalidade sem duplicar exigências? | Sim. Não cria Documento Exigido, e o arquivo aproveitado sai uma vez |
| Precisa de atributo novo? | **Sim, mas não no Documento Exigido**: uma tabela pequena por Edital. Nenhum dado existente diz a finalidade |
| Como preservar no momento da convocação? | A **obrigação** já é preservada: a lista congelada da `115`. O **encaminhamento** é preservado **em cada exportação**, que grava a versão da definição aplicada. Congelá-lo na convocação impediria corrigir a favor da minimização |
| Alterações posteriores e chamadas anteriores? | A versão nova vale para toda exportação **seguinte**, inclusive de pessoas de chamadas anteriores. Não muda exportações passadas, que ficam registradas com a versão que aplicaram |
| PDF e Retificação? | **Nem PDF nem Retificação**, porque a obrigação não muda. A Retificação só é necessária se o setor precisar de documento que o Edital **não** exigiu: é obrigação nova do candidato, pelas regras existentes. A transparência ao titular (LGPD, art. 9º) é dever institucional do aviso de privacidade do Edital, e não regra do sistema (pendência 6 da spec) |

### 4.3 Responsabilidade pelo recebimento: a revisão

| Modelo | Escopo | Quem concede | Estrutura nova | Avaliação |
|---|---|---|---|---|
| Só papel novo na unidade | toda a unidade | gestão de acessos (`107`) | entrada no catálogo | **Insuficiente**: o Registro Acadêmico veria bolsistas, e a Coordenação UAB veria alunos. Mistura competências |
| Capacidade pelo modelo existente | toda a unidade | idem | idem | É o mesmo que o anterior: na `107`, a capacidade só se concede por papel |
| Só designação por Edital e Perfil | o Edital, por Perfis | a definir | uma tabela | Preciso, mas a barra não a enxerga sem consulta por requisição (`navegacao.py:9`), e desligar o servidor que sai do setor exige revogar Edital por Edital |
| **Papel + designação, os dois pela gestão de acessos** | o Edital, por Perfis | **`acesso:gerir`**, na unidade do Edital | entrada no catálogo + uma tabela | **Recomendado** |

**Por que os dois, pela mesma mão:**

- **O papel dá três coisas**:
  - o item da barra, sem consulta nova;
  - a alavanca institucional: revogar o papel corta todas as designações de uma vez, quando o
    servidor sai do setor;
  - o "negar por padrão": ninguém o tem.
- **A designação dá o recorte**: o Edital e os Perfis.
- **Sem designação, o papel não dá nada.**
- **A gestão de acessos** já concede com motivo, recusa autoconcessão, registra na trilha da unidade e
  é a função que a `107` criou para isso.

**Por que não a presidência.** O pedido de revisão pede que ela não administre sozinha o acesso dos
setores. Além disso, quem conduz a seleção decidir quem recebe documentos de candidatos borraria a
separação. Ela **vê** as designações do Edital, e não as concede.

### 4.4 Rastreabilidade: a revisão

A primeira versão dizia *"documentação obtida"* e derivava quatro situações por pessoa. Ambas saem.

| Fato | O que o GPS registra | O que o GPS afirma |
|---|---|---|
| Documento visualizado | evento, quando o arquivo é servido `inline` | *"Visualizado"* |
| Download individual | evento, quando o arquivo é servido como `attachment` | *"Download disponibilizado"*. O GPS não sabe se terminou |
| Pacote gerado e disponibilizado para download | registro da exportação, com hash e resultado, gravado depois de montado e antes de a resposta começar. Na geração síncrona, gerar e disponibilizar são o mesmo ato | *"Pacote gerado e disponibilizado para download"*. O GPS não sabe se a transferência terminou |
| Encaminhamento efetivamente realizado | **não há** mecanismo; nada é registrado | nunca |
| Recebimento institucional confirmado | **não há** mecanismo; nada é registrado | nunca |

**Estados derivados.** O histórico de exportações basta. Por pessoa, a página mostra só o **fato**
*"Última exportação: DD/MM, por ‹nome›"*, lido do histórico. Não há situação "obtida", "mudou depois"
ou "deixou de estar apta". O aviso de quem deixou de estar apto depois de exportado fica para depois
(§6 da spec).

## 5. Base do limite de tamanho e o que falta verificar

**O limite inicial é uma coisa, e a capacidade da VM é outra.** O primeiro é um valor configurável
para começar. A segunda só se mede na VM real, que ainda não existe: a
[implantação recomendada](../../doc/implantacao-em-producao-ubuntu.md) não ensaiou nginx, systemd nem
certbot (§0 dela).

### 5.1 O que se sabe

| Fato | Valor | Fonte | Verificado? |
|---|---|---|---|
| Workers | 5 síncronos (2 × vCPU + 1) | §12.1 da implantação | recomendação |
| Tempo-limite do worker | 120 s; nginx `proxy_read_timeout` 130 s | §12.1, §14 | recomendação |
| `/tmp` | `PrivateTmp=yes`, no disco do sistema, de 40 GB, compartilhado | §4, §12.2 | recomendação |
| Buffering de resposta no nginx | **não configurado** na implantação; o comportamento com resposta grande **não foi ensaiado** | §14 | **não** |
| Documento | teto de 10 MiB; média estimada de 1,5 MB | `base.py:365`; §4 | o teto, sim; a média, premissa |
| Transação por requisição | **não há** `ATOMIC_REQUESTS` nas settings | `config/settings/` | sim |

### 5.2 O pior caso que o desenho assume

O desenho **não** presume buffering do nginx nem liberação antecipada do worker:

- **O worker fica ocupado durante toda a transferência.** No gunicorn síncrono, o tempo-limite vale
  para a requisição inteira, e o worker não sinaliza vida ao árbitro enquanto escreve a resposta. Uma
  transferência que passe de 120 s é cortada: o worker é morto, e o cliente recebe um ZIP truncado ou
  um 502.
- **Um ZIP truncado é inválido**: o diretório central fica no fim do arquivo, e os descompactadores o
  recusam. O operador percebe e repete. O registro, gravado antes da transferência, continua dizendo só
  *"gerado e disponibilizado"*, o que é verdade.
- **Disco**: cada geração ocupa até L no `/tmp` privado, sem nome. Com 5 workers, são 5 × L. Se o nginx
  bufferizar (não verificado), pode somar outros L por resposta no disco dele.

### 5.3 O limite inicial

- **Uso esperado.** No Cenário A, 40 × 5 × 1,5 MB = **300 MB**.
- **Transferência.** 400 MB em menos de 100 s, deixando folga para a geração, exige ~32 Mbps
  efetivos entre o servidor e o operador. É plausível na rede institucional, **mas não está
  verificado**.
- **Disco.** O pior caso, 5 × 400 MB, mais 5 × 400 MB se o nginx bufferizar, é 4 GB num disco de
  sistema de 40 GB.

**Proposta aprovada:** 400 MB, configurável (D-019). Acima dele, recusa antes de ler.

### 5.4 O que a validação na VM mede (critério de homologação, não de implementação)

1. O tempo de verificação e de geração de um pacote no limite.
2. O tempo de transferência desse pacote a um operador da rede do setor, com o worker observado.
3. O uso do `/tmp` privado e do disco do nginx durante 2 exportações simultâneas.
4. O comportamento com o tempo-limite forçado: ZIP truncado, registro intacto, temporário liberado e
   trava liberada.

**Se a medição não couber**, a primeira medida é **reduzir o limite**, porque a seleção menor resolve.
A segunda é ajustar o proxy, e é decisão da TI. **Geração assíncrona não entra automaticamente**: só
por decisão do usuário, se as duas não bastarem.
