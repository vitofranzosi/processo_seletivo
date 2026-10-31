import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key")
DEBUG = False
# A marca de que esta é a configuração de produção, e só `production.py` a liga. Quem grava dado
# fictício a consulta antes de escrever (`seed_demo`): publicação é ato imutável, e um Edital de
# demonstração publicado em produção não sai mais de lá. A marca, e não o nome do módulo de
# settings, porque o nome é escolha de quem implanta e pode variar; a marca vem junto com as
# demais barreiras de `production.py` (auditoria de administração institucional, 30/10).
AMBIENTE_DE_PRODUCAO = False
ALLOWED_HOSTS = [v for v in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",") if v]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
USE_TZ = True
TIME_ZONE = "America/Sao_Paulo"
# A interface é institucional brasileira e escreve tudo em português — menos as datas, que o
# Django formatava em `en-us` por falta desta linha: "Sept. 5, 2026, 11:30 p.m." ao lado de
# "05/09/2026 23:04" na mesma tela (E2E15-009). O idioma governa também o separador decimal, e é
# por isso que ele entra aqui e não num filtro de template: `92,50` e `92.50` na mesma página
# seriam a mesma inconsistência escrita com outro caractere.
LANGUAGE_CODE = "pt-br"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "processo_seletivo.processos",
    "processo_seletivo.editais",
    "processo_seletivo.publicacoes",
    "processo_seletivo.seguranca",
    "processo_seletivo.auditoria",
    "processo_seletivo.interface",
    # A jornada do candidato (009): o domínio em `inscricoes`, o canal do ator externo em
    # `portal`. São dois apps porque são duas coisas — e `portal` não é uma tela a mais de
    # `interface`: a autenticação, a sessão, a base visual e o alvo de dispositivo são outros.
    "processo_seletivo.inscricoes",
    "processo_seletivo.portal",
    # A identidade do candidato (010): domínio próprio, pela mesma linha que separa `inscricoes`
    # de `portal`. Os modelos e a reconciliação com o legado moram aqui; o `portal` continua
    # sendo o canal, e não ganha `models.py` — pôr a identidade lá o transformaria em canal e
    # domínio ao mesmo tempo, que é o que a separação anterior evitou.
    "processo_seletivo.identidade",
    # A organização do trabalho (011): quem integra a comissão do Processo e quem atua em cada
    # Etapa. App próprio porque é autorização operacional sobre Processo e Edital, e não o ciclo
    # de vida normativo deles — as telas continuam em `interface`, que já é o canal dos dois atores.
    "processo_seletivo.comissoes",
    # A execução do trabalho (012): a atribuição de inscrições a quem já está alocado, a avaliação
    # que ela autoriza e o impedimento que a bloqueia. App separado de `comissoes` pela mesma razão
    # que separa organizar de executar: a 011 responde quem pode trabalhar em cada Etapa, a 012
    # responde quais inscrições cabem a cada um — e misturá-las entregaria a confusão à 013.
    "processo_seletivo.avaliacoes",
    # A consequência do trabalho (013): o Resultado da Etapa, que transforma a Avaliação concluída
    # em `HABILITADA` ou `ELIMINADA`. App próprio, e não um modelo dentro de `avaliacoes`, porque o
    # Resultado não é uma avaliação: é a consequência dela, com ciclo de vida, imutabilidade e
    # autoria próprios — e é o agregado sobre o qual a classificação e a publicação serão
    # construídas. As duas direções de dependência são reais e opostas, e o ciclo se quebra com
    # import local, como `reabrir` já faz com `comando_de_comissao` (013, T-001).
    "processo_seletivo.resultados",
    # A ordem entre participantes (015): o ato de ordenação e suas posições. App próprio pela mesma
    # razão que separou `resultados` de `avaliacoes` — ordenar não é resultado de Etapa: o ato tem
    # universo declarado, autoridade, sucessão e imutabilidade próprios, e é sobre ele que a 016
    # crescerá. O Resultado é lido e nunca escrito daqui (015, T-010).
    "processo_seletivo.classificacao",
    # A divulgação do que foi ordenado (017): o ato de publicar um resultado, a situação congelada
    # de cada participante e o documento oficial. App próprio pela mesma razão que separou
    # `classificacao` de `resultados` — publicar não é ordenar: o ato tem autoridade signatária,
    # instante, sucessão e conteúdo congelado próprios. A direção da dependência é única:
    # `divulgacao` lê `classificacao` e `publicacoes`, e nenhum dos dois passa a conhecê-la
    # (017, T-001).
    "processo_seletivo.divulgacao",
    # A contestação do que foi divulgado (018): a peça recursal, o juízo de admissibilidade e a
    # decisão que julga o mérito. App próprio pela mesma razão que separou `divulgacao` de
    # `classificacao` — julgar não é publicar: a autoridade é outra, o impedimento bloqueia, e a
    # decisão é fonte jurídica de um Resultado sucessor. **A dependência é de mão dupla**, e é a
    # única da linhagem: `recursos` lê `resultados` e `divulgacao`, e `resultados` cita
    # `DecisaoRecurso` — porque só assim "todo sucessor cita a decisão" é constraint, e não
    # promessa. O ciclo se quebra por referência tardia, como o Django resolve (018, T-001).
    "processo_seletivo.recursos",
    # O sorteio como ato auditável (021): a relação de habilitados congelada, a ocorrência da fonte
    # externa e o `AtoDeOrdenacao` constituído por sorteio. App próprio porque o vocabulário e o
    # ciclo de vida existem **antes** da ordem — a relação é publicada dias antes, e é ela o
    # compromisso do universo. A direção da dependência é única: `sorteios` lê `classificacao`,
    # `publicacoes` e `inscricoes`, e nenhum deles passa a conhecê-lo (021, R-002).
    "processo_seletivo.sorteios",
    # A ocupação de vaga da `016`: quantas vagas cada lista de concorrência tem publicadas, quantas
    # estão ocupadas e quantas faltam, mais o movimento que reverte cota para a ampla. App próprio
    # pela mesma razão do `sorteios`, e a direção da dependência é única: `ocupacao` lê
    # `classificacao`, `publicacoes` e `resultados`, e **nenhum deles passa a conhecê-lo**. Fosse
    # `classificacao` a ler a apuração para descobrir a causa da faixa seguinte, a `014` deixaria de
    # ser compreensível sozinha — contra a fronteira que a decisão de 11/09/2026 fixou (016, R-002).
    "processo_seletivo.ocupacao",
    # O ato que alcança a pessoa (019): convocar quem a ordem indica para a vaga que a `016` apurou
    # como faltante, registrar o que ela respondeu e chamar o suplente quando a vaga vaga. App
    # próprio, e não um módulo dentro de `ocupacao`, pela mesma razão que fez a `016` não morar em
    # `classificacao`: o nome do módulo ficaria falso — `ocupacao` **conta**, e convocar é alcançar
    # pessoa. A direção da dependência é única: `convocacao` lê `ocupacao`, `classificacao` e
    # `resultados`, e **nenhum deles passa a conhecê-la**. A exclusão e a inclusão que os desfechos
    # produzem chegam por uma porta que mora em `ocupacao`, com o ato de origem como UUID opaco —
    # uma FK na direção contrária inverteria a dependência no grafo de migrations, que é onde ela
    # é irreversível (019, R-003).
    "processo_seletivo.convocacao",
    # O Requerimento de Matrícula (029): o que a pessoa declara para que a candidatura vire dado
    # apto à matrícula, e a base de referência de CEP que ajuda a preenchê-lo. App próprio pela
    # razão que fez a `016` não morar em `classificacao` e a `019` não morar em `ocupacao` — o ato
    # é outro. A Inscrição é o ato de **disputar** a vaga, e por isso ela congela na submissão; o
    # Requerimento é o ato de **habilitar o vínculo** que a disputa deu, praticado às vezes meses
    # depois. Guardá-lo dentro de `inscricoes` diria, na estrutura, que dado de matrícula é dado de
    # seleção — que é a confusão que esta feature existe para desfazer.
    #
    # A direção da dependência: `requerimentos` lê `inscricoes`, `convocacao` e `publicacoes`, e
    # nenhum deles passa a conhecê-lo. `inscricoes` consulta **só** o predicado que não alcança
    # `convocacao` (`domain/disponibilidade.py::exigido_na_inscricao`), para que o ciclo
    # `inscricoes → requerimentos → convocacao → inscricoes` não se feche.
    "processo_seletivo.requerimentos",
    # A unidade que pratica o ato e quem pode responder por ele (060). App próprio porque quatro
    # apps a leem — a criação de Processo, as duas publicações e o comprovante — e nenhum é dono
    # dela; `seguranca` é dono do escopo, mas não guarda cadastro, e pôr as tabelas em `publicacoes`
    # faria `processos` depender de quem publica. A Unidade materializa o `institution_scope`, e
    # nada aponta para ela por chave estrangeira (060, D-001).
    "processo_seletivo.unidades",
    # A exportação de matrículas (031): o que o candidato declarou no Requerimento, no formato que
    # o Registro Acadêmico importa. App próprio, e é o **último** da lista por uma razão que vale
    # como teste: ele é a ponta da leitura, e **ninguém o importa**. A `029` custou uma sessão a um
    # ciclo de importação (`inscricoes → requerimentos → convocacao → inscricoes`); um app que
    # nenhum outro conhece não entra em ciclo nenhum, e `tests/test_matriculas_e_ponta.py` prende
    # essa propriedade. Se algum dia outro app o importar, a feature deixou de ser ponta.
    "processo_seletivo.matriculas",
    "processo_seletivo.avisos",
    # A fonte de consulta do assistente de dúvidas (070): responde a perguntas sugeridas sobre o
    # Edital vigente, com a versão e a origem de cada informação. **Sem `models.py`**: nada é
    # gravado, e a resposta deriva do conteúdo publicado, que é imutável (`D-006`). Registrada como
    # os vizinhos porque as Fases B e C crescem dentro dela. O nome não é `consulta`, que já é a
    # consulta pública de `publicacoes`, nem `assistente`, que na gestão é o de composição
    # (`R-001`).
    "processo_seletivo.duvidas",
]

# **Só o *acesso* à fonte da semente mora aqui**: quanto tempo esperar e quantas vezes tentar são
# decisões de operação. **Qual fonte** não é uma delas, e chegou a ser: havia aqui um
# `SORTEIO_FONTE_ADAPTADOR` que escolhia o adaptador por ambiente, e ele ficou órfão quando a
# FR-076 fechou o vocabulário de fontes. Manter uma variável que ninguém lê é pior que não a ter —
# ela sugere que trocar a fonte da semente é configuração, quando é norma publicada no `drawMethod`
# do marco, alterável só por Retificação (021, FR-076, D-013).
SORTEIO_FONTE_TIMEOUT_SEGUNDOS = float(os.environ.get("SORTEIO_FONTE_TIMEOUT_SEGUNDOS", "10"))
SORTEIO_FONTE_TENTATIVAS = int(os.environ.get("SORTEIO_FONTE_TENTATIVAS", "3"))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # `shared/templates` não pertence a app nenhum: guarda o que os dois canais compartilham
        # sem que um dependa do outro — hoje, a página de erro. Os tokens visuais moravam aqui até a
        # 089, e passaram a `shared/static` (abaixo). `APP_DIRS` continua encontrando o resto.
        "DIRS": [BASE_DIR / "processo_seletivo" / "shared" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "processo_seletivo.interface.identidade.contexto_identidade",
                # A barra do shell da gestão (076), derivada da identidade acima, sem consulta.
                "processo_seletivo.interface.navegacao.contexto_da_navegacao",
                "processo_seletivo.portal.identidade.contexto_candidato",
            ],
            # O endereço versionado das folhas (089), nas bases dos dois canais e na página de erro.
            # Mora em `shared/`, que não é app, e por isso é declarado aqui, e não descoberto.
            "libraries": {"estaticos": "processo_seletivo.shared.estaticos"},
        },
    }
]
STATIC_URL = "static/"
# Os tokens visuais dos dois canais (089). Como os modelos de `shared/`, os estáticos de `shared/`
# não pertencem a app nenhum: são declarados aqui, e o portal não passa a depender de um diretório
# da gestão.
STATICFILES_DIRS = [BASE_DIR / "processo_seletivo" / "shared" / "static"]

# Seletor de identidade: substitui a autenticação institucional enquanto ela não existe.
# Nunca deve estar ligado em produção — ver specs/002-frontend-administrativo/plan.md, Decisão 4.
INTERFACE_SELETOR_IDENTIDADE = os.getenv("INTERFACE_SELETOR_IDENTIDADE", "false").lower() == "true"

# O adaptador da autenticação institucional da gestão (106, contrato do adaptador): o caminho de
# uma classe que cumpre o contrato de `seguranca/autenticacao.py`. Vazio, a entrada
# institucional não existe — e em produção, sem ela, a gestão continua respondendo 503. Nenhum
# provedor real foi integrado ainda; o simulado mora no código de teste, e `production.py` o recusa.
GESTAO_PROVEDOR_INSTITUCIONAL = os.getenv("GESTAO_PROVEDOR_INSTITUCIONAL", "").strip()


# Os prazos da sessão institucional da gestão, em minutos (107, `D-009`): a duração máxima, contada
# da entrada, e o limite de inatividade, contado da última ação na gestão. Os padrões são os que o
# usuário decidiu em 30/10/2026 — 8 horas e 30 minutos (spec da 107, P4) —, e valem fora de
# produção; em produção a decisão manda declará-los expressamente, e `production.py` os exige
# quando há provedor (`D-010`).
def _minutos(nome, padrao):
    # Vazio é não declarado, e vale o padrão; qualquer outra coisa que não seja inteiro positivo é
    # erro de quem configurou, e não se troca pelo padrão em silêncio.
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao
    if not valor.isdigit() or int(valor) <= 0:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(f"{nome}: o prazo da sessão é em minutos inteiros e positivos.")
    return int(valor)


GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS = _minutos("GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS", 480)
GESTAO_SESSAO_INATIVIDADE_MINUTOS = _minutos("GESTAO_SESSAO_INATIVIDADE_MINUTOS", 30)

# O único *backend* de autenticação: o institucional, que autentica a identidade entregue pelo
# adaptador e **não aceita usuário e senha** (106, `D-008`). Sem esta linha, o padrão do Django
# seria o `ModelBackend`, e um `createsuperuser` com senha abriria uma porta que ninguém declarou.
AUTHENTICATION_BACKENDS = ["processo_seletivo.seguranca.autenticacao.BackendInstitucional"]

# Identidade do candidato (009): eixo próprio, e enquanto o provedor institucional não existir,
# um de demonstração. Como o seletor acima, nunca em produção — ver `production.py`.
PORTAL_IDENTIDADE_DEMO = os.getenv("PORTAL_IDENTIDADE_DEMO", "false").lower() == "true"

# A fonte de demonstração do sorteio (046, `FR-757`): semente fixa, sem rede, para `seed_demo`,
# o roteiro do `quickstart` e a suíte. Um sorteio publicado com ela seria previsível, e por isso
# ela só existe no vocabulário onde este valor é verdadeiro — `development.py` e `test.py` o
# ligam, a base não, e `production.py` recusa subir com ele (`FR-758`).
SORTEIO_FONTE_DE_DEMONSTRACAO = (
    os.getenv("SORTEIO_FONTE_DE_DEMONSTRACAO", "false").lower() == "true"
)

# O canal de e-mail que a 010 inaugura: até ela, o projeto não enviava mensagem nenhuma. O
# mecanismo vem do ambiente porque desenvolvimento imprime no terminal e produção entrega de
# verdade — e é justamente por isso que `production.py` recusa subir com um mecanismo que não
# entrega: seria imprimir o código de acesso no log e chamar isso de autenticação.
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
# **Sem limite, um servidor de correio que aceita a conexão e não responde prende o worker** até os
# 120 s do gunicorn — e o código de acesso é o único fator de autenticação do candidato (gap I-4 do
# runbook). O backend SMTP do Django aplica este valor à conexão, e por isso ele vale para os quatro
# envios de uma vez: código, comprovante, convocação e aviso (066, `R-006`, `FR-1270`).
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))

# Os avisos complementares aos candidatos (066). **Desligados por padrão**, e é produção quem herda
# o padrão: a ativação depende da validação institucional de LGPD e da infraestrutura de correio
# (`D-009`). Desligada, ninguém confirma aviso e o despacho não tenta nada; o histórico e os modelos
# continuam (`FR-1282`).
AVISOS_AOS_CANDIDATOS = os.getenv("AVISOS_AOS_CANDIDATOS", "false").lower() == "true"
# O ritmo é o do timer: no máximo este número por execução, uma execução por minuto (`R-005`).
# Valor inicial, e não compromisso: o limite real é o da conta de envio da instituição.
AVISOS_LIMITE_POR_MINUTO = int(os.getenv("AVISOS_LIMITE_POR_MINUTO", "60"))
AVISOS_MAX_TENTATIVAS = int(os.getenv("AVISOS_MAX_TENTATIVAS", "3"))
# Minutos de espera antes da 2ª, da 3ª… tentativa de uma falha temporária (`FR-1269`).
AVISOS_INTERVALOS_DE_RETENTATIVA = tuple(
    int(minutos)
    for minutos in os.getenv("AVISOS_INTERVALOS_DE_RETENTATIVA", "5,15").split(",")
    if minutos.strip()
)
# Pendente há mais que isto faz o histórico dizer que o despacho pode estar parado (`FR-1272`).
AVISOS_ALERTA_DE_PENDENTE_MIN = int(os.getenv("AVISOS_ALERTA_DE_PENDENTE_MIN", "10"))
# **A janela é o que impede religar a chave de disparar mensagem antiga** (`R-016`, `FR-1283`): o
# banco não vê a chave mudar, e por isso o critério é a idade do aviso, e não o instante da
# ativação.
AVISOS_JANELA_DE_DESPACHO_HORAS = int(os.getenv("AVISOS_JANELA_DE_DESPACHO_HORAS", "24"))


# O piloto interno do assistente do Edital (071, `R-009`). **Desligado por padrão**, e é produção
# quem herda o padrão: o piloto roda na máquina da equipe, em sessões acompanhadas (`D-012`). Um
# serviço por configuração, `ollama` ou `openrouter`, e nenhuma troca entre eles (`FR-1499`).
ASSISTENTE_PILOTO = os.getenv("ASSISTENTE_PILOTO", "false").lower() == "true"
ASSISTENTE_SERVICO = os.getenv("ASSISTENTE_SERVICO", "").strip()
# O painel do assistente na página pública da seleção, só no desenvolvimento local (074, `FR-1680`):
# o candidato conversa sem a identidade da gestão, e é por isso que produção recusa subir com ele
# (`production.py`). Independente do piloto: as sugestões respondem sem modelo, e a pergunta livre
# cai num estado explícito quando o serviço não está configurado.
ASSISTENTE_NA_PAGINA_DO_EDITAL = (
    os.getenv("ASSISTENTE_NA_PAGINA_DO_EDITAL", "false").lower() == "true"
)
# Quantas conversas a página pública abre por sessão e Edital (074, `FR-1685`): o limite de turnos é
# por conversa, e "Nova conversa" sem teto daria turnos novos sem fim.
ASSISTENTE_CONVERSAS_POR_SESSAO = int(os.getenv("ASSISTENTE_CONVERSAS_POR_SESSAO", "3"))
ASSISTENTE_ENDERECO = os.getenv("ASSISTENTE_ENDERECO", "").strip().rstrip("/")
ASSISTENTE_MODELO = os.getenv("ASSISTENTE_MODELO", "").strip()
# Só do ambiente, nunca de arquivo versionado nem do `.env` (`FR-1502`). Ninguém a imprime: ela só
# existe no cabeçalho montado pelo adaptador.
ASSISTENTE_CREDENCIAL = os.getenv("ASSISTENTE_CREDENCIAL", "")
# Abaixo dos 120 s do gunicorn e dos 130 s do nginx do guia de implantação (§12.1, §14.2): a pessoa
# recebe "tempo esgotado", e não um 502 (`FR-1500`).
ASSISTENTE_TEMPO_LIMITE_SEGUNDOS = float(os.getenv("ASSISTENTE_TEMPO_LIMITE_SEGUNDOS", "90"))
# O contexto **efetivo**, e não o nominal do modelo: o primeiro valor a medir na L4 (`FR-1480`).
ASSISTENTE_CONTEXTO_TOKENS = int(os.getenv("ASSISTENTE_CONTEXTO_TOKENS", "32768"))
# A reserva da resposta, inclusive do raciocínio quando ele está ligado (`R-007`).
ASSISTENTE_SAIDA_MAXIMA_TOKENS = int(os.getenv("ASSISTENTE_SAIDA_MAXIMA_TOKENS", "2048"))
# Sempre enviados, porque o padrão do serviço não é confiável (`FR-1498`). Pontos de partida: cada
# troca registra os usados.
ASSISTENTE_TEMPERATURA = float(os.getenv("ASSISTENTE_TEMPERATURA", "0.2"))
ASSISTENTE_TOP_P = float(os.getenv("ASSISTENTE_TOP_P", "0.9"))
ASSISTENTE_SEMENTE = int(os.getenv("ASSISTENTE_SEMENTE", "7"))
ASSISTENTE_RACIOCINIO = os.getenv("ASSISTENTE_RACIOCINIO", "false").lower() == "true"
# O `tokenizer.json` publicado com o modelo, fora do repositório (`R-006`).
ASSISTENTE_TOKENIZER = os.getenv("ASSISTENTE_TOKENIZER", "").strip()
# O acréscimo do molde de conversa por mensagem; quem o mede é a verificação de conexão.
ASSISTENTE_TOKENS_POR_MENSAGEM = int(os.getenv("ASSISTENTE_TOKENS_POR_MENSAGEM", "8"))
# O acréscimo fixo de cada chamada, que não depende de quantas mensagens ela leva. No ensaio de
# 14/10 no OpenRouter, eram ~250 tokens com 2 ou 3 mensagens — provavelmente o esquema da saída,
# injetado pelo provedor —, e pô-los no acréscimo por mensagem sobrecontava cada turno de
# histórico (`R-006`).
ASSISTENTE_TOKENS_POR_CHAMADA = int(os.getenv("ASSISTENTE_TOKENS_POR_CHAMADA", "0"))
# Abaixo disto, os tokens que o serviço informa ter lido acusam um corte (`FR-1482`).
ASSISTENTE_TOLERANCIA_DE_TOKENS = float(os.getenv("ASSISTENTE_TOLERANCIA_DE_TOKENS", "0.02"))
# Menor que o número de processos que atendem requisições: com cinco, no máximo dois (`D-008`).
ASSISTENTE_TETO_SIMULTANEO = int(os.getenv("ASSISTENTE_TETO_SIMULTANEO", "2"))
ASSISTENTE_TURNOS_POR_CONVERSA = int(os.getenv("ASSISTENTE_TURNOS_POR_CONVERSA", "20"))
ASSISTENTE_PERGUNTA_MAXIMA = int(os.getenv("ASSISTENTE_PERGUNTA_MAXIMA", "800"))
# Exigir retenção zero do provedor no OpenRouter, quando o modelo tiver quem a ofereça.
ASSISTENTE_ZDR = os.getenv("ASSISTENTE_ZDR", "false").lower() == "true"
# O provedor do OpenRouter, fixo (`FR-1499`): sem troca automática, o roteamento pelo mais barato
# caía num provedor que recusava 3 de 5 perguntas com 429 (ensaio de 14/10). Vazio, o OpenRouter
# escolhe, ainda sem troca. O nome é o do OpenRouter, por exemplo `parasail`.
ASSISTENTE_PROVEDOR = os.getenv("ASSISTENTE_PROVEDOR", "").strip()
# `truncate`/`shift` desligados no Ollama, só depois de quem opera a L4 confirmar que a versão
# instalada os aceita: a API não o informa, e uma versão que não os conhece os ignora em silêncio
# (`R-017`). A conferência da contagem vale de qualquer modo.
ASSISTENTE_OLLAMA_SEM_CORTE = os.getenv("ASSISTENTE_OLLAMA_SEM_CORTE", "false").lower() == "true"
# A quantização que a avaliação mede, como o Ollama a escreve (`Q4_K_M`). Só a verificação de
# conexão a lê, e vazia é divergência: sem ela, uma troca de quantização no servidor passaria por
# outra configuração sem ninguém ver (US7, cenário 2; DP-7).
ASSISTENTE_QUANTIZACAO = os.getenv("ASSISTENTE_QUANTIZACAO", "").strip()

# Existe um proxy à frente da aplicação? (010) Só com isto ligado o cabeçalho `X-Forwarded-For` é
# lido para distinguir origens no limite de solicitações de código. Ele é escrito pelo cliente:
# confiar nele sem um proxy que o sobrescreva torna o limite por origem contornável com um
# cabeçalho aleatório por requisição. O padrão é não confiar.
PORTAL_ATRAS_DE_PROXY = os.getenv("PORTAL_ATRAS_DE_PROXY", "false").lower() == "true"

# Para onde mandar quem o sistema não consegue mais atender sozinho (010). Duas telas dizem
# "procure o atendimento institucional" — o CPF congelado depois da primeira inscrição enviada, e a
# participação anterior que a pessoa não conseguiu confirmar —, e ambas eram becos sem saída: nem
# e-mail, nem telefone, nem link. São justamente os dois pontos em que ela já está travada.
# Vazio em desenvolvimento; em produção a ausência impede subir.
#
# **É o canal da instituição, e não o de uma unidade** (109). A unidade pode declarar o seu no
# `unidades.json` (`atendimento`), e então as comunicações de um Edital dela o usam; este fica como
# a recaída delas e como o único canal da conta do candidato, que não é de unidade nenhuma. Não é
# configuração de correio: servidor, remetente e credencial são os `EMAIL_*`, um só para todos.
PORTAL_ATENDIMENTO = os.getenv("PORTAL_ATENDIMENTO", "").strip()

# Documentos do candidato (009). A raiz é privada: fica fora da árvore estática e nunca é servida
# pelo servidor web — todo acesso passa pela aplicação, que confere titularidade ou permissão
# (FR-051). Vazia em desenvolvimento significa "esta máquina não recebe arquivo"; em produção a
# ausência impede subir.
ARQUIVOS_CANDIDATOS_RAIZ = os.getenv("ARQUIVOS_CANDIDATOS_RAIZ", "")
# O limite é da aplicação, e não do documento exigido (FR-046): um Edital não negocia tamanho de
# arquivo. Lê-se daqui para que mudá-lo não seja mexer em código.
ARQUIVOS_CANDIDATOS_LIMITE_BYTES = int(
    os.getenv("ARQUIVOS_CANDIDATOS_LIMITE_BYTES", str(10 * 1024 * 1024))
)

# Anexos do Edital (020). O limite é da aplicação pela mesma razão do de cima — um Edital não
# negocia tamanho de arquivo (FR-013) —, e é metade dele porque as duas pontas não são simétricas:
# o candidato digitaliza documento em papel, e o formulário que a instituição publica nasce
# digital. Aqui os bytes moram em coluna binária, então o limite protege o banco.
EDITAL_ANEXOS_LIMITE_BYTES = int(os.getenv("EDITAL_ANEXOS_LIMITE_BYTES", str(5 * 1024 * 1024)))

# **Campos por envio** (`doc/achado-etapa-perfis-recusa-acima-de-mil-campos.md`, DP-21). O padrão do
# Django é mil, e a composição grava a coleção inteira num POST só (`replace_draft`): o 27º Perfil
# de duas Modalidades já passava do teto, e o envio morria com 400 antes da view. O valor é medido,
# e não chutado, sobre o maior Edital previsto — o multicampi da `051`: N = 66 Perfis, cada um com
# 4 Modalidades, o quadro repartido em 4 linhas, 2 fatos exigidos e 2 marcos de 3 critérios, sobre
# 2 Etapas. Contado no formulário que a tela devolve, em 29/09/2026:
#
#   Perfis         3 + 67·N = 4.425  (67 = 15 do Perfil + 8·4 Modalidades + 3·4 linhas + 4·2 fatos)
#   Classificação 11 + 89·N = 5.885  (89 = 1 + 44·2 marcos; o marco de 3 critérios envia 44)
#   Retificação   41 + 92·N = 6.113  (o formulário inteiro do Edital publicado — o mais pesado)
#
# O dobro do maior, arredondado ao milhar acima. A folga cobre Modalidade ou marco a mais por Perfil
# e ~140 Perfis na forma acima; `test_limite_de_campos_da_composicao.py` recompõe esse Edital e
# reprova se algum dos três envios passar daqui.
#
# **Vale para toda rota, e não só para `/gestao/`**: o Django lê este valor ao interpretar o corpo,
# antes de qualquer rota ou view, e não oferece limite por caminho. O que ele protege — a CPU gasta
# interpretando um corpo com campos demais — continua limitado: treze mil campos custam ~10 ms, e o
# corpo segue preso aos 2,5 MB do `DATA_UPLOAD_MAX_MEMORY_SIZE`, que não muda. Constante, e não
# variável de ambiente, para que o valor em produção seja o que o guardião verificou.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 13_000

MIDDLEWARE = [
    # O primeiro, para que a resposta de todo middleware de dentro — a recusa do envio grande, a
    # recusa do domínio — passe por ele na volta e leve a política (091, `politica_de_conteudo.py`).
    "processo_seletivo.shared.politica_de_conteudo.PoliticaDeConteudoMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Antes do CSRF, que é quem lê o corpo primeiro: o envio acima do limite de campos morre nessa
    # leitura, e só daqui ele volta como página da gestão, e não como 400 cru (`erros.py`).
    "processo_seletivo.interface.erros.EnvioAcimaDoLimiteMiddleware",
    # A interface administrativa autentica por sessão: sem esta verificação os `{% csrf_token %}`
    # dos formulários não são fiscalizados por ninguém e uma página externa pratica atos
    # irreversíveis em nome de quem estiver com a sessão aberta. As views da API são
    # `csrf_exempt` por construção do DRF e continuam autenticando por cabeçalho.
    "django.middleware.csrf.CsrfViewMiddleware",
    "processo_seletivo.shared.api.middleware.CorrelationIdMiddleware",
    "processo_seletivo.interface.erros.RecusaDoDominioMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# A recusa da verificação acima na moldura da área, e não na página do framework, que traz o estilo
# embutido e sairia sem desenho sob a política de segurança de conteúdo (093, `erros.py`).
CSRF_FAILURE_VIEW = "processo_seletivo.interface.erros.falha_de_csrf"
database_role = os.getenv("DB_ROLE", "runtime")
database_user = os.getenv(
    "DB_MIGRATION_USER" if database_role == "migration" else "DB_RUNTIME_USER",
    os.getenv("DB_USER", "processo_seletivo_runtime"),
)
database_password = os.getenv(
    "DB_MIGRATION_PASSWORD" if database_role == "migration" else "DB_RUNTIME_PASSWORD",
    os.getenv("DB_PASSWORD", ""),
)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "processo_seletivo"),
        "USER": database_user,
        "PASSWORD": database_password,
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
REST_FRAMEWORK = {
    # Só JSON: o contrato declara application/json e a Browsable API do DRF exigiria
    # engine de template e staticfiles, superfície que uma API institucional não precisa.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": (
        "processo_seletivo.shared.api.negotiation.JsonAlwaysNegotiation"
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "processo_seletivo.shared.api.problems.problem_exception_handler",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "processo_seletivo.shared.observability.JsonFormatter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "processo_seletivo": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
