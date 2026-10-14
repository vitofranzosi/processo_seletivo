"""Uma pergunta ao assistente do Edital, de ponta a ponta (071, `R-011`).

**Sem requisição**, como a consulta da `070` (`FR-1448` da `070`): a tela e o comando de avaliação
chamam a mesma função, e nada aqui lê sessão. O acesso — o alcance do Edital e a permissão — é
verificado por quem chama, a cada pergunta (`FR-1460`).

**A ordem é a do `R-011`**, e cada passo pode terminar a troca num estado (data-model §4), sempre
gravado — a avaliação precisa das recusas tanto quanto das respostas:

1. a pergunta: tamanho e máscara;
2. a leitura da `070`, no instante, e as fontes completas;
3. as mensagens, a contagem e o orçamento;
4. **uma** chamada, fora de qualquer transação;
5. o descarte do raciocínio, e a conferência da saída;
6. a gravação, com a `ordem` alocada na própria gravação, sob trava da conversa;
7. uma linha de log, sem texto.

**Nenhuma retentativa** (`FR-1505`): a falha do serviço vira estado, e a próxima tentativa é uma
nova pergunta de alguém.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import replace

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Max

from processo_seletivo.duvidas.application.consultar import contexto as ler_contexto
from processo_seletivo.duvidas.application.limites import (
    recusa_antes_da_chamada,
    vaga_do_assistente,
)
from processo_seletivo.duvidas.domain import catalogo, leitura, respostas, sugestoes
from processo_seletivo.duvidas.domain import conferencia as conferencias
from processo_seletivo.duvidas.domain import fontes as derivacao
from processo_seletivo.duvidas.domain import mensagens as montagem
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    ESTADOS,
    EXCEDE_O_CONTEXTO,
    INCOMPLETA,
    INDISPONIVEL,
    LIMITE_DE_USO,
    MODELO_DIFERENTE,
    NAO_PASSOU_NA_CONFERENCIA,
    PERGUNTA_RECUSADA,
    POSSIVEL_CORTE,
    RESPONDIDA_E_CONFERIDA,
    RESPOSTA_DA_SUGESTAO,
    SEM_TOKENIZER,
)
from processo_seletivo.duvidas.domain.mascara import mascarar, mascarar_resposta, tem_padrao_pessoal
from processo_seletivo.duvidas.infrastructure import inferencia, tokens
from processo_seletivo.duvidas.models import TrocaDoPiloto

#: A permissão do piloto, escrita aqui e em `interface/identidade.py`; um teste confere as duas.
PERMISSAO = "assistente:piloto"

logger = logging.getLogger("processo_seletivo.duvidas.piloto")


def perguntar(*, edital_id, conversa, pergunta, instante, origem, correlacao="") -> TrocaDoPiloto:
    """A troca gravada, em qualquer estado.

    Levanta `SemVersaoVigente` da `070` quando o Edital não tinha publicação vigente no instante:
    aí não há conversa, e nada se grava (`FR-1469`).
    """
    inicio = time.monotonic()
    texto = mascarar((pergunta or "").strip())
    troca = TrocaDoPiloto(
        conversa=conversa,
        edital_id=edital_id,
        instante=instante,
        origem=origem,
        pergunta=texto,
        servico=settings.ASSISTENTE_SERVICO,
        modelo_configurado=settings.ASSISTENTE_MODELO,
        parametros=inferencia.parametros_configurados(),
        versao_das_instrucoes=montagem.VERSAO_DAS_INSTRUCOES,
    )
    medidos = informados = None
    custo = None

    if not texto or len(texto) > settings.ASSISTENTE_PERGUNTA_MAXIMA:
        return _gravar(troca, PERGUNTA_RECUSADA, inicio, correlacao)
    # No serviço externo, o padrão pessoal recusa em vez de mascarar: a pergunta não sai da rede
    # com o que quer que a máscara deixasse passar ao lado dele (`FR-1503`, `CB-11`).
    if inferencia.externo() and tem_padrao_pessoal(pergunta or ""):
        return _gravar(troca, PERGUNTA_RECUSADA, inicio, correlacao)
    recusa = recusa_antes_da_chamada(conversa=conversa)
    if recusa is not None:
        return _gravar(troca, recusa, inicio, correlacao)

    lido = ler_contexto(edital_id=edital_id, instante=instante)
    troca.versao = lido.versao.id
    troca.versao_curta = lido.versao.identificador_curto
    fontes = derivacao.fontes_completas(lido)
    turnos = historico_permitido(conversa, edital_id, lido.versao.id)
    orcamento = montagem.orcamento_de_entrada(
        settings.ASSISTENTE_CONTEXTO_TOKENS, settings.ASSISTENTE_SAIDA_MAXIMA_TOKENS
    )
    # O excesso, na ordem do `FR-1481`: sai o turno mais antigo, inteiro, até caber; nenhuma fonte é
    # cortada. Sem histórico e ainda sem caber, a pergunta não sai (`D-003`).
    da_conversa = escolha_da_conversa(conversa, edital_id, lido.versao.id)
    while True:
        montadas = montagem.montar(
            lido, fontes, [(p, r) for _, p, r in turnos], texto, da_conversa=da_conversa
        )
        try:
            medidos = tokens.contar(montadas.mensagens)
        except tokens.SemTokenizer:
            return _gravar(troca, SEM_TOKENIZER, inicio, correlacao)
        if medidos <= orcamento or not turnos:
            break
        turnos = turnos[1:]
    troca.impressao_das_fontes = montadas.impressao_das_fontes
    troca.historico_desde = turnos[0][0] if turnos else None
    if medidos > orcamento:
        return _gravar(troca, EXCEDE_O_CONTEXTO, inicio, correlacao, medidos=medidos)

    # Uma vaga do teto global durante a chamada, e só durante ela: a gravação vem depois, fora da
    # trava (`FR-1506`). Sem vaga, nenhuma chamada.
    devolucao = falha = None
    with vaga_do_assistente() as vaga:
        if vaga:
            troca.chamou_o_servico = True
            try:
                devolucao = inferencia.conversar(
                    montadas.mensagens, montagem.ESQUEMA_DA_SAIDA, troca.parametros
                )
            except inferencia.FalhaDoServico as recusada:
                falha = recusada
    if not vaga:
        return _gravar(troca, LIMITE_DE_USO, inicio, correlacao, medidos=medidos)
    if falha is not None:
        estado = falha.codigo if falha.codigo in ESTADOS else INDISPONIVEL
        return _gravar(troca, estado, inicio, correlacao, medidos=medidos, provedor=falha.provedor)
    # O raciocínio do modelo não vai à troca, à tela nem ao log (`FR-1492`).
    devolucao = replace(devolucao, raciocinio="")
    troca.modelo_que_respondeu = devolucao.modelo
    informados, custo = devolucao.tokens_de_entrada, devolucao.custo
    medida = dict(medidos=medidos, informados=informados, custo=custo, provedor=devolucao.provedor)
    if devolucao.modelo != settings.ASSISTENTE_MODELO:
        # Outro modelo respondeu: a avaliação mediria o que não acredita medir (`FR-1499`).
        return _gravar(troca, MODELO_DIFERENTE, inicio, correlacao, **medida)

    if devolucao.termino != "stop":
        # Encerrada por limite de saída, ou sem término normal: o que veio está pela metade
        # (`FR-1483`), e o JSON pela metade nem chega à conferência.
        return _gravar(troca, INCOMPLETA, inicio, correlacao, **medida)
    tolerancia = settings.ASSISTENTE_TOLERANCIA_DE_TOKENS
    if informados is not None and informados < medidos * (1 - tolerancia):
        # O serviço leu menos do que se mandou: o padrão do Ollama descarta mensagens antigas em
        # silêncio quando o contexto estoura, e uma fonte cortada é uma condição omitida
        # (`FR-1482`).
        return _gravar(troca, POSSIVEL_CORTE, inicio, correlacao, **medida)

    conferida = conferencias.conferir(devolucao.texto, fontes, permitidos=(lido.numero, lido.ano))
    if conferida.saida is not None:
        troca.tipo = conferida.saida.tipo
        troca.trechos = [
            {**trecho.como_dict(), "texto": mascarar_resposta(trecho.texto)}
            for trecho in conferida.saida.trechos
        ]
        citadas = set(conferida.saida.citadas())
        troca.fontes_citadas = [fonte.como_dict() for fonte in fontes if fonte.id in citadas]
        troca.fontes_citadas += [
            {**fonte.como_dict(), "aviso_da_aplicacao": True}
            for fonte in avisos_da_aplicacao(fontes, citadas)
        ]
    troca.conferencia = [motivo.como_dict() for motivo in conferida.motivos]
    estado = RESPONDIDA_E_CONFERIDA if conferida.aprovada else NAO_PASSOU_NA_CONFERENCIA
    return _gravar(troca, estado, inicio, correlacao, **medida)


def responder_sugestao(
    *, edital_id, conversa, codigo, perfil, instante, origem, correlacao=""
) -> TrocaDoPiloto:
    """A pergunta sugerida, respondida pela `070`, gravada como turno da conversa (Fase C).

    **Sem o modelo, e sem conferência**: a resposta sai dos dados, e é a mesma que a tela da `070`
    mostra. **Com o tipo dela**: "depende da leitura" e o detalhe em anexo continuam ditos — ser
    determinística não quer dizer que a pergunta foi respondida por inteiro.

    O que entra nos trechos é o que o histórico vai repetir ao modelo: a explicação, os avisos e os
    dados. O texto do Edital fica nas fontes citadas, e não nos trechos — ele já vai inteiro nas
    fontes da chamada seguinte.

    Levanta `SemVersaoVigente` como `perguntar`, e `catalogo.ParametroRecusado` quando a sugestão
    não vale para este Edital ou para o Perfil escolhido.
    """
    inicio = time.monotonic()
    lido = ler_contexto(edital_id=edital_id, instante=instante)
    texto, resposta = resposta_da_sugestao(lido, codigo, perfil)
    if catalogo.PERFIL not in catalogo.POR_CODIGO[codigo].parametros:
        perfil = None
    troca = TrocaDoPiloto(
        conversa=conversa,
        edital_id=edital_id,
        instante=instante,
        origem=origem,
        pergunta=texto,
        servico=settings.ASSISTENTE_SERVICO,
        modelo_configurado=settings.ASSISTENTE_MODELO,
        versao_das_instrucoes=montagem.VERSAO_DAS_INSTRUCOES,
        versao=lido.versao.id,
        versao_curta=lido.versao.identificador_curto,
    )
    # O limite da conversa vale também aqui: cada sugestão é um turno a mais no histórico.
    recusa = recusa_antes_da_chamada(conversa=conversa)
    if recusa is not None:
        return _gravar(troca, recusa, inicio, correlacao)
    preencher_com_a_resposta(troca, lido, codigo, resposta, perfil)
    return _gravar(troca, RESPOSTA_DA_SUGESTAO, inicio, correlacao)


def resposta_da_sugestao(lido, codigo, perfil):
    """`(pergunta em palavras, resposta da 070)`, ou `catalogo.ParametroRecusado`.

    A opção vai junto da pergunta, pelo nome que o candidato reconhece: é por ela que o modelo sabe,
    na continuação, de qual opção se falava.
    """
    pergunta = catalogo.POR_CODIGO.get(codigo)
    if pergunta is None or pergunta not in catalogo.oferecidas(lido.conteudo):
        raise catalogo.ParametroRecusado("Esta pergunta não vale para este Edital.")
    if catalogo.PERFIL not in pergunta.parametros:
        perfil = None
    modalidade = catalogo.SEM_MODALIDADE if catalogo.MODALIDADE in pergunta.parametros else None
    resposta = respostas.responder(lido, codigo, perfil=perfil, modalidade=modalidade)
    if not perfil:
        return sugestoes.texto_no_painel(codigo), resposta
    perfis = lido.conteudo.get("profiles") or []
    opcao = sugestoes.nome_da_opcao(leitura.perfil_por_codigo(lido.conteudo, perfil), perfis)
    return f"{sugestoes.texto_no_painel(codigo)} — {opcao}", resposta


def preencher_com_a_resposta(troca, lido, codigo, resposta, perfil):
    """O tipo, os trechos compostos para o painel e as fontes da `070` (`domain/sugestoes.py`)."""
    troca.tipo = resposta.tipo
    troca.trechos = sugestoes.compor(lido, codigo, resposta, perfil)
    troca.fontes_citadas = [referencia.como_dict() for referencia in resposta.referencias]


def avisos_da_aplicacao(fontes, citadas):
    """O que a aplicação acrescenta à resposta, sem o modelo (`FR-1490`).

    O valor que uma Retificação já publicada vai pôr no lugar de **uma fonte citada**, e o desfecho
    do Edital: o modelo pode deixá-los de fora, e a aplicação não. Vêm das próprias fontes
    calculadas, e não de uma leitura nova — e sem repetir as que o modelo já citou.
    """
    return [
        fonte
        for fonte in fontes
        if fonte.id not in citadas
        and ((fonte.altera and fonte.altera in citadas) or fonte.lugar == "Desfecho")
    ]


def historico_permitido(conversa, edital_id, versao):
    """Os turnos `(ordem, pergunta, resposta)` que o modelo pode ver, do mais antigo (`FR-1495`).

    **Lidos da tabela, e nunca do navegador** (`FR-1494`): um turno forjado num formulário não
    existe aqui. **Só da mesma versão vigente**: mudou a versão, o que se disse sobre a anterior não
    volta ao modelo — é o caminho pelo qual uma regra superada reapareceria sem ninguém perceber
    (`D-006`). **Só os conferidos**, e as sugestões respondidas pela `070`: uma resposta recusada
    não foi mostrada, e não pode virar a premissa da seguinte; a da sugestão foi mostrada, e saiu
    dos dados. A resposta vai como o texto dos trechos, sem as fontes: o histórico é conversa, e
    não fonte; a conferência só aceita as fontes da chamada.
    """
    turnos = []
    for troca in TrocaDoPiloto.objects.filter(
        conversa=conversa,
        edital_id=edital_id,
        versao=versao,
        estado__in=(RESPONDIDA_E_CONFERIDA, RESPOSTA_DA_SUGESTAO),
    ).order_by("ordem"):
        turnos.append((troca.ordem, troca.pergunta, texto_da_resposta(troca.trechos or [])))
    return turnos


def escolha_da_conversa(conversa, edital_id, versao) -> str:
    """A última opção escolhida por sugestão nesta conversa, na mesma versão, ou `""`.

    Dita ao modelo numa mensagem própria (`mensagens.montar`): no histórico ela só aparecia
    implícita, no nome do polo, e sem dizer que a lista de concorrência não foi informada.
    """
    trocas = TrocaDoPiloto.objects.filter(
        conversa=conversa, edital_id=edital_id, versao=versao, estado=RESPOSTA_DA_SUGESTAO
    ).order_by("-ordem")
    for troca in trocas:
        for trecho in troca.trechos or []:
            if trecho["natureza"] == "contexto":
                return trecho["texto"]
    return ""


def texto_da_resposta(trechos):
    """A resposta como o histórico a repete: os trechos em sequência, e a lista como lista.

    O trecho `contexto` fica de fora: ele vai ao modelo pela mensagem do sistema, e não como algo
    que o assistente tenha dito.
    """
    trechos = [trecho for trecho in trechos if trecho["natureza"] != "contexto"]
    if not any(trecho["natureza"] == "item" for trecho in trechos):
        return " ".join(trecho["texto"] for trecho in trechos)
    linhas = []
    for trecho in trechos:
        if trecho["natureza"] == "item":
            detalhe = f" ({trecho['detalhe']})" if trecho.get("detalhe") else ""
            linhas.append(f"- {trecho['texto']}{detalhe}")
        else:
            linhas.append(trecho["texto"])
    return "\n".join(linhas)


def _chave_da_conversa(conversa) -> int:
    return int.from_bytes(hashlib.sha256(f"conversa:{conversa}".encode()).digest()[:8], "big") >> 1


def _gravar(
    troca, estado, inicio, correlacao, *, medidos=None, informados=None, custo=None, provedor=""
):
    """A `ordem` alocada aqui, numa transação curta — a chamada já terminou (data-model §3).

    Duas abas da mesma conversa gravam na ordem em que terminam; a trava consultiva da conversa
    impede que leiam o mesmo máximo. Fora do PostgreSQL não há trava: o SQLite serializa a escrita.
    """
    troca.estado = estado
    with transaction.atomic():
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(%s)", [_chave_da_conversa(troca.conversa)]
                )
        ultima = TrocaDoPiloto.objects.filter(conversa=troca.conversa).aggregate(
            ultima=Max("ordem")
        )["ultima"]
        troca.ordem = (ultima or 0) + 1
        troca.save()
    _registrar(troca, inicio, correlacao, medidos, informados, custo, provedor)
    return troca


def _registrar(troca, inicio, correlacao, medidos, informados, custo, provedor=""):
    """Uma linha por troca, só com o necessário ao diagnóstico, e nunca texto (`FR-1508`)."""
    campos = {
        "edital": str(troca.edital_id),
        "versao": troca.versao_curta,
        "origem": troca.origem,
        "servico": troca.servico,
        "modelo": troca.modelo_que_respondeu or troca.modelo_configurado,
        # Quem serviu ou recusou, no OpenRouter; vazio no Ollama, que é ele mesmo o serviço.
        "provedor": provedor or None,
        "estado": troca.estado,
        "tipo": troca.tipo or None,
        "motivos": [motivo["regra"] for motivo in troca.conferencia or []],
        "tokens_medidos": medidos,
        "tokens_informados": informados,
        # Acima do medido não descarta, mas acusa um acréscimo por mensagem subestimado (`R-006`).
        "acima_do_medido": bool(
            informados
            and medidos
            and informados > medidos * (1 + settings.ASSISTENTE_TOLERANCIA_DE_TOKENS)
        ),
        "custo": custo,
        "segundos": round(time.monotonic() - inicio, 2),
        "correlacao": correlacao or None,
    }
    logger.info("troca_do_piloto %s", json.dumps(campos, ensure_ascii=False, sort_keys=True))
