"""Plugin temporário do pytest: registra cada desenho da tela da Ocupação e os estados no HTML.

Não muda o produto nem a suíte: envolve `Template.render` do backend de templates do Django só
durante esta execução, e grava uma linha por desenho num arquivo por processo.
"""

import json
import os
import re
from pathlib import Path

SAIDA = Path(os.environ.get("REGISTRO_DA_OCUPACAO", "registro-da-ocupacao"))
TELAS = {
    "interface/ocupacao.html",
    "interface/ocupacao_acrescimo.html",
    "interface/ocupacao_nao_preenchida.html",
    "interface/ocupacao_historico.html",
}

# Estado -> trecho literal do template que só aquele ramo escreve.
CABECA = {
    "nota_do_cadastro_legado": 'class="nota"',
    "marco_intermediario": "Abrir a ocupação da",
    "quem_le_e_nao_apura": "A presidência não é papel",
    "erro_ao_apurar": "Não foi possível apurar:",
    "erro_no_acrescimo": "Não foi possível acrescentar a vaga:",
    "erro_no_desfazimento_do_acrescimo": "Não foi possível desfazer a vaga acrescida:",
    "erro_na_declaracao_de_nao_preenchida": "Não foi possível declarar a vaga não preenchida:",
    "erro_no_desfazimento_da_declaracao": "Não foi possível desfazer a declaração de vaga",
    "sucesso_apuracao": "<strong>Apuração emitida</strong>",
    "sucesso_faixa_seguinte": "Faixa seguinte emitida",
    "sucesso_acrescimo": "Vaga acrescida: ",
    "sucesso_desfazimento_do_acrescimo": "Vaga acrescida desfeita:",
    "sucesso_declaracao_de_nao_preenchida": "Vaga declarada não preenchida:",
    "sucesso_desfazimento_da_declaracao": "Declaração de vaga não preenchida desfeita:",
    "apuracao_seguinte_emitida_pelo_ato": "foi emitida por este ato",
    "apuracao_seguinte_pendente": "não foi emitida:",
    "proximo_nesta_lista_com_passo": "<strong>Próximo nesta lista:</strong>",
    "proximo_nesta_lista_sem_nada": "Nada mais em aberto nesta lista.",
    "ainda_neste_marco": "<strong>Ainda neste marco:</strong>",
    "retorno_ao_centro": "Voltar ao Centro de Controle do Edital",
}
SECAO = {
    "sem_quadro": "não publicou quadro de vagas",
    "sem_quadro_quem_nao_retifica": "quem elabora Retificações é quem pode declará-la",
    "nao_apurada": "Ocupação ainda não apurada.",
    "apurada": 'aria-label="Vagas, pela apuração vigente"',
    "obsoleta": "Esta apuração está obsoleta.",
    "causa_ordem_sucedida": "a ordem deste recorte foi sucedida",
    "causa_corte_obsoleto": "o corte deste recorte não é o que ela leu",
    "causa_quadro_retificado": "a linha do quadro que ela leu mudou por Retificação",
    "causa_movimento_posterior": "um movimento de vaga alcançou este recorte depois dela",
    "causa_efeito_posterior": "um efeito registrado depois dela",
    "causa_acrescimo_posterior": "uma vaga acrescida ou desfeita depois dela",
    "causa_declaracao_posterior": "uma vaga declarada não preenchida, ou o desfazimento",
    "acrescidas_no_resumo": "Acrescidas depois da publicação</li>",
    "nota_efetivas_por_movimento": "porque um movimento de vaga alcançou",
    "nota_efetivas_por_acrescimo": "As efetivas somam às publicadas",
    "movimento_de_reversao": "Reversão de cota:",
    "declaracao_desfeita_na_lista": "declaração desfeita:",
    "declaracao_que_nao_se_desfaz": "Esta declaração não se desfaz agora",
    "form_desfazer_declaracao": "Desfazer esta declaração",
    "silente_dois_caminhos": "o Edital precisa declarar a reversão, por Retificação",
    "silente_quem_nao_retifica": "que é ato de quem elabora o Edital",
    "form_declarar_nao_preenchida": "Declarar a vaga não preenchida</button>",
    "declaracao_para_quem_nao_apura": "é ato de quem apura a ocupação deste marco",
    "link_historico": "Ver o histórico deste recorte",
    "link_convocacao": "Abrir a convocação deste recorte",
    "sem_inscrito": "<strong>Não se aplica.</strong>",
    "sem_ordem": "ainda não tem ordem emitida",
    "form_apurar": "Apurar a ocupação deste recorte",
    "sucessao_fechada": '<details class="sucessao">',
    "sucessao_aberta": '<details class="sucessao" open>',
    "form_faixa_seguinte": "Pedir a faixa seguinte",
    "faixa_sem_continuacao": "não publicou que admite chamar além da faixa",
    "faixa_sem_regra_de_corte": "não declara regra de corte",
    "lista_de_acrescimos": "Vagas acrescidas depois da publicação</h3>",
    "acrescimo_na_lista": "— acréscimo de",
    "desfazimento_na_lista": "— desfazimento de",
    "acrescimo_com_referencia": " Referência: ",
    "form_desfazer_acrescimo": "Conferir o desfazimento",
    "form_acrescentar": "Conferir o acréscimo",
    "acrescimo_fora_da_linha_geral": "Este Perfil reparte vagas entre modalidades",
}
DECLARACAO = re.compile(r"não preenchidas?\. Fundamento:")
FRASE_DA_VAGA = re.compile(
    r'<p class="aviso" role="status">(?!Este Edital não publicou quadro|Ocupação ainda não '
    r"apurada|<strong>Esta apuração está obsoleta)"
)
CORTE = '<section aria-labelledby="recorte-'


def _estados(html):
    cabeca, *secoes = html.split(CORTE)
    # O que vem depois do último `</section>` é rodapé da moldura, e não estado da tela.
    pagina = [nome for nome, trecho in CABECA.items() if trecho in cabeca.split("<h1>")[-1]]
    blocos = []
    for secao in secoes:
        secao = secao.split("</section>")[0]
        marcas = [nome for nome, trecho in SECAO.items() if trecho in secao]
        if DECLARACAO.search(secao):
            marcas.append("declaracao_na_lista")
        if FRASE_DA_VAGA.search(secao):
            marcas.append("frase_da_vaga")
        if "apurada" in marcas and "obsoleta" not in marcas:
            marcas.append("vigente")
        blocos.append(sorted(marcas))
    return sorted(pagina), blocos


def pytest_configure(config):
    from django.template.backends.django import Template

    if getattr(Template, "_registro_da_ocupacao", False):
        return
    original = Template.render
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivo = SAIDA / f"{os.getpid()}.jsonl"

    def render(self, context=None, request=None):
        html = original(self, context, request)
        nome = getattr(self.template, "name", None)
        if nome in TELAS:
            linha = {
                "teste": os.environ.get("PYTEST_CURRENT_TEST", "").rsplit(" (", 1)[0],
                "tela": nome,
            }
            if nome == "interface/ocupacao.html":
                linha["pagina"], linha["recortes"] = _estados(html)
            else:
                linha["erro"] = 'class="erro"' in html
                linha["form"] = "<form" in html.split("<h1>")[-1]
            with arquivo.open("a", encoding="utf-8") as saida:
                saida.write(json.dumps(linha, ensure_ascii=False) + "\n")
        return html

    Template.render = render
    Template._registro_da_ocupacao = True
