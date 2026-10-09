# Implantação em produção numa VM Ubuntu Server

Manual de primeira implantação, arquitetura de produção, atualização, backup e restauração, runbook
e checklists do Sistema de Processos Seletivos e Editais do Cefor/Ifes. É escrito para quem conhece
Linux, mas não conhece o projeto por dentro.

**Como ler.** Cada afirmação sobre o sistema traz a **Evidência** — arquivo e linha do repositório.
O que é **constatado** vem com essa evidência. O que é **recomendado** para produção vem marcado como
recomendação e **não existe no repositório**: nenhum arquivo de nginx, systemd ou script `ps-*` deste
documento está versionado. Todos são criados na VM, pelos comandos daqui.

**Ensaiado, e não só escrito.** Em 29/09/2026 o caminho de produção foi executado contra PostgreSQL
local, com as dependências travadas do `uv.lock` e as settings de produção. Foram ensaiados a
preparação do banco em três passos, o `check --deploy`, o gunicorn atrás de proxy simulado, o CSRF,
o backup com `pg_dump` e a restauração num banco novo. Os resultados estão citados onde servem de
prova. O que **não** pôde ser ensaiado — nginx, certbot, ufw e systemd, por falta de uma VM Ubuntu —
está dito em cada seção.

Os comandos indicam quem os executa:

- **[admin]** — usuário administrativo pessoal, com `sudo`;
- **[app]** — usuário da aplicação, sempre por meio do `ps-manage`, que troca de usuário sozinho.

Os placeholders:

| Placeholder | Significado |
|---|---|
| `<DOMINIO>` | ex.: `processoseletivo.exemplo.edu.br` |
| `<IP_DO_SERVIDOR>` | IP público fixo da VM |
| `<ADMIN>` | login do administrador |
| `<REDE_ADMINISTRATIVA>` | CIDR de onde o SSH é aceito |
| `<REPOSITORIO>` | `org/repo` no GitHub |
| `<SHA>` | commit a implantar |
| `<SMTP_HOST>`, `<SMTP_USUARIO>` | servidor e conta de envio |
| `<REMETENTE>` | endereço remetente das mensagens |
| `<HOST_BACKUP>` | servidor de backup fora da VM |
| `<EMAIL_ALERTA>` | quem recebe os alertas |
| `<IP_MONITORAMENTO>` | origem do monitoramento externo |

---

## Sumário

1. [Resumo executivo](#1-resumo-executivo)
2. [Arquitetura encontrada no projeto](#2-arquitetura-encontrada-no-projeto)
3. [Arquitetura proposta para produção](#3-arquitetura-proposta-para-produção)
4. [Pré-requisitos](#4-pré-requisitos)
5. [Preparação da VM](#5-preparação-da-vm)
6. [Hardening](#6-hardening)
7. [Instalação das dependências](#7-instalação-das-dependências)
8. [Código e releases](#8-código-e-releases)
9. [Banco de dados](#9-banco-de-dados)
10. [Configuração e segredos](#10-configuração-e-segredos)
11. [Migrations e bootstrap](#11-migrations-e-bootstrap)
12. [Serviço da aplicação](#12-serviço-da-aplicação)
13. [HTTPS/TLS](#13-httpstls)
14. [Reverse proxy](#14-reverse-proxy)
15. [Static, documentos e arquivos privados](#15-static-documentos-e-arquivos-privados)
16. [E-mail](#16-e-mail)
17. [Smoke test](#17-smoke-test)
18. [Backup](#18-backup)
19. [Restore](#19-restore)
20. [Logs e auditoria](#20-logs-e-auditoria)
21. [Monitoramento](#21-monitoramento)
22. [Atualização](#22-atualização)
23. [Rollback](#23-rollback)
24. [Runbook de incidentes](#24-runbook-de-incidentes)
25. [Checklist de segurança e LGPD](#25-checklist-de-segurança-e-lgpd)
26. [Gaps encontrados no projeto](#26-gaps-encontrados-no-projeto)
27. [Possíveis evoluções futuras](#27-possíveis-evoluções-futuras)
28. [Auditoria cruzada](#28-auditoria-cruzada)
- [Apêndice A — Deploy Cheat Sheet](#apêndice-a--deploy-cheat-sheet)
- [Apêndice B — GO-LIVE (imprimível)](#apêndice-b--go-live--processo-seletivo)

A ordem segue a execução, e por isso difere num ponto da ordem pedida: migrations (§11) vêm antes do
serviço (§12), porque o serviço não fica pronto com migration pendente, e o certificado (§13) vem
antes do proxy completo (§14), porque o nginx não carrega um `server` TLS sem certificado.

---

## 1. Resumo executivo

**O sistema ainda não pode entrar em produção institucional.** Há dois bloqueadores (§26):

1. **A interface de gestão não tem autenticação de produção.** Sem o seletor de identidade — que
   `config.settings.production` recusa —, `/gestao/identificar` responde **503**. Ninguém consegue
   criar, publicar ou conduzir um Edital, e não existe como criar o primeiro usuário administrativo.
   Correção: um adaptador de autenticação institucional, que é o passo pendente "Caminho de produção".
2. **Não existe política institucional de retenção e descarte** de dados pessoais. O README a
   declara precondição para receber dado real.

**O que este documento entrega mesmo assim.** Uma VM endurecida, com a aplicação no ar sob as
settings de produção, que já recusam subir inseguras. O portal público responde, a gestão responde
503 por construção, e backup, restauração, monitoramento e atualização estão prontos. Quando o
adaptador de autenticação existir, a entrada em operação é uma atualização comum (§22), e não um
projeto de infraestrutura.

**A arquitetura, em uma linha:** nginx (TLS) → gunicorn (systemd, usuário sem privilégio) →
PostgreSQL local, mais um diretório privado de documentos. Não há fila, worker, cache nem
agendador, porque o sistema não os tem (§2). Os únicos jobs são manutenção e backup, por timers do
systemd.

**Os riscos operacionais mais caros, se ignorados:**

- **`DJANGO_SECRET_KEY` é segredo persistente.** Ela assina os códigos de verificação dos
  comprovantes de inscrição. Perdê-la, ou trocá-la, invalida todos os comprovantes já emitidos (§10).
- **O e-mail é o único fator de autenticação do candidato.** SMTP fora do ar significa candidato sem
  acesso (§16).
- **Publicação é imutável e nada é excluído.** Um teste que publique em produção fica público para
  sempre. Nunca rode `seed_demo` em produção (§11, §17).
- **O HSTS de um ano é obrigatório pelo código.** Um certificado vencido torna o site inacessível,
  sem contorno, para quem já o visitou (§13).

---

## 2. Arquitetura encontrada no projeto

Tudo nesta seção é **constatado**.

| Componente | O que existe | Evidência |
|---|---|---|
| Linguagem e framework | Python `>=3.13,<3.14`, Django 5.2.17, DRF 3.16.1, psycopg 3.3 (binary), openpyxl 3.1.5 | `backend/pyproject.toml:9-18`, `backend/uv.lock` |
| Gerenciador de dependências | `uv`, com lock versionado; o Dockerfile fixa o uv 0.9 | `backend/uv.lock`, `Dockerfile:14` |
| SGBD | **Somente PostgreSQL**; SQLite só na suíte. O CI valida contra o PostgreSQL 18 | `config/settings/base.py:257-266`, `config/settings/test.py`, `.github/workflows/backend.yml` |
| Papéis do banco | Dois papéis: migração (dono do esquema) e runtime (DML). O runtime **não** tem `UPDATE`/`DELETE` em 34 tabelas append-only, que também têm gatilhos | `processo_seletivo/seguranca/papeis.py:26-121`, `seguranca/management/commands/provisionar_papeis.py` |
| Preparação do banco | provisionar → migrar → provisionar de novo; a segunda passada é a que tranca | `backend/Makefile` (`preparar`), `scripts/docker/entrypoint.sh` |
| Settings | `base`, `development`, `test` e `production`. `production` **recusa subir** com qualquer pressuposto inseguro | `config/settings/production.py` |
| Entrada WSGI | `config.wsgi` usa `production` por padrão; o **`manage.py` usa `development`** | `config/wsgi.py:14`, `manage.py:7` |
| Servidor de aplicação | **Nenhum** entre as dependências. O Dockerfile roda `runserver` e se declara só de desenvolvimento | `pyproject.toml:9-18`, `Dockerfile:8-10,59` |
| Workers, filas, agendador | **Não existem.** Prazos, fases do Cronograma e vigência de Retificação são calculados na leitura | ausência de celery, rq, huey, dramatiq e apscheduler; `inscricoes/domain/periodo.py`, `publicacoes/application/selectors.py` |
| E-mail | SMTP **síncrono**, dentro da requisição: código de acesso, comprovante e convocação. O aviso aos candidatos (066) sai **fora** da requisição, por timer (§16.4). Só STARTTLS (`EMAIL_USE_TLS`), sem `EMAIL_USE_SSL`; `EMAIL_TIMEOUT` desde a 066 | `config/settings/base.py:172-178`, `identidade/application/mensagem.py`, `convocacao/application/comunicar.py` |
| Cache | Nenhum `CACHES`. O limite de pedidos de código é contado **no banco** | `identidade/application/desafio.py:14-16` |
| Sessões | Backend de banco padrão, cookie único `sessionid`, validade de 2 semanas. Nada limpa sessões expiradas | ausência de `SESSION_ENGINE` e `SESSION_COOKIE_AGE`; `production.py:242-247` |
| Documentos do candidato | Disco, em `ARQUIVOS_CANDIDATOS_RAIZ`, como `inscricoes/<uuid>/<uuid>.pdf`. O arquivo nunca tem URL, e todo download passa pela aplicação | `inscricoes/storage.py:27-72`, `portal/arquivos.py` |
| Anexos do Edital e PDFs publicados | Bytes **no banco**, em `BinaryField`. O PDF é gerado em Python puro, com fontes base-14, sem dependência de sistema | `editais/models/anexos.py:43`, `publicacoes/infrastructure/pdf.py`, `divulgacao/models.py` |
| Exportação de matrículas | `.xlsx` montado em memória e **não guardado**; fica só o registro da geração | `matriculas/infrastructure/planilha.py`, `matriculas/models.py` |
| Arquivos estáticos | 22 arquivos JS em `interface/static/interface/` e `portal/static/portal/`; o CSS é inline. **Não há `STATIC_ROOT`** — o `collectstatic` falha (ensaiado) | `config/settings/base.py:150` |
| Integrações externas | SMTP. Loteria Federal (`https://servicebus2.caixa.gov.br/...`), chamada **só por ação do gestor**. Base de CEP carregada de arquivo `.zip` local | `sorteios/infrastructure/fontes/loteria_federal.py:22`, `doc/runbook-base-de-cep.md` |
| Saúde | `/health` (não toca o banco), `/readiness` (banco e migrations pendentes, 503 se falhar), `/metrics` (exige autenticação da API) | `processo_seletivo/shared/api/operacional.py` |
| Logs | JSON, uma linha por evento, no **stdout**, com `correlationId`. Não há arquivo de log | `config/settings/base.py:281-294`, `shared/observability.py` |
| Correlação | `X-Correlation-ID` de entrada é aceito (ASCII até 100 caracteres), ecoado na resposta e gravado na auditoria | `shared/api/middleware.py` |
| Auditoria funcional | `RegistroAuditoria`, append-only em três camadas (modelo, gatilho, privilégio), consultável em `/gestao/.../auditoria` e na API | `processo_seletivo/auditoria/` |
| Autenticação da gestão | **Seletor de identidade de desenvolvimento**; em produção, 503 | `interface/views.py:606-610`, `interface/identidade.py:6-8` |
| Autenticação do candidato | Sem senha: código de 6 dígitos por e-mail, validade de 10 min, 5 tentativas, 5 pedidos por hora por endereço e 30 por hora por origem | `identidade/domain/codigo.py`, `identidade/application/desafio.py:35-42` |
| Autenticação da API admin | Adaptador de desenvolvimento, que produção recusa; **não há classe institucional** | `seguranca/api/authentication.py`, `production.py:199-228` |
| CORS | Não existe, e não é necessário: a mesma origem serve tudo | ausência de `django-cors-headers` |
| Seeds e fixtures obrigatórias | **Nenhuma.** `seed_demo` é só demonstração | `processos/management/commands/seed_demo.py:1-6` |
| Docker | `Dockerfile` e `compose.yaml` **só para desenvolvimento** | `Dockerfile:8-10`, `compose.yaml:11-13` |

**Conflitos com o cenário pedido:**

- **"Acesso público à aplicação pela Internet"** vale para o portal (`/selecoes/`) e para a API
  pública. A gestão hoje não autentica ninguém em produção (B-1). Quando autenticar, avalie restringi-la
  à rede institucional ou VPN (§27).
- **"Criar o primeiro usuário administrativo"** não tem caminho. O `django.contrib.admin` não está
  instalado (`base.py:21-26`), o `createsuperuser` criaria um usuário que nada lê, e os papéis da
  gestão são um dicionário fixo, escolhido no seletor (`interface/identidade.py:20-100`).

---

## 3. Arquitetura proposta para produção

Recomendação. Nada disto está no repositório.

```
                         Internet
                            │
                ┌───────────▼────────────┐
                │ ufw: 22 (só <REDE_ADM>)│
                │      80, 443           │
                └───────────┬────────────┘
                            │ :443 (TLS) / :80 (ACME e 301)
                ┌───────────▼────────────┐   /static/interface/, /static/portal/
                │ nginx (www-data)       │── alias para a release ativa (só JS)
                │ TLS · limites de corpo │
                │ X-Forwarded-* · manut. │
                └───────────┬────────────┘
                            │ http://127.0.0.1:8000  (loopback, nunca exposto)
                ┌───────────▼────────────┐
                │ gunicorn (systemd)     │  processoseletivo.service
                │ usuário processoseletivo, sem shell, sistema de arquivos só leitura
                └──┬──────────┬──────────┘
                   │          │
   127.0.0.1:5432  │          │  leitura e escrita só aqui
┌──────────────────▼──┐   ┌───▼──────────────────────────────┐
│ PostgreSQL 18       │   │ /var/lib/processoseletivo/arquivos│
│ (postgres)          │   │ documentos dos candidatos (0700)  │
└─────────────────────┘   └───────────────────────────────────┘
        saída: SMTP :587 · servicebus2.caixa.gov.br :443 (dia do sorteio) · backup (sftp)
        timers: ps-backup (diário) · ps-verificar (5 min) · ps-limpeza (semanal) · ps-ceps (mensal) · certbot
```

| Componente | Porta | Exposição | Processo e unit | Usuário |
|---|---|---|---|---|
| SSH | 22/tcp | só `<REDE_ADMINISTRATIVA>` | `ssh.service` | root, com login só por chave |
| nginx | 80/tcp, 443/tcp | pública | `nginx.service` | master root; workers `www-data` |
| gunicorn | 127.0.0.1:8000 | **interna** | `processoseletivo.service` | `processoseletivo` |
| PostgreSQL | 127.0.0.1:5432 e socket | **interna** | `postgresql@18-main.service` | `postgres` |
| Backup, verificação, limpeza e CEP | — | — | `ps-*.timer` | root, e `processoseletivo` via `ps-manage` |
| certbot | — | — | `certbot.timer` | root |

| Caminho | Conteúdo | Dono e modo | Backup |
|---|---|---|---|
| `/opt/processoseletivo/repo.git` | espelho do repositório | root, 0755 | não: é reconstruível |
| `/opt/processoseletivo/releases/<data>-<sha12>/` | `backend/` do commit, com `venv` próprio, `REVISION` e `PACOTES` | root, só leitura | não: é reconstruível pelo SHA |
| `/opt/processoseletivo/current` | symlink para a release ativa | root | — |
| `/opt/processoseletivo/python/` | CPython 3.13 gerenciado pelo uv | root, 0755 | não |
| `/etc/processoseletivo/app.env` | ambiente de runtime, **com segredos** | root:root, 0600 | **não**: fica no cofre (§10) |
| `/etc/processoseletivo/migracao.env` | credencial do papel de migração | root:root, 0600 | **não**: fica no cofre |
| `/etc/processoseletivo/restic.env`, `restic.senha` | acesso ao repositório de backup | root:root, 0600 | **não**: fica no cofre |
| `/etc/processoseletivo/alerta.env` | destinatário dos alertas | root:root, 0600 | sim |
| `/etc/processoseletivo/gunicorn.conf.py` | configuração do gunicorn | root, 0644 | sim |
| `/var/lib/processoseletivo/arquivos/` | **documentos dos candidatos** | processoseletivo, 0700 | **sim** |
| `/var/lib/processoseletivo/implantacoes.log` | histórico de versões ativadas | root, 0644 | sim |
| `/var/lib/processoseletivo/ceps/` | `.zip` da base de CEP | root:processoseletivo, 0750 | não: vem do storage institucional |
| `/var/lib/postgresql/18/main/` | dados do PostgreSQL | postgres | sim, via `pg_dump` |
| `/var/backups/processoseletivo/` | dumps locais (7 dias) e marca do último backup | root, 0700 | vai para o restic |
| `/var/log/nginx/processoseletivo.*.log` | acesso e erro do proxy | www-data/adm | não; rotação local |
| journald (`journalctl -u processoseletivo`) | log da aplicação e dos timers | root | não; retenção local |
| `/var/log/postgresql/` | log do banco | postgres/adm | não |

Não há `/var/log/processoseletivo/`: a aplicação só escreve no stdout (`base.py:281-294`), e o
journald já coleta, carimba a hora e rotaciona. Um arquivo à parte duplicaria dado pessoal em log
sem ganho.

---

## 4. Pré-requisitos

| Item | Valor sugerido | Premissa e justificativa |
|---|---|---|
| Sistema | **Ubuntu Server 24.04 LTS**, x86_64 | Suporte padrão até 2029. É a série em que os caminhos abaixo foram pensados: nginx 1.24, systemd 255, timesyncd. Com a 26.04, confira as versões dos pacotes |
| PostgreSQL | **18**, do repositório oficial PGDG | É a versão que o CI valida (`backend.yml`). O README aceita 16+, mas só a 18 é verificada a cada push |
| Python | **3.13**, instalado pelo `uv` | `requires-python = ">=3.13,<3.14"`. O Ubuntu 24.04 traz 3.12 |
| vCPU | 2 no mínimo, **4 recomendadas** | Workers síncronos (2×vCPU+1), PDF gerado em Python puro, PostgreSQL no mesmo host |
| RAM | 4 GB no mínimo, **8 GB recomendados** | ~90 MB por worker ocioso (medido); ~150–250 MB com upload; `shared_buffers` de 1 GB; o resto é cache de página para PDFs |
| Disco do sistema | 40 GB | SO, releases (~150 MB cada, 5 guardadas), logs |
| Disco de dados | pelo cálculo abaixo, **volume separado** montado em `/var/lib` | Crescer o volume de documentos sem mexer no sistema |
| DNS | registro `A` (e `AAAA`, se houver IPv6) de `<DOMINIO>` para `<IP_DO_SERVIDOR>` | Exigido pelo HTTP-01 do Let's Encrypt |
| Portas de entrada | 22 (restrita), 80, 443 | — |
| Saída | 53, 123/udp, 80/443 (apt, PGDG, PyPI, GitHub, ACME, Caixa), 587 para `<SMTP_HOST>`, 22 para `<HOST_BACKUP>` | Alinhe com o firewall institucional |
| Certificado | Let's Encrypt, ou certificado institucional (§13) | Veja se há registro CAA no domínio |
| SMTP | conta institucional com STARTTLS na 587, remetente autorizado (SPF, DKIM) | É o único canal de autenticação do candidato |
| Backup | servidor ou storage **fora da VM**, de preferência append-only | Regra 3-2-1 (§18) |
| Cofre de senhas institucional | obrigatório | Guarda `DJANGO_SECRET_KEY`, a senha do restic e o SMTP |
| Acesso ao console da VM | pelo hipervisor | É o caminho de volta se o SSH falhar (§6) |

**Estimativa de disco para documentos** (premissa a confirmar com o setor):

```
documentos ≈ inscrições por ano × documentos por inscrição × tamanho médio × anos retidos
exemplo: 5.000 × 5 × 1,5 MB × 2 anos ≈ 75 GB   (teto por arquivo: 10 MiB, base.py:200-202)
banco    ≈ 5–20 GB  (Editais, anexos e PDFs publicados em bytea, ~300 MB da base de CEP, auditoria)
backup local ≈ 7 dumps × tamanho do dump
```

Comece com o dobro da estimativa e alerta em 80% (§21). Os documentos **só crescem**: não há
expurgo implementado (§26, B-2).

**O SLO de carga não foi medido** (p95 ≤ 2 s nas consultas públicas; RC-96 em
`doc/auditoria-de-consolidacao-2026-09-26.md`). Meça em homologação, com o mesmo dimensionamento,
antes do go-live:

```bash
# de uma máquina externa, contra homologação
cd backend && uv run python scripts/carga_publica.py --base-url https://<DOMINIO_HOMOLOGACAO>/api/v1 --edital <uuid> --workers 50 --duracao 60
```

---

## 5. Preparação da VM

**[admin]** Parta de uma VM recém-instalada, com um usuário administrativo pessoal (`<ADMIN>`) no
grupo `sudo` e a chave SSH dele já autorizada.

### 5.1 Atualização e identidade

```bash
sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname processoseletivo
[ -f /var/run/reboot-required ] && sudo reboot
```

### 5.2 Fuso horário e relógio — antes de instalar o PostgreSQL

O relógio decide a validade de 10 minutos do código de acesso, a abertura e o encerramento de
inscrições, a vigência de Retificações, o instante gravado em cada registro de auditoria e o da
publicação de resultados. Relógio errado é ato com data errada.

O banco guarda instantes em UTC (`USE_TZ = True`) e a instituição lê em `America/Sao_Paulo`
(`base.py:11-12`). O fuso do SO define a hora dos logs e dos timers.

```bash
sudo timedatectl set-timezone America/Sao_Paulo
sudo mkdir -p /etc/systemd/timesyncd.conf.d
printf '[Time]\nNTP=a.st1.ntp.br b.st1.ntp.br c.st1.ntp.br d.st1.ntp.br\n' \
  | sudo tee /etc/systemd/timesyncd.conf.d/processoseletivo.conf
sudo systemctl restart systemd-timesyncd
```

Havendo NTP institucional, ponha-o primeiro na lista. Os servidores `*.st1.ntp.br` são os públicos
do NTP.br.

**Como verificar:**

```bash
timedatectl                          # Time zone: America/Sao_Paulo (-03); System clock synchronized: yes
timedatectl timesync-status          # Server: um dos configurados; Offset na casa dos ms
```

### 5.3 Locale para o banco

```bash
sudo locale-gen pt_BR.UTF-8
locale -a | grep -i pt_BR            # pt_BR.utf8
```

### 5.4 Atualizações automáticas de segurança

O Ubuntu Server já vem com `unattended-upgrades` para a origem de segurança.

```bash
cat /etc/apt/apt.conf.d/20auto-upgrades     # as duas linhas com "1"
sudo unattended-upgrade --dry-run -d 2>&1 | tail -3
```

Duas ressalvas de operação:

- O reboot automático fica desligado (`Unattended-Upgrade::Automatic-Reboot "false"`, o padrão).
  Reinicie na janela de manutenção quando existir `/var/run/reboot-required`, e **nunca** no último
  dia de inscrições nem durante a publicação de resultado.
- Os pacotes do PGDG **não** são atualizados automaticamente, porque não são origem de segurança do
  Ubuntu. Confira `apt list --upgradable | grep postgresql` todo mês e aplique na janela.

---

## 6. Hardening

### 6.1 Usuários, grupos e donos

| Usuário | Para quê | Login |
|---|---|---|
| `<ADMIN>` (um por pessoa) | administrar, via `sudo` | SSH por chave |
| `processoseletivo` | roda o gunicorn e o `manage.py` | **nenhum**: `nologin`, sem senha |
| `postgres` | o PostgreSQL, e o provisionamento de papéis por *peer* | nenhum |
| `www-data` | os workers do nginx | nenhum |

Contas pessoais, e não uma conta `admin` compartilhada, porque o `sudo` registra quem fez o quê
(`journalctl _COMM=sudo`), e o `ps-ativar` grava `SUDO_USER` no histórico de implantação.

**[admin]**

```bash
sudo groupadd --system acesso-ssh
sudo usermod -aG acesso-ssh <ADMIN>                    # repita para cada administrador

sudo useradd --system --user-group --home-dir /var/lib/processoseletivo --no-create-home \
  --shell /usr/sbin/nologin processoseletivo

sudo install -d -o root -g root -m 0755 /opt/processoseletivo /opt/processoseletivo/releases
sudo install -d -o root -g processoseletivo -m 0750 /etc/processoseletivo /var/lib/processoseletivo
sudo install -d -o processoseletivo -g processoseletivo -m 0700 /var/lib/processoseletivo/arquivos
sudo install -d -o root -g processoseletivo -m 0750 /var/lib/processoseletivo/ceps
sudo install -d -o root -g root -m 0700 /var/backups/processoseletivo /var/backups/processoseletivo/banco
sudo install -d -o root -g root -m 0755 /var/cache/processoseletivo /var/www/letsencrypt /var/www/processoseletivo/_erro
sudo touch /var/lib/processoseletivo/implantacoes.log
```

Por que estes modos:

- `/etc/processoseletivo` é 0750 com grupo da aplicação, porque o gunicorn precisa ler o
  `gunicorn.conf.py`. Os `.env` dentro dele são 0600 root: o **systemd** os lê como root antes de
  trocar de usuário, e a aplicação nunca lê o arquivo.
- `arquivos/` é 0700 da aplicação. Os arquivos que o Django grava saem 0644 (padrão, §15), e é o
  diretório que os protege.

**Como verificar:**

```bash
id processoseletivo                   # uid de sistema, grupo próprio
getent passwd processoseletivo        # termina em /usr/sbin/nologin
sudo namei -l /var/lib/processoseletivo/arquivos
```

### 6.2 SSH

> ⚠️ **Antes de aplicar, garanta que o login por chave funciona e mantenha uma sessão aberta.**
> Teste numa **segunda** sessão antes de fechar a primeira, e tenha o console do hipervisor à mão.
> Desligar a senha sem chave funcionando, ou pôr `AllowGroups` sem estar no grupo, tranca você
> para fora.

**[admin]**

```bash
ssh-keygen -lf ~/.ssh/authorized_keys          # a sua chave está aqui?
id -nG <ADMIN> | grep -w acesso-ssh            # você está no grupo? (refaça o login se acabou de entrar)

sudo tee /etc/ssh/sshd_config.d/10-processoseletivo.conf >/dev/null <<'CONF'
# Arquivo 10-*: o sshd usa o PRIMEIRO valor encontrado, e este vem antes do 50-cloud-init.conf,
# que em imagens de nuvem religa PasswordAuthentication.
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
AllowGroups acesso-ssh
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
CONF

sudo sshd -t && sudo systemctl restart ssh
```

**Como verificar** (sem fechar a sessão atual):

```bash
sudo sshd -T | grep -Ei '^(permitrootlogin|passwordauthentication|kbdinteractiveauthentication|allowgroups)'
# permitrootlogin no · passwordauthentication no · kbdinteractiveauthentication no · allowgroups acesso-ssh
# numa SEGUNDA janela:  ssh <ADMIN>@<IP_DO_SERVIDOR>  → entra
#                       ssh -o PubkeyAuthentication=no <ADMIN>@<IP_DO_SERVIDOR>  → Permission denied (publickey)
```

### 6.3 Firewall

**[admin]** A regra do SSH entra **antes** do `enable`.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from <REDE_ADMINISTRATIVA> to any port 22 proto tcp comment 'SSH administrativo'
#   sem rede administrativa fixa (desaconselhado):  sudo ufw limit 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP: ACME e redirecionamento'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw show added          # confira antes de ligar
sudo ufw enable
```

O PostgreSQL (5432) e o gunicorn (8000) **não** entram no firewall: escutam só em loopback. O
firewall é a segunda camada, não a primeira.

**Como verificar:**

```bash
sudo ufw status verbose       # Default: deny (incoming); 22 só da rede; 80 e 443 ALLOW
# depois das §9 e §12:
sudo ss -tulpn                # 0.0.0.0/[::] só em :22, :80 e :443; 127.0.0.1:5432 e 127.0.0.1:8000
# de OUTRA máquina:
nmap -Pn -p 1-65535 <IP_DO_SERVIDOR>   # abertas: 80 e 443 (e 22 só se a máquina estiver na rede adm.)
```

### 6.4 Fail2ban — avaliação

Com login só por chave, força bruta de senha no SSH não tem o que adivinhar, e restringir a porta
22 à rede administrativa (§6.3) elimina a exposição — o que é mais forte do que banir depois de N
tentativas. Para o portal, a aplicação já limita os pedidos de código por endereço e por origem, no
banco (`desafio.py:35-42`).

**Recomendação: dispensável com o SSH restrito por origem.** Se o SSH precisar ficar aberto à
Internet, ele reduz ruído no log:

```bash
sudo apt install -y fail2ban
printf '[sshd]\nenabled = true\nbackend = systemd\nmaxretry = 5\nfindtime = 10m\nbantime = 1h\n' \
  | sudo tee /etc/fail2ban/jail.d/sshd.local
sudo systemctl restart fail2ban && sudo fail2ban-client status sshd
```

### 6.5 Superfície restante

```bash
systemctl list-units --type=service --state=running    # nada além do esperado: ssh, nginx, postgresql,
                                                       # processoseletivo, systemd-*, cron, unattended-upgrades…
```

Desligue o que não for usado, como servidores de impressão ou de arquivos herdados da imagem.

---

## 7. Instalação das dependências

Nada de compilador, nem de biblioteca de PDF ou imagem:

- o `psycopg[binary]` traz a `libpq` na própria wheel (`uv.lock`);
- o `openpyxl` é Python puro;
- o PDF é escrito em Python puro, com fontes base-14 (`publicacoes/infrastructure/pdf.py:41-46`).

### 7.1 Pacotes do sistema

**[admin]**

```bash
sudo apt install -y git curl ca-certificates nginx certbot restic dnsutils
sudo rm -f /etc/nginx/sites-enabled/default      # o default_server é o deste projeto (§14)
```

### 7.2 PostgreSQL 18 (PGDG)

```bash
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh     # adiciona o repositório oficial; confirme
sudo apt install -y postgresql-18
```

**Como verificar:**

```bash
pg_lsclusters                                        # 18  main  5432 online postgres …
sudo -u postgres psql -Atc 'show server_version'     # 18.x
```

### 7.3 uv e Python 3.13

Uma versão fixa do `uv`, verificada por checksum, em vez de `curl | sh`. O Dockerfile usa a série
0.9; use uma versão estável igual ou superior, e registre-a.

```bash
UV_VERSAO=<VERSAO_UV>            # ex.: a última 0.9.x ou mais nova, de github.com/astral-sh/uv/releases
cd /tmp
curl -fsSLO "https://github.com/astral-sh/uv/releases/download/${UV_VERSAO}/uv-x86_64-unknown-linux-gnu.tar.gz"
curl -fsSLO "https://github.com/astral-sh/uv/releases/download/${UV_VERSAO}/uv-x86_64-unknown-linux-gnu.tar.gz.sha256"
sha256sum -c uv-x86_64-unknown-linux-gnu.tar.gz.sha256        # deve dizer: OK
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo install -m 0755 uv-x86_64-unknown-linux-gnu/uv uv-x86_64-unknown-linux-gnu/uvx /usr/local/bin/

sudo env UV_PYTHON_INSTALL_DIR=/opt/processoseletivo/python uv python install 3.13
sudo chmod -R a+rX /opt/processoseletivo/python
```

**Como verificar:**

```bash
uv --version
sudo env UV_PYTHON_INSTALL_DIR=/opt/processoseletivo/python uv python find 3.13   # caminho sob /opt/processoseletivo/python
```

**Não remova versões antigas do Python** enquanto houver release que as use: o venv de cada release
aponta para o interpretador com que foi criado.

---

## 8. Código e releases

### 8.1 Princípios

- **Produção só recebe commit que está na `main`** e passou no CI (workflow *Backend*: lint,
  formatação, `makemigrations --check` e a suíte contra PostgreSQL 18). O `ps-construir` recusa o
  que não descende da `main`.
- **O repositório não tem tags hoje** (`git tag` vazio). Implanta-se pelo **SHA completo**.
  Recomendação ao projeto: criar uma tag anotada por release (`vAAAA.MM.N`). O script aceita tag
  também, e registra os dois.
- **Cada release é um diretório imutável, com venv próprio.** Rollback de código é trocar um
  symlink (§23).
- **Segredo não entra na release:** ele vive em `/etc/processoseletivo`. O `.dockerignore` e o
  `.gitignore` já excluem `.env`.

### 8.2 Acesso de leitura ao repositório

Use uma *deploy key* só de leitura, e não um token pessoal.

**[admin]**

```bash
sudo ssh-keygen -t ed25519 -N '' -C 'deploy@processoseletivo' -f /root/.ssh/deploy_processoseletivo
sudo cat /root/.ssh/deploy_processoseletivo.pub
# GitHub → repositório → Settings → Deploy keys → Add (sem "Allow write access")
sudo tee -a /root/.ssh/config >/dev/null <<'CONF'
Host github-processoseletivo
  HostName github.com
  User git
  IdentityFile /root/.ssh/deploy_processoseletivo
  IdentitiesOnly yes
CONF
sudo ssh -T github-processoseletivo              # aceite a chave do host; "successfully authenticated"
sudo git clone --mirror git@github-processoseletivo:<REPOSITORIO>.git /opt/processoseletivo/repo.git
```

### 8.3 Scripts de operação

Todos ficam em `/usr/local/sbin`, com dono root e modo 0750. Cada um faz uma coisa.

**`ps-construir`** — constrói uma release a partir de um commit, **sem ativá-la**:

```bash
sudo tee /usr/local/sbin/ps-construir >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Constrói uma release a partir de um commit ou tag, SEM ativá-la.
# Uso: sudo ps-construir <sha-ou-tag>      Imprime o diretório criado.
set -euo pipefail
umask 022
BASE=/opt/processoseletivo
# Fora do uv.lock: o projeto não declara servidor WSGI (gap I-2). Versão fixa aqui até isso mudar.
GUNICORN_VERSAO=26.2.0
REF="${1:?informe o SHA completo ou a tag a implantar}"

export UV_PYTHON_INSTALL_DIR="$BASE/python" UV_PYTHON_DOWNLOADS=never \
       UV_CACHE_DIR=/var/cache/processoseletivo/uv UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

git -C "$BASE/repo.git" fetch --prune --tags origin
SHA=$(git -C "$BASE/repo.git" rev-parse --verify "${REF}^{commit}")
if ! git -C "$BASE/repo.git" merge-base --is-ancestor "$SHA" refs/heads/main; then
  echo "RECUSADO: $SHA não está na main." >&2
  exit 1
fi

DEST="$BASE/releases/$(date +%Y%m%d-%H%M%S)-${SHA:0:12}"
mkdir "$DEST"
# Só backend/: é tudo o que roda. doc/ e specs/ não têm lugar no servidor.
git -C "$BASE/repo.git" archive --format=tar "$SHA" backend | tar -x -C "$DEST"
cd "$DEST/backend"
UV_PROJECT_ENVIRONMENT="$DEST/venv" uv sync --locked --python 3.13
uv pip install --python "$DEST/venv/bin/python" "gunicorn==$GUNICORN_VERSAO"
"$DEST/venv/bin/python" -m compileall -q "$DEST/backend/config" "$DEST/backend/processo_seletivo"
uv pip freeze --python "$DEST/venv/bin/python" > "$DEST/PACOTES"
{
  echo "commit=$SHA"
  echo "ref=$REF"
  echo "construida_em=$(date --iso-8601=seconds)"
  echo "construida_por=${SUDO_USER:-root}"
  echo "gunicorn=$GUNICORN_VERSAO"
} > "$DEST/REVISION"
chmod -R a+rX,go-w "$DEST"
echo "$DEST"
SCRIPT
```

**`ps-manage`** — o `manage.py` de uma release, com o ambiente de produção, **como o usuário da
aplicação**. É o único jeito de chamar o `manage.py` em produção: sem ele, o `manage.py` cai em
`config.settings.development` (`manage.py:7`) e não enxerga variável nenhuma. O projeto não usa
`python-dotenv`.

```bash
sudo tee /usr/local/sbin/ps-manage >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# manage.py da release, com o ambiente de produção, como o usuário da aplicação.
# Uso: sudo ps-manage [--release DIR] [--migracao] <comando> [argumentos]
#   --migracao  conecta como o papel de migração (DB_ROLE=migration) — só migrate e carga de CEP.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "execute com sudo" >&2; exit 1; }
RELEASE=/opt/processoseletivo/current
PAPEL=runtime
while [ $# -gt 0 ]; do
  case "$1" in
    --release) RELEASE="$2"; shift 2 ;;
    --migracao) PAPEL=migration; shift ;;
    *) break ;;
  esac
done
set -a
. /etc/processoseletivo/app.env
if [ "$PAPEL" = migration ]; then . /etc/processoseletivo/migracao.env; export DB_ROLE=migration; fi
set +a
export HOME=/var/lib/processoseletivo PYTHONDONTWRITEBYTECODE=1
cd "$RELEASE/backend"
exec setpriv --reuid=processoseletivo --regid=processoseletivo --init-groups -- \
  "$RELEASE/venv/bin/python" manage.py "$@"
SCRIPT
```

**`ps-migrar`** — provisionar, migrar e provisionar de novo, **sem senha de superusuário em lugar
nenhum**. O provisionamento conecta como `postgres`, por *peer*, pelo socket local, e usa as
settings `base`: o comando só precisa do banco, e as barreiras de `production` não têm o que dizer
sobre ele. As senhas dos papéis vêm do ambiente, nunca da linha de comando, onde apareceriam no `ps`.
Sequência ensaiada: `0 de 34`, as migrations, e `34 de 34`.

```bash
sudo tee /usr/local/sbin/ps-migrar >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Provisionar, migrar, provisionar de novo — a ordem de seguranca/papeis.py.
# Uso: sudo ps-migrar [--so-provisionar] [DIR_DA_RELEASE]   (padrão: a release ativa)
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "execute com sudo" >&2; exit 1; }
SO_PROVISIONAR=0
[ "${1:-}" = --so-provisionar ] && { SO_PROVISIONAR=1; shift; }
RELEASE="${1:-/opt/processoseletivo/current}"

provisionar() {
  (
    set -a; . /etc/processoseletivo/app.env; . /etc/processoseletivo/migracao.env; set +a
    alvo_runtime="$DB_RUNTIME_USER"; alvo_migracao="$DB_MIGRATION_USER"
    # A CONEXÃO é a do superusuário, por peer no socket; os PAPÉIS criados são os do ambiente.
    export DJANGO_SETTINGS_MODULE=config.settings.base DB_ROLE=runtime \
           DB_HOST=/var/run/postgresql DB_RUNTIME_USER=postgres \
           HOME=/var/lib/postgresql PYTHONDONTWRITEBYTECODE=1
    cd "$RELEASE/backend"
    setpriv --reuid=postgres --regid=postgres --init-groups -- \
      "$RELEASE/venv/bin/python" manage.py provisionar_papeis \
        --migration-role "$alvo_migracao" --runtime-role "$alvo_runtime"
  )
}

if [ "$SO_PROVISIONAR" = 1 ]; then provisionar; exit 0; fi
echo "== provisionar (1/2)"; provisionar
echo "== migrate";           /usr/local/sbin/ps-manage --release "$RELEASE" --migracao migrate --noinput
echo "== provisionar (2/2)"; saida=$(provisionar); echo "$saida"
# "N de M": o N diferente do M significa tabela append-only sem a trava do privilégio.
read -r n m <<<"$(echo "$saida" | sed -nE 's/.* ([0-9]+) de ([0-9]+) tabelas append-only.*/\1 \2/p')"
if [ -z "${n:-}" ] || [ "$n" != "$m" ]; then
  echo "FALHA: a segunda passada trancou ${n:-?} de ${m:-?} tabelas append-only." >&2; exit 1
fi
SCRIPT
```

**`ps-ativar`** — aponta `current` para a release, reinicia, espera o `/readiness` e **registra**:

```bash
sudo tee /usr/local/sbin/ps-ativar >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Aponta `current` para a release, reinicia a aplicação, espera o readiness e registra o ato.
# Uso: sudo ps-ativar /opt/processoseletivo/releases/<nome>
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "execute com sudo" >&2; exit 1; }
BASE=/opt/processoseletivo
NOVA=$(realpath -e "${1:?informe o diretório da release}")
case "$NOVA" in "$BASE"/releases/*) ;; *) echo "não é uma release: $NOVA" >&2; exit 1 ;; esac
ANTERIOR=-
[ -e "$BASE/current" ] && ANTERIOR=$(readlink -f "$BASE/current")
DOMINIO=$(. /etc/processoseletivo/app.env; echo "${DJANGO_ALLOWED_HOSTS%%,*}")

ln -sfn "$NOVA" "$BASE/current.tmp" && mv -T "$BASE/current.tmp" "$BASE/current"
# restart, e não HUP: o master do gunicorn manteria o venv e o diretório da release antiga.
systemctl restart processoseletivo || true
estado=FALHOU
for _ in $(seq 1 30); do
  if curl -fsS -o /dev/null -H "Host: $DOMINIO" -H 'X-Forwarded-Proto: https' \
       http://127.0.0.1:8000/readiness; then estado=ativada; break; fi
  sleep 2
done
commit=$(sed -n 's/^commit=//p' "$NOVA/REVISION")
printf '%s\t%s\t%s\t%s\tanterior=%s\t%s\n' "$(date --iso-8601=seconds)" "$estado" "$commit" \
  "$(basename "$NOVA")" "$(basename "$ANTERIOR")" "${SUDO_USER:-root}" \
  >> /var/lib/processoseletivo/implantacoes.log
echo "$estado: $(basename "$NOVA")  (anterior: $(basename "$ANTERIOR"))"
[ "$estado" = ativada ]
SCRIPT

sudo chmod 0750 /usr/local/sbin/ps-construir /usr/local/sbin/ps-manage /usr/local/sbin/ps-migrar /usr/local/sbin/ps-ativar
```

### 8.4 Construir a primeira release

**[admin]** Escolha o commit: o último da `main` com o workflow *Backend* verde, conferido na aba
*Actions* do GitHub ou com `gh run list --branch main --workflow Backend`.

```bash
sudo git -C /opt/processoseletivo/repo.git log --oneline -5 main
R=$(sudo ps-construir <SHA> | tail -1); echo "$R"
```

**Como verificar:**

```bash
cat "$R/REVISION"                                   # commit=<SHA>
grep -Ei '^(django|gunicorn|psycopg)==' "$R/PACOTES"  # django==5.2.x, gunicorn==26.2.0, psycopg==3.3.x
"$R/venv/bin/python" --version                      # Python 3.13.x
```

**Qual versão estava em produção no dia X?** Consulte o histórico de ativações. Ele entra no
backup (§18).

```bash
cat /var/lib/processoseletivo/implantacoes.log      # data · estado · commit · release · anterior · quem
cat /opt/processoseletivo/current/REVISION          # a de agora
```

---

## 9. Banco de dados

### 9.1 Configuração

**[admin]** O Ubuntu inclui `conf.d/` no `postgresql.conf`, e por isso a configuração do projeto
fica num arquivo próprio:

```bash
sudo tee /etc/postgresql/18/main/conf.d/processoseletivo.conf >/dev/null <<'CONF'
# Só loopback: a aplicação está no mesmo host. Nunca '*'.
listen_addresses = 'localhost'
password_encryption = 'scram-sha-256'
timezone = 'America/Sao_Paulo'          # para quem usa psql; a aplicação conecta em UTC (USE_TZ)
log_timezone = 'America/Sao_Paulo'

# 8 GB de RAM dividida com o gunicorn e com o cache de página dos documentos.
shared_buffers = 1GB
effective_cache_size = 4GB
work_mem = 16MB
maintenance_work_mem = 256MB

# Logs sem valores de parâmetro: consultas carregam CPF, e-mail e nome.
log_min_duration_statement = 2000
log_parameter_max_length = 0
log_parameter_max_length_on_error = 0
log_lock_waits = on
log_line_prefix = '%m [%p] %q%u@%d '
CONF
```

O `pg_hba.conf` é substituído por uma versão mínima: o superusuário só por *peer*, e os dois papéis
da aplicação só pelo loopback, com senha:

```bash
sudo cp /etc/postgresql/18/main/pg_hba.conf /etc/postgresql/18/main/pg_hba.conf.original
sudo tee /etc/postgresql/18/main/pg_hba.conf >/dev/null <<'CONF'
# TYPE  DATABASE           USER                                                ADDRESS        METHOD
local   all                postgres                                                           peer
host    processo_seletivo  processo_seletivo_runtime,processo_seletivo_owner   127.0.0.1/32   scram-sha-256
host    processo_seletivo  processo_seletivo_runtime,processo_seletivo_owner   ::1/128        scram-sha-256
CONF
sudo systemctl restart postgresql@18-main
```

### 9.2 O banco

O locale é explícito, para não herdar o do instalador. Os papéis **não** são criados aqui: quem os
cria é o `provisionar_papeis`, na §11, com a política versionada em `seguranca/papeis.py`.

```bash
sudo -u postgres createdb --encoding=UTF8 --locale=pt_BR.UTF-8 --template=template0 processo_seletivo
# Ninguém conecta por herança de PUBLIC; o provisionar_papeis concede CONNECT aos dois papéis.
# Ensaiado: a aplicação conecta normalmente depois deste REVOKE.
sudo -u postgres psql -c 'REVOKE CONNECT ON DATABASE processo_seletivo FROM PUBLIC;'
```

**Nota sobre o collation.** O CI roda com o locale padrão da imagem `postgres:18` (`en_US.utf8`),
cuja ordenação de texto latino é equivalente à de `pt_BR`. Numa **troca de versão do Ubuntu**, a
glibc pode mudar a ordenação e invalidar índices de texto: rode `REINDEX DATABASE` na janela de
manutenção dessa troca.

**Como verificar:**

```bash
sudo ss -ltnp | grep 5432                                     # só 127.0.0.1:5432 e [::1]:5432
sudo -u postgres psql -Atc "select datname, pg_encoding_to_char(encoding), datcollate from pg_database where datname='processo_seletivo'"
#   processo_seletivo|UTF8|pt_BR.UTF-8
sudo -u postgres psql -Atc 'select count(*) from pg_hba_file_rules where error is not null'   # 0
```

---

## 10. Configuração e segredos

### 10.1 Variáveis

Os nomes são os que o código lê (`config/settings/base.py`, `config/settings/production.py`).
"Recusa" significa que `production.py` **impede o processo de iniciar** sem ela, com mensagem que
nomeia a variável.

| Variável | Classe | Valor em produção | Evidência e observação |
|---|---|---|---|
| `DJANGO_SETTINGS_MODULE` | obrigatória, comum | `config.settings.production` | O `manage.py` cai em `development` sem ela (`manage.py:7`); o `wsgi.py` já usa `production` |
| `DJANGO_SECRET_KEY` | **obrigatória, segredo persistente** | `<GERAR_SEGREDO_ALEATORIO>` | Recusa se tiver menos de 50 caracteres ou for valor de desenvolvimento (`production.py:70-78`). **Assina os códigos de verificação dos comprovantes** (`inscricoes/domain/autenticidade.py:17,61`) |
| `DJANGO_ALLOWED_HOSTS` | obrigatória, comum | `<DOMINIO>` | Recusa se vazio ou `*` (`production.py:80-85`) |
| `DB_NAME`, `DB_HOST`, `DB_PORT` | comum | `processo_seletivo`, `127.0.0.1`, `5432` | `base.py:257-266` |
| `DB_ROLE` | comum | `runtime` | `migration` só via `ps-manage --migracao` (`base.py:248-256`) |
| `DB_RUNTIME_USER` | comum | `processo_seletivo_runtime` | — |
| `DB_RUNTIME_PASSWORD` | **obrigatória, segredo** | `<GERAR_SEGREDO_ALEATORIO>` | Recusa se vazia (`production.py:230-234`) |
| `DB_MIGRATION_USER`, `DB_MIGRATION_PASSWORD` | segredo | `processo_seletivo_owner`, `<GERAR_SEGREDO_ALEATORIO>` | **Só** em `migracao.env`: a aplicação em serviço não enxerga |
| `ARQUIVOS_CANDIDATOS_RAIZ` | obrigatória, comum | `/var/lib/processoseletivo/arquivos` | Recusa se ausente, relativa ou dentro do código (`production.py:124-132`) |
| `DJANGO_EMAIL_BACKEND` | obrigatória, comum | `django.core.mail.backends.smtp.EmailBackend` | Recusa console, arquivo, memória e nulo (`production.py:143-157`) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` | comum | `<SMTP_HOST>`, `587`, `true` | Só STARTTLS: a porta 465 (SSL implícito) **não funciona** (`base.py:172-178`) |
| `EMAIL_HOST_USER` | comum | `<SMTP_USUARIO>` | — |
| `EMAIL_HOST_PASSWORD` | segredo | do cofre | — |
| `DEFAULT_FROM_EMAIL` | obrigatória, comum | `<REMETENTE>` | Recusa se vazio (`production.py:158-163`) |
| `PORTAL_ATENDIMENTO` | obrigatória, comum | e-mail, telefone ou página do atendimento | Recusa se vazio; aparece em duas telas do candidato (`production.py:189-196`) |
| `PORTAL_ATRAS_DE_PROXY` | obrigatória, comum | `true` | Recusa sem declaração (`production.py:175-183`). Com `true`, o portal lê o **primeiro** item do `X-Forwarded-For` (`portal/views.py:606-610`) |
| `API_AUTHENTICATION_CLASSES` | obrigatória, comum | `rest_framework.authentication.RemoteUserAuthentication` | **Provisório, e nega tudo.** Passa na barreira (`production.py:199-228`) e **não autentica ninguém**, porque não há `RemoteUserBackend`: a API admin e o `/metrics` respondem 403 (ensaiado). Troque pela classe institucional quando existir |
| `DJANGO_SECURE_SSL_REDIRECT` | obrigatória `true` | `true` | `production.py:237,250-255` |
| `DJANGO_SECURE_HSTS_SECONDS` | obrigatória, pelo menos 1 ano | `31536000` | idem |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | opcional | **`false`** | O padrão do código é `true`. Veja §13.4 |
| `DJANGO_SECURE_HSTS_PRELOAD` | opcional | **`false`** | O padrão do código é `true`. Veja §13.4 |
| `DJANGO_TRUST_PROXY_SSL_HEADER` | obrigatória **nesta topologia** | `true` | Sem ela, `request.is_secure()` é falso atrás do nginx: o redirecionamento HTTPS entra em laço e o CSRF recusa todo POST (`production.py:258-259`) |
| `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` | opcional | padrão, 10 MiB | Se mudar, ajuste o `client_max_body_size` de `/selecoes/` (§14) |
| `EDITAL_ANEXOS_LIMITE_BYTES` | opcional | padrão, 5 MiB | Se mudar, ajuste o de `/gestao/` |
| `SORTEIO_FONTE_TIMEOUT_SEGUNDOS`, `SORTEIO_FONTE_TENTATIVAS` | opcional | padrão, 10 e 3 | `base.py:130-131` |

**Proibidas em produção** — ausentes, ou `false`:

- `INTERFACE_SELETOR_IDENTIDADE`, `PORTAL_IDENTIDADE_DEMO` e `SORTEIO_FONTE_DE_DEMONSTRACAO`
  (recusam o boot);
- `DB_USER` e `DB_PASSWORD`, fallback que mascararia um `DB_RUNTIME_*` ausente;
- `TEST_DB_ENGINE`.

O `DJANGO_DEBUG` do `.env.example` **não é lido** por código nenhum: `production` fixa
`DEBUG = False` (`production.py:56`). As `POSTGRES_*` só servem ao `compose.yaml`.

### 10.2 Onde ficam e como se geram

| Arquivo | Conteúdo | Quem lê |
|---|---|---|
| `/etc/processoseletivo/app.env` (0600 root) | tudo da tabela, **menos** `DB_MIGRATION_*` | systemd, como root, antes de trocar de usuário; os scripts `ps-*` |
| `/etc/processoseletivo/migracao.env` (0600 root) | `DB_MIGRATION_USER`, `DB_MIGRATION_PASSWORD` | só `ps-manage --migracao` e `ps-migrar` |

**Formato:** o mesmo arquivo é lido pelo systemd (`EnvironmentFile=`) e pelo shell dos scripts
(`set -a; . arquivo`). Por isso: uma variável por linha, no formato `CHAVE=valor`, e aspas duplas
se o valor tiver espaço. **Nada de `$`, crase ou barra invertida.** Os segredos abaixo saem de
`token_urlsafe`, que só usa `A–Z a–z 0–9 - _`.

**Gerar sem deixar o valor em lugar nenhum além do arquivo.** As **aspas simples** fazem a geração
acontecer dentro do shell do root: o histórico do shell e o registro do `sudo` (`auth.log`) guardam o
comando, e não o valor. Com aspas duplas, o valor seria expandido antes e iria para os dois.

**[admin]**

```bash
sudo install -m 0600 -o root -g root /dev/null /etc/processoseletivo/app.env
sudo install -m 0600 -o root -g root /dev/null /etc/processoseletivo/migracao.env
sudo sh -c 'g() { python3 -c "import secrets; print(secrets.token_urlsafe(64))"; }
  echo "DJANGO_SECRET_KEY=$(g)"                     >> /etc/processoseletivo/app.env
  echo "DB_RUNTIME_PASSWORD=$(g)"                   >> /etc/processoseletivo/app.env
  echo "DB_MIGRATION_USER=processo_seletivo_owner"  >> /etc/processoseletivo/migracao.env
  echo "DB_MIGRATION_PASSWORD=$(g)"                 >> /etc/processoseletivo/migracao.env'
sudo -e /etc/processoseletivo/app.env        # complete com o modelo abaixo; a senha do SMTP é digitada aqui
```

Modelo do restante do `app.env`:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_ALLOWED_HOSTS=<DOMINIO>
DB_NAME=processo_seletivo
DB_HOST=127.0.0.1
DB_PORT=5432
DB_ROLE=runtime
DB_RUNTIME_USER=processo_seletivo_runtime
ARQUIVOS_CANDIDATOS_RAIZ=/var/lib/processoseletivo/arquivos
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=<SMTP_HOST>
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=<SMTP_USUARIO>
EMAIL_HOST_PASSWORD=<SMTP_SENHA>
DEFAULT_FROM_EMAIL=<REMETENTE>
PORTAL_ATENDIMENTO="<CANAL_DE_ATENDIMENTO>"
PORTAL_ATRAS_DE_PROXY=true
API_AUTHENTICATION_CLASSES=rest_framework.authentication.RemoteUserAuthentication
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=false
DJANGO_SECURE_HSTS_PRELOAD=false
DJANGO_TRUST_PROXY_SSL_HEADER=true
```

**Copie para o cofre institucional de senhas, agora:**

- `DJANGO_SECRET_KEY` — **insubstituível**;
- `DB_RUNTIME_PASSWORD` e `DB_MIGRATION_PASSWORD` — regeneráveis na restauração, mas é mais simples
  ter;
- a senha do SMTP;
- mais tarde, a senha do restic (§18) — **insubstituível**: sem ela, o backup é ilegível.

**Como verificar:**

```bash
sudo stat -c '%a %U:%G %n' /etc/processoseletivo/*.env        # 600 root:root
sudo grep -cE '^[A-Z_]+=' /etc/processoseletivo/app.env        # ~25 linhas
sudo grep -nE '\$|`|\\' /etc/processoseletivo/*.env && echo "CARACTERE PROIBIDO" || echo ok
```

### 10.3 Ambientes

| | Desenvolvimento | Homologação | Produção |
|---|---|---|---|
| Como sobe | `docker compose up` ou `make runserver` (README) | **Esta mesma receita**, em outra VM | esta receita |
| Settings | `config.settings.development` (`DEBUG` ligado, sorteio de demonstração) | `config.settings.production` | `config.settings.production` |
| Identidade | seletor e demo ligados | **a mesma barreira de produção**: a gestão responde 503 até B-1 | idem |
| Domínio | `localhost` | `<DOMINIO_HOMOLOGACAO>`, com certificado próprio | `<DOMINIO>` |
| Banco | local, descartável | próprio, **só com dado sintético** | próprio |
| E-mail | console ou mailpit | SMTP real, só com caixas de teste da equipe | SMTP institucional |
| Documentos | `/tmp/...` ou volume | raiz própria | `/var/lib/processoseletivo/arquivos` |
| Segredos | fracos, do `.env.example` | **gerados, e diferentes dos de produção** | cofre |
| Logs | terminal | journald | journald, com retenção definida |
| `seed_demo` | sim | só se o banco for descartável | **nunca** |

**Nunca copie o banco de produção** para desenvolvimento ou homologação: ele tem CPF, endereço,
documentos e dados de matrícula, e o projeto não tem ferramenta de anonimização (§26). Uma
homologação com a **mesma `DJANGO_SECRET_KEY`** de produção validaria comprovantes de produção, então
não reuse. Um piloto com a gestão operável antes do B-1 exigiria settings de desenvolvimento
expostas numa rede, e essa é uma decisão de governança, fora do escopo deste documento.

---

## 11. Migrations e bootstrap

### 11.1 Pré-voo das settings, antes de tocar o banco

**[admin]**

```bash
R=/opt/processoseletivo/releases/<nome>          # a construída na §8.4
sudo ps-manage --release "$R" check --deploy
```

**Sucesso** é terminar sem `ERRORS`. Com os valores da §10, o esperado são exatamente dois avisos,
`security.W005` (subdomínios) e `security.W021` (preload), consequência deliberada do §13.4 — foi o
resultado do ensaio. Um `ImproperlyConfigured: <VARIÁVEL>: ...` é a barreira de `production.py`
nomeando o que falta: corrija o `app.env` e repita.

### 11.2 Provisionar, migrar, provisionar

```bash
sudo ps-migrar "$R"
```

Saída esperada, tal como no ensaio:

```
== provisionar (1/2)
Papéis provisionados. 0 de 34 tabelas append-only estão sem UPDATE nem DELETE para o runtime.
As demais ainda não existem neste banco. Aplique as migrations e execute este comando outra vez…
== migrate
  Applying … OK
== provisionar (2/2)
Papéis provisionados. 34 de 34 tabelas append-only estão sem UPDATE nem DELETE para o runtime.
```

O `34` cresce a cada tabela append-only nova. O que importa é o **N igual ao M** na segunda
passada; o script falha se não for. Os três passos são idempotentes
(`seguranca/papeis.py:11-16`).

**Como verificar:**

```bash
sudo ps-manage --release "$R" migrate --check; echo $?      # 0: nenhuma migration pendente
sudo -u postgres psql -d processo_seletivo -Atc \
  "select rolname, rolsuper, rolcreaterole, rolcreatedb from pg_roles where rolname like 'processo_seletivo_%'"
#   processo_seletivo_owner|f|f|f
#   processo_seletivo_runtime|f|f|f          ← nenhum dos dois é superusuário
sudo -u postgres psql -d processo_seletivo -Atc \
  "select has_table_privilege('processo_seletivo_runtime','auditoria_registroauditoria','DELETE')"   # f
```

### 11.3 Base de CEP (opcional, recomendada)

Sem ela nada bloqueia: o candidato digita o endereço inteiro e o código IBGE fica vazio
(`doc/runbook-base-de-cep.md`). Com ela, o Requerimento de Matrícula preenche município e UF. O
`.zip`, de 379 MB, vem do storage institucional.

```bash
sudo install -m 0640 -o root -g processoseletivo <ARQUIVO_BAIXADO>.zip /var/lib/processoseletivo/ceps/banco-ceps.zip
sha256sum /var/lib/processoseletivo/ceps/banco-ceps.zip        # confira contra o que o storage publica
sudo ps-manage --migracao carregar_ceps /var/lib/processoseletivo/ceps/banco-ceps.zip --se-mudou   # ~40 s
sudo ps-manage situacao_dos_ceps                                  # sai com 0 quando está tudo bem
```

### 11.4 O que **não** existe para fazer

- **Primeiro usuário administrativo:** não há como (B-1). `createsuperuser` não serve, porque o
  admin do Django não está instalado e a gestão não lê `auth.User`.
- **Cadastro institucional inicial:** Processo, Edital, Comissão e demais dados nascem na gestão,
  pela interface.
- **Fixtures obrigatórias:** nenhuma.
- **`seed_demo`: NUNCA em produção.** Ele **publica** Editais de demonstração. Publicação é
  imutável, e as tabelas append-only recusam `DELETE` por gatilho e por privilégio: os Editais
  falsos ficariam públicos para sempre. E como produção recusa a fonte de sorteio de demonstração,
  ele pode falhar no meio, depois de já ter publicado.

---

## 12. Serviço da aplicação

### 12.1 Configuração do gunicorn

Recomendação, com os valores do ensaio.

```bash
sudo tee /etc/processoseletivo/gunicorn.conf.py >/dev/null <<'CONF'
# Configuração do gunicorn do Processo Seletivo (não versionada no repositório).
wsgi_app = "config.wsgi:application"
# Só loopback: quem fala com a aplicação é o nginx.
bind = ["127.0.0.1:8000"]
# Workers síncronos: 2 × vCPU + 1. Cada um tem ~90 MB ocioso (medido) e pode passar de 150 MB
# durante uma Retificação com anexos, que são lidos inteiros em memória. Confira a RAM antes de subir.
workers = 5
worker_class = "sync"
# 120 s porque o SMTP não tem timeout na aplicação (gap I-4) e há atos síncronos pesados, como a
# consolidação e a exportação. Um worker preso além disso é morto, e o pedido recebe 502.
timeout = 120
graceful_timeout = 30
keepalive = 2
# Recicla workers aos poucos, contra acúmulo de memória.
max_requests = 1000
max_requests_jitter = 100
# Carrega a aplicação no master: settings inválidas falham antes de abrir a porta, com a mensagem
# de production.py no journal. Nenhum AppConfig.ready() abre conexão com o banco.
preload_app = True
forwarded_allow_ips = "127.0.0.1"
# Acesso é registrado pelo nginx. Registrar aqui também só duplicaria IP em log.
accesslog = None
errorlog = "-"
loglevel = "info"
CONF
sudo chmod 0644 /etc/processoseletivo/gunicorn.conf.py
```

### 12.2 Unit do systemd

`Type=notify` é seguro: o gunicorn envia `READY=1` ao terminar de subir
(`gunicorn/arbiter.py:211`).

```bash
sudo tee /etc/systemd/system/processoseletivo.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo (Cefor/Ifes) — aplicação Django sob gunicorn
After=network-online.target postgresql@18-main.service
Wants=network-online.target postgresql@18-main.service

[Service]
Type=notify
NotifyAccess=main
User=processoseletivo
Group=processoseletivo
WorkingDirectory=/opt/processoseletivo/current/backend
EnvironmentFile=/etc/processoseletivo/app.env
Environment=PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/processoseletivo/current/venv/bin/gunicorn --config /etc/processoseletivo/gunicorn.conf.py
# HUP recarrega os workers da MESMA release. Deploy é restart (ps-ativar).
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=40
Restart=on-failure
RestartSec=5
UMask=0027
SyslogIdentifier=processoseletivo

# Endurecimento: sistema de arquivos só leitura, exceto a raiz dos documentos; /tmp privado. O /tmp
# recebe uploads acima de 2,5 MB e cópias verificadas de documento acima de 2 MiB, e o systemd o
# apaga quando o serviço para.
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/processoseletivo/arquivos
PrivateTmp=yes
PrivateDevices=yes
ProtectHome=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectHostname=yes
RestrictSUIDSGID=yes
RestrictRealtime=yes
RestrictNamespaces=yes
LockPersonality=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
SystemCallArchitectures=native
CapabilityBoundingSet=
AmbientCapabilities=

[Install]
WantedBy=multi-user.target
UNIT
```

**Ativar pela primeira vez.** O `ps-ativar` cria o symlink `current`, reinicia o serviço e espera o
readiness:

```bash
sudo systemctl daemon-reload
sudo systemctl enable processoseletivo
sudo ps-ativar "$R"                     # ativada: <nome>  (anterior: -)
```

**Como verificar:**

```bash
systemctl is-active processoseletivo                        # active
systemctl status processoseletivo --no-pager                # "Gunicorn arbiter booted"; 1 master + 5 workers
ps -o user,pid,ppid,rss,cmd -C gunicorn                     # todos como processoseletivo
sudo ss -ltnp | grep 8000                                   # 127.0.0.1:8000 apenas
journalctl -u processoseletivo -n 50 --no-pager             # sem ImproperlyConfigured
curl -s -H 'Host: <DOMINIO>' -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/readiness
#   {"status":"ready","checks":{"database":true,"migrations":true}}
systemd-analyze security processoseletivo | tail -1         # exposição baixa ("OK"/"MEDIUM" já é bom)
```

Os cabeçalhos no `curl` local não são opcionais. Sem `X-Forwarded-Proto: https` a resposta é **301**
para HTTPS; sem o `Host` do domínio, **400**. Os dois comportamentos foram ensaiados.

Comandos do dia a dia:

```bash
sudo systemctl restart processoseletivo      # reinício: ~2–5 s sem resposta (o nginx mostra a página de indisponível)
sudo systemctl stop processoseletivo         # parada graciosa: termina as requisições em curso, até 30 s
journalctl -u processoseletivo -f            # acompanhar
journalctl -u processoseletivo --since "1 hour ago" -p warning
```

---

## 13. HTTPS/TLS

### 13.1 Qual certificado

- **Let's Encrypt**, se o domínio institucional permitir. Confira o CAA:
  `dig +short CAA exemplo.edu.br`. Vazio, ou contendo `letsencrypt.org`, permite. Uma lista de CAA
  sem ele bloqueia a emissão. Emitir implica aceitar os termos de assinante do Let's Encrypt, e
  aceitá-los pela instituição é decisão de quem implanta.
- **Certificado institucional** (ICPEdu/RNP ou a AC contratada), se a política do domínio exigir.
  Veja §13.5.

### 13.2 nginx provisório, só HTTP, para o desafio ACME

O `server` TLS não carrega sem certificado, então primeiro um nginx que só responde ao desafio:

```bash
sudo tee /etc/nginx/sites-available/processoseletivo >/dev/null <<'CONF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    location ^~ /.well-known/acme-challenge/ { root /var/www/letsencrypt; }
    location / { return 444; }
}
CONF
sudo ln -sfn /etc/nginx/sites-available/processoseletivo /etc/nginx/sites-enabled/processoseletivo
sudo nginx -t && sudo systemctl reload nginx
```

Se a VM não tiver IPv6, remova as linhas `listen [::]:…`, aqui e na §14.

### 13.3 Emissão e renovação

```bash
sudo certbot certonly --webroot -w /var/www/letsencrypt -d <DOMINIO> \
  --email <EMAIL_RESPONSAVEL> --no-eff-email --agree-tos \
  --deploy-hook 'systemctl reload nginx'
```

O `--deploy-hook` fica gravado em `/etc/letsencrypt/renewal/<DOMINIO>.conf`, e cada renovação
recarrega o nginx.

**Como verificar:**

```bash
sudo ls -l /etc/letsencrypt/live/<DOMINIO>/                # fullchain.pem, privkey.pem
systemctl list-timers certbot.timer                        # próxima execução agendada
sudo certbot renew --dry-run                               # "Congratulations, all simulated renewals succeeded"
```

### 13.4 HSTS: o que o código obriga e o que se escolhe

`production.py` **exige** `SECURE_SSL_REDIRECT` e HSTS de pelo menos um ano (`production.py:237-255`).
O cabeçalho sai da aplicação, pelo `SecurityMiddleware`, e só em resposta HTTPS — ensaiado:
`Strict-Transport-Security: max-age=31536000`.

**Consequência:** depois da primeira visita, o navegador **se recusa** a falar HTTP com `<DOMINIO>`
por um ano, e não oferece o botão "continuar assim mesmo" para um certificado inválido. Certificado
vencido é site fora do ar para todo candidato que já o visitou. Por isso o monitoramento de validade
(§21) não é opcional.

Os dois ajustes que o código deixa escolher, e que vêm **ligados por padrão**:

- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=false`. Com `true`, todo subdomínio de `<DOMINIO>` herda a
  exigência. É inofensivo se não houver nenhum, mas é compromisso sem necessidade.
- `DJANGO_SECURE_HSTS_PRELOAD=false`. O *preload* se pede para o domínio registrável, e não para um
  subdomínio. Ligá-lo aqui não inscreve nada e sinaliza um compromisso que a instituição não tomou.
  A inscrição no preload é decisão do domínio `exemplo.edu.br` inteiro e é difícil de desfazer.

### 13.5 Certificado institucional

```bash
sudo install -d -m 0750 /etc/ssl/processoseletivo
sudo install -m 0644 <CADEIA_COMPLETA>.pem /etc/ssl/processoseletivo/fullchain.pem   # certificado + intermediárias
sudo install -m 0600 <CHAVE_PRIVADA>.pem   /etc/ssl/processoseletivo/privkey.pem
```

Na §14, troque os dois caminhos `ssl_certificate*` por estes. A renovação é manual: agende o lembrete
30 dias antes do vencimento. O `ps-verificar` alerta com 21 dias. A chave privada vai para o cofre,
e não para o backup.

---

## 14. Reverse proxy

nginx do Ubuntu 24.04 (1.24). A configuração não pôde ser ensaiada fora de uma VM: valide com
`nginx -t` a cada passo.

### 14.1 Formato de log e cabeçalhos globais

O `$request_id` do nginx vai para a aplicação como `X-Correlation-ID`, que a grava no log e **na
auditoria** (`shared/api/middleware.py`). Uma linha do log de acesso leva, pelo `rid=`, ao registro
de auditoria do mesmo pedido. O `$uri`, sem query string, e a ausência de `Referer` são
minimização.

```bash
sudo tee /etc/nginx/conf.d/processoseletivo.conf >/dev/null <<'CONF'
server_tokens off;
log_format processoseletivo '$remote_addr [$time_iso8601] "$request_method $uri $server_protocol" '
                            '$status $body_bytes_sent $request_time rid=$request_id';
CONF
```

### 14.2 Proxy para a aplicação

```bash
sudo tee /etc/nginx/snippets/processoseletivo-proxy.conf >/dev/null <<'CONF'
# Modo de manutenção: existe o arquivo, a aplicação sai do ar com página própria (§22).
if (-f /etc/nginx/processoseletivo.manutencao) { return 503; }

proxy_pass http://127.0.0.1:8000;
proxy_http_version 1.1;
proxy_set_header Connection "";
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
# SOBRESCREVE, e não acrescenta: o portal confia no PRIMEIRO item deste cabeçalho para o limite de
# pedidos por origem (portal/views.py:606-610). Com $proxy_add_x_forwarded_for, um cliente escreveria
# o primeiro item e contornaria o limite.
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
# Correlação escolhida pelo proxy, e não pelo cliente: é ela que vai para a auditoria.
proxy_set_header X-Correlation-ID $request_id;
proxy_redirect off;
proxy_connect_timeout 5s;
proxy_send_timeout 130s;
proxy_read_timeout 130s;    # acima do timeout do gunicorn (120 s)
CONF
```

### 14.3 Páginas de erro do proxy

Só os erros que o **nginx** gera: 502 e 504 quando a aplicação não responde, e 503 na manutenção.
Os erros da aplicação passam intactos, porque `proxy_intercept_errors` fica desligado. Isso inclui o
503 de `/gestao/identificar`, que explica a falta de autenticação institucional.

```bash
sudo tee /var/www/processoseletivo/_erro/indisponivel.html >/dev/null <<'HTML'
<!doctype html><html lang="pt-br"><meta charset="utf-8"><title>Indisponível</title>
<body style="font-family:sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem">
<h1>Sistema temporariamente indisponível</h1>
<p>O sistema de processos seletivos não respondeu. Tente novamente em alguns minutos.</p></body></html>
HTML
sudo tee /var/www/processoseletivo/_erro/manutencao.html >/dev/null <<'HTML'
<!doctype html><html lang="pt-br"><meta charset="utf-8"><title>Em manutenção</title>
<body style="font-family:sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem">
<h1>Sistema em manutenção</h1>
<p>Uma atualização está em andamento. O sistema volta em alguns minutos.</p></body></html>
HTML
```

### 14.4 O site

```bash
sudo tee /etc/nginx/sites-available/processoseletivo >/dev/null <<'CONF'
# Host desconhecido: recusa sem responder. ALLOWED_HOSTS já devolveria 400, mas assim a varredura
# não chega à aplicação.
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 444;
}
server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    server_name _;
    ssl_reject_handshake on;
}

# HTTP do domínio: só o desafio ACME e o redirecionamento.
server {
    listen 80;
    listen [::]:80;
    server_name <DOMINIO>;
    location ^~ /.well-known/acme-challenge/ { root /var/www/letsencrypt; }
    location / { return 301 https://<DOMINIO>$request_uri; }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <DOMINIO>;

    ssl_certificate     /etc/letsencrypt/live/<DOMINIO>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<DOMINIO>/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:processoseletivo:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    access_log /var/log/nginx/processoseletivo.access.log processoseletivo;
    error_log  /var/log/nginx/processoseletivo.error.log warn;

    # Corpo: 3 MB no geral (o Django limita campos a 2,5 MB). O corpo é bufferizado pelo nginx
    # antes de chegar ao gunicorn, e por isso um upload lento não prende um worker síncrono.
    client_max_body_size 3m;
    client_body_timeout 60s;
    send_timeout 60s;

    error_page 502 504 /_erro/indisponivel.html;
    error_page 503     /_erro/manutencao.html;
    location ^~ /_erro/ { internal; root /var/www/processoseletivo; }

    # Estáticos: o projeto não tem STATIC_ROOT (gap I-3), e o collectstatic falha. Servem-se direto
    # da release ativa; os diretórios só têm JS. "no-cache" porque os nomes não são versionados —
    # sem isso, o navegador usaria o JS da release anterior depois de um deploy.
    location ^~ /static/interface/ {
        alias /opt/processoseletivo/current/backend/processo_seletivo/interface/static/interface/;
        add_header Cache-Control "no-cache" always;
        add_header X-Content-Type-Options "nosniff" always;
        access_log off;
    }
    location ^~ /static/portal/ {
        alias /opt/processoseletivo/current/backend/processo_seletivo/portal/static/portal/;
        add_header Cache-Control "no-cache" always;
        add_header X-Content-Type-Options "nosniff" always;
        access_log off;
    }
    location ^~ /static/ { return 404; }

    # Operacionais: /readiness revela o estado do banco e das migrations, e fica restrito. /metrics
    # não autentica ninguém hoje (API_AUTHENTICATION_CLASSES provisória), e fica fechado.
    location = /readiness {
        allow 127.0.0.1;
        allow ::1;
        # allow <IP_MONITORAMENTO>;
        deny all;
        include snippets/processoseletivo-proxy.conf;
    }
    location = /metrics { deny all; }

    # Portal do candidato: um PDF de até 10 MiB por envio (ARQUIVOS_CANDIDATOS_LIMITE_BYTES).
    location ^~ /selecoes/ {
        client_max_body_size 12m;
        include snippets/processoseletivo-proxy.conf;
    }
    # Gestão: a Retificação envia vários anexos de até 5 MiB num POST só (interface/views.py, _artefatos_enviados).
    location ^~ /gestao/ {
        client_max_body_size 60m;
        include snippets/processoseletivo-proxy.conf;
    }
    location / {
        include snippets/processoseletivo-proxy.conf;
    }
}
CONF
sudo nginx -t && sudo systemctl reload nginx
```

`location` e `alias` terminam os dois em `/`, e não é detalhe: com a barra só num deles, o `alias`
abre caminho para `../`.

**Como verificar:**

```bash
curl -sI http://<DOMINIO>/selecoes/ | head -3                         # 301 → https://<DOMINIO>/selecoes/
curl -sI https://<DOMINIO>/health                                      # 200
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMINIO>/readiness   # 403 de fora; 200 de 127.0.0.1
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMINIO>/metrics     # 403
curl -sI https://<DOMINIO>/static/interface/htmx.min.js | grep -Ei '^(HTTP|content-type|cache-control)'
#   HTTP/2 200 · application/javascript · no-cache
curl -sI --path-as-is https://<DOMINIO>/static/interface/../../../config/settings/base.py | head -1   # 400 ou 404, nunca 200
curl -sk -o /dev/null -w '%{http_code}\n' -H 'Host: outro.exemplo' https://<IP_DO_SERVIDOR>/   # falha no handshake (000)
curl -sI https://<DOMINIO>/selecoes/ | grep -Ei 'strict-transport|x-frame|x-content-type|referrer|cross-origin|server'
#   Strict-Transport-Security: max-age=31536000 · X-Frame-Options: DENY · nosniff · same-origin · Server: nginx (sem versão)
openssl s_client -connect <DOMINIO>:443 -servername <DOMINIO> </dev/null 2>/dev/null | grep -E 'Protocol|Cipher'
```

Recomenda-se também um teste externo de TLS, como o SSL Labs, com nota A esperada.

---

## 15. Static, documentos e arquivos privados

### 15.1 STATIC não é MEDIA

| | O que é | Onde mora | Como é servido | Público? |
|---|---|---|---|---|
| **Static** | 22 arquivos JS do código | na release, `.../static/interface/` e `.../static/portal/` | nginx, por `alias` (§14) | sim, e é código |
| **Documentos do candidato** | PDFs de inscrição, os mais sensíveis | `/var/lib/processoseletivo/arquivos/inscricoes/<uuid-inscrição>/<uuid>.pdf` | **só pela aplicação**, com autorização | **nunca** |
| **Anexos do Edital** | PDFs publicados pela instituição | banco (`ArtefatoAnexo.bytes`) | `/api/v1/public/anexos/<uuid>`, só depois de congelado na publicação | sim, por decisão normativa |
| **PDFs do Edital e do resultado** | documento oficial | banco (`DocumentoPublicado`, `DocumentoDoResultado`) | API pública e portal | sim |
| **Comprovante, prévia do Edital e `.xlsx` de matrícula** | gerados a cada pedido | não são guardados | pela aplicação, com `no-store` | não |

**Não há `MEDIA_URL` nem `MEDIA_ROOT`**, e **não se deve criar** `location` no nginx para
`/var/lib/processoseletivo/arquivos`. É exatamente o que a barreira de `production.py:124-132`
existe para impedir.

### 15.2 Auditoria do acesso aos documentos (constatado)

- **URL pública:** nenhuma. O `ArmazenamentoPrivado.url()` sempre lança exceção
  (`inscricoes/storage.py:50-61`).
- **Nome no disco:** UUID gerado pelo servidor. O nome enviado pela pessoa vira só metadado
  (`nome_original`) e **nunca** decide caminho (`storage.py:64-72`, `inscricoes/models.py:346`).
- **Path traversal:** o caminho é todo gerado pelo servidor, e o Django ainda o passa por
  `safe_join`.
- **Tipo aceito:** só PDF, conferido pelos *magic bytes* `%PDF-`, até 10 MiB, e arquivo vazio é
  recusado (`shared/arquivos.py:56-93`). **Não há antivírus** (§27).
- **Integridade:** SHA-256 gravado no upload (`content_hash`), reconferido no envio da inscrição e
  a cada leitura da equipe. Divergência dá 409 e fica registrada na auditoria
  (`interface/views.py:5103-5119`).

Autorização de download, rota a rota:

| Quem | Rota | Regra |
|---|---|---|
| Candidato | `/selecoes/inscricoes/<uuid>/documentos/<uuid>/arquivo` | titularidade; 404 para quem não é o titular (`portal/views.py:1871-1884`) |
| Comissão | `/gestao/inscricoes/<uuid>/documentos/<uuid>` | permissão `inscricao:consultar` e escopo institucional; o acesso é auditado |
| Avaliador | `/gestao/minhas-etapas/.../documentos/<uuid>` | exige Atribuição; auditado |
| Julgador de recurso | `/gestao/recursos/<uuid>/instrucao/<uuid>` | permissão, e o ato de instrução precisa alcançar o documento; auditado |

**Temporários:** uploads acima de 2,5 MB passam pelo `/tmp`, e a cópia verificada acima de 2 MiB
também (`portal/arquivos.py:24`). A unit usa `PrivateTmp=yes`, e esses arquivos ficam num `/tmp`
só do serviço, apagado quando ele para. O nginx também bufferiza os corpos grandes em
`/var/lib/nginx/body`, legível só pelo `www-data`, e apaga ao fim da requisição.

**Descarte:** os documentos só são apagados enquanto a inscrição é rascunho, por substituição ou
remoção (`inscricoes/application/rascunho.py`). Depois do envio são imutáveis. **Não há expurgo**
(B-2), e documentos de quem nunca enviou a inscrição ficam para sempre.

### 15.3 Como verificar

```bash
sudo stat -c '%a %U:%G %n' /var/lib/processoseletivo/arquivos        # 700 processoseletivo:processoseletivo
sudo -u www-data ls /var/lib/processoseletivo/arquivos 2>&1 | head -1 # Permission denied
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMINIO>/var/lib/processoseletivo/arquivos/   # 404
# Depois de haver documentos: um UUID válido de documento, sem sessão, não pode dar 200
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMINIO>/selecoes/inscricoes/<uuid>/documentos/<uuid>/arquivo   # 302 (login) ou 404
```

---

## 16. E-mail

### 16.1 O que envia e quando

Constatado: três fluxos, todos **síncronos, dentro da requisição**. Todos capturam a exceção, gravam
no log e **não** desfazem a ação do usuário.

| Fluxo | Evidência | Efeito de SMTP fora do ar |
|---|---|---|
| **Código de acesso** (entrar, adicionar credencial, retomar) | `identidade/application/mensagem.py:87-137` | o candidato **não entra**; a tela mostra a mesma mensagem neutra de sempre |
| Comprovante de inscrição, depois do commit | `inscricoes/application/mensagem.py:68-102` | a inscrição vale; o e-mail não chega |
| Comunicação da convocação | `convocacao/application/comunicar.py:334-378` | registrada como `FALHA` |
| Aviso complementar aos candidatos (066), **fora da requisição** | `avisos/application/despacho.py`, pelo timer `ps-avisos` (§16.4) | a tentativa fica em falha temporária e é retentada; nada se perde |

**Não há recuperação de senha:** o candidato não tem senha. O código tem 6 dígitos, vale 10 minutos,
aceita 5 tentativas e fica guardado só em hash PBKDF2 (`identidade/domain/codigo.py`). O código e o
endereço **não** são registrados em log. Ensaiado: numa falha de SMTP, o log trouxe o traceback da
conexão recusada, e **nenhuma** ocorrência do e-mail de teste.

### 16.2 Requisitos do SMTP

- STARTTLS na porta 587 (`EMAIL_USE_TLS=true`). **A 465, com SSL implícito, não é suportada** (gap).
- Conta de envio própria do sistema, com `DEFAULT_FROM_EMAIL` autorizado a enviar por ela.
- SPF, DKIM e DMARC do domínio remetente cobrindo o servidor, senão o código cai no spam.
- **Timeout na aplicação**: `EMAIL_TIMEOUT` (padrão 20 s), desde a 066, vale para os quatro envios. O
  gap I-4 está fechado quanto ao timeout. Peça mesmo assim ao setor de correio um servidor que
  responda rápido, e redundante: é o único fator de autenticação do candidato (RC-93).
- **Dia de pico** (último dia de inscrições): confira limite de envio por minuto e por dia da conta.
- **Limite da conta para os avisos**: obtenha do setor de correio quantas mensagens por minuto e por
  dia a conta aceita, e ajuste `AVISOS_LIMITE_POR_MINUTO` (padrão 60) **antes** de ligar os avisos.

### 16.4 Avisos aos candidatos (066)

**Desligados em produção até duas validações**: a institucional de LGPD, com o encarregado de dados,
e a da infraestrutura de correio (limite acima). Enquanto `AVISOS_AOS_CANDIDATOS` não for `true`,
ninguém confirma aviso e o despacho não envia nada; o histórico e os modelos continuam acessíveis.

O despacho é um comando periódico, e não um worker: `manage.py despachar_avisos`, a cada minuto,
com no máximo `AVISOS_LIMITE_POR_MINUTO` mensagens por execução. Ele sai com código diferente de 0
**só** quando a conexão com o servidor de correio não abre — é isso que aciona o `OnFailure`.

| Variável | Padrão | Uso |
|---|---|---|
| `AVISOS_AOS_CANDIDATOS` | `false` | liga a confirmação e o despacho |
| `AVISOS_LIMITE_POR_MINUTO` | 60 | mensagens por execução, uma execução por minuto |
| `AVISOS_MAX_TENTATIVAS` | 3 | tentativas de uma falha temporária |
| `AVISOS_INTERVALOS_DE_RETENTATIVA` | `5,15` | minutos antes da 2ª e da 3ª tentativa |
| `AVISOS_ALERTA_DE_PENDENTE_MIN` | 10 | o histórico avisa que o despacho pode estar parado |
| `AVISOS_JANELA_DE_DESPACHO_HORAS` | 24 | aviso mais velho que isto expira sem envio — religar a chave não dispara mensagem antiga |

A unidade systemd está na §21.4. **Um timer desabilitado não alerta nada**: o histórico do aviso
mostra "o despacho pode não estar processando", e a conferência de `systemctl list-timers` da §21.4
é a que pega o caso antes de alguém olhar a tela.

### 16.3 Teste

```bash
# Conectividade e TLS até o servidor
openssl s_client -starttls smtp -connect <SMTP_HOST>:587 -servername <SMTP_HOST> </dev/null 2>/dev/null | grep -E 'Verify return|Protocol'
# Envio real, com as settings de produção
sudo ps-manage sendtestemail <CAIXA_DE_TESTE_DA_EQUIPE>
journalctl -u processoseletivo --since "10 min ago" | grep -i 'Falha ao enviar' || echo "sem falha registrada"
```

**Sucesso** é a mensagem chegar na caixa de entrada, e não no spam, com o remetente certo.

---

## 17. Smoke test

**Em produção, teste não se desfaz.** Publicação é imutável e nada é excluído. Os fluxos que criam
Processo, Edital, inscrição ou resultado se testam em **homologação**, com a mesma release e dado
sintético. Em produção, só o que não deixa ato normativo para trás.

### 17.1 Técnico, em produção

```bash
D=<DOMINIO>
systemctl is-active processoseletivo nginx postgresql@18-main       # active ×3
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -H 'Accept: text/html' https://$D/   # 302 → /selecoes/
curl -s -o /dev/null -w '%{http_code}\n' https://$D/selecoes/                 # 200: vitrine pública
curl -s -o /dev/null -w '%{http_code}\n' https://$D/selecoes/acesso           # 200: tela de acesso
curl -s -H 'Accept: application/json' https://$D/ | head -c 200; echo         # JSON do serviço
curl -s -o /dev/null -w '%{http_code}\n' https://$D/gestao/identificar        # 503 — esperado até B-1
curl -s -o /dev/null -w '%{http_code}\n' https://$D/api/v1/admin/processos    # 403 — API admin fechada
curl -s -o /dev/null -w '%{http_code}\n' https://$D/nao-existe                # 404
curl -s https://$D/nao-existe | grep -c 'URLconf'                             # 0: não é a página técnica do DEBUG
curl -s -o /dev/null -w '%{http_code}\n' https://$D/static/portal/envio.js    # 200
```

**Erro 500.** Não há rota que o provoque de propósito, e não se deve criar uma. O projeto também
não tem `500.html`, então o Django responde o texto genérico "Server Error (500)", sem traceback,
porque `DEBUG` é `False`. Um 500 real aparece no journal como `django.request` `ERROR`.

**Erro 502 e página de indisponível:**

```bash
sudo systemctl stop processoseletivo
curl -s -o /dev/null -w '%{http_code}\n' https://$D/selecoes/     # 502, com a página "temporariamente indisponível"
sudo systemctl start processoseletivo
```

### 17.2 Funcional em produção, sem ato normativo

| # | Fluxo | Como | Sucesso |
|---|---|---|---|
| 1 | Página inicial e vitrine | abrir `https://<DOMINIO>/` | redireciona à vitrine, e os estilos e scripts carregam (DevTools sem 404) |
| 2 | OTP e e-mail | `/selecoes/acesso` com a caixa de teste da equipe | o código chega em menos de 1 min; digitado, entra. Fica um registro de identidade dessa caixa, aceitável e documentado |
| 3 | Área do candidato | depois de entrar | abre, e "Sair" encerra |
| 4 | CSRF atrás do proxy | o próprio item 2 (é um POST) | não dá 403. Com `DJANGO_TRUST_PROXY_SSL_HEADER` errado, daria |
| 5 | Espera de reenvio | pedir um segundo código para a mesma caixa em menos de 60 s | nenhum código novo chega, e a tela mostra a mesma mensagem neutra (`desafio.py:36`) |
| 6 | Consulta a resultados e Editais | `/selecoes/` e a API pública | respondem, vazias até a primeira publicação |

### 17.3 Funcional em homologação — hoje bloqueado por B-1

A lista pedida — administração, autenticação da gestão, criação de Processo, publicação, inscrição
com upload, download autorizado pela comissão, operações da comissão, PDF, resultados — **depende
da gestão**, que responde 503 sob as settings de produção. Quando a autenticação institucional
existir:

- rode em homologação o roteiro de `doc/roteiro-teste-operacional-assistido-28-2026.md`;
- confira, em especial, que o avaliador **sem** Atribuição recebe 404 ao abrir um documento, e que
  o acesso da comissão aparece na trilha de auditoria;
- em produção, o primeiro Edital real é o teste.

---

## 18. Backup

### 18.1 O que precisa sobreviver à destruição da VM

| Dado | Onde | Como entra no backup |
|---|---|---|
| Banco inteiro: atos, auditoria, inscrições, anexos, PDFs publicados, CEP | PostgreSQL | `pg_dump -Fc`, diário |
| **Documentos dos candidatos** | `/var/lib/processoseletivo/arquivos` | restic, diário, **depois** do dump |
| Histórico de implantações | `/var/lib/processoseletivo/implantacoes.log` | restic |
| Configuração sem segredo: nginx, units, scripts, `gunicorn.conf.py` | `/etc/...`, `/usr/local/sbin/ps-*` | restic |
| **Segredos**: `app.env`, `migracao.env`, senha do restic, chave TLS institucional | `/etc/processoseletivo`, `/etc/ssl` | **fora do backup: no cofre institucional** |
| Código | GitHub e `repo.git` | reconstruível pelo SHA do `implantacoes.log` |

**Por que o banco antes dos arquivos.** Os arquivos copiados depois do dump são um **superconjunto**
dos que o dump referencia: pode sobrar arquivo, mas não faltar. Na ordem inversa, uma inscrição
enviada no intervalo apontaria para um documento que não está no backup. A exceção é um rascunho
cujo documento seja substituído exatamente nesse intervalo. A conferência da §19.4 aponta esses
casos como `AUSENTE`, e eles são de rascunho, não de inscrição enviada — documento enviado é
imutável (`inscricoes/models.py:367-387`).

**Por que os segredos ficam fora.** O backup costuma ter retenção mais longa e mais gente com acesso
do que a VM. Os segredos têm ciclo próprio, de rotação e revogação. O que é insubstituível — a
`DJANGO_SECRET_KEY` e a senha do restic — fica no cofre, desde a §10.

### 18.2 Regra 3-2-1

| Cópia | Onde | Independente da VM? |
|---|---|---|
| 1 — operacional | o próprio banco e o disco | não |
| 2 — local | `/var/backups/processoseletivo/banco` (7 dias de dumps) | **não**: o mesmo disco. Serve para restaurar rápido, não para desastre |
| 3 — externa | repositório **restic** em `<HOST_BACKUP>`, cifrado, com retenção | **sim** |
| extra | snapshot da VM no hipervisor, antes de cada deploy | não substitui backup: mesma infraestrutura, sem retenção controlada |

Para o "2 mídias, 1 fora do local", o `<HOST_BACKUP>` deve ficar em outro storage, e de preferência
outro prédio. **Destino append-only é fortemente recomendado** (rest-server com `--append-only`, ou
snapshots do lado do servidor). Uma VM comprometida com credencial de escrita **apaga** o próprio
backup.

### 18.3 Repositório restic

**[admin]**

```bash
sudo ssh-keygen -t ed25519 -N '' -C 'backup@processoseletivo' -f /root/.ssh/backup_processoseletivo
# autorize a chave pública em <USUARIO_BACKUP>@<HOST_BACKUP>, restrita a sftp
sudo tee -a /root/.ssh/config >/dev/null <<'CONF'
Host <HOST_BACKUP>
  User <USUARIO_BACKUP>
  IdentityFile /root/.ssh/backup_processoseletivo
  IdentitiesOnly yes
CONF
sudo sh -c 'umask 077; python3 -c "import secrets; print(secrets.token_urlsafe(48))" > /etc/processoseletivo/restic.senha'
sudo install -m 0600 /dev/null /etc/processoseletivo/restic.env
sudo tee /etc/processoseletivo/restic.env >/dev/null <<'CONF'
RESTIC_REPOSITORY=sftp:<HOST_BACKUP>:/<CAMINHO_NO_SERVIDOR>/processoseletivo
RESTIC_PASSWORD_FILE=/etc/processoseletivo/restic.senha
CONF
sudo bash -c 'set -a; . /etc/processoseletivo/restic.env; set +a; restic init'
sudo cat /etc/processoseletivo/restic.senha     # → COFRE, agora. Sem ela o backup é ilegível.
```

### 18.4 Script e agendamento

```bash
sudo tee /usr/local/sbin/ps-backup >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Backup: banco primeiro, depois documentos e configuração, para o restic fora da VM.
set -euo pipefail
umask 077
DIR=/var/backups/processoseletivo
ARQ="$DIR/banco/processo_seletivo-$(date +%Y%m%d-%H%M%S).dump"

runuser -u postgres -- pg_dump --format=custom processo_seletivo > "$ARQ.parcial"
pg_restore --list "$ARQ.parcial" > /dev/null          # o dump é legível?
mv "$ARQ.parcial" "$ARQ"
# Resumo com o nome relativo, para conferir com `sha256sum -c` em qualquer diretório da restauração.
( cd "$DIR/banco" && sha256sum "$(basename "$ARQ")" > "$(basename "$ARQ").sha256" )

set -a; . /etc/processoseletivo/restic.env; set +a
restic backup --host processoseletivo --tag diario \
  "$ARQ" "$ARQ.sha256" \
  /var/lib/processoseletivo/arquivos \
  /var/lib/processoseletivo/implantacoes.log \
  /etc/processoseletivo/gunicorn.conf.py /etc/processoseletivo/alerta.env \
  /etc/systemd/system/processoseletivo.service /etc/systemd/system/ps-*.service /etc/systemd/system/ps-*.timer \
  /etc/nginx/sites-available/processoseletivo /etc/nginx/snippets/processoseletivo-proxy.conf \
  /etc/nginx/conf.d/processoseletivo.conf /etc/postgresql/18/main/conf.d/processoseletivo.conf \
  /etc/postgresql/18/main/pg_hba.conf /usr/local/sbin

# Retenção remota. Com destino append-only, a retenção é feita no servidor de backup: remova as duas linhas.
restic forget --host processoseletivo --keep-daily 14 --keep-weekly 8 --keep-monthly 12
[ "$(date +%u)" = 7 ] && { restic prune; restic check; }

find "$DIR/banco" -type f \( -name 'processo_seletivo-*.dump*' -o -name 'pre-deploy-*.dump' \) -mtime +7 -delete
date --iso-8601=seconds > "$DIR/ultimo-sucesso"
SCRIPT
sudo chmod 0750 /usr/local/sbin/ps-backup
```

Os timers e o alerta de falha (o `ps-alerta` está na §21):

```bash
sudo tee /etc/systemd/system/ps-backup.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — backup (banco, documentos, configuração)
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-backup
Nice=10
IOSchedulingClass=idle
UNIT
sudo tee /etc/systemd/system/ps-backup.timer >/dev/null <<'UNIT'
[Unit]
Description=Backup diário do Processo Seletivo
[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=10m
Persistent=true
[Install]
WantedBy=timers.target
UNIT
sudo systemctl daemon-reload && sudo systemctl enable --now ps-backup.timer
```

**Frequência, retenção e o RPO:**

| | Valor | Justificativa |
|---|---|---|
| Frequência | diária, às 02:30 | RPO de até 24 h fora dos períodos críticos |
| **Durante inscrições abertas e publicação de resultado** | a cada 4 h: `OnCalendar=*-*-* 00/4:30:00` | um dia de inscrições perdidas é irrecuperável: o candidato não reenvia o que não sabe que se perdeu |
| Retenção remota | 14 diários, 8 semanais, 12 mensais | ~1 ano de pontos de restauração. **Ajuste à política de retenção (B-2)**: backup também guarda dado pessoal, inclusive o que já foi descartado da produção |
| Retenção local | 7 dias | restauração rápida; o disco é o mesmo |
| Compressão | a do `pg_dump -Fc` e a deduplicação do restic | — |
| Criptografia | AES-256 do restic, com a chave no cofre | o dump local, 0600 root, fica em claro no disco da VM, e é por isso que ele vive só 7 dias |

**Como verificar:**

```bash
sudo systemctl start ps-backup.service && systemctl status ps-backup.service --no-pager   # status=0/SUCCESS
sudo ls -l /var/backups/processoseletivo/banco/ && cat /var/backups/processoseletivo/ultimo-sucesso
sudo bash -c 'set -a; . /etc/processoseletivo/restic.env; set +a; restic snapshots --host processoseletivo | tail -5'
systemctl list-timers ps-backup.timer
```

**Backup sem restauração testada não conta.** A §19 é obrigatória antes do go-live, e depois
trimestral.

---

## 19. Restore

### 19.1 Quando usar cada caminho

| Situação | Caminho |
|---|---|
| Deploy com migration falhou, janela de manutenção ainda fechada | dump `pre-deploy` local (§23) |
| Banco corrompido ou apagado, VM íntegra | último dump local ou do restic → §19.3 |
| VM perdida | VM nova → §19.2 → §19.3 → §19.4 |
| Teste trimestral de restauração | VM **descartável** → o caminho completo, e o registro em §19.5 |

### 19.2 VM nova até a aplicação instalada

Execute as §§ 5 a 9 e a §10, com estas diferenças:

- **`DJANGO_SECRET_KEY` do cofre**, a mesma de antes. Uma nova invalida os comprovantes emitidos.
- As senhas dos papéis do banco podem ser novas: o `provisionar_papeis` as redefine.
- **O mesmo commit** que estava em produção, tirado do `implantacoes.log` restaurado:
  `ps-construir <SHA>`, **sem ativar** ainda.
- Num **teste** de restauração, use `<DOMINIO_DE_TESTE>` e outra caixa de SMTP. Deixe
  `DJANGO_EMAIL_BACKEND` apontando para uma caixa de teste, para que nenhuma mensagem chegue a
  candidato real.

### 19.3 Banco

```bash
sudo bash -c 'set -a; . /etc/processoseletivo/restic.env; set +a; restic snapshots --host processoseletivo'
sudo bash -c 'set -a; . /etc/processoseletivo/restic.env; set +a; restic restore <ID_DO_SNAPSHOT> --target /srv/restauracao'
sudo sh -c 'cd /srv/restauracao/var/backups/processoseletivo/banco && sha256sum -c processo_seletivo-*.sha256'   # …: OK

R=/opt/processoseletivo/releases/<nome-construído>
# Se o banco "processo_seletivo" já existir e estiver corrompido, renomeie-o — não o apague:
#   sudo -u postgres psql -c 'ALTER DATABASE processo_seletivo RENAME TO processo_seletivo_avariado_<data>'
sudo -u postgres createdb --encoding=UTF8 --locale=pt_BR.UTF-8 --template=template0 processo_seletivo
sudo -u postgres psql -c 'REVOKE CONNECT ON DATABASE processo_seletivo FROM PUBLIC;'
sudo ps-migrar --so-provisionar "$R"                       # 1ª passada: cria os papéis — "0 de 34"
sudo sh -c "runuser -u postgres -- pg_restore --exit-on-error --single-transaction -d processo_seletivo \
  < /srv/restauracao/var/backups/processoseletivo/banco/<ARQUIVO>.dump"
sudo ps-migrar --so-provisionar "$R"                       # 2ª passada — "34 de 34"
sudo ps-manage --release "$R" migrate --check; echo $?     # 0
```

Esta sequência foi ensaiada. O `pg_restore` roda numa transação única e aborta no primeiro erro. A
posse das tabelas volta ao papel de migração, os 46 gatilhos voltam, e o papel de runtime continua
**sem** `DELETE` na auditoria (`permission denied for table auditoria_registroauditoria`).

Se `migrate --check` sair com 1, o dump é mais antigo que a release. Rode `sudo ps-migrar "$R"`, que
aplica as migrations que faltam.

### 19.4 Documentos e integridade

```bash
sudo rsync -a --delete-after /srv/restauracao/var/lib/processoseletivo/arquivos/ /var/lib/processoseletivo/arquivos/
sudo chown -R processoseletivo:processoseletivo /var/lib/processoseletivo/arquivos
sudo chmod 0700 /var/lib/processoseletivo/arquivos
sudo cp /srv/restauracao/var/lib/processoseletivo/implantacoes.log /var/lib/processoseletivo/implantacoes.log
```

Conferência de cada documento do banco contra o arquivo em disco, pelo `content_hash` (SHA-256)
gravado no upload:

```bash
sudo tee /usr/local/sbin/ps-conferir-documentos >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Confere cada documento registrado no banco contra o arquivo em disco (SHA-256).
set -euo pipefail
RAIZ=/var/lib/processoseletivo/arquivos
total=0; ausentes=0; divergentes=0
while IFS='|' read -r hash caminho; do
  total=$((total + 1)); f="$RAIZ/$caminho"
  if [ ! -f "$f" ]; then echo "AUSENTE $caminho"; ausentes=$((ausentes + 1)); continue; fi
  [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$hash" ] || { echo "DIVERGENTE $caminho"; divergentes=$((divergentes + 1)); }
done < <(runuser -u postgres -- psql -d processo_seletivo -At -c \
          "select content_hash, arquivo from inscricoes_documentosubmetido")
echo "documentos: $total · ausentes: $ausentes · divergentes: $divergentes"
[ "$ausentes" -eq 0 ] && [ "$divergentes" -eq 0 ]
SCRIPT
sudo chmod 0750 /usr/local/sbin/ps-conferir-documentos
sudo ps-conferir-documentos
```

Um `AUSENTE` numa inscrição **enviada** é perda real: investigue antes de abrir o sistema. Num
**rascunho**, é o intervalo entre o dump e a cópia dos arquivos (§18.1).

### 19.5 Subir, testar e registrar

```bash
sudo ps-ativar "$R"
# nginx e certificado: §13 e §14 (numa VM de teste, com <DOMINIO_DE_TESTE>)
# smoke test: §17.1
sudo rm -rf /srv/restauracao
echo "$(date --iso-8601=seconds) restauração de teste · snapshot <ID> · duração <MIN> min · resultado <OK/FALHA> · por <ADMIN>" \
  | sudo tee -a /var/lib/processoseletivo/restauracoes.log
```

A duração medida é o **RTO real**. Registre-a no checklist de go-live.

---

## 20. Logs e auditoria

### 20.1 Onde está cada coisa

| Log | Onde | Rotação e retenção |
|---|---|---|
| Aplicação: JSON com `level`, `logger`, `message`, `correlationId`, `code`, `status`, `actor` | `journalctl -u processoseletivo` | journald (§20.2) |
| Timers: backup, verificação, limpeza, CEP | `journalctl -u ps-backup -u ps-verificar -u ps-limpeza -u ps-ceps` | journald |
| Proxy (acesso, com `rid=`) | `/var/log/nginx/processoseletivo.access.log` | `/etc/logrotate.d/nginx` (padrão: diário, 14) |
| Proxy (erro) | `/var/log/nginx/processoseletivo.error.log` | idem |
| Banco | `/var/log/postgresql/postgresql-18-main.log` | logrotate do pacote |
| Sistema, SSH e sudo | `journalctl`, `journalctl -u ssh`, `journalctl _COMM=sudo` | journald |
| Implantações e restaurações | `/var/lib/processoseletivo/implantacoes.log`, `restauracoes.log` | permanentes, e vão para o backup |
| **Trilha de auditoria funcional** | tabela `auditoria_registroauditoria`, append-only | **permanente**; é dado, não log |

**Log técnico não é trilha de auditoria.** O log diz o que o **software** fez: erro, recusa,
falha de SMTP. A auditoria diz o que uma **pessoa** fez: quem, qual ato, sobre o quê, estado antes e
depois, motivo, instante. Ela é imutável em três camadas, e nenhuma política de retenção de log a
alcança.

### 20.2 Retenção

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nStorage=persistent\nSystemMaxUse=2G\nMaxRetentionSec=180day\n' \
  | sudo tee /etc/systemd/journald.conf.d/processoseletivo.conf
sudo systemctl restart systemd-journald
sudo sed -i 's/^\(\s*rotate\s\+\)[0-9]\+/\1180/' /etc/logrotate.d/nginx    # 180 arquivos diários
```

**180 dias é uma proposta, não uma norma.** Os logs de acesso guardam IP, instante e caminho, que
contém UUIDs de inscrição. Defina o prazo com o encarregado de dados (LGPD). Avalie também, com a
área jurídica, se o art. 15 do Marco Civil da Internet (guarda de registros de acesso a aplicações)
se aplica à instituição.

### 20.3 Investigar

```bash
# Erros da aplicação na última hora
journalctl -u processoseletivo --since "1 hour ago" -o cat | grep -E '"level": "(ERROR|CRITICAL)"'
# Recusas de operação (4xx de domínio), com o ator
journalctl -u processoseletivo --since today -o cat | grep operacao_recusada
# Workers mortos por timeout
journalctl -u processoseletivo --since today | grep -E 'WORKER TIMEOUT|Worker .* was sent'
# Falhas de envio de e-mail
journalctl -u processoseletivo --since today -o cat | grep -i 'Falha ao enviar'
# Tudo o que aconteceu num pedido, do proxy à auditoria, pelo rid
grep 'rid=<RID>' /var/log/nginx/processoseletivo.access.log
journalctl -u processoseletivo -o cat | grep '<RID>'
```

**Quem fez o quê, quando.** A trilha é a fonte:

- pela interface, em `/gestao/editais/<id>/auditoria` e `/gestao/processos/<id>/auditoria`, com o
  papel Auditor (`auditoria:consultar`);
- pela API, em `GET /api/v1/admin/auditoria?aggregateType=&aggregateId=`.

Enquanto B-1 fechar as duas portas, consulte pelo banco. **Esse acesso direto não é auditado pela
aplicação**: restrinja-o a quem precisa e registre o motivo fora do sistema.

```bash
sudo -u postgres psql -d processo_seletivo -c "
  select occurred_at, actor_subject, operation, aggregate_type, aggregate_id, previous_state, new_state, reason
  from auditoria_registroauditoria
  where correlation_id = '<RID>'            -- ou: aggregate_id = '<uuid>' / occurred_at between … and …
  order by occurred_at"
```

Publicação de resultado:

- `divulgacao_publicacaoresultado` — o ato, com autoridade e instante;
- `divulgacao_documentodoresultado` — o PDF publicado;
- `publicacoes_publicacao` e `publicacoes_versaoconsolidada` — o Edital.

Todas são append-only.

### 20.4 Lacunas da trilha (constatado)

Registradas em §26, I-7. **Não** são auditados:

- a entrada do candidato por código;
- o download do próprio documento pelo candidato;
- os eventos de credencial, gravados com escopo vazio e por isso invisíveis na consulta da gestão.

A exportação de matrículas fica em `matriculas_geracaodearquivo`, e não em `RegistroAuditoria`.
Para esses casos, o que resta é o log de acesso do nginx (IP, instante, caminho) — daí a
importância de definir a retenção dele.

---

## 21. Monitoramento

### 21.1 Três camadas, sem Prometheus

| Camada | O que cobre | Por quê |
|---|---|---|
| **Externa** (obrigatória): monitor institucional (Zabbix, Nagios…) ou serviço de uptime, de **fora** da VM | `https://<DOMINIO>/health` a cada 1–5 min; validade do certificado | uma VM parada não avisa que parou |
| **Local**: `ps-verificar` a cada 5 min, com alerta por e-mail | serviços, readiness, disco, memória, carga, certificado, idade do backup, NTP | é o que só se vê de dentro |
| **Aplicação** | `/readiness` (banco e migrations), journal | já existem (`shared/api/operacional.py`) |

O `/metrics` existe, mas não serve para isso hoje: exige autenticação da API (fechada, I-1), e os
contadores são por processo e zeram no restart.

### 21.2 Alerta por e-mail

Usa o SMTP da própria aplicação, sem instalar MTA:

```bash
printf 'ALERTA_PARA=<EMAIL_ALERTA>\n' | sudo tee /etc/processoseletivo/alerta.env && sudo chmod 0600 /etc/processoseletivo/alerta.env
sudo tee /usr/local/sbin/ps-alerta >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Chamado por OnFailure=ps-alerta@%n: envia as últimas linhas da unidade que falhou.
set -euo pipefail
UNIDADE="${1:?unidade}"
PS_ALERTA_PARA=$(. /etc/processoseletivo/alerta.env; echo "$ALERTA_PARA")
PS_ALERTA_ASSUNTO="[processoseletivo] falha em $UNIDADE ($(hostname))"
PS_ALERTA_CORPO=$(journalctl -u "$UNIDADE" -n 40 --no-pager -o short-iso)
export PS_ALERTA_PARA PS_ALERTA_ASSUNTO PS_ALERTA_CORPO
exec /usr/local/sbin/ps-manage shell --no-imports -c "import os; from django.core.mail import send_mail; send_mail(os.environ['PS_ALERTA_ASSUNTO'], os.environ['PS_ALERTA_CORPO'], None, os.environ['PS_ALERTA_PARA'].split(','))"
SCRIPT
sudo chmod 0750 /usr/local/sbin/ps-alerta
sudo tee /etc/systemd/system/ps-alerta@.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — alerta de falha em %i
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-alerta %i
UNIT
```

Se o SMTP estiver fora do ar, o alerta também falha. É mais uma razão para a camada externa.

### 21.3 Verificação local

```bash
sudo tee /usr/local/sbin/ps-verificar >/dev/null <<'SCRIPT'
#!/usr/bin/env bash
# Sai com 1, listando os problemas, quando algo precisa de atenção.
set -uo pipefail
# Na janela de manutenção (§22.3b) o 503 é esperado: não alerta.
[ -f /etc/nginx/processoseletivo.manutencao ] && { echo "em manutenção"; exit 0; }
problemas=()
DOMINIO=$(. /etc/processoseletivo/app.env; echo "${DJANGO_ALLOWED_HOSTS%%,*}")

for s in processoseletivo nginx postgresql@18-main; do
  systemctl is-active --quiet "$s" || problemas+=("serviço $s inativo")
done
curl -fsS -o /dev/null -m 10 -H "Host: $DOMINIO" -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/readiness \
  || problemas+=("readiness falhou (banco fora ou migration pendente)")
curl -fsS -o /dev/null -m 10 "https://$DOMINIO/health" || problemas+=("https://$DOMINIO/health falhou")

for m in / /var/lib/postgresql /var/lib/processoseletivo /var/backups/processoseletivo; do
  uso=$(df --output=pcent "$m" | tail -1 | tr -dc 0-9)
  [ "$uso" -lt 80 ] || problemas+=("disco de $m em ${uso}%")
done
disp=$(awk '/MemAvailable/ {print $2}' /proc/meminfo); total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
[ $((disp * 100 / total)) -ge 10 ] || problemas+=("memória disponível abaixo de 10%")
carga=$(cut -d' ' -f2 /proc/loadavg | cut -d. -f1)
[ "$carga" -lt $(( $(nproc) * 2 )) ] || problemas+=("carga média de 5 min em $carga")

fim=$(echo | openssl s_client -connect "$DOMINIO:443" -servername "$DOMINIO" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$fim" ]; then
  dias=$(( ($(date -d "$fim" +%s) - $(date +%s)) / 86400 ))
  [ "$dias" -ge 21 ] || problemas+=("certificado vence em $dias dias")
else problemas+=("não foi possível ler o certificado"); fi

if [ -f /var/backups/processoseletivo/ultimo-sucesso ]; then
  horas=$(( ($(date +%s) - $(date -d "$(cat /var/backups/processoseletivo/ultimo-sucesso)" +%s)) / 3600 ))
  [ "$horas" -le 26 ] || problemas+=("último backup concluído há ${horas}h")
else problemas+=("nenhum backup concluído registrado"); fi

[ "$(timedatectl show -p NTPSynchronized --value)" = yes ] || problemas+=("relógio não sincronizado")

if [ ${#problemas[@]} -gt 0 ]; then printf 'PROBLEMA: %s\n' "${problemas[@]}"; exit 1; fi
echo ok
SCRIPT
sudo chmod 0750 /usr/local/sbin/ps-verificar
sudo tee /etc/systemd/system/ps-verificar.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — verificação local
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-verificar
UNIT
sudo tee /etc/systemd/system/ps-verificar.timer >/dev/null <<'UNIT'
[Unit]
Description=Verificação local a cada 5 minutos
[Timer]
OnCalendar=*:0/5
[Install]
WantedBy=timers.target
UNIT
```

Um problema persistente gera um e-mail a cada 5 minutos, de propósito, até ser tratado.

### 21.4 Manutenção periódica

**[paliativo para o gap I-5]** Sessões expiradas e desafios de acesso terminais (que guardam
e-mails) não têm rotina no projeto. Os dois comandos abaixo foram testados:

```bash
sudo tee /etc/systemd/system/ps-limpeza.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — sessões expiradas e desafios de acesso terminais
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-manage clearsessions
ExecStart=/usr/local/sbin/ps-manage shell --no-imports -c "from processo_seletivo.identidade.application.desafio import limpar_terminais; print('desafios removidos:', limpar_terminais())"
UNIT
sudo tee /etc/systemd/system/ps-limpeza.timer >/dev/null <<'UNIT'
[Unit]
Description=Limpeza semanal
[Timer]
OnCalendar=Sun *-*-* 03:30:00
Persistent=true
[Install]
WantedBy=timers.target
UNIT

# Base de CEP: o job mensal do runbook. O .zip novo é posto no lugar por quem o baixa do storage
# institucional; o --se-mudou não faz nada quando o arquivo é o mesmo.
sudo tee /etc/systemd/system/ps-ceps.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — atualização da base de CEP
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-manage --migracao carregar_ceps /var/lib/processoseletivo/ceps/banco-ceps.zip --se-mudou
ExecStartPost=-/usr/local/sbin/ps-manage situacao_dos_ceps
UNIT
sudo tee /etc/systemd/system/ps-ceps.timer >/dev/null <<'UNIT'
[Unit]
Description=Atualização mensal da base de CEP
[Timer]
OnCalendar=*-*-01 04:00:00
Persistent=true
[Install]
WantedBy=timers.target
UNIT

# Avisos aos candidatos (066, §16.4): o despacho, a cada minuto. Instale junto com o resto; ele não
# faz nada enquanto AVISOS_AOS_CANDIDATOS não for true.
sudo tee /etc/systemd/system/ps-avisos.service >/dev/null <<'UNIT'
[Unit]
Description=Processo Seletivo — despacho dos avisos aos candidatos
OnFailure=ps-alerta@%n.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/ps-manage despachar_avisos
UNIT
sudo tee /etc/systemd/system/ps-avisos.timer >/dev/null <<'UNIT'
[Unit]
Description=Despacho dos avisos aos candidatos, a cada minuto
[Timer]
OnCalendar=*-*-* *:*:00
AccuracySec=5s
[Install]
WantedBy=timers.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now ps-verificar.timer ps-limpeza.timer ps-avisos.timer
sudo systemctl enable --now ps-ceps.timer          # só se a base de CEP for usada (§11.3)
```

`limpar_terminais` apaga, por estado e não por idade, só desafio consumido, expirado ou esgotado, e
preserva a reconciliação pendente (`identidade/application/desafio.py:268-293`). Não há comando
equivalente para documentos e rascunhos antigos: o descarte deles depende da política (B-2).

**Como verificar:**

```bash
systemctl list-timers 'ps-*' certbot.timer        # todos com próxima execução — ps-avisos inclusive
sudo systemctl start ps-avisos.service;    journalctl -u ps-avisos -n 3 --no-pager      # "Despacho de avisos: ..."
sudo systemctl start ps-verificar.service; journalctl -u ps-verificar -n 3 --no-pager   # "ok"
sudo systemctl start ps-limpeza.service;   journalctl -u ps-limpeza -n 5 --no-pager     # "desafios removidos: N"
# teste do alerta: deve chegar um e-mail em <EMAIL_ALERTA>
sudo systemctl start ps-alerta@teste.service
```

---

## 22. Atualização

### 22.1 Antes

- O commit está na `main`, com o workflow *Backend* verde.
- **Não é período crítico**: último dia de inscrições, prazo recursal no fim, publicação de
  resultado agendada. Atualização entra fora desses momentos.
- O backup do dia terminou (`cat /var/backups/processoseletivo/ultimo-sucesso`).
- Snapshot da VM no hipervisor, se disponível.

### 22.2 Construir e conferir, sem tocar o que está no ar

```bash
cat /opt/processoseletivo/current/REVISION                          # versão atual
R=$(sudo ps-construir <SHA> | tail -1)
sudo ps-manage --release "$R" check --deploy                          # sem ERRORS
sudo ps-manage --release "$R" --migracao migrate --plan               # quais migrations entram
```

Leia as notas do PR ou da release. **Variável nova exigida** por `production.py` aparece aqui, no
`check --deploy`, como `ImproperlyConfigured`: acrescente-a ao `app.env` antes de seguir.

### 22.3a Sem migrations — segundos de indisponibilidade

```bash
sudo ps-ativar "$R"          # ativada: …; o nginx mostra "indisponível" nos ~2–5 s do restart
```

### 22.3b Com migrations — janela de manutenção

Migration com o sistema recebendo escrita disputa lock com as requisições, e o código antigo pode
não entender o esquema novo. A janela fecha as duas coisas.

```bash
sudo touch /etc/nginx/processoseletivo.manutencao          # nginx passa a devolver 503 (manutenção); sem reload
sudo systemctl stop processoseletivo
sudo sh -c 'umask 077; runuser -u postgres -- pg_dump -Fc processo_seletivo > /var/backups/processoseletivo/banco/pre-deploy-$(date +%Y%m%d-%H%M%S).dump'
sudo ps-migrar "$R"                                        # "N de N" na segunda passada
sudo ps-ativar "$R"                                        # readiness pelo loopback, com o nginx ainda em manutenção
# smoke test pelo loopback, antes de reabrir:
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: <DOMINIO>' -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/selecoes/   # 200
sudo rm /etc/nginx/processoseletivo.manutencao             # reabre
```

**Se algo falhar antes do `rm`**, a janela continua fechada e ninguém escreveu nada: vá para a
§23.2.

### 22.4 Depois

```bash
tail -1 /var/lib/processoseletivo/implantacoes.log         # a linha "ativada" com o SHA novo
# §17.1 completo, e a §17.2 itens 1–3
journalctl -u processoseletivo --since "15 min ago" -p warning --no-pager
# Limpeza: manter as 5 releases mais recentes. Nunca apague a ativa nem a imediatamente anterior.
ls -1dt /opt/processoseletivo/releases/* | tail -n +6
#   confira a lista e então:  ls -1dt /opt/processoseletivo/releases/* | tail -n +6 | sudo xargs rm -rf
```

Apagar releases antigas remove código reconstruível, e não dado. Os dumps `pre-deploy-*` saem sozinhos
em 7 dias.

---

## 23. Rollback

**Rollback de código e rollback de banco são coisas diferentes.** O primeiro é trocar um symlink. O
segundo é voltar o banco a um instante anterior, e **perde tudo o que foi escrito depois dele**.

### 23.1 Só código — nenhuma migration aplicada

```bash
cat /var/lib/processoseletivo/implantacoes.log | tail -5            # a coluna "anterior="
sudo ps-ativar /opt/processoseletivo/releases/<release-anterior>
```

### 23.2 Código e banco — migration aplicada, janela ainda fechada

Nada foi escrito depois do dump `pre-deploy` (§22.3b), então voltar a ele não perde dado.

```bash
A=/opt/processoseletivo/releases/<release-anterior>
sudo systemctl stop processoseletivo
sudo -u postgres psql -c "ALTER DATABASE processo_seletivo RENAME TO processo_seletivo_falho_$(date +%Y%m%d%H%M)"
sudo -u postgres createdb --encoding=UTF8 --locale=pt_BR.UTF-8 --template=template0 processo_seletivo
sudo -u postgres psql -c 'REVOKE CONNECT ON DATABASE processo_seletivo FROM PUBLIC;'
sudo ps-migrar --so-provisionar "$A"
sudo sh -c "runuser -u postgres -- pg_restore --exit-on-error --single-transaction -d processo_seletivo \
  < /var/backups/processoseletivo/banco/pre-deploy-<carimbo>.dump"
sudo ps-migrar --so-provisionar "$A"                          # "34 de 34" (ou o M da release anterior)
sudo ps-manage --release "$A" migrate --check; echo $?        # 0
sudo ps-ativar "$A"
sudo rm /etc/nginx/processoseletivo.manutencao
```

O banco falho é **renomeado, e não apagado**: é a evidência para entender o que deu errado. Apague-o
só depois, deliberadamente.

### 23.3 Depois de reabrir — há dado novo

Se o sistema já recebeu escrita depois da migration — inscrições, atos, auditoria —, voltar ao dump
**apaga essas escritas**, inclusive registros de auditoria. Nesta ordem de preferência:

1. **Corrigir para frente:** uma release nova com a correção, pela §22.
2. Se o defeito é só de código e a versão anterior é compatível com o esquema novo, o que é raro e
   precisa ser **confirmado com quem desenvolveu**: §23.1.
3. Voltar ao dump só com decisão institucional registrada, sabendo o que se perde.

**Não reverta migrations com `migrate <app> <anterior>`.** Das migrations do projeto, 33 têm
`RunPython`, e várias criam gatilhos de imutabilidade. Reverter pode apagar coluna com dado, falhar
no meio contra uma tabela append-only, ou desligar uma garantia sem aviso. "Nada é excluído" vale
também aqui.

---

## 24. Runbook de incidentes

Para cada caso: o que verificar, onde está o log, os comandos, e o que **não** fazer por impulso.

**Aplicação fora do ar** (o site não abre)

- Verificar: `systemctl status processoseletivo nginx postgresql@18-main --no-pager`.
- Log: `journalctl -u processoseletivo -n 100 --no-pager` e `/var/log/nginx/processoseletivo.error.log`.
- Causa comum: `ImproperlyConfigured: <VAR>` no journal. Uma variável foi removida ou alterada.
  Corrija o `app.env` e rode `sudo systemctl restart processoseletivo`.
- Não fazer: ligar `DEBUG`, apontar para `config.settings.development` ou ligar o seletor "para
  ver o erro". É exatamente o que as barreiras existem para impedir.

**HTTP 502 ou 504**

- 502 é o gunicorn sem responder; 504 é uma requisição que passou de 130 s.
- `journalctl -u processoseletivo --since "30 min ago" | grep -E 'WORKER TIMEOUT|Booting worker|Exception'`
- Timeouts em série costumam ser SMTP lento (I-4) ou uma operação pesada. Confira o SMTP (§16.3) e
  `ps -o pid,etime,rss,cmd -C gunicorn`.
- Não fazer: aumentar os workers sem olhar a memória (`free -m`). Um OOM derruba o PostgreSQL junto.

**HTTP 503**

- Página de **manutenção**: o arquivo `/etc/nginx/processoseletivo.manutencao` existe. Esquecido
  depois de um deploy?
- 503 em `/gestao/identificar`: esperado até B-1.
- 503 no `/readiness`: `curl -s -H 'Host: <DOMINIO>' -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/readiness`.
  `"migrations": false` é migration pendente (uma release ativada sem `ps-migrar`); `"database": false`
  é o caso seguinte.

**Banco indisponível**

- `systemctl status postgresql@18-main`, `pg_lsclusters`,
  `tail -100 /var/log/postgresql/postgresql-18-main.log`.
- Disco cheio é a causa mais comum (caso seguinte). Depois, `max_connections`: confira com
  `sudo -u postgres psql -c 'select count(*) from pg_stat_activity'`.
- Não fazer: `pg_resetwal`, apagar arquivos de `pg_wal`, ou `DROP` de qualquer coisa. Restaure pela
  §19 se o cluster não voltar.

**Disco cheio**

- `df -h`, e depois
  `sudo du -xh --max-depth=2 /var | sort -h | tail -15`.
- Candidatos legítimos a limpeza:
  - `journalctl --vacuum-size=1G`;
  - dumps locais antigos, em `/var/backups/processoseletivo/banco`, desde que o restic os tenha;
  - releases antigas (§22.4).
- Não fazer: apagar nada em `/var/lib/processoseletivo/arquivos` nem em `/var/lib/postgresql`.
  Cresça o volume.

**Certificado expirando ou expirado**

- `sudo certbot certificates` e `sudo certbot renew --dry-run`.
- Falhas comuns: a porta 80 bloqueada no firewall institucional, DNS alterado, CAA novo.
- `journalctl -u certbot -n 50`. Com o certificado institucional: §13.5.
- Não fazer: desligar o HSTS "para os usuários conseguirem entrar". O navegador já guardou a
  exigência por um ano: resolva o certificado.

**Timer ou "worker" parado.** Não há worker de fila (§2); os jobs são timers.

- `systemctl list-timers 'ps-*'` e `systemctl --failed`.
- `journalctl -u ps-backup -n 50`. Um backup falhando é o mais grave: o RPO cresce a cada dia.

**Erro após deploy**

- `tail -3 /var/lib/processoseletivo/implantacoes.log`.
- `journalctl -u processoseletivo --since "<hora do deploy>"`.
- Decida entre a §23.1, a §23.2 e a §23.3 conforme houve migration e se a janela já reabriu.

**E-mail não sendo enviado** (candidato diz que o código não chega)

- `journalctl -u processoseletivo --since today -o cat | grep -c 'Falha ao enviar'`.
- `sudo ps-manage sendtestemail <CAIXA_DE_TESTE>`.
- Se o envio funciona, peça ao candidato para olhar o spam e confira SPF/DKIM do remetente.
- Os limites do próprio sistema também parecem "não chegou": 60 s entre pedidos, 5 por hora por
  endereço, 30 por hora por origem. A mensagem é neutra de propósito.
- Não fazer: mudar para o backend de console "para ler o código no log". `production.py` recusa,
  e seria entregar a autenticação de qualquer candidato a quem lê log.

**Upload falhando**

- 413 no navegador ou no log do nginx: passou do `client_max_body_size` (§14).
- Recusa pela aplicação: só PDF, até 10 MiB, e arquivo vazio é recusado. A mensagem aparece na tela.
- 500 com `PermissionError` no journal: donos de `/var/lib/processoseletivo/arquivos` (§6.1). Um
  restore com `rsync` sem `chown` é a causa típica.
- `OSError: [Errno 28]`: disco cheio.
- Não fazer: `chmod 777` no diretório de documentos.

**Suspeita de acesso indevido**

- Preserve antes de investigar:
  - `sudo cp /var/log/nginx/processoseletivo.access.log* /root/incidente-$(date +%F)/`;
  - `journalctl --since … > …`.
- A trilha de auditoria é imutável: consulte-a (§20.3).
- Acione o CSIRT e o encarregado de dados da instituição. Incidente com dado pessoal tem
  comunicação obrigatória à ANPD e aos titulares, conforme o caso.

---

## 25. Checklist de segurança e LGPD

### 25.1 Auditoria da VM — comandos e resultado esperado

| Item | Comando | Esperado |
|---|---|---|
| Portas expostas | `sudo ss -tulpn` | públicas só `:22`, `:80`, `:443`; `5432` e `8000` só em `127.0.0.1`/`::1` |
| Firewall | `sudo ufw status verbose` | deny por padrão; 22 só da rede administrativa |
| Varredura externa | `nmap -Pn -p- <IP_DO_SERVIDOR>`, de fora | 80 e 443 |
| Processos como root | `ps -eo user,comm \| sort -u \| grep -v '^root'` e revise os de root | gunicorn como `processoseletivo`; workers do nginx como `www-data`; PostgreSQL como `postgres` |
| Segredos | `sudo stat -c '%a %U %n' /etc/processoseletivo/*.env /etc/processoseletivo/restic.senha` | `600 root` |
| Segredo no Git | `git -C /opt/processoseletivo/repo.git log --all -p -S 'DJANGO_SECRET_KEY=' --oneline \| grep -v change-me \| head` | nada além do `.env.example` |
| Segredo no histórico | `sudo grep -hE 'SECRET_KEY=\|PASSWORD=' /root/.bash_history ~<ADMIN>/.bash_history` | nada |
| Diretórios graváveis pela aplicação | `sudo -u processoseletivo find / -writable -type d 2>/dev/null \| grep -vE '^/(proc\|sys\|dev\|run\|tmp\|var/tmp)'` | só `/var/lib/processoseletivo/arquivos` (e, fora do serviço, o que o SO dá a todo usuário) |
| Código só leitura | `sudo find /opt/processoseletivo -perm -o+w` | vazio |
| SSH | `sudo sshd -T \| grep -Ei 'permitroot\|passwordauth\|allowgroups'` | `no`, `no`, `acesso-ssh` |
| TLS | SSL Labs, ou `openssl s_client` (§14) | TLS 1.2 e 1.3 apenas; nota A |
| Banco | `sudo -u postgres psql -c 'show listen_addresses'`; `select … from pg_hba_file_rules` | `localhost`; só as 3 regras da §9 |
| Papéis do banco | §11.2 | nenhum superusuário; runtime sem `DELETE` na auditoria |
| Cabeçalhos | `curl -sI https://<DOMINIO>/selecoes/` | HSTS, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: same-origin`, COOP |
| Cookies | DevTools, depois de entrar no portal | `sessionid` e `csrftoken` com `Secure`, `HttpOnly`, `SameSite=Lax` (`production.py:242-247`) |
| CSRF | §17.2, item 4; `Origin` forjado → 403 (ensaiado) | — |
| CORS | `curl -sI -H 'Origin: https://evil.example' https://<DOMINIO>/api/v1/public/editais/…` | nenhum `Access-Control-Allow-Origin` |
| Documentos privados | §15.3 | sem URL; `www-data` não lê |
| `/metrics` e `/readiness` | §14 | 403 de fora |
| Dependências | numa estação ou no CI: `cd backend && uv export --locked --no-dev --format requirements-txt > /tmp/req.txt && uvx pip-audit -r /tmp/req.txt` | nenhuma vulnerabilidade sem tratamento |
| Pacotes do SO | `apt list --upgradable`; `pro security-status` | sem atualização de segurança pendente há mais de uma semana |
| Backup | `restic snapshots`; o `restauracoes.log` | snapshot de hoje; restauração testada há menos de 3 meses |
| Dado pessoal em log | `sudo grep -cE '[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}' /var/log/nginx/processoseletivo.access.log` | 0 (CPF não trafega em URL) |
| Avisos aos candidatos (066) | `sudo grep AVISOS_AOS_CANDIDATOS /etc/processoseletivo/*.env` | `false`, ou ausente, até a validação de LGPD com o encarregado de dados e a do limite da conta de correio (§16.4) |

### 25.2 LGPD — implicações operacionais

Não é parecer jurídico. É o que a operação precisa garantir, ou decidir com o encarregado de dados.

| Tema | Situação constatada | O que a operação faz |
|---|---|---|
| **Acesso aos documentos** | Autorizado por titularidade ou por permissão com escopo; o acesso da equipe é auditado (§15.2) | Conceder papel é ato de gestão: revise os papéis a cada Processo. O banco e a raiz de arquivos só são acessíveis a administradores da VM, que devem ser poucos e nominais (§6.1) |
| **Arquivos temporários** | Uploads e cópias acima de ~2 MB passam por `/tmp`; o `openpyxl` escreve a planilha em `/tmp` enquanto a monta | `PrivateTmp=yes` isola e apaga esses arquivos (§12.2). Os buffers do nginx ficam em `/var/lib/nginx`, só para `www-data` |
| **Logs** | A aplicação não registra CPF, e-mail nem código (`identidade/application/mensagem.py:107-109`). Um traceback de SMTP pode conter o destinatário. O nginx registra IP e caminho. O PostgreSQL pode registrar valores em erro de constraint | `log_parameter_max_length = 0` (§9). Retenção definida (§20.2). Acesso aos logs só para administradores |
| **Nunca em log** | senha (não existe), código de acesso (só hash), token (a API não tem) | não ligue `DEBUG`, o backend de e-mail de console, nem `log_statement = 'all'` no PostgreSQL |
| **Backups** | Cifrados (restic). O dump local fica em claro, 0600, por 7 dias | a retenção do backup é também retenção de dado pessoal: alinhe à política (B-2). Descarte na produção **não** descarta nos backups até expirarem |
| **Retenção e descarte** | **Não implementados** (B-2). Rascunhos, documentos, desafios com e-mail e sessões crescem sem limite | a limpeza de sessões e desafios é semanal (§21.4); para documentos e rascunhos, a política institucional é precondição |
| **Contas administrativas** | a gestão não tem contas hoje (B-1) | quando tiver: nominais, com o menor papel necessário, revogadas no fim do Processo |
| **Exportação de matrículas** | o `.xlsx` não é guardado; a geração é registrada | o arquivo baixado sai do controle do sistema: o destino (Registro Acadêmico) precisa de canal e guarda próprios |
| **Cópias para outros ambientes** | não existe anonimização | nunca copie produção para desenvolvimento ou homologação (§10.3) |
| **Incidente** | — | §24, "Suspeita de acesso indevido": preservar, acionar CSIRT e encarregado |

---

## 26. Gaps encontrados no projeto

A classificação segue a regra do pedido: **BLOQUEADOR** não deveria entrar em produção antes da
correção; **IMPORTANTE** entra com risco conhecido; **MELHORIA** fica para depois. Cada item traz a
evidência. Nenhum foi corrigido neste documento: governança é do usuário.

### BLOQUEADOR

**B-1 — A gestão não tem autenticação de produção.**

- Evidência:
  - `interface/views.py:606-610` responde 503 quando o seletor está desligado;
  - `interface/identidade.py:6-8` diz que o seletor "não é fronteira de segurança";
  - `production.py:87-91` recusa o seletor;
  - não há LDAP, OIDC, SAML, `RemoteUserMiddleware`, `LoginView` nem `AUTHENTICATION_BACKENDS`;
  - os papéis são o dicionário fixo `PAPEIS` (`interface/identidade.py:20-100`).
- Efeito: ninguém cria, publica ou conduz Edital em produção, e não existe primeiro usuário
  administrativo.
- Correção: um adaptador institucional que produza o `Actor` de `seguranca/domain.py`, com o papel
  vindo do diretório, e que **rotacione a sessão no login**. A `identificar` atual não chama
  `cycle_key()`. Registrado como RC-92, e como passo "Caminho de produção" em
  `doc/decisoes-pendentes-da-consolidacao.md:603`.

**B-2 — Não há política de retenção e descarte.**

- Evidência:
  - o README, § "Antes de receber dado pessoal real", a lista como precondição;
  - não há comando de expurgo (os únicos comandos são `provisionar_papeis`, `carregar_ceps`,
    `situacao_dos_ceps` e `seed_demo`);
  - `DesafioDeAcesso.email_canonico` guarda qualquer endereço digitado (`identidade/models.py`).
- Efeito: dado pessoal acumulado sem prazo, na produção e nos backups.
- Correção: decisão institucional e, depois dela, rotina no código.

### IMPORTANTE

**I-1 — Não há classe de autenticação institucional para a API admin.**

- Evidência: `production.py:199-228`; a única subclasse de `BaseAuthentication` é o adaptador de
  desenvolvimento (`seguranca/api/authentication.py`).
- Paliativo: `RemoteUserAuthentication`, que passa na barreira e **não autentica ninguém**. A API
  admin e o `/metrics` ficam fechados (ensaiado: 403).

**I-2 — Não há servidor WSGI nas dependências.**

- Evidência: `pyproject.toml:9-18`; o Dockerfile roda `runserver`.
- Paliativo: `gunicorn==26.2.0` instalado fora do lock (§8.3), **sem verificação de hash**.
- Correção: um extra `prod` no `pyproject.toml`, travado no `uv.lock`.

**I-3 — Não há `STATIC_ROOT`.**

- Evidência: `base.py:150`; o `collectstatic` falha (ensaiado).
- Paliativo: `alias` do nginx para os diretórios `static/` da release (§14).
- Correção: `STATIC_ROOT` e `collectstatic`, idealmente com nomes versionados (`ManifestStaticFilesStorage`).

**I-4 — Não há `EMAIL_TIMEOUT` nem `EMAIL_USE_SSL`.** *O timeout foi resolvido pela 066
(`EMAIL_TIMEOUT`, padrão 20 s); falta o `EMAIL_USE_SSL`.*

- Evidência: `base.py:172-178`.
- Efeito: um SMTP lento prendia o worker até 120 s, e a porta 465 continua inutilizável.
- Correção: o `EMAIL_TIMEOUT` já está no `base.py`; falta o `EMAIL_USE_SSL`.

**I-5 — Sessões e desafios sem limpeza.**

- Evidência: não há `SESSION_*` nem agendamento de `clearsessions`; `limpar_terminais`
  (`identidade/application/desafio.py:268`) só é chamada por teste.
- Paliativo: timer semanal (§21.4).
- Relacionado: a sessão vale 2 semanas, e o "Sair" do portal remove a chave da sessão sem descartar a
  sessão (`portal/identidade.py:123-124`). Correção: `SESSION_COOKIE_AGE` explícito, e `flush()` no
  logout.

**I-6 — HSTS com subdomínios e preload ligados por padrão.**

- Evidência: `production.py:238-240`; o `.env.example` também traz `true`.
- Paliativo: `false` no `app.env` (§13.4).

**I-7 — Lacunas na trilha de auditoria.**

- Não são auditados: a entrada do candidato por código (`identidade/application/desafio.py`) e o
  download do próprio documento (`portal/views.py:1871-1884`).
- Os eventos de credencial são gravados com escopo vazio e ficam invisíveis na consulta
  (`identidade/application/credenciais.py`).
- A exportação de matrículas fica fora de `RegistroAuditoria` (`matriculas/models.py`).

**I-8 — SLO de carga não medido.**

- Evidência: RC-96; `backend/scripts/carga_publica.py` existe e nunca rodou contra ambiente
  implantado.
- Ação: medir em homologação (§4).

**I-9 — `DJANGO_SECRET_KEY` é segredo persistente.**

- Evidência: `inscricoes/domain/autenticidade.py:17,61`.
- Efeito: rotacionar a chave, por rotina ou após incidente, invalida os comprovantes emitidos.
- Tratamento operacional: cofre (§10). Correção de projeto: chave própria para esse HMAC, separada
  da do Django.

**I-10 — O e-mail é o único fator do candidato** (RC-93). SMTP fora do ar significa candidato sem
acesso, sem alternativa. Ação: SMTP institucional com redundância e monitorado.

### MELHORIA

- **M-1 — Não há Content-Security-Policy.** Teste em modo *Report-Only* antes de aplicar: há `<style>`
  inline e htmx.
- **M-2 — Não há `500.html` institucional.** A resposta é o texto genérico do Django.
- **M-3 — Arquivos gravados com `0644`**, o padrão do Django. Mitigado pelo diretório 0700.
  Correção: `FILE_UPLOAD_PERMISSIONS = 0o640`.
- **M-4 — Arquivo órfão possível** se a gravação cair antes do commit (`inscricoes/application/rascunho.py:467-521`).
  Nada reconcilia; o `ps-conferir-documentos` só olha na direção banco → disco.
- **M-5 — Nome de anexo de rascunho em cabeçalho, via f-string sem escape** (`interface/views.py:1351`).
  Só a equipe alcança, e o Django recusa quebra de linha em cabeçalho.
- **M-6 — Não há antivírus nos uploads.** Mitigado por: só PDF por *magic bytes*, servido como
  `application/pdf`, nunca executado no servidor.
- **M-7 — Métricas em memória, por worker.** Zeram no restart.
- **M-8 — `DJANGO_DEBUG` no `.env.example` não é lido por código nenhum.** Engana quem lê.
- **M-9 — Não há tags de release no repositório.** Implanta-se por SHA.
- **M-10 — Não há ferramenta de anonimização** para gerar base de homologação a partir de
  produção.

---

## 27. Possíveis evoluções futuras

Nenhuma é requisito inicial. Cada uma tem um gatilho objetivo.

| Evolução | Quando se justifica |
|---|---|
| Restringir `/gestao/` e `/api/v1/admin/` à rede institucional ou VPN, no nginx | quando B-1 estiver resolvido e a comissão trabalhar da rede institucional |
| PITR, com arquivamento de WAL (pgBackRest ou `archive_command`) | se um RPO de 4 h no período de inscrições for insuficiente |
| PostgreSQL em VM própria | quando a medição de carga (I-8) mostrar disputa de CPU ou memória |
| Segunda VM de aplicação e balanceador | quando indisponibilidade de minutos no último dia de inscrições for inaceitável e medida como risco |
| Armazenamento de objetos para documentos | quando o volume de documentos não couber com folga num volume da VM |
| Antivírus (ClamAV) nos uploads | se a política institucional exigir, ou se os documentos passarem a ser abertos fora do navegador |
| CSP | depois do *Report-Only* sem violações (M-1) |
| Egress restrito no firewall (SMTP, DNS, NTP, apt, PyPI e GitHub no deploy, Caixa, backup) | se a instituição exigir contenção de exfiltração |
| Logs centralizados (SIEM institucional) | se a instituição já tiver um: envie journald e nginx |
| Métricas (Prometheus e afins) | depois de M-7 e com equipe para operar |

---

## 28. Auditoria cruzada

O tutorial foi confrontado com o repositório, pergunta a pergunta.

1. **Todos os serviços necessários foram contemplados?** Sim. PostgreSQL, a aplicação (gunicorn),
   o proxy e o SMTP, externo, são tudo o que o código usa (§2). As tarefas periódicas que o projeto
   pede e não agenda — CEP mensal (runbook), limpeza de sessões e desafios — viraram timers (§21.4).
2. **Algum serviço mencionado não existe?** Não. Não há Redis, fila, Celery nem worker. O nginx, o
   gunicorn, o restic e os timers são **recomendações**, marcadas como tal, e nenhum está no
   repositório.
3. **Todas as variáveis obrigatórias foram configuradas?** Sim. As dez barreiras de
   `production.py` estão cobertas pela §10, e o ensaio subiu com exatamente aquele conjunto. A
   `DJANGO_TRUST_PROXY_SSL_HEADER`, que o código não exige mas a topologia sim, está marcada.
4. **Os diretórios persistentes estão protegidos e em backup?** Documentos (0700, restic), banco
   (`pg_dump`, restic), histórico de implantação (restic). Os segredos estão protegidos (0600) e
   **deliberadamente** fora do backup, no cofre.
5. **Algum dado seria perdido se a VM fosse destruída hoje?** Só o escrito depois do último backup
   (RPO de 24 h, ou de 4 h em período crítico) e os logs locais. E **tudo**, se a
   `DJANGO_SECRET_KEY` ou a senha do restic não estiverem no cofre: a §10 e a §18.3 mandam copiá-las
   no momento em que são geradas.
6. **Alguma porta desnecessária exposta?** Não. 5432 e 8000 só em loopback (verificado na §6.3), e
   o SSH restrito por origem.
7. **Algum processo roda como root sem necessidade?** O master do nginx, por projeto, para abrir as
   portas 80 e 443. Os scripts `ps-*` rodam como root só para ler os `.env` 0600, e trocam de
   usuário (`setpriv`) antes de executar código da aplicação. A aplicação nunca roda como root.
8. **Algum segredo pode parar no Git ou no histórico?** O `.gitignore` e o `.dockerignore` excluem
   `.env`, e os segredos nunca estão no diretório do código. A geração usa aspas simples, para que
   nem o histórico do shell nem o `auth.log` do `sudo` vejam o valor (§10.2). As senhas dos papéis
   não aparecem em linha de comando: o `ps-migrar` as passa pelo ambiente.
9. **Documentos dos candidatos podem ser acessados sem autorização?** Pelo servidor web, não: não
   há `location` nem URL, e o `www-data` não lê o diretório. Pela aplicação, as regras são as da
   §15.2. Pela VM, só root e o usuário da aplicação.
10. **O backup cobre banco e arquivos?** Sim, na mesma execução e na ordem que garante um
    superconjunto (§18.1), com conferência por hash na restauração (§19.4).
11. **O restore reconstrói o ambiente?** Sim, desde que exista o cofre (`DJANGO_SECRET_KEY`, restic,
    SMTP) e o repositório (o código pelo SHA). A configuração sem segredo volta do restic, e o
    certificado se reemite.
12. **A atualização tem rollback?** Sim: de código, pelo symlink (§23.1); de banco, pelo dump
    `pre-deploy` com a janela fechada (§23.2). Depois de reaberta a janela, a regra é explícita, e
    não há reversão de migration (§23.3).
13. **Algum ponto obriga a adivinhar o próximo passo?** Três dependem de decisão externa, e estão
    nomeados:
    - a autenticação institucional (B-1): sem ela, os smoke tests da gestão não têm como rodar;
    - a política de retenção (B-2);
    - as escolhas do domínio (Let's Encrypt ou certificado institucional, §13.1).

    O resto tem comando e resultado esperado.

**O que não pôde ser ensaiado**, por falta de uma VM Ubuntu nesta sessão: nginx, certbot, ufw,
systemd, timesyncd, restic e os scripts `ps-*` inteiros. Os oito scripts `ps-*` foram extraídos deste
documento e passaram em `bash -n` e no `shellcheck -S warning` sem aviso. O primeiro deploy numa VM real deve seguir este documento **com os "Como verificar"**, e
corrigi-lo onde divergir.

---

## Apêndice A — Deploy Cheat Sheet

Para quem já leu o tutorial uma vez. **[admin]**, sempre com `sudo`.

### Primeira implantação

```bash
# VM
sudo apt update && sudo apt full-upgrade -y
sudo timedatectl set-timezone America/Sao_Paulo              # + NTP (§5.2) → timedatectl: synchronized yes
sudo locale-gen pt_BR.UTF-8
# Usuário, diretórios, SSH, firewall: §6.1, §6.2 (sshd -t; teste numa 2ª sessão!), §6.3
sudo ufw status verbose
# Pacotes
sudo apt install -y git curl ca-certificates nginx certbot restic dnsutils && sudo rm -f /etc/nginx/sites-enabled/default
sudo apt install -y postgresql-common && sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh && sudo apt install -y postgresql-18
# uv (checksum) + Python: §7.3
sudo env UV_PYTHON_INSTALL_DIR=/opt/processoseletivo/python uv python install 3.13
# Código: deploy key + mirror (§8.2); scripts ps-* (§8.3)
sudo git clone --mirror git@github-processoseletivo:<REPOSITORIO>.git /opt/processoseletivo/repo.git
R=$(sudo ps-construir <SHA> | tail -1)
# Banco: conf.d + pg_hba (§9.1)
sudo -u postgres createdb --encoding=UTF8 --locale=pt_BR.UTF-8 --template=template0 processo_seletivo
sudo -u postgres psql -c 'REVOKE CONNECT ON DATABASE processo_seletivo FROM PUBLIC;'
# Segredos: app.env + migracao.env (§10.2) → COFRE
sudo ps-manage --release "$R" check --deploy                 # só W005 e W021
sudo ps-migrar "$R"                                          # 0 de 34 … 34 de 34
# Serviço: gunicorn.conf.py + unit (§12)
sudo systemctl daemon-reload && sudo systemctl enable processoseletivo && sudo ps-ativar "$R"
# TLS: nginx provisório (§13.2) → certbot (§13.3) → certbot renew --dry-run
# Proxy completo (§14) → sudo nginx -t && sudo systemctl reload nginx
sudo ps-manage sendtestemail <CAIXA_DE_TESTE>
# Backup (§18) → sudo systemctl start ps-backup.service → restic snapshots
# Monitoramento e limpeza (§21) → systemctl list-timers 'ps-*'
# Smoke test (§17.1) · restauração testada em VM descartável (§19) · GO-LIVE (Apêndice B)
```

### Atualização

```bash
cat /opt/processoseletivo/current/REVISION && cat /var/backups/processoseletivo/ultimo-sucesso
R=$(sudo ps-construir <SHA> | tail -1)
sudo ps-manage --release "$R" check --deploy
sudo ps-manage --release "$R" --migracao migrate --plan
# SEM migrations:
sudo ps-ativar "$R"
# COM migrations:
sudo touch /etc/nginx/processoseletivo.manutencao
sudo systemctl stop processoseletivo
sudo sh -c 'umask 077; runuser -u postgres -- pg_dump -Fc processo_seletivo > /var/backups/processoseletivo/banco/pre-deploy-$(date +%Y%m%d-%H%M%S).dump'
sudo ps-migrar "$R"
sudo ps-ativar "$R"
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: <DOMINIO>' -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/selecoes/   # 200
sudo rm /etc/nginx/processoseletivo.manutencao
# depois: §17.1 · tail -1 /var/lib/processoseletivo/implantacoes.log
```

### Rollback

```bash
sudo ps-ativar /opt/processoseletivo/releases/<anterior>                 # só código
# código + banco, com a janela ainda fechada: §23.2 (renomear banco → createdb → provisionar → pg_restore pre-deploy → provisionar → ativar)
```

### Diagnóstico rápido

```bash
systemctl status processoseletivo nginx postgresql@18-main --no-pager
journalctl -u processoseletivo -n 100 --no-pager
curl -s -H 'Host: <DOMINIO>' -H 'X-Forwarded-Proto: https' http://127.0.0.1:8000/readiness
sudo ps-verificar
tail -50 /var/log/nginx/processoseletivo.error.log
df -h; free -m
```

---

## Apêndice B — GO-LIVE — PROCESSO SELETIVO

```
GO-LIVE — PROCESSO SELETIVO (Cefor/Ifes)              Data: ____/____/______
Responsável: ______________________   Versão (SHA): ____________________________

PRECONDIÇÕES DE PROJETO (sem elas, NÃO há go-live)
[ ] B-1 resolvido: autenticação institucional na gestão, e API_AUTHENTICATION_CLASSES real
[ ] B-2 resolvido: política de retenção e descarte aprovada pelo encarregado de dados
[ ] Carga medida em homologação com carga_publica.py (p95 ≤ 2 s) — resultado: ________

INFRAESTRUTURA
[ ] DNS de <DOMINIO> aponta para <IP_DO_SERVIDOR> (A/AAAA)
[ ] ufw: deny por padrão; 22 só da rede administrativa; 80 e 443 abertas
[ ] nmap externo: só 80 e 443 (e 22 da rede administrativa)
[ ] SSH: root desligado, senha desligada, AllowGroups acesso-ssh, testado em 2ª sessão
[ ] Relógio: America/Sao_Paulo, NTP sincronizado
[ ] Atualizações de segurança automáticas ativas; nenhum reboot pendente
[ ] Console do hipervisor acessível à equipe

APLICAÇÃO
[ ] Versão registrada: /opt/processoseletivo/current/REVISION = SHA acima, na main, CI verde
[ ] implantacoes.log com a linha "ativada"
[ ] check --deploy sem ERRORS (só W005/W021, se HSTS conservador)
[ ] DEBUG desligado: /nao-existe sem "URLconf"
[ ] Settings de produção: seletor, identidade demo e sorteio demo ausentes
[ ] Migrations aplicadas: migrate --check = 0; readiness = ready
[ ] Provisionamento: "N de N tabelas append-only" na 2ª passada
[ ] gunicorn como processoseletivo, em 127.0.0.1:8000; systemd-analyze security revisado
[ ] Estáticos: /static/interface/htmx.min.js = 200
[ ] Base de CEP carregada (se usada): situacao_dos_ceps = 0

SEGURANÇA
[ ] HTTPS válido; http → 301 https; SSL Labs A
[ ] certbot renew --dry-run OK (ou lembrete do certificado institucional agendado)
[ ] HSTS decidido (subdomínios/preload) e registrado
[ ] PostgreSQL só em localhost; pg_hba com 3 regras; papéis sem superusuário
[ ] Runtime sem DELETE em auditoria_registroauditoria
[ ] /readiness e /metrics = 403 de fora
[ ] Documentos: diretório 0700; www-data sem leitura; nenhuma URL pública
[ ] Segredos 0600 root, fora do Git, fora do histórico
[ ] DJANGO_SECRET_KEY, senha do restic e SMTP NO COFRE (conferido por 2ª pessoa)
[ ] pip-audit sem pendência

DADOS
[ ] Backup completo realizado hoje (ultimo-sucesso) e visível em restic snapshots
[ ] Cópia fora da VM confirmada (e append-only, se disponível)
[ ] Restauração testada em VM descartável — data: ______ RTO: ______ min
[ ] ps-conferir-documentos sem AUSENTE/DIVERGENTE na restauração
[ ] Frequência de 4 h agendada para o período de inscrições

FUNCIONAL
[ ] Vitrine /selecoes/ abre, com estilos e scripts
[ ] Código de acesso chega em < 1 min (fora do spam) e o login funciona
[ ] Área do candidato abre; "Sair" encerra
[ ] sendtestemail recebido
[ ] (após B-1) Em homologação: Processo → Edital → publicação → inscrição com upload
    → download pela comissão (auditado) → avaliação → resultado → PDF
[ ] (após B-1) Avaliador sem Atribuição recebe 404 no documento
[ ] 502 mostra a página "indisponível"; 503 de manutenção funciona

OPERAÇÃO
[ ] Logs acessíveis: journalctl -u processoseletivo; nginx; postgresql
[ ] Retenção de logs definida com o encarregado: ______ dias
[ ] Monitoramento externo de /health e do certificado, alertando a: ____________
[ ] ps-verificar ativo; alerta de teste recebido
[ ] Timers ativos: ps-backup, ps-verificar, ps-limpeza, (ps-ceps), certbot
[ ] Procedimento de atualização e de rollback lido pela equipe (§22, §23)
[ ] Runbook (§24) acessível fora da VM
[ ] Canal PORTAL_ATENDIMENTO atendido por alguém
[ ] Calendário de congelamento: sem deploy no último dia de inscrições nem na publicação

Assinaturas:  Infraestrutura ______________   Sistema ______________   Encarregado de dados ______________
```
