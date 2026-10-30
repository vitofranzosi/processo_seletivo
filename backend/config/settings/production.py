"""Configuração de produção que se recusa a subir insegura (FR-016 a FR-018 da 003).

A segurança de um sistema que publica atos normativos não pode depender de alguém lembrar de
exportar uma variável. Este módulo transforma cada pressuposto em precondição de inicialização:
falta de segredo, hosts abertos, HTTPS desligado, banco sem senha, seletor de identidade ligado
ou adaptador provisório de autenticação impedem o processo de iniciar, com mensagem que nomeia
a variável a corrigir.

O adaptador `InstitutionalBearerAuthentication` aceita `subject|escopo|permissões` sem assinatura:
qualquer cliente declara a própria identidade e as próprias permissões. Enquanto a integração com
o diretório institucional não existir, esta barreira é o que impede implantar sem fronteira de
segurança alguma.

Sobre o alcance dessa barreira, para que ninguém a leia como mais do que é: ela **recusa o que
sabe ser inseguro** — o módulo de autenticação de desenvolvimento e os esquemas do DRF que não
carregam identidade institucional — e exige que a classe escolhida exista e seja importável. Ela
**não prova** que a classe declarada fale com o diretório do Ifes; nenhuma configuração pode
provar isso. Quem implanta continua respondendo pela escolha; o que o módulo garante é que a
escolha seja explícita, exista, e não seja um dos caminhos conhecidamente inseguros.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .base import *  # noqa: F403
from .base import (
    ARQUIVOS_CANDIDATOS_RAIZ,
    ASSISTENTE_NA_PAGINA_DO_EDITAL,
    ASSISTENTE_PILOTO,
    ASSISTENTE_SERVICO,
    ASSISTENTE_TEMPO_LIMITE_SEGUNDOS,
    BASE_DIR,
    DATABASES,
    DEFAULT_FROM_EMAIL,
    EMAIL_BACKEND,
    EMAIL_HOST,
    INTERFACE_SELETOR_IDENTIDADE,
    PORTAL_IDENTIDADE_DEMO,
    REST_FRAMEWORK,
    SECRET_KEY,
    SORTEIO_FONTE_DE_DEMONSTRACAO,
)

# Módulo inteiro, não uma classe: qualquer adaptador de desenvolvimento que nasça ao lado do
# atual herdaria a mesma recusa sem precisar lembrar de atualizar esta lista.
MODULO_DE_DESENVOLVIMENTO = "processo_seletivo.seguranca.api.authentication."
# Esquemas do DRF que autenticam, mas não contra o diretório institucional: senha no cabeçalho,
# sessão do próprio Django e token emitido por esta aplicação não são identidade do Ifes.
ESQUEMAS_NAO_INSTITUCIONAIS = frozenset(
    {
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    }
)
SEGREDOS_INADMISSIVEIS = frozenset({"", "unsafe-development-key", "change-me"})

DEBUG = False
AMBIENTE_DE_PRODUCAO = True


def _exigir(condicao, variavel, motivo):
    if not condicao:
        raise ImproperlyConfigured(f"{variavel}: {motivo}")


def _booleano(nome, padrao="true"):
    return os.getenv(nome, padrao).lower() == "true"


# Os mesmos limites que `check --deploy` fiscaliza (security.W009), aplicados antes de subir:
# descobrir a chave fraca por aviso de comando é descobrir tarde demais.
_exigir(
    SECRET_KEY not in SEGREDOS_INADMISSIVEIS
    and len(SECRET_KEY) >= 50
    and len(set(SECRET_KEY)) >= 5
    and not SECRET_KEY.startswith("django-insecure-"),
    "DJANGO_SECRET_KEY",
    "é obrigatória em produção, com ao menos 50 caracteres e 5 caracteres distintos, e não pode "
    "ser o valor de desenvolvimento nem uma chave gerada com o prefixo 'django-insecure-'.",
)

ALLOWED_HOSTS = [v.strip() for v in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if v.strip()]
_exigir(
    ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS,
    "DJANGO_ALLOWED_HOSTS",
    "deve listar explicitamente os hosts institucionais; vazio ou '*' não é admissível.",
)

_exigir(
    not INTERFACE_SELETOR_IDENTIDADE,
    "INTERFACE_SELETOR_IDENTIDADE",
    "o seletor de identidade permite escolher quem se é e não pode existir em produção.",
)

# A mesma barreira, para o outro eixo de identidade (FR-024 da 009). O provedor de demonstração
# do portal deixa qualquer pessoa dizer quem é; em produção, uma inscrição atribuída assim não
# vale nada — e não seria descoberta por quem a recebe.
#
# **A 010 apagou o caminho que esta guarda vigiava, e mesmo assim ela fica** (FR-048). A
# identificação por declaração não existe mais: quem entra prova o controle de um endereço. A
# variável continua definida e continua recusando o boot como armadilha — se o caminho voltar,
# por descuido ou por atalho de alguém com pressa, produção não sobe.
_exigir(
    not PORTAL_IDENTIDADE_DEMO,
    "PORTAL_IDENTIDADE_DEMO",
    "o provedor de identidade de demonstração deixa qualquer pessoa declarar-se candidato e não "
    "pode existir em produção.",
)

# A terceira barreira de demonstração (046, `FR-758`). A fonte de demonstração do sorteio tem
# semente fixa: um Edital que a declarasse publicaria um sorteio cujo resultado se conhece antes
# da extração. Em produção ela não pertence ao vocabulário de fontes, e esta guarda impede que uma
# variável de ambiente a traga de volta.
_exigir(
    not SORTEIO_FONTE_DE_DEMONSTRACAO,
    "SORTEIO_FONTE_DE_DEMONSTRACAO",
    "a fonte de demonstração do sorteio tem semente fixa, e um sorteio publicado com ela seria "
    "previsível; ela não pode existir em produção.",
)

# Onde os documentos do candidato ficam (FR-051 da 009). Três exigências, e cada uma cobre um
# jeito conhecido de vazar arquivo: declarada, porque o padrão vazio significa "esta máquina não
# recebe arquivo" e em produção ela recebe; absoluta, porque relativa depende do diretório de
# onde o processo subiu; e fora da árvore do código, porque é ali que mora o que o servidor web
# publica sem perguntar a ninguém.
_raiz_de_arquivos = Path(ARQUIVOS_CANDIDATOS_RAIZ) if ARQUIVOS_CANDIDATOS_RAIZ else None
_exigir(
    _raiz_de_arquivos is not None
    and _raiz_de_arquivos.is_absolute()
    and not _raiz_de_arquivos.is_relative_to(Path(BASE_DIR)),
    "ARQUIVOS_CANDIDATOS_RAIZ",
    "deve declarar um diretório absoluto para os documentos do candidato, fora da árvore do "
    "código; documento de candidato não pode ser servido diretamente pelo servidor web.",
)

# O canal de e-mail (FR-081 da 010). Autenticar sem senha depende inteiramente de a mensagem
# chegar: com um mecanismo que não entrega, o código de acesso vai para o log do servidor e
# qualquer pessoa com acesso a ele entra como qualquer candidato. É pior do que não ter
# autenticação, porque parece ter.
#
# O alcance desta barreira é o mesmo que este módulo já declara sobre a autenticação
# institucional, e a redação segue a mesma honestidade: ela **recusa o que sabe não entregar**, e
# **não prova** que um servidor configurado entregue mensagem alguma. Nenhuma verificação de
# inicialização pode provar isso.
MECANISMOS_QUE_NAO_ENTREGAM = frozenset(
    {
        "django.core.mail.backends.console.EmailBackend",
        "django.core.mail.backends.dummy.EmailBackend",
        "django.core.mail.backends.locmem.EmailBackend",
        "django.core.mail.backends.filebased.EmailBackend",
    }
)
_exigir(
    EMAIL_BACKEND not in MECANISMOS_QUE_NAO_ENTREGAM,
    "DJANGO_EMAIL_BACKEND",
    "o mecanismo de envio configurado não entrega mensagem alguma; em produção o código de "
    "acesso do candidato iria para o log do servidor, e autenticação que não sai da máquina não "
    "é autenticação.",
)
_exigir(
    bool(DEFAULT_FROM_EMAIL.strip()),
    "DEFAULT_FROM_EMAIL",
    "sem remetente declarado a mensagem com o código de acesso não é enviada, e o candidato "
    "fica sem caminho para entrar.",
)
# **O backend SMTP sem servidor subia**, e só o primeiro envio acusava, com um "please run
# connect() first" que não diz qual variável falta (073, `FR-1660`). A regra vale só para ele: é o
# único backend que lê `EMAIL_HOST`, e um de terceiros, que o projeto não tem, poderia não precisar.
_exigir(
    EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend" or bool(EMAIL_HOST.strip()),
    "EMAIL_HOST",
    "com o envio por SMTP, declare o servidor de correio que o setor de correio forneceu; vazio, "
    "o serviço sobe e o primeiro código de acesso não sai.",
)

# Há proxy à frente? (FR-030 da 010) A pergunta precisa ser **respondida**, e não assumida.
#
# O limite por origem existe para conter quem varre endereços. Atrás de um proxy, `REMOTE_ADDR` é
# o mesmo para todo mundo — e sem declarar isso, o teto de trinta pedidos por hora deixa de valer
# por origem e passa a valer para a instituição inteira. No último dia do prazo, isso recusa
# candidato legítimo em bloco, com a mesma mensagem neutra de sempre, e ninguém entende por quê.
#
# Não há padrão seguro para adivinhar: confiar no cabeçalho sem proxy torna o limite contornável
# com um valor aleatório por requisição; não confiar com proxy transforma o limite em teto global.
# Quem implanta sabe qual é a topologia, e é essa a única resposta que serve.
_atras_de_proxy = os.getenv("PORTAL_ATRAS_DE_PROXY", "").strip().lower()
_exigir(
    _atras_de_proxy in {"true", "false"},
    "PORTAL_ATRAS_DE_PROXY",
    "declare 'true' quando houver proxy ou balanceador à frente da aplicação, e 'false' quando ela "
    "receber a conexão diretamente. Sem a declaração, o limite de solicitações por origem ou é "
    "contornável por cabeçalho forjado, ou recusa candidatos legítimos em bloco — e qual dos dois "
    "depende da topologia, que só quem implanta conhece.",
)

# Sem canal de atendimento declarado, duas telas do candidato viram beco sem saída: o CPF congelado
# depois da primeira inscrição enviada só se corrige por ato institucional, e a participação
# anterior que a pessoa não conseguiu confirmar só se recupera por atendimento. Mandar "procure o
# atendimento" sem dizer qual é abandonar quem já está travado.
PORTAL_ATENDIMENTO = os.getenv("PORTAL_ATENDIMENTO", "").strip()
_exigir(
    bool(PORTAL_ATENDIMENTO),
    "PORTAL_ATENDIMENTO",
    "declare o canal de atendimento ao candidato — um e-mail, um telefone ou o endereço de uma "
    "página. Duas telas mandam procurá-lo, e são os dois pontos em que o sistema não resolve "
    "sozinho: CPF congelado e participação anterior não confirmada.",
)

# O piloto do assistente (071) nasce na máquina da equipe, e não aqui. Ligado em produção, só com
# o serviço local: a pergunta não sai da rede institucional (`FR-1503`). E com o tempo-limite
# abaixo do gunicorn do guia de implantação (§12.1), que não é versionado e não se lê daqui.
_exigir(
    not ASSISTENTE_PILOTO or ASSISTENTE_SERVICO == "ollama",
    "ASSISTENTE_SERVICO",
    "o piloto do assistente, em produção, só fala com o serviço local; o OpenRouter é para a "
    "avaliação na máquina da equipe, com perguntas sintéticas.",
)
_exigir(
    not ASSISTENTE_PILOTO or ASSISTENTE_TEMPO_LIMITE_SEGUNDOS <= 110,
    "ASSISTENTE_TEMPO_LIMITE_SEGUNDOS",
    "o tempo-limite da inferência precisa ficar abaixo dos 120 s do servidor de aplicação, para "
    "que a pessoa receba 'tempo esgotado', e não um erro do servidor.",
)

# O painel na página pública (074) deixa qualquer visitante conversar com o modelo, sem
# autenticação nem os requisitos da abertura ao público, que são da implantação (`FR-1684`). Como o
# seletor de identidade, ele existe só na máquina de desenvolvimento.
_exigir(
    not ASSISTENTE_NA_PAGINA_DO_EDITAL,
    "ASSISTENTE_NA_PAGINA_DO_EDITAL",
    "o assistente na página pública da seleção é só do desenvolvimento local; a abertura ao "
    "público depende dos requisitos da implantação.",
)

# A entrada institucional da gestão (106, `D-009`). **Sem provedor, a gestão continua bloqueada**:
# a página de acesso responde 503 e não oferece nada, e nenhum caminho cai para a demonstração
# (`FR-3027`). Com provedor, três recusas, cada uma nomeando a variável (`FR-3026`):
#
# - o código de teste não é implantável: o provedor simulado mora em `tests.` e responde a quem a
#   suíte mandar, sem rede e sem provedor nenhum por trás;
# - a classe que se declara de teste (`apenas_para_testes`) também não, more onde morar;
# - nome que não se importa falharia só na primeira entrada, com 500.
#
# O alcance é o mesmo que este módulo declara para a API: recusa o que sabe ser inseguro, e **não
# prova** que a classe declarada fale com o provedor do Ifes. O adaptador não deve importar modelos
# no topo do módulo, porque é importado aqui, antes de os apps existirem.
GESTAO_PROVEDOR_INSTITUCIONAL = os.getenv("GESTAO_PROVEDOR_INSTITUCIONAL", "").strip()
if GESTAO_PROVEDOR_INSTITUCIONAL:
    _exigir(
        not GESTAO_PROVEDOR_INSTITUCIONAL.startswith("tests."),
        "GESTAO_PROVEDOR_INSTITUCIONAL",
        "o provedor declarado é do código de teste: ele autentica quem a suíte mandar, sem "
        "provedor nenhum por trás, e não pode existir em produção.",
    )
    try:
        _provedor = import_string(GESTAO_PROVEDOR_INSTITUCIONAL)
    except ImportError as _erro:
        raise ImproperlyConfigured(
            f"GESTAO_PROVEDOR_INSTITUCIONAL: {GESTAO_PROVEDOR_INSTITUCIONAL} não pôde ser "
            f"importado ({_erro})."
        ) from _erro
    _exigir(
        not getattr(_provedor, "apenas_para_testes", False),
        "GESTAO_PROVEDOR_INSTITUCIONAL",
        "o provedor declarado se declara de teste, e não autentica contra o provedor "
        "institucional.",
    )
    # Os prazos da sessão são decisão do usuário, e não padrão do código (107, `D-010`): com
    # provedor, produção não sobe sem os dois declarados, e a proposta da base não vira valor de
    # produção por omissão.
    for _prazo in ("GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS", "GESTAO_SESSAO_INATIVIDADE_MINUTOS"):
        _valor = os.getenv(_prazo, "").strip()
        _exigir(
            _valor.isdigit() and int(_valor) > 0,
            _prazo,
            "com a entrada institucional, o prazo da sessão precisa ser declarado, em minutos "
            "inteiros e positivos: 8 horas e 30 minutos são proposta, e não valor aprovado.",
        )

# O *backend* de autenticação é só o institucional (`D-008`). A base já o declara assim; a guarda é
# para quem acrescentar o `ModelBackend` — usuário e senha nesta aplicação — ou o
# `RemoteUserBackend`, que confia num cabeçalho que o cliente pode enviar.
AUTHENTICATION_BACKENDS = ["processo_seletivo.seguranca.autenticacao.BackendInstitucional"]

# A autenticação institucional é incremento próprio; até lá, produção não sobe.
API_AUTHENTICATION_CLASSES = [
    v.strip() for v in os.getenv("API_AUTHENTICATION_CLASSES", "").split(",") if v.strip()
]
_exigir(
    bool(API_AUTHENTICATION_CLASSES),
    "API_AUTHENTICATION_CLASSES",
    "deve declarar explicitamente a autenticação institucional; sem ela não há fronteira de "
    "segurança e o backend autoriza contra permissões que o próprio cliente declara.",
)
_recusadas = [
    classe
    for classe in API_AUTHENTICATION_CLASSES
    if classe.startswith(MODULO_DE_DESENVOLVIMENTO) or classe in ESQUEMAS_NAO_INSTITUCIONAIS
]
_exigir(
    not _recusadas,
    "API_AUTHENTICATION_CLASSES",
    f"{', '.join(_recusadas)} não autentica contra o diretório institucional. O adaptador de "
    "desenvolvimento aceita identidade e permissões declaradas pelo próprio cliente; os esquemas "
    "do DRF autenticam contra esta aplicação, não contra o Ifes.",
)
for _classe in API_AUTHENTICATION_CLASSES:
    # Nome inexistente falharia só na primeira requisição autenticada, em produção, com 500.
    try:
        import_string(_classe)
    except ImportError as _erro:
        raise ImproperlyConfigured(
            f"API_AUTHENTICATION_CLASSES: {_classe} não pôde ser importada ({_erro})."
        ) from _erro
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_AUTHENTICATION_CLASSES": API_AUTHENTICATION_CLASSES}

_exigir(
    DATABASES["default"]["PASSWORD"],
    "DB_RUNTIME_PASSWORD",
    "o usuário de runtime do banco precisa de senha em produção.",
)

# Transporte: o SecurityMiddleware já está na cadeia; aqui só se liga o que ele fiscaliza.
SECURE_SSL_REDIRECT = _booleano("DJANGO_SECURE_SSL_REDIRECT")
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _booleano("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = _booleano("DJANGO_SECURE_HSTS_PRELOAD")
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"

_exigir(
    SECURE_SSL_REDIRECT and SECURE_HSTS_SECONDS >= 31536000,
    "DJANGO_SECURE_SSL_REDIRECT/DJANGO_SECURE_HSTS_SECONDS",
    "produção exige HTTPS obrigatório e HSTS de ao menos um ano; desligá-los é decisão "
    "explícita de quem opera, não padrão.",
)

# Atrás de proxy institucional, o cabeçalho é a única evidência de que a origem foi HTTPS.
if os.getenv("DJANGO_TRUST_PROXY_SSL_HEADER", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
