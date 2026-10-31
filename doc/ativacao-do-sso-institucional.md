# O que falta para ativar o SSO institucional

*Desde a [`106`](../specs/106-identidade-institucional-preparada/spec.md), 30/10/2026; atualizado
pela [`107`](../specs/107-gestao-de-acessos/spec.md), no mesmo dia, que deu tela à gestão de
acessos.* A
arquitetura está pronta para receber a identidade do provedor do Ifes; o provedor real não foi
integrado. Este documento lista o que falta, na ordem em que se resolve, e o que cada item pede.

## 1. Decisões do usuário

Respondidas pelo usuário em 30/10/2026, exceto o provedor e o portão do diretório — o registro
completo está na [spec da 107](../specs/107-gestao-de-acessos/spec.md), §Decisões do usuário.
Nenhuma muda o código já entregue; as abertas bloqueiam a ativação.

| # | Decisão | Situação | Onde se aplica |
|---|---|---|---|
| 1 | Provedor e protocolo (decisão 1 do estudo) | **aberta**: OIDC na aplicação, ou SAML/OIDC terminado no proxy | a classe do adaptador |
| 2 | Qual identificador do provedor localiza a pessoa (decisão 2) | **decidida em 30/10**: o estável do provedor, com o emissor — em OIDC, `iss` + `sub`; nome e e-mail não associam | a classe do adaptador; nenhum dado gravado |
| 3 | Quem é o administrador institucional de acessos (decisão 4) | **decidida em 30/10**: duas pessoas designadas nominalmente por ato formal, contas individuais, o ato como motivo | o comando `conceder_administracao_institucional`, com `--adicional` para a segunda |
| 4 | Quem concede na unidade (decisão 5) | **decidida em 30/10**: o papel próprio, separado do Gestor; acúmulo só por concessão explícita | nada muda: é o catálogo atual |
| 5 | Tempo de sessão e inatividade (decisão 11) | **decidida em 30/10**: 8 h e 30 min, declarados expressamente em produção; ajustes, documentados | `GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS=480` e `GESTAO_SESSAO_INATIVIDADE_MINUTOS=30` no `app.env` (§5) |
| 6 | Portão do diretório (decisão 3) | **aberta**: sem portão — toda conta entra e vê "sem acesso" | o adaptador |
| 7 | Suspensão de pessoa (P1 da `107`) | **decidida em 30/10**: suspensão global e revogação por unidade; o administrador institucional suspende; o institucional, a implantação; motivo, trilha e fim de todas as sessões | incremento 2 da `107`: "Administração de acessos" → "Suspender ou reativar pessoas", e os comandos `suspender_pessoa` e `reativar_pessoa` |
| 8 | O que a reativação devolve (P2 da `107`) | **decidida em 30/10**: os vínculos vigentes voltam, os revogados não; nenhuma sessão anterior volta | idem |
| 9 | Retirar ou substituir a administração institucional (P3 da `107`) | **decidida em 30/10**: comando de implantação, com motivo e trilha; a substituição numa operação só | os comandos `retirar_administracao_institucional` e `substituir_administracao_institucional` (incremento 2 da `107`) |
| 10 | A retirada pode deixar nenhum administrador institucional? | **decidida**: só com a opção explícita `--sem-administracao`; a troca de pessoa, pela substituição | o comando de retirada (`D-018` e P5 da `107`) |

A **segregação mais estrita** (quem elabora não homologa) é emenda à FR-021 da `001`, e não faz
parte da ativação.

## 2. O adaptador

Escrever uma classe que cumpra o [contrato](../specs/106-identidade-institucional-preparada/contracts/adaptador-e-configuracao.md):
`nome`, `iniciar(request, *, retorno, estado)` e `concluir(request, *, estado)`.

- **OIDC na aplicação:** `iniciar` redireciona ao endpoint de autorização com `state=estado`, um
  `nonce` guardado na sessão e o desafio do **PKCE** (`code_challenge`, S256); `concluir` troca o
  código pelo token com o `code_verifier` e valida assinatura (JWKS), `iss`, `aud`, `nonce` e
  validade. A gestão lê o `state` do retorno e o confere contra a sessão antes de chamar `concluir`;
  o adaptador não precisa refazer essa conferência, e não deve renomear o parâmetro. Uma biblioteca cliente vai às dependências — Authlib ou
  `mozilla-django-oidc` usado só como cliente. **Não** use o *backend* dela: a autorização é a do GPS,
  e o *backend* da biblioteca associa contas pelo e-mail.
- **SAML/OIDC no proxy:** `concluir` lê o que o proxy injeta, e só do proxy. O nginx precisa apagar o
  cabeçalho que vier do cliente, e a aplicação precisa aceitá-lo só da conexão do proxy. Esse é o
  risco principal dessa forma, e pede teste próprio (E-15 do estudo).
- O módulo do adaptador **não importa modelos no topo**: `production.py` o importa antes de os apps
  existirem.
- Testes do adaptador contra um provedor de homologação, e não só o simulado.

### Condições do adaptador, registradas na revisão do #345

Não são entrega da `106`; são o que o adaptador real precisa cumprir.

- **O identificador externo é emissor + `sub`, e não o `sub` sozinho.** O `sub` só é único dentro do
  emissor (`iss`). O `nome` do adaptador vai a `IdentidadeExterna.provedor`; se um mesmo adaptador
  puder falar com mais de um emissor, o `identificador` precisa levar o emissor junto — ou cada
  emissor ser um adaptador com `nome` próprio. Mudar isso depois de gravado é trocar a associação de
  todas as pessoas.
- **PKCE e `nonce`**, como acima, mesmo com cliente confidencial.
- **No proxy**, o cabeçalho de identidade é apagado da requisição do cliente e só aceito da conexão
  do proxy (abaixo).

## 3. As telas

A `107` entregou as cinco que a `106` deixou fora; ver o [quickstart](../specs/107-gestao-de-acessos/quickstart.md).

| Tela | Situação |
|---|---|
| Exibir o nome no lugar do identificador | **na barra, na página de acesso e nas telas de acesso** (`107`). As demais telas que mostram o `subject` de outra pessoa — históricos da comissão, da trilha, do Edital — continuam com o identificador: incremento 2 da `107` |
| "Sem acesso a nenhuma unidade" | **feita** (`107`): `/gestao/sem-acesso`, com o nome, a quem pedir e a troca para o escopo em que a pessoa ainda atua |
| Seletor de unidade na barra | **feito** (`107`) |
| Acessos da unidade e administração institucional | **feitas** (`107`): consulta, concessão e revogação com busca de pessoas, confirmação, motivo e histórico |
| A recusa que nomeia quem concede | continua a frase canônica da `033`, "a quem administra o sistema no Cefor"; mudá-la é decisão da `033` |

## 4. O que não foi feito, e é preciso antes de abrir

- **Suspensão e reativação** de uma pessoa em todas as unidades, **inclusive do administrador
  institucional** (decisões 7 e 8). Decididas em 30/10 e **implementadas** no incremento 2 da `107`
  (US6, US7). A suspensão troca o hash da sessão, para que
  nenhuma sessão anterior volte na reativação (`D-015` da `107`): `is_active=False` sozinho não
  basta, porque a sessão parada durante a suspensão voltaria a valer.
- **Duração da sessão** (decisão 5): o mecanismo entrou com a `107`, e os valores foram decididos —
  480 e 30 minutos, declarados no `app.env` (§5). Produção com provedor não sobe sem eles.
- **Retirada e substituição da administração institucional** (decisão 9): decididas e
  **implementadas** (US8 da `107`), pelos comandos de implantação:

  ```bash
  ps-manage retirar_administracao_institucional --provedor <nome> --identificador <id> --motivo "Portaria nº …"
  ps-manage substituir_administracao_institucional --de-provedor <nome> --de-identificador <id> --para-provedor <nome> --para-identificador <id> --motivo "Portaria nº …"
  ps-manage suspender_pessoa --provedor <nome> --identificador <id> --motivo "…"
  ```
- **Comissão apontando para pessoa.** O `identity_subject` da comissão continua texto livre; com o
  identificador opaco, incluir um membro por ele é impraticável. Falta a busca da pessoa.
- **API.** Continua fechada em produção. A recusa da `SessionAuthentication` deve ser revista quando
  houver consumidor, porque a sessão passa a nascer do provedor.
- **Retenção (B-2).** A `auth_user` guarda nome e e-mail de servidores, e entra na política.
- **Trilha da unidade.** Os eventos `ENTRADA`, `SAIDA`, `TROCA_DE_UNIDADE`, `ACESSO_CONCEDER` e
  `ACESSO_REVOGAR` já são gravados; a leitura é a spec do grupo 2 do parecer.

## 5. A implantação

1. Configurar o provedor e declarar no `app.env`:

   ```
   GESTAO_PROVEDOR_INSTITUCIONAL=<o caminho da classe do adaptador>
   GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS=480
   GESTAO_SESSAO_INATIVIDADE_MINUTOS=30
   ```

   Os dois prazos são a decisão de 30/10/2026; mudá-los é decisão nova, e se documenta aqui.
   Produção recusa subir se a classe não se importar, se estiver em `tests.`, se declarar
   `apenas_para_testes`, ou se faltar um dos prazos.
2. Subir e rodar `ps-migrar` (provisionar, migrar, provisionar: **46 de 46** desde o incremento 2 da
   `107`; e a semente das Unidades, que num banco existente diz que não se aplica).
3. Conceder os dois administradores institucionais designados pelo ato — o segundo com
   `--adicional`. **Desde a `110` o papel se chama Administrador institucional, e administra também o
   registro de Unidades**: o ato que designa a pessoa deve dizer as duas responsabilidades. Se já
   houver alguém com o papel concedido antes da `110`, a ampliação precisa de autorização expressa
   antes do deploy dela (passo 0 da [migração da 110](../specs/110-cadastro-de-unidades/migracao.md)):

   ```bash
   ps-manage conceder_administracao_institucional --provedor <nome> --identificador <id> --motivo "Portaria nº …"
   ```

4. Cada pessoa entra uma vez com a conta institucional e vê a tela sem acesso — é o que a torna
   encontrável na busca. O Administrador institucional, em "Administração de acessos", concede o
   Administrador de acessos do Cefor; este, em "Acessos da unidade", concede os papéis. Uma unidade
   nova entra pela tela "Unidades", do mesmo Administrador institucional, antes da concessão do
   administrador de acessos dela. Tudo pela interface, com motivo e trilha (`107`, `110`).
5. O Gestor cadastra as autoridades. Só então a primeira publicação é possível.

**Não há migração de dado.** A gestão nunca abriu em produção, e nenhum ato real foi gravado com
identidade de demonstração. Se essa premissa falhar, pare: os `subject` antigos ficam nas tabelas
append-only como estão, e a correspondência com as pessoas novas precisa de decisão própria.
