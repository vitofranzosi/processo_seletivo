# Homologação com o seletor de demonstração

*Desde a [`106`](../specs/106-identidade-institucional-preparada/spec.md), 30/10/2026.* Este
documento diz o que mantém a homologação funcionando enquanto o SSO institucional não chega, e o
que não fazer para não quebrá-la.

## O que não mudou

- A entrada é a mesma: `/gestao/identificar` → "Acessar ambiente de demonstração" → escolher a
  identidade e os papéis. Os oito papéis são os mesmos, e a sessão guarda o mesmo
  `{subject, escopo, papeis, origem}`.
- Elaboração, homologação, publicação, retificação e comissões se percorrem como antes. A suíte
  que as exercita pelo seletor passou sem nenhuma mudança de resultado esperado.
- Os dados e os documentos já gravados nos bancos de homologação não foram tocados. A migration da
  `106` só cria três tabelas vazias e dois gatilhos sobre a `auth_user`.

## O que é preciso ligar

Uma variável só, a de sempre:

```bash
INTERFACE_SELETOR_IDENTIDADE=true
```

Ela é lida por `make runserver` a partir do `backend/.env`, e pelo `docker compose`. Um `manage.py`
chamado à mão fora do `make` não lê o `.env` — exporte a variável antes.

**Depois de atualizar o código**, rode o `make preparar` (ou `ps-migrar` no servidor). O
`provisionar_papeis` passa a informar **44 de 44** tabelas append-only; se o primeiro número vier
`0`, a segunda passada não rodou.

## O que não fazer

| Não faça | Por quê |
|---|---|
| Carregar `config.settings.production` na homologação | a marca de produção desliga o seletor **em execução**, mesmo com a variável ligada (`FR-3003`); a gestão responde 503 |
| Declarar `GESTAO_PROVEDOR_INSTITUCIONAL` sem provedor de verdade | a página de acesso passa a oferecer "Entrar com a conta institucional", e o botão leva a um provedor que não existe. O seletor continua ao lado, mas a tela muda |
| Apontar `GESTAO_PROVEDOR_INSTITUCIONAL` para o provedor simulado | ele mora em `backend/tests/` e responde só a quem a suíte mandar; fora dos testes, ninguém entra por ele |
| Criar usuário com `createsuperuser` esperando acesso | o único *backend* é o institucional, que não aceita senha; o superusuário não tem vínculo e não entra (`D-008` da `106`) |
| Dar a identidades de demonstração nomes que começam por `pessoa-` | é o formato do identificador institucional; as duas origens não se cruzam, mas um relatório da trilha ficaria ambíguo |

## Os dois modos lado a lado

Num ambiente com o seletor **e** um provedor de homologação — o caso de quando o SSO entrar em
teste —, as duas entradas convivem na mesma página. Elas não se misturam:

- quem entra pelo seletor não cria pessoa, identidade externa nem vínculo;
- quem entra pelo provedor tem os papéis dos vínculos, e não os que escolheria no seletor;
- entrar por uma descarta a sessão da outra.

O seletor deixa qualquer pessoa declarar qualquer identidade, inclusive o identificador de uma
pessoa institucional. É a natureza da demonstração, e é por isso que ela nunca existe em produção.

## Verificação

```bash
cd backend && make lint check test-pg
```
