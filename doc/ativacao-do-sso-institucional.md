# O que falta para ativar o SSO institucional

*Desde a [`106`](../specs/106-identidade-institucional-preparada/spec.md), 30/10/2026.* A
arquitetura está pronta para receber a identidade do provedor do Ifes; o provedor real não foi
integrado. Este documento lista o que falta, na ordem em que se resolve, e o que cada item pede.

## 1. Decisões do usuário

Nenhuma bloqueia o código já entregue; todas bloqueiam a ativação.

| # | Decisão | Proposta da 106 | Onde se aplica |
|---|---|---|---|
| 1 | Provedor e protocolo (decisão 1 do estudo) | OIDC na aplicação, ou SAML/OIDC terminado no proxy | a classe do adaptador |
| 2 | Qual identificador do provedor localiza a pessoa (decisão 2) | o identificador imutável (`sub`, `objectGUID`) | a classe do adaptador; nenhum dado gravado |
| 3 | Quem é o administrador institucional de acessos (decisão 4) | quem a portaria indicar | o comando `conceder_administracao_institucional` |
| 4 | Quem concede na unidade (decisão 5) | papel próprio, separado do Gestor | uma linha em `seguranca/acessos.py` |
| 5 | Tempo de sessão e inatividade (decisão 11) | 8 h absolutas, 30 min de inatividade | a sessão institucional |
| 6 | Portão do diretório (decisão 3) | sem portão: toda conta entra e vê "sem acesso" | o adaptador |

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

## 3. As telas que ficaram fora

| Tela | Por que ficou fora | O que já existe |
|---|---|---|
| Exibir o nome no lugar do identificador | o `subject` institucional é `pessoa-<uuid>`, e 18 templates mostram o `subject` cru ("Continuar como pessoa-1b4e…", "por pessoa-1b4e…") | o nome está em `auth_user.first_name`; falta um filtro único |
| "Sem acesso a nenhuma unidade" | quem entra sem vínculo volta à página de acesso, como quem não entrou | o estado é detectável: sessão institucional sem `Actor` |
| Seletor de unidade na barra | a troca existe (`POST /gestao/unidade-ativa`) e não tem botão | `identidade.trocar_unidade`, com trilha |
| Acessos da unidade e administração institucional | conceder e revogar existem só na camada de aplicação | `seguranca/application/acessos.py`, com todas as recusas e a trilha |
| A recusa que nomeia quem concede | `recusa.html` manda pedir "a quem administra o sistema no Cefor" | o papel existe: Administrador de acessos da unidade |

## 4. O que não foi feito, e é preciso antes de abrir

- **Suspensão urgente** de uma pessoa em todas as unidades, **inclusive do administrador
  institucional**. O mecanismo nativo existe — `is_active=False` derruba a sessão na requisição
  seguinte —, mas falta o ato com motivo e trilha, e falta dizer quem suspende o administrador
  institucional, que hoje só o comando de implantação alcança.
- **Duração da sessão** (decisão 5 da tabela acima): 8 h absolutas e 30 min de inatividade são
  proposta, e nada as impõe ainda. Até lá, a sessão institucional dura o que o `SESSION_COOKIE_AGE`
  do Django disser.
- **Comissão apontando para pessoa.** O `identity_subject` da comissão continua texto livre; com o
  identificador opaco, incluir um membro por ele é impraticável. Falta a busca da pessoa.
- **API.** Continua fechada em produção. A recusa da `SessionAuthentication` deve ser revista quando
  houver consumidor, porque a sessão passa a nascer do provedor.
- **Retenção (B-2).** A `auth_user` guarda nome e e-mail de servidores, e entra na política.
- **Trilha da unidade.** Os eventos `ENTRADA`, `SAIDA`, `TROCA_DE_UNIDADE`, `ACESSO_CONCEDER` e
  `ACESSO_REVOGAR` já são gravados; a leitura é a spec do grupo 2 do parecer.

## 5. A implantação

1. Configurar o provedor e declarar `GESTAO_PROVEDOR_INSTITUCIONAL` no `app.env`. Produção recusa
   subir se a classe não se importar, se estiver em `tests.` ou se declarar `apenas_para_testes`.
2. Subir e rodar `ps-migrar` (provisionar, migrar, provisionar: **44 de 44**).
3. Conceder o primeiro administrador institucional:

   ```bash
   ps-manage conceder_administracao_institucional --provedor <nome> --identificador <id> --motivo "Portaria nº …"
   ```

4. O administrador institucional concede o Administrador de acessos do Cefor; este concede os
   papéis. Até haver tela, pela camada de aplicação, num `ps-manage shell` — o que é aceitável só
   para os primeiros acessos, e é registrado na trilha como qualquer concessão.
5. O Gestor cadastra as autoridades. Só então a primeira publicação é possível.

**Não há migração de dado.** A gestão nunca abriu em produção, e nenhum ato real foi gravado com
identidade de demonstração. Se essa premissa falhar, pare: os `subject` antigos ficam nas tabelas
append-only como estão, e a correspondência com as pessoas novas precisa de decisão própria.
