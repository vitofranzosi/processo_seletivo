# Verificação: Entrega documental controlada ao setor da formalização (117)

Implementação de 04/11/2026, na branch `claude/frosty-curie-806663`, sobre a `main` em `fb0e1ddc`
(com a `115`, a documentação da `117` e a implementação da `116`). As tarefas T001 a T039 estão
marcadas; H01 a H03 são de homologação e ficam com o usuário e a TI.

## A suíte

`cd backend && make lint check test-pg`, com os grupos `navegador` e `assistente` instalados, 4
workers, banco próprio (`DB_NAME=ps117s`):

- `ruff check` e `ruff format --check`: limpos;
- `manage.py check` e `makemigrations --check`: sem pendência;
- pytest: **15409 passed, 12 skipped, nenhuma falha, em 630 s** (os 12 pulados são os doze deliberados que o `AGENTS.md` descreve para quem tem os dois grupos).

`provisionar_papeis` depois da `0001` diz **53 de 53** tabelas append-only protegidas.

O que a feature acrescentou:

| Arquivo | Casos |
|---|---|
| `unit/formalizacao/test_caminhos.py` | 43 (nomes hostis, colisões, neutralização do CSV) |
| `unit/formalizacao/test_conjunto.py` | 13 (seletor: desfechos, sucessões, chamada mais recente, situações, aproveitamento) |
| `unit/formalizacao/test_grafia_da_trilha.py` | 3 |
| `integration/formalizacao/test_definicao.py` | 19 |
| `integration/formalizacao/test_acesso.py` | 25 |
| `integration/formalizacao/test_exportacao.py` | 20 |
| `integration/formalizacao/test_comprovante.py` | 10 |
| `integration/formalizacao/test_falhas.py` | 7 |
| `integration/formalizacao/test_ciclo_de_vida.py` | 8 (transacionais) |
| `integration/formalizacao/test_concorrencia.py` | 3 (transacionais) |
| `interface/test_permissoes_da_formalizacao.py` | 11 |
| `interface/test_vocabulario_da_formalizacao.py` | 10 |
| `interface/test_arquivo_indisponivel.py` | 3 |
| `authorization/test_papel_da_formalizacao.py` | 4 |
| `performance/test_exportacao_de_formalizacao.py` | 2 |
| `navegador/test_jornada_da_formalizacao.py` | 3 |

### SC-1111, medido

No CI e aqui, o Cenário A tem 40 aptos com 5 documentos de 1,5 MB (200 arquivos, 300 MB). A
verificação e a montagem são medidas e relatadas **em separado** pelo próprio teste:

```
[117 · SC-1111] Cenário A: 40 aptos, 200 arquivos, 300 MB — verificação 0.13 s, montagem 0.34 s (transferência não medida no CI)
```

Os dois números são de um Mac com o disco quente: o cache de páginas tem os arquivos que o cenário
acabou de gravar. Eles provam que o código cabe com folga nos 30 s e que não há consulta por pessoa
(a página e a verificação de 5 e de 45 aptos custam o mesmo, com a folga de duas consultas). **Não
dizem nada da VM**: lá a leitura vem do disco frio, e a transferência, que o CI não mede, ocupa o
worker. Isso é o item 5 da homologação, com o roteiro em
`doc/implantacao-em-producao-ubuntu.md` §15.4.

## O que mudou em teste e código existentes, e por quê

| Onde | Mudança | Por quê |
|---|---|---|
| `specs/009-…/spec.md` (FR-069), `specs/115-…/spec.md` (FR-3606) | o texto aprovado da D-016, com a nota de revisão | T002; a nota cita a decisão por assunto, porque `D-016` dentro da spec de outra feature seria lido como decisão dela |
| `portal/arquivos.py` | `copia_verificada` converte `OSError` em `ArquivoIndisponivel` (409) | FR-3695 |
| `interface/views.py` | as views da inscrição, da mesa e da convocação gravam `ARQUIVO_INDISPONIVEL` antes da recusa; o rótulo na trilha | FR-3695 |
| `seguranca/papeis.py`, `AGENTS.md` | +4 append-only; `M` de 49 para 53 | T005 |
| `interface/identidade.py`, `demonstracao.py` | o papel e a descrição; o ícone no seletor; `LIMIAR_DA_BUSCA` de 9 para 10 | o seletor só de papéis continua sem busca com dez papéis |
| `interface/navegacao.py`, `base.html`, `base_de_acesso.html` | a seção Formalização, com o ícone novo `i-pacote` | o guardião exige um ícone por seção; `i-prancheta` é de Minhas Etapas |
| `interface/acessos.py`, `acessos.html` | a seção *Editais da formalização* e o link | T016 |
| `interface/acoes.py` | a ação *Documentos para a formalização* no detalhe do Edital, para a condução e o auditor | o caminho até a definição |
| `auditoria/selectors.py`, `interface/trilha_da_unidade.py` | a trilha do Edital reúne as designações e os documentos da inscrição abertos pelo setor; a da unidade lê a designação como acesso | T035, FR-3668 |
| `tests/migrations/test_migrations.py` | `formalizacao` em `APPS` e cinco gatilhos em `TRIGGERS_POR_APP` | o teste desfaz e refaz o grafo; sem o app, os gatilhos sumiam |
| `tests/seguranca/test_homologacao_preservada.py`, `test_vinculos.py` | 53 tabelas; 10 papéis | contagens literais que a feature sobe |
| `tests/interface/test_shell_da_gestao.py`, `test_folha_estatica.py` | o papel no ator do teste da barra; as folhas novas | idem |
| `tests/test_gramatica_das_portas.py`, inventário da `033` | o módulo novo na varredura; quatro funções classificadas | todo `raise Http404` novo exige linha |

## Divergências entre a implementação e a spec

1. **"Selecionar todos" é o botão *Verificar e exportar todos os aptos*.** A página não tem
   JavaScript (a CSP o permitiria por arquivo, mas a tela não precisa dele): o alcance *recorte*,
   que a FR-3682 já define como "todos os aptos do alcance", é um botão, e a seleção marcada é o
   outro. O Cenário A cabe em **três** gestos, e não quatro (SC-1101). O quickstart diz "marca
   *Selecionar todos*"; o efeito é o mesmo.
2. **Os avisos da definição ficam visíveis ao lado de cada documento**, e não aparecem "ao marcar"
   (FR-3658): pela mesma razão, sem JavaScript. Eles não impedem a gravação.
3. **A ordem das recusas no download** é a da matriz primeiro e o comprovante depois: quem perdeu o
   papel recebe 403 e quem perdeu a designação, 404, antes de o comprovante ser lido; o
   comprovante de outro servidor designado é *verificação inválida*. Os dois acontecem antes de
   qualquer arquivo ser lido, como a FR-3689a manda. O comprovante "de outra unidade" nunca chega
   ao download — o Edital de outra unidade é inexistente —, e por isso é provado em
   `comprovante.conferir`.
4. **A exceção inesperada responde 500**, com a página própria (*"A exportação não foi
   concluída…"*), e não a genérica: é falha, e não recusa (FR-021 da `002`).
5. **A designação no modo de demonstração** não passa pela tela de Acessos, que é só da entrada
   institucional (107). Os testes de tela e a demonstração gravam a designação direto; a tela de
   Acessos é provada pela entrada institucional (`ac::test_a_tela_de_acessos_designa_e_revoga`).

## A demonstração no navegador (T039)

Duas formas, as duas a 1280 px e a 375 px:

- **A jornada automatizada** `navegador/test_jornada_da_formalizacao.py`, num Chromium de verdade,
  com o console vigiado (nenhuma violação de CSP) e `scrollWidth` medido a 375: Cenário A
  (definição pela presidência, verificação completa, download e conferência do ZIP), Cenário E (as
  recusas por URL) e Cenário F (a verificação parcial **antes** do download, o ZIP `-parcial` com as
  três pessoas e o arquivo ausente respondendo *"Arquivo indisponível"*). As capturas estão em
  `capturas/cenario-*.jpg`.
- **Ao vivo, no painel do app**, sobre um banco de demonstração (`ps117demo`, entrada
  `formalizacao-117` do `.claude/launch.json`, porta 8017) montado pela fixture da feature: o Edital
  73/2026 com cinco aptas. A presidência gravou a definição (identificação, certificado, certidão e
  histórico) com motivo; Rui, com o papel Formalização, viu só o Edital em que está designado e
  verificou *"Pacote completo: 5 de 5"*. Pelo shell, apagou-se o arquivo de Beatriz Costa e
  acrescentou-se um byte à certidão de Carlos Menezes; a verificação seguinte disse, antes de
  qualquer download, *"Pacote parcial: 3 de 5 pessoas incluídas"*, com os dois nomeados e o motivo
  de cada um, e o botão *"Baixar pacote parcial (3 pessoas)"*. A 375 px a página mede 375 de largura
  e o console não teve erro. Capturas em `capturas/demonstracao-*.jpg`.

O download pelo painel não foi feito: o ZIP é baixado e aberto pela jornada automatizada.


## O que a revisão de código corrigiu (04/11/2026)

A revisão do PR #373 levantou oito achados; os oito foram tratados no mesmo PR.

1. **A pessoa sem documento a exportar era contada como incluída.** Se os documentos definidos não
   se aplicavam a ela, ou ela não tinha enviado o facultativo, ela entrava no "N de M" e no registro
   — e, quando as demais eram excluídas por falha, a verificação oferecia um pacote com zero
   arquivos, cujo registro o banco recusa (`ck_exportacao_formalizacao_com_arquivo`): o download
   virava *exportação interrompida*. Agora a população da exportação é só de quem tem documento a
   exportar; a pessoa continua na página. Testes:
   `ex::test_quem_nao_tem_documento_a_exportar_nao_entra_na_exportacao`,
   `::test_so_quem_nao_tem_documento_sobra_e_nao_ha_o_que_baixar`.
2. **A população era lida antes da trava e da transação**, na verificação, no download e na pessoa
   única. Agora `_compor` roda dentro da transação, depois da trava — a definição, os desfechos e
   as conferências lidos são os do momento em que os arquivos se leem —, e o limite continua
   conferido antes do primeiro arquivo. **O que sobra é o do nível de isolamento**: sob *read
   committed*, um desfecho gravado no segundo em que a montagem lê os arquivos não é visto por ela,
   e o pacote corresponde ao estado do início da leitura. Fechar isso pediria trancar os desfechos
   do Edital durante a montagem, o que bloquearia a comissão; não foi feito.
3. **O conteúdo publicado era lido de quatro a seis vezes por requisição.** Agora `_conteudos`
   guarda a leitura na instância do Edital, e a lista do setor lê as versões de todos os Editais
   numa consulta (`guardar_conteudos`).
4. **A lista lia as versões uma vez por designação** — mesma correção.
5. **Os registros de exportação eram lidos duas vezes por página** (última exportação e histórico).
   Agora uma leitura serve às duas (`exportacoes_do_edital`).
6. **A designação aceitava Edital em qualquer estado no serviço.** Agora `conferir` recusa o que não
   é publicado nem encerrado (`ESTADOS_DESIGNAVEIS`), e a tela usa o mesmo conjunto. Teste:
   `ac::test_edital_sem_publicacao_nao_recebe_designacao`.
7. **O evento do documento e o tamanho legível estavam duplicados.** A view usa
   `exportar.registrar_evento` e `conjunto.tamanho_legivel`; o alias privado `_megabytes` saiu.
8. **O teste da suspensão aceitava qualquer resposta diferente de 200.** Agora exige o que a
   suspensão produz: a sessão encerrada e o redirecionamento à identificação.

Depois das correções, `make lint check test-pg` deu **15411 passed, 12 skipped e 1 falha** — a de
`performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`, o
teste de tempo que o `AGENTS.md` descreve como oscilante com 4 workers. A feature não toca a
ocupação; isolado, ele passou quatro de quatro, e na rodada anterior a suíte inteira o tinha passado.


## Achados registrados, sem escopo aqui

- **A view do documento instruído no recurso (`documento_instruido`, `036`)** chama
  `copia_verificada` como as outras três. Com `ArquivoIndisponivel` sendo recusa do domínio, ela
  também deixou de responder 500 para arquivo ausente — responde 409 pela página da área —, mas
  **sem** o evento `ARQUIVO_INDISPONIVEL`, que a FR-3695 só pede às três views nomeadas. Gravar o
  evento ali é uma linha, e é decisão do usuário (FR-3705).
- **`CLAUDE.md` diz que dois arquivos de jornada pulam sem o grupo `navegador`**; desde a `115` são
  três, e com a `117` quatro. A frase não foi corrigida aqui.

## O que esta verificação não cobre

- **A capacidade da VM** (H01): verificação, montagem e transferência de um pacote no limite, o
  disco do `/tmp` privado e do nginx com duas exportações, o tempo-limite forçado. O roteiro está no
  guia de implantação, §15.4. O limite de produção é o que a medição sustentar.
- **A exportação real por um servidor do setor** (H02), que diz se as pastas e o manifesto servem.
- **O aviso de privacidade do Edital** (H03), texto institucional da área de proteção de dados.
- **A transferência cortada no meio por um worker morto** foi provada pelo fechamento do arquivo da
  resposta (`cv::test_o_cliente_que_desconecta_fecha_o_temporario_e_o_registro_continua`) e pela
  conexão fechada soltando a trava (`cv::test_a_conexao_fechada_solta_a_trava`), e não matando um
  gunicorn de verdade: isso é o item 4 do roteiro da VM.

## Revisão de 12/11/2026 — a presidência também designa (D-025)

**No navegador, com dados sintéticos** (banco próprio `ps_117pres_dev`, `seed_demo` e duas pessoas
fictícias com o papel Formalização, *Rui Registro* e *Bia Coordenação*; Edital 51/2026 de
demonstração, presidido por `paulo.presidente`):

1. Como presidência, a seção "Quem acessa os documentos" mostra a frase de que designar não dá
   acesso aos documentos, a escolha entre as duas pessoas com o papel, os dois Perfis do Edital e o
   motivo. Rui designado só em *Professor de Informática*: a seção confirma e lista a designação com
   o Perfil, a data e a autoria (`capturas/revisao-1211-presidencia-designou-1280.jpg`).
2. A segunda designação de Rui volta à seção com a frase do domínio, "Esta pessoa já está designada
   para este Edital…" (`capturas/revisao-1211-recusa-ja-vigente-1280.jpg`).
3. A revogação, com motivo, volta à seção com a confirmação, e a lista fica vazia.
4. Na trilha, os dois eventos têm a base `comissao:presidir`, o autor, a unidade e o motivo.
5. A presidência que acabou de designar recebe **403** na página do setor do mesmo Edital
   (FR-6704).
6. Como gestor com `comissao:gerir` e sem presidir, a seção diz "só para leitura", sem formulário; o
   POST forjado recebe **403**, com a frase que nomeia as duas bases: *"…depende da permissão de
   conceder e revogar os acessos da unidade ou da presidência deste Processo — cada uma basta
   sozinha…"*.
7. A 375 px, a seção cabe sem rolagem horizontal (`scrollWidth` igual a 375), com o "Revogar"
   abaixo do motivo (`capturas/revisao-1211-presidencia-375.jpg`). O console mostra só o 403
   esperado do passo 5, sem violação de CSP.
