"""A prévia do aviso: o que vai sair, para quem e de onde veio — e nada gravado (066, `FR-1259`).

**A assinatura detecta que o mundo mudou entre ler e confirmar** (`R-010`), no desenho de
`divulgacao/application/publicar.py::assinatura_da_previa`. Ela cobre o ato citado e as linhas do
universo — inscrição, elegibilidade, endereço. Uma retificação publicada, um desfecho registrado ou
uma credencial trocada entre a prévia e o clique a mudam, e a confirmação é recusada em vez de
mandar para uma lista que o operador não viu.

**O texto não entra nela.** Assunto, corpo, modelo e justificativa são escolha do operador,
submetidos no mesmo pedido; não têm como ficar obsoletos, e são **validados**, não assinados.
"""

from django.conf import settings

from processo_seletivo.avisos.domain import mensagem, nomes, variaveis
from processo_seletivo.shared.canonical import canonical_sha256

NATUREZA_POR_EXTENSO = {nomes.PRELIMINAR: "preliminar", nomes.DEFINITIVA: "definitivo"}


def assinatura(universo, *, motivo=nomes.PRIMEIRO_AVISO):
    return canonical_sha256(
        {
            "origem": universo.origem,
            "motivo": motivo,
            "marco": str(universo.marco_id),
            "lista": str(universo.lista_id) if universo.lista_id else None,
            "natureza": universo.natureza,
            "referencia": universo.referencia,
            "publicacoes": sorted(str(p.id) for p in universo.publicacoes),
            "linhas": sorted(
                [str(linha.inscricao.id), linha.elegibilidade, linha.endereco]
                for linha in universo.linhas
            ),
        }
    )


def valores(universo, *, enderecos):
    """As variáveis que valem para todos os destinatários deste universo (contracts/mensagem.md).

    `enderecos` traz os links absolutos que só a requisição sabe montar: `pagina`, `area` e, por
    publicação, `publicacao[id]`. É por isso que o texto se congela na confirmação, que é uma
    requisição, e o despacho não precisa conhecer o endereço público do sistema (`R-007`).
    """
    cabecalho = universo.cabecalho
    resultado = {
        "edital": cabecalho.get("edital", ""),
        "processo_seletivo": cabecalho.get("processo", ""),
        "perfil": cabecalho.get("perfil", ""),
        "pagina_do_processo_seletivo": enderecos.get("pagina", ""),
        "area_do_candidato": enderecos.get("area", ""),
    }
    if universo.data_da_publicacao is not None:
        resultado["data_da_publicacao"] = mensagem.instante(universo.data_da_publicacao)
    if universo.origem == nomes.RESULTADO:
        resultado["etapa"] = cabecalho.get("marco", "")
        resultado["natureza_do_resultado"] = NATUREZA_POR_EXTENSO.get(universo.natureza, "")
        if len(universo.publicacoes) == 1:
            resultado["link_da_publicacao"] = enderecos.get("publicacao", {}).get(
                str(universo.publicacoes[0].id), ""
            )
    else:
        resultado["referencia_da_publicacao"] = universo.referencia
    return resultado


def destino(universo, valores_):
    """Para onde o rodapé aponta (`R-008`): a publicação, a referência, ou a página do processo."""
    return mensagem.destino_oficial(
        link_da_publicacao=valores_.get("link_da_publicacao", ""),
        referencia_da_publicacao=valores_.get("referencia_da_publicacao", ""),
        pagina=valores_.get("pagina_do_processo_seletivo", ""),
    )


def congelar(universo, *, assunto, corpo, enderecos):
    """O texto final do aviso: validado, resolvido, com a linha de retificação e o rodapé."""
    assunto, corpo = mensagem.validar_texto(assunto=assunto, corpo=corpo)
    citadas = len(universo.publicacoes)
    variaveis.validar(assunto, origem=universo.origem, publicacoes_citadas=citadas, campo="assunto")
    variaveis.validar(corpo, origem=universo.origem, publicacoes_citadas=citadas, campo="corpo")
    valores_ = valores(universo, enderecos=enderecos)
    return mensagem.congelar(
        assunto=assunto,
        corpo=corpo,
        valores=valores_,
        origem=universo.origem,
        datas_retificadas=universo.datas_retificadas,
        destino=destino(universo, valores_),
        atendimento=getattr(settings, "PORTAL_ATENDIMENTO", ""),
    )


def compor(universo, *, assunto, corpo, enderecos, exemplo=0, motivo=nomes.PRIMEIRO_AVISO):
    """A prévia inteira, sem gravar nada.

    Devolve as contagens, as linhas, a mensagem como sai para uma pessoa real da lista (`exemplo`
    escolhe qual, para "ver outra") e a assinatura. Texto inválido não impede a prévia: ele volta
    como `erro`, com o campo, para a tela mostrar onde está o problema.
    """
    from processo_seletivo.shared.api.problems import DomainError

    recebem = universo.recebem
    previa = {
        "universo": universo,
        "contagens": universo.contagens(),
        "inelegiveis": universo.inelegiveis_por_motivo(),
        "assinatura": assinatura(universo, motivo=motivo),
        "exemplo": None,
        "indice_do_exemplo": 0,
        "erro": None,
    }
    if not (assunto or corpo):
        return previa
    try:
        assunto_final, corpo_final = congelar(
            universo, assunto=assunto, corpo=corpo, enderecos=enderecos
        )
    except DomainError as erro:
        previa["erro"] = erro
        return previa
    if recebem:
        indice = exemplo % len(recebem)
        pessoa = recebem[indice]
        previa["indice_do_exemplo"] = indice
        previa["exemplo"] = {
            "nome": pessoa.inscricao.nome,
            "endereco": pessoa.endereco,
            "assunto_e_corpo": mensagem.para_a_pessoa(
                assunto=assunto_final, corpo=corpo_final, nome_do_candidato=pessoa.inscricao.nome
            ),
        }
    return previa


__all__ = ["NATUREZA_POR_EXTENSO", "assinatura", "compor", "congelar", "destino", "valores"]
