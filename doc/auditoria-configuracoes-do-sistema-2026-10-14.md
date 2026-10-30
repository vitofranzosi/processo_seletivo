# Auditoria — Configurações do sistema: interface ou implantação

*Auditoria de 14/10/2026, sobre a `main` em `6fac8189` (depois da `071` e do #279). Nada foi
implementado nem migrado. As seções 4 e 5 foram revistas no mesmo dia, a pedido do usuário, e a
revisão abriu a spec `073`. Caminhos de código são relativos a
`backend/processo_seletivo/`, salvo quando começam por `backend/`, `specs/` ou `doc/`. Nenhum valor
de credencial foi lido nem é reproduzido aqui.*

**A pergunta:** quais configurações precisam de interface administrativa e quais devem continuar na
implantação, para facilitar a operação sem overengineering.

## Resumo em cinco linhas

1. **Uma área de configuração e diagnóstico se justifica, mas depois da autenticação da
   gestão.** O que muda na operação corrente já tem tela: modelos de aviso, autoridades e comissão.
   E-mail e assistente mudam pouco, mas errar neles é fácil e caro, e o diagnóstico hoje é difícil.
   Enquanto a gestão responder 503 em produção (B-1), uma página não ajuda quem implanta (§4).
2. **O problema é de procedimento e de diagnóstico.** As variáveis estão bem guardadas pelo código:
   `production.py` recusa subir sem as essenciais. Mas estão descritas em quatro lugares, com
   referências de linha vencidas. Nenhum procedimento ensina a ver a configuração carregada, nem a testar
   a conexão sem a ação real (P-11, P-12). O #281 resolveu a dispersão; o resto é da `073`.
3. **A troca OpenRouter ↔ Ollama é segura, mas não é simples.** O comando
   `verificar_servico_de_inferencia` pega quase todo erro de configuração — foi ensaiado nesta
   auditoria. Falta um roteiro único: hoje a troca exige juntar o quickstart da `071`, o `R-009` e os
   comentários do `base.py`, e o `export` da configuração anterior sobrevive no mesmo shell.
4. **O e-mail, em produção, uma pessoa da TI configura seguindo o guia de implantação** (§10 e §16).
   Há três arestas: a porta 465 não é suportada, `EMAIL_HOST` vazio passa no boot e falha com
   mensagem obscura, e o guia não diz que o despacho dos avisos lê o `app.env` novo antes do
   serviço web.
5. **Menor próxima entrega: o #281 e uma `073` só com as lacunas que restam** (§5). São uma seção
   única "configurar → verificar → testar" no guia, com comandos que já existem, e duas correções
   pequenas de código. Comando novo não se justifica: o ensaio da §4.3 mostrou que os existentes
   bastam. A página fica registrada como evolução depois do B-1.

---

## 1. Inventário

**Legenda.**

- **Escopo:** **Imp** é implantação, a máquina e a topologia. **Ins** é a instituição, o Ifes.
  **Uni** é a unidade. **Edi** é o Edital.
- **Reinício:** ✔ quando o processo web precisa ser reiniciado. As settings são lidas na carga, e o
  gunicorn usa `preload_app`.
- **Recomendação:** **M** é manter como está, **P** é melhorar o procedimento e **I** é oferecer
  interface.
- **(H)** marca o que é hipótese a confirmar: quem altera, ou com que frequência.

### 1.1 Instituição e unidades

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Linhas da instituição no cabeçalho ("Ministério da Educação", "Instituto Federal do Espírito Santo") | constante `INSTITUICAO`, `publicacoes/infrastructure/pdf.py:1093-1094` | desenvolvimento; só se o órgão mudar de nome (H: nunca) | Ins | ✔ (deploy) | não | o documento publicado não se regenera; os atos novos sairiam com o nome novo | M |
| Unidade: sigla, nome, linhas do cabeçalho, local, ativa | `unidades/unidades.json`, aplicado por `sincronizar_unidades` no `make preparar` e no `ps-migrar` | TI, a pedido do Cefor, quando entrar um campus ou mudar um nome (H: raro, ~26 unidades que mudam em anos, `specs/060-unidades-e-autoridades/research.md:52-53`) | Uni | não (é dado, e a próxima publicação já o lê) | não | **nenhum sobre o publicado**: a publicação congela a Unidade (`FR-1130`, `FR-1131` da `060`); a Retificação seguinte sai com o nome novo | M — decisão `R-003` da `060`: diff revisado + trilha com o ator `implantacao` |
| Autoridade habilitada (cargo, nome, ato de nomeação, vigência) | banco, tela `gestao/autoridades` (`interface/urls.py:47`), permissão `autoridade:gerir` do Gestor | Gestor da unidade, quando muda a direção ou a portaria | Uni | não | não | imutável depois do primeiro uso (`unidades/models.py:75-78`); a Publicação congela o identificador | M — já tem interface |
| "Cefor/Ifes" na identidade visual (título das páginas, marca, comprovante, nome do serviço) | `interface/templates/interface/base.html:6,1307`, `portal/templates/portal/base.html:6,948`, `portal/templates/portal/comprovante.html:22`, `shared/api/operacional.py:56` | desenvolvimento | Ins | ✔ (deploy) | não | nenhum | M enquanto houver uma unidade (ver §2, P-6) |
| Escopo padrão da identidade de desenvolvimento | `ESCOPO_PADRAO = "cefor"`, `interface/identidade.py:21`; o mesmo literal em `processos/management/commands/seed_demo.py:37` e na chave do `unidades.json` | desenvolvimento | Uni | ✔ | não | nenhum | M — some com o adaptador institucional (B-1) |

### 1.2 Contatos e atendimento

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Canal de atendimento ao candidato | `PORTAL_ATENDIMENTO`, `config/settings/base.py:286`; obrigatório em produção (`config/settings/production.py:192-199`). Lido em oito pontos: portal, convocação, avisos e assistente | TI, a pedido da seleção, quando o e-mail ou o telefone do setor mudar (H: raro) | Ins, de fato; o texto o trata como da comissão | ✔ | não | as telas mostram o valor novo; **o aviso já confirmado guarda o antigo**, porque o texto congela na confirmação (`avisos/domain/mensagem.py:8-10`); o PDF publicado não o usa | P |
| Contato da comissão dentro do Edital | conteúdo do Edital (seções) | elaborador, no ciclo do Edital | Edi | — | — | **norma publicada**: só muda por Retificação | M — não é configuração |
| "Esta mensagem é automática; não responda." e a ausência de `Reply-To` | rodapé fixo, `avisos/domain/mensagem.py:24-32`; nenhum `reply_to` no código | desenvolvimento | Ins | ✔ | não | nenhum | M — o rodapé aponta o atendimento. Confirmar com o setor se ninguém espera resposta por e-mail (H) |

### 1.3 Envio de e-mail

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Mecanismo, servidor, porta, STARTTLS, tempo-limite | `DJANGO_EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_TIMEOUT` (`config/settings/base.py:186-197`); produção recusa mecanismo que não entrega (`production.py:146-160`) | TI, na implantação e quando o setor de correio trocar o servidor (H: raro) | Imp | ✔ web; o despacho dos avisos lê o `app.env` a cada execução | não | nenhum sobre atos; código de acesso, comprovante e convocação passam a sair pelo servidor novo | P |
| Usuário e senha do SMTP | `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (`base.py:190-191`) | TI, na rotação da senha | Imp | ✔ | **sim** | nenhum | P — fora do `.env.example` (ver P-2) |
| Remetente | `DEFAULT_FROM_EMAIL` (`base.py:187`); obrigatório em produção (`production.py:161-166`) | TI, a pedido da instituição (H: raro) | Ins | ✔ web | não | os avisos pendentes saem com o remetente novo | P |
| Endereço de resposta | inexistente | — | — | — | — | — | M (ver §1.2) |
| Textos das mensagens do sistema: código de acesso, mudança de credencial, comprovante, convocação | constantes `ASSUNTO`/`CORPO` em `identidade/application/mensagem.py`, `inscricoes/application/mensagem.py:41-43` e `convocacao/application/comunicar.py:39-47` | desenvolvimento | Ins | ✔ (deploy) | não | nenhum | M — mensagem do sistema, e não da seleção; o texto da seleção é o aviso, que já tem modelos |
| Modelos de aviso aos candidatos | banco, por unidade; tela `gestao/modelos-de-aviso` (`interface/urls.py:470-472`); três iniciais criados por `sincronizar_unidades` (`unidades/management/commands/sincronizar_unidades.py:35-41`) | quem gere avisos na unidade, a qualquer momento | Uni | não | não | o aviso confirmado congela o texto | M — já tem interface |
| Avisos ligados, ritmo, tentativas, janela | `AVISOS_*` (`base.py:203-219`); desligados em produção até a validação de LGPD | TI, **depois** da decisão institucional; `AVISOS_LIMITE_POR_MINUTO` segundo o limite da conta | Imp | ✔ web; o timer lê a cada minuto | não | religar não dispara aviso velho: a janela de 24 h os expira (`base.py:216-219`) | M — ligar é ato de governança, e não preferência de tela |

### 1.4 Assistente (LLM)

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Habilitação do piloto | `ASSISTENTE_PILOTO` (`base.py:225`); papel próprio `participante-piloto-assistente` (`interface/identidade.py`) | equipe, por sessão de piloto | Imp | ✔ | não | nenhum sobre atos: a resposta deriva do conteúdo publicado, que é imutável | M |
| Serviço, endereço, modelo | `ASSISTENTE_SERVICO`, `ASSISTENTE_ENDERECO`, `ASSISTENTE_MODELO` (`base.py:226-228`); em produção, só `ollama` (`production.py:204-209`) | equipe, ao trocar OpenRouter ↔ Ollama (H: algumas vezes no piloto) | Imp | ✔ | não | nenhum; os registros do piloto guardam o modelo de cada troca | P |
| Credencial | `ASSISTENTE_CREDENCIAL` (`base.py:231`), lida de arquivo fora do repositório e exportada no shell; só o OpenRouter a usa (`duvidas/infrastructure/inferencia/openrouter.py:55`) | quem detém a chave | Imp | ✔ | **sim** | nenhum | M — o limite de gasto fica no painel do OpenRouter (`FR-1507`) |
| Provedor e retenção no OpenRouter | `ASSISTENTE_PROVEDOR`, `ASSISTENTE_ZDR` (`base.py:261-265`) | equipe | Imp | ✔ | não | nenhum | P — o Ollama os ignora, mas eles sobrevivem no shell |
| Tokenizer, acréscimos de tokens, quantização, contexto | `ASSISTENTE_TOKENIZER`, `ASSISTENTE_TOKENS_POR_MENSAGEM`, `ASSISTENTE_TOKENS_POR_CHAMADA`, `ASSISTENTE_QUANTIZACAO`, `ASSISTENTE_CONTEXTO_TOKENS` (`base.py:236-273`) | equipe, medidos para cada par serviço × modelo | Imp | ✔ | não | nenhum | P — **mudam junto com o serviço**, e é aí que a troca erra |
| Limites: tempo, teto simultâneo, turnos, tamanho da pergunta, geração | `base.py:234-259` | equipe, depois das medições na L4 | Imp | ✔ | não | nenhum | M |

### 1.5 Permissões e alcance por unidade

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Papéis e o que cada um pode | dicionário fixo `PAPEIS`, `interface/identidade.py:20-126` | desenvolvimento, por spec | Ins | ✔ (deploy) | não | nenhum sobre atos; a trilha registra a permissão usada | M |
| Quem tem qual papel, e em qual unidade | **não existe em produção**: o seletor de desenvolvimento escolhe papéis e fixa o escopo `cefor`; produção responde 503 (`interface/views.py:629`), gap **B-1** do guia | a definir com o adaptador institucional | Ins/Uni | — | — | — | M — decisão de B-1 (grupos do diretório), e não tela de configuração |
| Comissão do Processo e alocação nas Etapas | banco, tela `gestao/processos/<id>/comissao` (`interface/urls.py:206`) | Gestor ou presidência, por Processo | Edi | não | não | append-only, com trilha | M — já tem interface |
| Autenticação da API | `API_AUTHENTICATION_CLASSES` (`production.py:218-247`) | TI, com B-1/I-1 | Imp | ✔ | não | nenhum | M |

### 1.6 Integrações e demais configurações

| Configuração | Onde, hoje | Quem altera, e quando | Escopo | Reinício | Segredo | Efeito sobre o que já existe | Rec. |
|---|---|---|---|---|---|---|---|
| Fonte da semente do sorteio | **norma do Edital** (`drawMethod` do marco), e não configuração (`base.py:138-143`) | elaborador; depois de publicado, só por Retificação | Edi | — | — | — | M — o exemplo de como o projeto já separa norma de configuração |
| Endereço da Loteria Federal; tempo e tentativas | `ENDERECO` em `sorteios/infrastructure/fontes/loteria_federal.py:22`; `SORTEIO_FONTE_TIMEOUT_SEGUNDOS` e `SORTEIO_FONTE_TENTATIVAS` (`base.py:144-145`) | desenvolvimento, se a Caixa mudar a API | Imp | ✔ | não | o sorteio já realizado guarda a ocorrência | M |
| Base de CEP | `carregar_ceps` e `situacao_dos_ceps`; `make ceps-situacao` | TI, na implantação e periodicamente | Imp | não | não | nenhum | M |
| Limites de arquivo | `ARQUIVOS_CANDIDATOS_LIMITE_BYTES`, `EDITAL_ANEXOS_LIMITE_BYTES` (`base.py:295-303`); **duplicados** no `client_max_body_size` do nginx | TI | Imp | ✔ + nginx | não | nenhum: o limite é da aplicação, e não do Edital (`FR-046` da `009`) | M — o guia já avisa da duplicação |
| Tempo-limite do gunicorn (120 s) | fora do repositório (guia §12.1); o assistente e o SMTP se medem contra ele (`production.py:210-215`) | TI | Imp | ✔ | não | nenhum | M |
| Validade e limites do código de acesso | constantes, `identidade/models.py:18-19` e `identidade/application/desafio.py:35-42` | desenvolvimento, por spec | Ins | ✔ (deploy) | não | nenhum | M — regra de segurança da `010` |
| Chave do Django | `DJANGO_SECRET_KEY` (`production.py:73-81`) | TI, **nunca por rotina** | Imp | ✔ | **sim, persistente** | trocá-la invalida os comprovantes já emitidos (gap I-9) | M |
| Banco, hosts, HTTPS, proxy, documentos | `DB_*`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECURE_*`, `PORTAL_ATRAS_DE_PROXY`, `ARQUIVOS_CANDIDATOS_RAIZ` (`base.py`, `production.py`) | TI, na implantação | Imp | ✔ | senhas do banco | nenhum | M — guia §10 |
| Recursos de demonstração | `INTERFACE_SELETOR_IDENTIDADE`, `PORTAL_IDENTIDADE_DEMO`, `SORTEIO_FONTE_DE_DEMONSTRACAO`; produção recusa as três (`production.py:90-120`) | ninguém, em produção | Imp | ✔ | não | — | M |

**Mecanismos administrativos que já existem**, e que qualquer proposta deve reaproveitar:

- três telas: autoridades e modelos de aviso, por unidade, e comissão, por Processo;
- `sincronizar_unidades`, com diff revisado e trilha;
- as recusas de boot do `production.py`, que nomeiam a variável a corrigir;
- `verificar_servico_de_inferencia`, que confere serviço, modelo, quantização, contexto, GPU, limite
  da chave e contagem de tokens, e sai com 1 quando há divergência;
- `sendtestemail`, do Django, já no guia (§16.3);
- os scripts `ps-manage`, `ps-migrar` e `ps-ativar` do guia (§8.3).

**Configuração × norma do Edital.** Fonte do sorteio, prazos, vagas, documentos exigidos e contato
da comissão são **norma publicada**: depois da publicação, só mudam por Retificação, e não entram em
tela de configuração nenhuma. O que o Edital publicado já congelou — unidade, autoridade, conteúdo —
não muda quando a configuração muda. O que **não** congela, e muda para tudo daí em diante: o canal
de atendimento nas telas, o remetente e o servidor de correio, e o serviço do assistente.

---

## 2. Problemas concretos

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| P-1 | **A troca do assistente não tem roteiro único.** As variáveis ficam no `R-009` da `071`, os passos no quickstart (roteiros B e D) e o formato do endereço no contrato. Nem o `.env.example` nem o guia de implantação citam `ASSISTENTE_*`. O endereço muda de forma entre os serviços: o OpenRouter leva `/api/v1` e o Ollama, a raiz. | `specs/071-piloto-assistente-do-edital/quickstart.md:60-80,118-127`; `research.md`, `R-009`; `duvidas/infrastructure/inferencia/ollama.py:44`, `openrouter.py:53` | média |
| P-2 | **A configuração do serviço anterior sobrevive no shell.** O quickstart configura por `export`. Quem troca para o Ollama no mesmo terminal leva `ASSISTENTE_PROVEDOR`, a credencial e o `ASSISTENTE_TOKENS_POR_MENSAGEM=9`, que foi medido no provedor do OpenRouter. A verificação acusa a contagem divergente, mas a causa não é óbvia para quem a lê. | `quickstart.md:65,79-80` | média |
| P-3 | **`include .env` sobrepõe o ambiente.** Quem puser `ASSISTENTE_SERVICO` no `backend/.env` não troca de serviço por `export`: o `make runserver` volta ao valor do arquivo, sem aviso. | `backend/Makefile:9-14` | média |
| P-4 | **Valor de serviço fora do vocabulário dá mensagem enganosa.** Com `ASSISTENTE_SERVICO=Ollama`, a saída é "nenhum serviço configurado", e não "serviço desconhecido". Ensaiado. | `duvidas/management/commands/verificar_servico_de_inferencia.py:54-59` | baixa |
| P-5 | **A segurança que o servidor exige pode não ser a que o sistema suporta.** O sistema só fala STARTTLS (`EMAIL_USE_TLS`), e não há `EMAIL_USE_SSL`. A porta 465 em si não é o erro: o erro é o servidor exigir SSL implícito. Com STARTTLS apontado para um servidor que só aceita SSL implícito, a conexão costuma ficar presa até o `EMAIL_TIMEOUT`, sem mensagem que diga a causa. Mas tempo esgotado também pode ser rede, firewall, endereço, porta ou servidor fora do ar: o sintoma sozinho não diagnostica. E o correio é o único fator de autenticação do candidato. | gap I-4, `doc/implantacao-em-producao-ubuntu.md:2532-2537`; `base.py:186-197` | **alta se** o servidor exigir a 465 (H) |
| P-6 | **`EMAIL_HOST` vazio passa no boot.** Com o backend SMTP e sem servidor, a aplicação sobe, e o primeiro envio falha com `SMTPServerDisconnected: please run connect() first`. Ensaiado com `sendtestemail`. | `production.py:146-166` não confere `EMAIL_HOST` | baixa — o teste do §16.3 pega |
| P-7 | **O guia não diz que o despacho e o web podem divergir.** Quem edita o `app.env` e não reinicia o serviço fica com os avisos saindo pelo servidor novo, porque o timer relê o arquivo a cada minuto, e o código de acesso pelo antigo. | guia §8.3 (`ps-manage` lê o `app.env`), §21.4 | baixa |
| P-8 | **Referências vencidas no guia e no `.env.example`.** O guia cita `base.py:172-178` para o correio, que hoje está em `:186-197`, e mantém no gunicorn o comentário "o SMTP não tem timeout (gap I-4)", resolvido pela `066`. O §16.4 vem antes do §16.3. O `.env.example` não tem `EMAIL_HOST_USER` nem `EMAIL_HOST_PASSWORD`, e ainda traz `DJANGO_DEBUG`, que nada lê (M-8). | `doc/implantacao-em-producao-ubuntu.md:131,874,1100,1580-1603`; `backend/.env.example:14,55-75` | baixa |
| P-9 | **"Cefor/Ifes" fixo fora do registro de unidades.** Está no rodapé dos avisos, na marca das duas interfaces e no comprovante. Hoje é correto. Com a segunda unidade, o aviso de um campus assinaria "Cefor/Ifes", e o canal de atendimento é um só para a instituição. | `avisos/domain/mensagem.py:31`; templates da §1.1; `base.py:286` | nenhuma hoje; **gatilho**: segunda unidade |
| P-10 | **As recusas de produção aparecem uma de cada vez**, como traceback. Quem implanta descobre as pendências uma a uma. O pré-voo da §11.1 do guia já manda corrigir e repetir o `check --deploy`, e cada repetição leva segundos, sem reiniciar nada. Ensaiado na revisão. | `config/settings/production.py:62-64`; guia §11.1 | baixa |
| P-11 | **Nenhum procedimento mostra a configuração carregada.** O `diffsettings` do Django imprime a chave e a senha do SMTP, e não pode entrar num procedimento. Já o `manage.py shell -c` com uma lista fechada de valores mostra o que o processo de diagnóstico carregou — e não os workers web em execução — e só diz se a senha está presente. Ensaiado: a senha plantada apareceu zero vezes. Falta o exemplo no guia. | Django `diffsettings` e `shell -c` | média |
| P-12 | **Nenhum procedimento separa o teste de conexão da ação real.** O `sendtestemail` sempre envia, e a verificação do assistente sempre faz uma inferência. Os meios já existem: a conexão do Django (`get_connection().open()`) conecta, negocia a segurança e autentica sem enviar, e duas leituras do Ollama (`/api/version`, `/api/tags`) não pedem inferência. Falta o exemplo no guia. | `duvidas/management/commands/verificar_servico_de_inferencia.py:68-88` | baixa |

**Situação depois do [PR #281](https://github.com/vitofranzosi/processo_seletivo/pull/281)**, de
14/10/2026, ainda sem merge:

- **resolvidos:** P-1, P-2 e P-3 (`doc/troca-do-servico-do-assistente.md`), P-7 (§16.5 do guia) e
  P-8 (referências, ordem do §16 e `.env.example`);
- **registrados:** P-5 (pergunta no checklist do §25) e P-9 (`doc/pendencias-da-060.md`);
- **documentado, e não corrigido:** P-6, pelo teste do §16.5;
- **ficam para a `073`:** P-4, P-5 como diagnóstico, P-6, P-11 e P-12, e a configuração do Ollama
  em produção, que nenhum documento da implantação descreve. O roteiro do #281 é da máquina da
  equipe.

**Não são problemas**, embora pareçam:

- a falta de `Reply-To`, que é coerente com o rodapé "não responda" mais o canal de atendimento;
- os textos fixos das mensagens do sistema, que não são texto da seleção;
- os papéis fixos em código, cuja atribuição é questão do B-1, e não de configuração;
- unidades em arquivo, por decisão registrada (`R-003` da `060`).

---

## 3. O que se resolve com documentação

*O que está abaixo foi entregue pelo #281, salvo onde indicado. Fica como registro do desenho.*

- **P-1, P-2 e P-3 — um roteiro de troca do assistente**, de uma página. O desenho:
  1. Dois arquivos fora do repositório, um por serviço, cada um com **todas** as `ASSISTENTE_*`.
     Quem troca não depende de lembrar o que desligar: a variável que um serviço não usa vai vazia
     no arquivo dele. A credencial continua em arquivo próprio, e só o do OpenRouter a lê.
  2. **Shell novo** a cada troca. Carrega-se o `.env` do banco e por cima o arquivo do serviço.
  3. `verificar_servico_de_inferencia`. Com divergência, não se segue.
  4. Reiniciar o `runserver`.
  5. Uma linha dizendo para nunca pôr `ASSISTENTE_*` no `backend/.env`, por causa do `include` do
     `Makefile`.

  O exemplo de endereço de cada serviço entra no próprio roteiro. O lugar natural é uma seção nova no
  quickstart da `071`, ou um `doc/` próprio apontado por ele.
- **P-7 e P-8 — um procedimento de troca do correio no guia de implantação**, no §16:
  1. pedir ao setor de correio servidor, porta, conta, limite por minuto e por dia, e SPF/DKIM;
  2. editar o `app.env` com `sudo -e`;
  3. `sudo systemctl restart processoseletivo`;
  4. o teste do §16.3;
  5. ajustar `AVISOS_LIMITE_POR_MINUTO` se o limite da conta mudou.

  No mesmo passo: corrigir as referências de linha, reordenar o §16, completar o `.env.example` com
  as duas variáveis de conta (sem valor) e retirar o `DJANGO_DEBUG`.
- **P-5 — uma pergunta ao setor de correio, registrada no checklist do §25:** o servidor aceita
  STARTTLS na 587? Se sim, P-5 não tem efeito e encerra-se como lacuna conhecida.
- **P-9 — uma linha no registro de pendências da `060`** (`doc/pendencias-da-060.md`): quando entrar
  a segunda unidade, o rodapé dos avisos e o canal de atendimento precisam vir da Unidade.

**Avaliação prática.** Com esses dois procedimentos, uma pessoa da TI faz as duas trocas sem ler
código.

- **E-mail**, em produção: hoje já faz, seguindo §10 e §16. Os tropeços previsíveis são reiniciar
  só o timer, ou testar com `EMAIL_HOST` vazio, e o procedimento acima fecha os dois.
- **Assistente**, na máquina da equipe: hoje faz com ajuda de quem conhece a `071`. O roteiro de
  arquivo por serviço tira a dependência, e a verificação já existente é a rede de segurança. Foi
  ensaiada nesta auditoria com Ollama inacessível, com valor fora do vocabulário e com OpenRouter
  sem credencial: as três saíram com código 1 e nomearam a divergência.
- **Em produção**, a troca não existe: só o Ollama é aceito.

---

## 4. O que justificaria interface

*Revista em 14/10/2026, a pedido do usuário. A primeira versão concluía "nada, hoje", e a conclusão
não estava demonstrada. Ela pesava a frequência de alteração e só considerava **editar** valores
por tela. Esta versão pesa também a dificuldade, o risco de erro e o diagnóstico. E compara um
procedimento único com uma área mínima de configuração e diagnóstico.*

### 4.1 Os critérios

Frequência é um critério, e não o único. Uma configuração rara pode justificar ajuda, se errar nela
for fácil, caro ou difícil de diagnosticar. É o caso do correio: um erro tranca todos os candidatos,
porque o e-mail é o único fator de autenticação deles (gap I-10). E do assistente, em que vários
parâmetros mudam juntos (P-1, P-2).

Duas conclusões da primeira versão estavam erradas:

- **Campos diferentes no banco e no ambiente não são duplicação de fonte.** Servidor e remetente no
  banco, com a senha no ambiente, não conflitam. O conflito só existe quando **o mesmo parâmetro**
  pode ser definido em dois lugares sem regra de precedência. Isso não impede uma interface futura:
  impede apenas que ela e o `app.env` definam o mesmo valor.
- **A `FR-084` da `010` é uma dependência, e não uma proibição.** Um envio de teste pela interface
  seria uma nova situação de envio, e a norma pode ser emendada com justificativa, como a `066` fez
  para os avisos. O envio de teste pela linha de comando não depende disso: ele não é envio do
  domínio, e o `sendtestemail` já existe.

Uma dependência, porém, é real e decide a ordem: **o B-1**. Hoje a gestão responde 503 em produção
(`interface/views.py:629`). Uma página administrativa não ajuda ninguém a implantar enquanto não
puder ser aberta. Até lá, o canal de quem implanta é o terminal do servidor.

### 4.2 Procedimento único × área mínima

| | Procedimento único + diagnóstico pela linha de comando | Página "Configuração e diagnóstico" |
|---|---|---|
| Disponível em produção | agora | depois do B-1 |
| Mostra a configuração carregada | sim, sem segredos | sim, a mesma leitura |
| Indica o erro e a correção | sim | sim |
| Testa conexão e envio | por ação explícita, no terminal | por botão; o envio de e-mail depende de emendar a `FR-084` |
| Corrige o valor | edição do `app.env` e reinício, guiados | edição de campos não secretos, quando houver necessidade e regra de precedência |
| Ajuda na instalação inicial | sim | não: a gestão ainda não abre |

As duas não competem. A segunda **mostra** o que a primeira já calcula, e é por isso que a primeira
deve ser escrita de modo que a página a reaproveite.

### 4.3 Os comandos que já existem bastam?

*Revisto depois do #281. A primeira revisão concluía que não bastavam e propunha um comando
agregador. O ensaio desta rodada desfez os três motivos.*

**Bastam, com exemplos completos no guia e duas correções pequenas.**

| Requisito | Com o que existe | Ensaiado |
|---|---|---|
| Mostrar a configuração carregada sem segredos | um **exemplo** no guia com `ps-manage shell -c` e uma lista fechada de valores, e não comando novo; a senha só como "presente". Mostra o processo de diagnóstico, e não os workers web em execução | sim: senha plantada, zero ocorrências |
| Indicar o erro e a ação | as recusas do `production.py`, uma por execução, em segundos (§11.1); os sintomas dos testes, numa tabela do guia | sim |
| Testar a conexão sem enviar | `get_connection().open()` e `close()`: conecta, negocia a segurança e autentica | sim, até a recusa da conexão |
| Testar o Ollama sem inferência | `curl` em `/api/version` e `/api/tags` | — |
| Ação real | `sendtestemail` e `verificar_servico_de_inferencia` | sim |

**O que a documentação não resolve:**

- **P-6.** O `EMAIL_HOST` vazio sobe e só falha no primeiro envio. Basta uma regra a mais nas recusas
  de produção.
- **P-4.** A verificação do assistente diz "nenhum serviço configurado" para um valor desconhecido. A
  correção é uma mensagem.

O comando agregador volta a ser necessário com a página depois do B-1, porque a página não roda
comandos no terminal. É ali que ele se especifica, junto com ela.

### 4.4 Avaliação por área

| Área | Agora (linha de comando) | Depois do B-1 (página) | Fica na configuração técnica |
|---|---|---|---|
| **E-mail** | mostrar servidor, porta, segurança, remetente e "credencial presente"; acusar a incompatibilidade de segurança (P-5) e o servidor vazio (P-6); testar a conexão e, à parte, o envio | mostrar o mesmo; envio de teste depois de emendar a `FR-084`; editar campos não secretos, se a operação pedir | usuário e senha do SMTP |
| **Assistente (Ollama)** | mostrar serviço, endereço, modelo e limites; testar a conexão sem inferência e, à parte, a conversa sintética | mostrar o mesmo e o estado da conexão; editar endereço, modelo e limites, se o assistente sair do piloto | credencial, quando houver |
| **Atendimento** | mostrar o canal em uso | editar o canal padrão, com permissão e trilha. Os contatos publicados nos Editais não mudam: são norma | — |
| **Estado da implantação** | a lista completa de pendências, separando desenvolvimento de produção | a mesma lista na página | banco, HTTPS, chave do Django |

**Não entra em nenhuma das duas:** ligar os avisos pela tela antes da validação de LGPD, editar
unidades fora do `unidades.json` (`R-003` da `060`) e atribuir papéis, que é parte do B-1.

---

## 5. Menor próxima entrega recomendada

*Revista duas vezes em 14/10/2026. A primeira versão recomendava só documentação. A segunda, um
comando agregador. Esta parte do que o #281 já entrega e do ensaio da §4.3.*

**Duas peças:**

1. **O [PR #281](https://github.com/vitofranzosi/processo_seletivo/pull/281)**, com o roteiro de troca
   do assistente na máquina da equipe, o §16.5 do guia, as referências vencidas e o `.env.example`.
2. **A spec `073`**, em
   [`specs/073-configurar-e-verificar-implantacao/spec.md`](../specs/073-configurar-e-verificar-implantacao/spec.md),
   recortada às lacunas que o #281 deixa:
   - uma seção única "Configurar, verificar e testar" no guia, para o correio e para o Ollama em
     produção, só com comandos que já existem;
   - a recusa de inicialização para o servidor de correio vazio (P-6);
   - a mensagem do serviço desconhecido (P-4).

**Sem comando novo.** A documentação e os comandos existentes resolvem a necessidade verificada. As
duas mudanças de código corrigem comportamento que engana, e não acrescentam capacidade.

**Registrados como evolução, fora da `073`:**

- **A página "Configuração e diagnóstico"**, depois do B-1, com o comando agregador que ela exigir.
  O envio de teste pela página depende de emendar a `FR-084` da `010`. A edição de campos não
  secretos depende de regra de precedência com o `app.env`.
- **O canal de atendimento por unidade** (P-9), em entrega separada.
- **O suporte a SSL implícito** (P-5). A `073` só ensina a reconhecer a incompatibilidade. Suportá-la
  depende da resposta do setor de correio.

**Hipóteses a confirmar com o setor**, e de que dependem as recomendações:

- com que frequência o canal de atendimento e o remetente mudam;
- se alguém espera resposta por e-mail às mensagens do sistema;
- qual porta e qual segurança o servidor de correio institucional exige;
- quando entra a segunda unidade.
