# ADR — Identidade e autorização da gestão

**Situação:** aceita para o incremento da [`106`](../specs/106-identidade-institucional-preparada/spec.md),
em 30/10/2026. Três pontos ficam **propostos ao usuário**, e nenhum deles bloqueia o que foi
implementado (§Propostas). Substitui, no que diverge, a proposta de ADR da §G do
[estudo do B-1](estudo-identidade-e-acessos-2026-10-30.md).

**Diagnóstico que a sustenta:** [Django Auth × identidade própria](diagnostico-autenticacao-da-gestao-2026-10-30.md).

## Contexto

- A gestão não tem autenticação de produção, e responde 503 lá. O seletor de demonstração é a
  entrada de desenvolvimento e homologação, e precisa continuar exatamente como está.
- O `Actor` é a fronteira única de autorização. A gestão o constrói em um ponto,
  `interface/identidade.ator_da_sessao`.
- O catálogo `PAPEIS` é regra de domínio, em código, com justificativa normativa em cada linha.
- O `subject` vai como texto a colunas append-only, e a segregação o compara. O valor que entrar em
  produção não se corrige depois.
- O provedor institucional ainda não foi escolhido. O pedido de 30/10 adia a integração real.

## Decisão

1. **O Django Auth guarda quem é a pessoa, e só isso.** Cada pessoa institucional é um
   `auth.User`. A senha é inutilizável, e `is_superuser`, `is_staff`, `groups` e
   `user_permissions` não autorizam nada. O único *backend* de autenticação declarado é o do GPS,
   que não aceita senha. O `django.contrib.admin` não é instalado.
2. **O identificador estável é gerado pelo GPS.** O `username` é `pessoa-<uuid4>`, nasce na
   primeira entrada e um gatilho do PostgreSQL recusa mudá-lo. É ele o `subject` dos atos e da
   trilha. Nenhum `auth_user` se exclui.
3. **Os identificadores do provedor só localizam a pessoa.** A tabela `IdentidadeExterna` associa
   `(provedor, identificador)` a um `User`, única nos dois sentidos, append-only. Trocar de
   provedor é acrescentar uma associação. Nunca se associa pelo e-mail.
4. **O GPS autoriza, por vínculos.** `Vinculo` (pessoa × escopo × papel, com quem concedeu e o
   motivo) e `RevogacaoDeVinculo` são append-only, com gatilho e privilégio ausente. "Quem tinha o
   papel X na unidade Y na data D" se responde pela tabela, e não só pela trilha.
5. **O `Actor` não muda de forma.** No modo institucional ele é recalculado a cada requisição, dos
   vínculos vigentes da **unidade ativa** da sessão: a revogação vale na requisição seguinte, e
   trocar de unidade não carrega permissão de uma para a outra. **Sem vínculo vigente na unidade
   ativa, não há `Actor`** — e por isso a presidência de uma comissão não alcança quem perdeu o
   acesso à unidade.
6. **O catálogo continua em código.** `PAPEIS` não muda. Os papéis de acesso ficam num catálogo
   ao lado, em `seguranca/acessos.py`, para que o seletor de demonstração continue com as mesmas
   oito caixas.
7. **Ninguém concede a si mesmo, e cada nível concede só o que é seu.** O administrador de acessos
   da unidade concede papéis operacionais na sua unidade; o administrador institucional concede o
   administrador de acessos de qualquer unidade e nenhum poder operacional. O administrador
   institucional nasce só por comando de implantação, com motivo, gravado sob o ator `implantacao`.
8. **A autenticação é um adaptador com contrato fixo.** O provedor entrega
   `IdentidadeAutenticada(provedor, identificador, nome, email)` de uma autenticação concluída, ou
   nada. O GPS nunca lê identidade de cabeçalho ou parâmetro do cliente: só o que o adaptador
   devolve, dentro de um retorno que carrega o estado criado na ida.
9. **A demonstração continua, e nunca em produção.** O seletor sai pela mesma chave de hoje.
   Produção recusa subir com ela, recusa um provedor marcado como de teste, e, **em execução**, o
   seletor se declara indisponível sempre que a marca de produção estiver ligada.

## Propostas ao usuário

São governança, e não técnica. O código as acomoda sem reescrita.

| | Proposta | Por que não bloqueia | O que muda se a resposta for outra |
|---|---|---|---|
| **Identificador do provedor** (decisão 2 do estudo) | o identificador imutável do provedor (`sub` do OIDC, `objectGUID`) | o `subject` dos atos é interno; o identificador externo só localiza a pessoa | a configuração do adaptador, e nenhum dado gravado |
| **Quem é o administrador institucional** (decisão 4) | quem a portaria indicar, uma ou duas pessoas, concedido pelo comando de implantação com o número da portaria como motivo | o papel existe e é inerte até o comando rodar | nada no código |
| **Quem concede na unidade** (decisão 5) | papel próprio, *Administrador de acessos da unidade*, separado do Gestor | a capacidade é `acesso:gerir`, e o papel que a recebe é uma linha do catálogo | uma linha: `acesso:gerir` passa ao Gestor, e o papel próprio deixa de ser concedido |

A **segregação mais estrita** (decisão 8 do estudo: quem elabora não homologa) continua fora. É
emenda à FR-021 da `001`, e não consequência deste incremento.

## Consequências

**Positivas.**

- A segregação passa a comparar uma identidade que não muda com o login, a sessão, a unidade ou o
  provedor.
- A revogação vale na requisição seguinte, e a presidência de comissão não abre caminho lateral.
- A integração real com o SSO se reduz a escrever uma classe que cumpra o contrato — tipicamente
  sobre uma biblioteca do ecossistema do Django — e a declará-la.
- Os testes atuais não mudam.

**Negativas.**

- Três tabelas append-only novas (o `M` do `provisionar_papeis` passa de 41 a **44**), e dois
  gatilhos sobre a `auth_user`, que é tabela do Django.
- O `User` guarda nome e e-mail da pessoa, que é dado pessoal e entra na política de retenção
  (B-2).
- O `subject` institucional é opaco. A gestão precisa exibir o nome no lugar dele antes da ativação
  ([pendências](ativacao-do-sso-institucional.md)).

## Rejeitadas

- **Identidade própria (alternativa B do diagnóstico):** mais uma tabela e a sessão escrita à mão,
  sem ganho de segurança, e com custo maior na integração real.
- **`username` igual ao login institucional:** muda com o nome da pessoa, e uma pessoa viraria duas
  na segregação.
- **`id` inteiro do Django como `subject`:** é de um banco só.
- **Grupos e permissões do Django como vínculo:** são globais, sem unidade, e a concessão não guarda
  quem, quando nem por quê.
- **`django.contrib.admin`:** escreve no ORM sem trilha e sem as recusas do domínio.
- **Associação automática pelo e-mail:** tomada de conta.
- **Escopo plural no `Actor`:** reescreveria todo chamador de `require_permission` sem requisito.
