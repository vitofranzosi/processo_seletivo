"""Maquete do Relatório Consolidado de Gestão — dados FICTÍCIOS (estudo de 24/10/2026).

Não é código de produto e não lê banco. Os doze Editais abaixo são inventados; o que este roteiro
garante é que **os totais saem das linhas**, pelas regras propostas no estudo, para que a maquete
não mostre número que a própria metodologia não produziria:

- a espécie de cada Edital é a regra da `099` (cancelado → interrupção; encerrado sem pendência →
  encerramento; o resto → acompanhamento);
- inscrições por vaga é Σ inscrições nos Perfis com vaga imediata ÷ Σ vagas imediatas desses
  Perfis, sobre os Editais não cancelados (D-012 da `040`), e nunca a média das razões;
- vagas com inscrição classificada e habilitada somam só recortes com apuração vigente e
  atualizada, e o denominador dito é o das vagas apuradas;
- fato não público (recurso, convocação, apuração) desce no máximo ao Edital — o nível em que o
  relatório individual já o mostra —, nunca a Perfil ou lista, e some em Edital com menos de cinco
  inscrições enviadas.

Uso: python gerar_maquete.py  →  escreve ../maquete.html; o PDF sai pelo Chrome sem cabeça.
"""

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI.parent / "maquete.html"

REFERENCIA = "24/10/2026, 14h00"
CRITERIO = "Editais com primeira publicação entre 01/01/2026 e 30/06/2026"
PAGINAS = 6


@dataclass
class Perfil:
    nome: str
    vagas: int  # imediatas
    reservadas: int  # das imediatas, em listas de modalidade reservada
    cr: str  # "" | "limitado" | "ilimitado"
    inscricoes: int


@dataclass
class Edital:
    numero: str
    titulo: str
    publicado: str  # dd/mm — primeira publicação
    situacao: str  # Publicado | Encerrado | Cancelado
    desfecho: str = ""  # dd/mm do encerramento ou cancelamento
    perfis: list = field(default_factory=list)
    marcos: int = 0  # marcos de classificação declarados
    definitivos: int = 0  # marcos com resultado definitivo vigente em todas as listas
    sem_resultado: int = 0  # marcos sem nenhum resultado publicado
    retificacoes: int = 0
    prorrogado: bool = False
    envios: dict = field(default_factory=dict)  # mês → inscrições enviadas
    recursos: tuple = (0, 0, 0, 0, 0)  # apresentados, não admitidos, indeferidos, deferidos, aguardando
    apuradas: int = 0  # vagas em recortes com apuração vigente e atualizada
    habilitadas: int = 0  # dessas, com inscrição classificada e habilitada
    desatualizadas: int = 0  # vagas em recortes com apuração desatualizada
    convocacoes: tuple = (0, 0, 0, 0, 0)  # realizadas, aceitas, aguardando, prazo vencido, outros desfechos
    posteriores: int = 0  # registros depois do encerramento

    @property
    def vagas(self):
        return sum(p.vagas for p in self.perfis)

    @property
    def inscricoes(self):
        return sum(p.inscricoes for p in self.perfis)

    @property
    def cancelado(self):
        return self.situacao == "Cancelado"

    @property
    def pendencias(self):
        if self.cancelado:
            return []
        p = []
        if self.sem_resultado:
            p.append(("resultado ainda não divulgado", self.sem_resultado))
        faltam = self.marcos - self.definitivos - self.sem_resultado
        if faltam:
            p.append(("resultado definitivo ainda não publicado", faltam))
        if self.recursos[4]:
            p.append(("recurso aguardando decisão", self.recursos[4]))
        if self.desatualizadas:
            p.append(("apuração das vagas desatualizada", 1))
        if self.convocacoes[2]:
            p.append(("convocação aguardando resposta", self.convocacoes[2]))
        if self.convocacoes[3]:
            p.append(("convocação com prazo encerrado sem registro de resposta", self.convocacoes[3]))
        return p

    @property
    def especie(self):
        if self.cancelado:
            return "interrupção"
        if self.situacao == "Encerrado" and not self.pendencias:
            return "encerramento"
        return "acompanhamento"


def P(nome, vagas, insc, reservadas=0, cr=""):
    return Perfil(nome, vagas, reservadas, cr, insc)


EDITAIS = [
    Edital("48/2025", "Curso de Aperfeiçoamento em Docência na EaD", "08/01", "Encerrado", "14/04",
           [P("Cursista — turma única", 50, 74, reservadas=10)], marcos=1, definitivos=1,
           envios={1: 41, 2: 33}, recursos=(2, 1, 1, 0, 0), apuradas=50, habilitadas=50,
           convocacoes=(58, 47, 0, 0, 11), posteriores=0),
    Edital("03/2026", "Tutores a distância — Licenciatura em Letras", "19/01", "Encerrado", "22/05",
           [P("Tutor — Polo Vila Azul", 4, 61), P("Tutor — Polo Serra Alta", 3, 22),
            P("Tutor — Polo Rio Claro", 3, 9), P("Tutor — Polo Mangue Seco", 2, 3)],
           marcos=4, definitivos=4, retificacoes=1, envios={2: 95},
           recursos=(6, 2, 3, 1, 0), apuradas=12, habilitadas=11, convocacoes=(14, 11, 0, 0, 3)),
    Edital("05/2026", "Professores formadores — Especialização em Educação Profissional", "02/02",
           "Encerrado", "05/06", [P("Formador — Didática", 2, 18), P("Formador — Avaliação", 2, 7),
                                  P("Formador — Tecnologias", 1, 4)],
           marcos=3, definitivos=3, envios={2: 29}, recursos=(3, 0, 3, 0, 0), apuradas=5,
           habilitadas=5, convocacoes=(6, 5, 0, 0, 1), posteriores=2),
    Edital("07/2026", "Especialização em Informática na Educação — ingresso discente", "23/02",
           "Encerrado", "30/07", [P("Polo Vila Azul", 40, 212, reservadas=20),
                                  P("Polo Serra Alta", 40, 96, reservadas=20)],
           marcos=2, definitivos=2, retificacoes=2, prorrogado=True, envios={3: 201, 4: 107},
           recursos=(9, 3, 5, 1, 0), apuradas=80, habilitadas=74, convocacoes=(96, 71, 3, 0, 22),
           posteriores=5),
    Edital("09/2026", "Técnico em Administração, modalidade EaD", "09/03", "Publicado",
           perfis=[P("Polo Vila Azul", 35, 140, reservadas=17), P("Polo Serra Alta", 35, 61, reservadas=17),
                   P("Polo Rio Claro", 35, 28, reservadas=17)],
           marcos=3, definitivos=3, envios={3: 118, 4: 111}, recursos=(7, 1, 6, 0, 0),
           apuradas=70, habilitadas=70, desatualizadas=35, convocacoes=(93, 52, 9, 4, 28)),
    Edital("11/2026", "Cadastro de reserva de revisores de texto", "16/03", "Encerrado", "26/06",
           [P("Revisor de texto", 0, 27, cr="ilimitado")], marcos=1, definitivos=1, envios={3: 27},
           recursos=(1, 0, 1, 0, 0), convocacoes=(2, 2, 0, 0, 0)),
    Edital("12/2026", "Designer instrucional", "30/03", "Encerrado", "10/07",
           [P("Designer instrucional", 1, 33, cr="limitado"), P("Ilustrador", 0, 12, cr="limitado")],
           marcos=2, definitivos=2, envios={4: 45}, recursos=(2, 0, 2, 0, 0), apuradas=1,
           habilitadas=1, convocacoes=(1, 0, 0, 1, 0)),
    Edital("14/2026", "Curso de extensão em Libras — nível básico", "13/04", "Encerrado", "29/06",
           [P("Cursista — turma única", 60, 31)], marcos=1, definitivos=1, envios={4: 12, 5: 19},
           apuradas=60, habilitadas=29, convocacoes=(31, 29, 0, 0, 2)),
    Edital("15/2026", "Professores mediadores — Pedagogia", "27/04", "Encerrado", "18/08",
           [P("Mediador — Fundamentos", 6, 14), P("Mediador — Estágio", 4, 2)],
           marcos=2, definitivos=1, sem_resultado=1, envios={5: 16}, apuradas=6, habilitadas=6,
           convocacoes=(6, 6, 0, 0, 0)),
    Edital("17/2026", "Tutores a distância — Pedagogia", "11/05", "Cancelado", "02/06",
           [P("Tutor — turma única", 8, 14)], marcos=1, envios={5: 14}),
    Edital("18/2026", "Especialização em Gestão Pública — ingresso discente", "25/05", "Publicado",
           perfis=[P("Polo Vila Azul", 30, 88, reservadas=15), P("Polo Rio Claro", 30, 51, reservadas=15)],
           marcos=2, retificacoes=1, prorrogado=True, envios={6: 92, 7: 47},
           recursos=(11, 2, 0, 0, 9)),
    Edital("21/2026", "Bolsista de apoio técnico ao laboratório", "15/06", "Encerrado", "04/09",
           [P("Apoio técnico", 2, 19)], marcos=1, definitivos=1, envios={6: 11, 7: 8},
           recursos=(1, 0, 1, 0, 0), apuradas=2, habilitadas=2, convocacoes=(3, 2, 0, 0, 1),
           posteriores=1),
]

PLURAIS = {
    "convocação aguardando resposta": "convocações aguardando resposta",
    "convocação com prazo encerrado sem registro de resposta": "convocações com prazo encerrado sem registro de resposta",
    "resultado ainda não divulgado": "resultados ainda não divulgados",
    "resultado definitivo ainda não publicado": "resultados definitivos ainda não publicados",
    "recurso aguardando decisão": "recursos aguardando decisão",
}

MESES = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun", 7: "jul", 8: "ago"}


def br(n):
    return f"{n:,}".replace(",", ".")


def dec(x):
    return f"{x:.1f}".replace(".", ",")


def plural(n, s, p):
    return s if n == 1 else p


# --- Consolidação --------------------------------------------------------------------------------

ativos = [e for e in EDITAIS if not e.cancelado]
cancelados = [e for e in EDITAIS if e.cancelado]
por_situacao = Counter(e.situacao for e in EDITAIS)
por_especie = Counter(e.especie for e in EDITAIS)
perfis = [p for e in ativos for p in e.perfis]
vagas = sum(e.vagas for e in ativos)
reservadas = sum(p.reservadas for p in perfis)
inscricoes = sum(e.inscricoes for e in ativos)
com_vaga = [p for p in perfis if p.vagas]
so_cr = [p for p in perfis if not p.vagas]
editais_so_cr = [e for e in ativos if e.vagas == 0]
numerador = sum(p.inscricoes for p in com_vaga)
razao = numerador / vagas
abaixo = [(e, p) for e in ativos for p in e.perfis if p.vagas and p.inscricoes < p.vagas]
sem_procura = [(e, p) for e, p in abaixo if p.inscricoes == 0]
marcos = sum(e.marcos for e in ativos)
definitivos = sum(e.definitivos for e in ativos)
editais_definitivos = [e for e in ativos if e.marcos and e.definitivos == e.marcos]
apuradas = sum(e.apuradas for e in ativos)
habilitadas = sum(e.habilitadas for e in ativos)
desatualizadas = sum(e.desatualizadas for e in ativos)
nao_apuradas = vagas - apuradas - desatualizadas
rec = [sum(e.recursos[i] for e in ativos) for i in range(5)]
conv = [sum(e.convocacoes[i] for e in ativos) for i in range(5)]
retificacoes = sum(e.retificacoes for e in EDITAIS)
editais_retificados = sum(1 for e in EDITAIS if e.retificacoes)
prorrogados = sum(1 for e in EDITAIS if e.prorrogado)
encerrados_pendentes = [e for e in ativos if e.situacao == "Encerrado" and e.pendencias]
com_posteriores = [e for e in ativos if e.posteriores]
posteriores = sum(e.posteriores for e in ativos)
publicados_abertos = [e for e in ativos if e.situacao == "Publicado"]
pendencias = Counter()
editais_por_pendencia = Counter()
for e in ativos:
    for tipo, n in e.pendencias:
        pendencias[tipo] += n
        editais_por_pendencia[tipo] += 1
envios = Counter()
for e in EDITAIS:
    envios.update(e.envios)
assert sum(envios.values()) == sum(e.inscricoes for e in EDITAIS), "envios por mês ≠ inscrições"
for e in EDITAIS:
    assert sum(e.envios.values()) == e.inscricoes, e.numero
    assert e.habilitadas <= e.apuradas
    assert e.apuradas + e.desatualizadas <= e.vagas, e.numero
    assert e.convocacoes[1] + e.convocacoes[2] + e.convocacoes[3] + e.convocacoes[4] == e.convocacoes[0], e.numero
    assert sum(e.recursos[1:]) == e.recursos[0], e.numero


# --- HTML ----------------------------------------------------------------------------------------

CSS = (AQUI / "maquete.css").read_text(encoding="utf-8")


def faixa(n):
    return (
        '<div class="faixa"><span><span class="maquete">MAQUETE</span> — dados fictícios</span>'
        f"<span>Relatório consolidado · 1º semestre de 2026 · dados até {REFERENCIA} · "
        f"emissão nº 1 · página {n} de {PAGINAS}</span></div>"
    )


def numero(valor, rotulo, base, de=None):
    de_ = f" <small>de {de}</small>" if de is not None else ""
    return (
        f'<div class="numero"><div class="valor">{valor}{de_}</div>'
        f'<div class="rotulo">{rotulo}</div><div class="base">{base}</div></div>'
    )


def folha(n, corpo):
    return f'<section class="folha">{faixa(n)}{corpo}</section>'


ORGAO = (
    '<div class="orgao">Ministério da Educação · <strong>Instituto Federal do Espírito Santo</strong>'
    "<br>Centro de Referência em Formação e em Educação a Distância</div>"
)

# Folha 1 — Panorama
pagina1 = f"""
{ORGAO}
<h1>Relatório Consolidado de Gestão dos Processos Seletivos</h1>
<p class="especie">1º semestre de 2026 — {len(EDITAIS)} Editais</p>
<p class="natureza">Relatório gerencial com base nos registros do GPS. Não é ato administrativo e não substitui as publicações oficiais de cada Edital.</p>
<div class="ficha">
  <div><span class="r">Conjunto analisado</span>{CRITERIO}, da unidade Cefor</div>
  <div><span class="r">Data de referência</span>dados até {REFERENCIA}: o relatório mostra a situação de cada Edital neste instante, e não a de 30/06</div>
  <div><span class="r">Situação no GPS</span>{por_situacao['Encerrado']} encerrados · {por_situacao['Publicado']} publicados · {por_situacao['Cancelado']} cancelado</div>
  <div><span class="r">Situação das providências</span><span class="pendente">{len([e for e in ativos if e.pendencias])} Editais com providência registrada em curso</span> · {por_especie['encerramento']} sem nenhuma</div>
</div>

<h2>Visão geral</h2>
<p class="sintese">Os {len(EDITAIS)} Editais publicados no semestre ofereceram <strong>{br(vagas)} vagas imediatas</strong> em {len(perfis)} perfis de vaga — {br(reservadas)} delas em listas reservadas — e abriram cadastro de reserva em {len(so_cr) + sum(1 for p in perfis if p.vagas and p.cr)} perfis, {len(so_cr)} dos quais só de cadastro de reserva. Receberam <strong>{br(inscricoes)} inscrições enviadas</strong>, sem contar as {sum(e.inscricoes for e in cancelados)} do Edital cancelado. Em {len(editais_definitivos)} Editais todos os resultados definitivos estão publicados. Há <strong>{br(habilitadas)} vagas com inscrição classificada e habilitada</strong> entre as {br(apuradas)} vagas já apuradas, e <strong>{br(conv[1])} convocações aceitas</strong> de {br(conv[0])} realizadas.</p>

<div class="numeros">
  {numero(br(vagas), "vagas imediatas", f"em {len(com_vaga)} de {len(perfis)} perfis; {len(so_cr)} perfis só de cadastro de reserva. Fora o Edital cancelado")}
  {numero(br(inscricoes), "inscrições enviadas", f"inscrições, e não pessoas: a mesma pessoa pode se inscrever em mais de um Edital. {len(publicados_abertos)} Editais seguem publicados")}
  {numero(dec(razao), "inscrições por vaga", f"{br(numerador)} inscrições para {br(vagas)} vagas, só nos perfis com vaga imediata. Não é média dos Editais")}
  {numero(len(editais_definitivos), "Editais com todos os resultados definitivos", f"{definitivos} de {marcos} resultados previstos já são definitivos", de=len(ativos))}
  {numero(br(habilitadas), "vagas com inscrição classificada e habilitada", f"nas vagas já apuradas; {br(nao_apuradas + desatualizadas)} vagas ainda sem apuração atualizada. Não é matrícula", de=br(apuradas))}
  {numero(br(conv[1]), "convocações aceitas", f"{conv[2]} aguardando resposta; {conv[3]} com prazo encerrado sem registro de resposta", de=br(conv[0]))}
</div>

<div class="atencao">
  <h2>Pontos de atenção</h2>
  <ol>
    <li><strong>{len(encerrados_pendentes)} Editais estão encerrados no GPS, mas ainda têm providência registrada.</strong> Encerrar o Edital fecha as inscrições, e convocações, recursos e apurações continuam correndo depois. Detalhe na página 4.</li>
    <li><strong>{len(com_posteriores)} Editais tiveram registros depois do encerramento</strong> — {posteriores} registros no total. Um relatório emitido antes deles mostraria números diferentes.</li>
    <li><strong>O GPS não registra matrículas.</strong> Este relatório mostra convocações aceitas, e não matrículas efetivadas. A confirmação vem do registro acadêmico.</li>
  </ol>
</div>
"""

# Folha 2 — Oferta e procura
linhas_editais = ""
for e in EDITAIS:
    if e.cancelado:
        razao_e = '<span class="aus">cancelado</span>'
    elif e.vagas == 0:
        razao_e = '<span class="aus">não se aplica</span>'
    else:
        num_e = sum(p.inscricoes for p in e.perfis if p.vagas)
        razao_e = dec(num_e / e.vagas)
    marca = ""
    linhas_editais += (
        f"<tr><td>{e.numero}</td><td>{e.titulo}</td><td class='n'>{len(e.perfis)}</td>"
        f"<td class='n'>{e.vagas if e.vagas else '<span class=aus>só CR</span>'}</td>"
        f"<td class='n'>{e.inscricoes}{marca}</td><td class='n'>{razao_e}</td></tr>"
    )
linhas_meses = "".join(
    f"<tr><td>{MESES[m]}/2026</td><td class='n'>{envios[m]}</td>"
    f"<td><span class='barra' data-v='{envios[m]}'>{'▇' * round(envios[m] / 12)}</span></td></tr>"
    for m in sorted(envios)
)
linhas_abaixo = "".join(
    f"<li>{e.numero} — {p.nome}: {p.inscricoes} {plural(p.inscricoes, 'inscrição', 'inscrições')} para {p.vagas} vagas</li>"
    for e, p in abaixo
)
pagina2 = f"""
<h2>Oferta e procura</h2>
<div class="duas">
<div>
<h3>O que foi oferecido</h3>
<table><tbody>
<tr><td>Vagas imediatas</td><td class="n">{br(vagas)}</td></tr>
<tr><td>— em listas de ampla concorrência</td><td class="n">{br(vagas - reservadas)}</td></tr>
<tr><td>— em listas reservadas</td><td class="n">{br(reservadas)}</td></tr>
<tr><td>Perfis de vaga</td><td class="n">{len(perfis)}</td></tr>
<tr><td>— só cadastro de reserva</td><td class="n">{len(so_cr)}</td></tr>
<tr><td>Edital cancelado (fora dos totais)</td><td class="n">{sum(e.vagas for e in cancelados)} vagas</td></tr>
</tbody></table>
<p class="nota">As listas reservadas não são somadas por modalidade: cada Edital nomeia as suas, e o GPS não tem catálogo comum que permita dizer, por exemplo, quantas vagas foram para pessoas com deficiência em todos eles.</p>
</div>
<div>
<h3>Procura ao longo do semestre</h3>
<table><thead><tr><th>Mês do envio</th><th class="n">Inscrições</th><th></th></tr></thead><tbody>{linhas_meses}</tbody></table>
<p class="nota">Envios dos Editais do conjunto, pela data em que cada inscrição foi enviada; inclui o Edital cancelado. {prorrogados} Editais tiveram o prazo de inscrição prorrogado.</p>
</div>
</div>

<h3>Por Edital</h3>
<table>
<thead><tr><th>Edital</th><th>Seleção</th><th class="n">Perfis</th><th class="n">Vagas imediatas</th><th class="n">Inscrições enviadas</th><th class="n">Inscrições por vaga</th></tr></thead>
<tbody>{linhas_editais}</tbody>
</table>
<p class="nota">Inscrições por vaga de cada Edital conta só os perfis com vaga imediata. Editais de natureza diferente — cursistas, tutores, bolsistas — não são comparáveis entre si por esta razão, e a tabela não os ordena por ela.</p>

<h3>Perfis com procura menor que a oferta</h3>
<ul class="compacta">{linhas_abaixo}</ul>
<p class="nota">Fato aritmético, com o período de inscrições encerrado. Ele não diz a causa: divulgação, calendário, requisitos e oferta concorrente não são registrados pelo GPS.</p>
"""

# Folha 3 — Execução
pagina3 = f"""
<h2>Execução das seleções</h2>
<div class="duas">
<div>
<h3>Situação dos Editais</h3>
<table><thead><tr><th>Espécie do relatório individual</th><th class="n">Editais</th></tr></thead><tbody>
<tr><td>De encerramento — encerrado, sem providência registrada</td><td class="n">{por_especie['encerramento']}</td></tr>
<tr><td>De acompanhamento — encerrado com providência em curso</td><td class="n">{len(encerrados_pendentes)}</td></tr>
<tr><td>De acompanhamento — ainda publicado</td><td class="n">{len(publicados_abertos)}</td></tr>
<tr><td>De interrupção — cancelado</td><td class="n">{por_especie['interrupção']}</td></tr>
</tbody></table>
<p class="nota">A espécie é a do relatório individual de cada Edital, pela mesma regra. Encerrado no GPS quer dizer inscrições fechadas, e não seleção concluída.</p>
</div>
<div>
<h3>Alterações</h3>
<table><tbody>
<tr><td>Retificações publicadas</td><td class="n">{retificacoes}</td></tr>
<tr><td>Editais retificados</td><td class="n">{editais_retificados} de {len(EDITAIS)}</td></tr>
<tr><td>Editais com prazo de inscrição prorrogado</td><td class="n">{prorrogados}</td></tr>
</tbody></table>
<p class="nota">A prorrogação é uma Retificação que adia o término das inscrições; outras mudanças de data aparecem só no relatório de cada Edital.</p>
</div>
</div>

<h3>Recursos</h3>
<table><thead><tr><th class="n">Apresentados</th><th class="n">Não admitidos</th><th class="n">Indeferidos</th><th class="n">Deferidos</th><th class="n">Aguardando decisão</th></tr></thead>
<tbody><tr><td class="n">{rec[0]}</td><td class="n">{rec[1]}</td><td class="n">{rec[2]}</td><td class="n">{rec[3]}</td><td class="n">{rec[4]}</td></tr></tbody></table>
<p class="nota">Recursos contra etapas e resultados diferentes, somados como pedidos. Não há taxa de deferimento do conjunto: um recurso de prova objetiva e um de análise curricular não são o mesmo objeto.</p>

<h2>Resultados</h2>
<div class="duas">
<div>
<h3>Resultados publicados</h3>
<table><tbody>
<tr><td>Resultados previstos nos Editais (um por marco de classificação de cada perfil)</td><td class="n">{marcos}</td></tr>
<tr><td>— com resultado definitivo vigente</td><td class="n">{definitivos}</td></tr>
<tr><td>— só com resultado preliminar</td><td class="n">{marcos - definitivos - sum(e.sem_resultado for e in ativos)}</td></tr>
<tr><td>— ainda não divulgados</td><td class="n">{sum(e.sem_resultado for e in ativos)}</td></tr>
</tbody></table>
</div>
<div>
<h3>Vagas imediatas</h3>
<table><tbody>
<tr><td>Com inscrição classificada e habilitada</td><td class="n">{br(habilitadas)}</td></tr>
<tr><td>Apuradas sem inscrição habilitada para elas</td><td class="n">{br(apuradas - habilitadas)}</td></tr>
<tr><td>Com apuração desatualizada</td><td class="n">{br(desatualizadas)}</td></tr>
<tr><td>Ainda não apuradas</td><td class="n">{br(nao_apuradas)}</td></tr>
<tr><td><strong>Total</strong></td><td class="n"><strong>{br(vagas)}</strong></td></tr>
</tbody></table>
<p class="nota">Classificada e habilitada é a apuração da vaga, e não matrícula, nem aceite.</p>
</div>
</div>

<h3>Convocações</h3>
<table><thead><tr><th class="n">Realizadas</th><th class="n">Convocação aceita</th><th class="n">Aguardando resposta</th><th class="n">Prazo encerrado sem registro</th><th class="n">Outros desfechos</th></tr></thead>
<tbody><tr><td class="n">{conv[0]}</td><td class="n">{conv[1]}</td><td class="n">{conv[2]}</td><td class="n">{conv[3]}</td><td class="n">{conv[4]}</td></tr></tbody></table>
<p class="nota">Outros desfechos são desistência, não atendimento, indeferimento da documentação e os demais registrados pela comissão. Prazo encerrado sem registro não é "não atendida": o não atendimento só existe quando a comissão o registra.</p>
"""

# Folha 4/5 — Pontos de atenção
linhas_pend = ""
for e in ativos:
    if not e.pendencias:
        continue
    itens = "; ".join(f"{n} {PLURAIS.get(t, t)}" if n > 1 else t for t, n in e.pendencias)
    linhas_pend += f"<tr><td>{e.numero}</td><td>{e.situacao}{(' em ' + e.desfecho) if e.desfecho else ''}</td><td>{itens}</td></tr>"
linhas_tipos = "".join(
    f"<tr><td>{t}</td><td class='n'>{editais_por_pendencia[t]}</td><td class='n'>{pendencias[t]}</td></tr>"
    for t in pendencias
)
pagina4 = f"""
<h2>Pontos de atenção</h2>
<h3>Providências registradas em curso</h3>
<table><thead><tr><th>Tipo</th><th class="n">Editais</th><th class="n">Ocorrências</th></tr></thead><tbody>{linhas_tipos}</tbody></table>
<p class="nota">Cada tipo é uma regra do relatório individual. O conjunto não cria pendência nova; ele conta as de cada Edital.</p>

<h3>Por Edital</h3>
<table><thead><tr><th>Edital</th><th>Situação no GPS</th><th>Providências em curso</th></tr></thead><tbody>{linhas_pend}</tbody></table>

<h3>Registros depois do encerramento</h3>
<table><thead><tr><th>Edital</th><th>Encerrado em</th><th class="n">Registros posteriores</th></tr></thead><tbody>
{''.join(f"<tr><td>{e.numero}</td><td>{e.desfecho}</td><td class='n'>{e.posteriores}</td></tr>" for e in com_posteriores)}
</tbody></table>
<p class="nota">Registros posteriores não são irregularidade: suplência e resposta a convocação depois do encerramento podem ser exatamente o que o Edital previa. O que eles mostram é que encerrado não quer dizer congelado.</p>

<h3>O que este relatório não diz</h3>
<ul class="compacta">
<li>quantas <strong>pessoas</strong> participaram: o GPS conta inscrições, e a mesma pessoa pode estar em vários Editais;</li>
<li>quantas <strong>matrículas</strong> foram efetivadas, nem quantas vagas foram de fato preenchidas;</li>
<li>se o cronograma foi <strong>cumprido</strong>: o GPS guarda as datas previstas e as dos atos registrados, e não a data em que cada evento aconteceu;</li>
<li>a <strong>causa</strong> de procura alta ou baixa, nem comparação de desempenho entre Editais de natureza diferente.</li>
</ul>
"""

# Folhas 5 e 6 — Anexo técnico
linhas_rel = "".join(
    f"<tr><td>{e.numero}</td><td>{e.titulo}</td><td>{e.publicado}/{'2026'}</td>"
    f"<td>{e.situacao}{(' em ' + e.desfecho) if e.desfecho else ''}</td><td>{e.especie}</td></tr>"
    for e in EDITAIS
)
pagina5 = f"""
<p class="anexo-titulo"><strong>Anexo técnico</strong></p>
<h2>A1. Editais considerados</h2>
<table><thead><tr><th>Edital</th><th>Seleção</th><th>1ª publicação</th><th>Situação no GPS</th><th>Espécie</th></tr></thead><tbody>{linhas_rel}</tbody></table>
<p class="nota">Cada Edital tem relatório individual próprio, emitido na tela dele, com etapas, listas, cronograma e documentos oficiais. A página pública de cada seleção é a referência dos atos.</p>

<h2>A2. Critério do conjunto</h2>
<table class="datas"><tbody>
<tr><td>Critério</td><td>{CRITERIO}. A data é a da primeira publicação do Edital no GPS, e não a das Retificações.</td></tr>
<tr><td>Unidade</td><td>Cefor — o relatório só alcança Editais da unidade de quem o emite.</td></tr>
<tr><td>Ficaram fora</td><td>3 Editais com número de 2026 ainda não publicados (em elaboração ou em revisão), e os publicados a partir de 01/07/2026. O Edital 48/2025 entrou: foi publicado em 08/01/2026.</td></tr>
<tr><td>Escolha manual</td><td>nenhuma: todos os Editais do critério foram mantidos.</td></tr>
<tr><td>Data de referência</td><td>{REFERENCIA}. O relatório não reconstitui o passado: emitido em outra data, pode trazer números diferentes para os mesmos Editais.</td></tr>
</tbody></table>
"""

pagina6 = f"""
<h2>A3. Definição de cada número</h2>
<dl class="defs">
<dt>Vagas imediatas</dt><dd>Soma das vagas imediatas publicadas no conteúdo vigente de cada Edital, já com as Retificações. Cadastro de reserva não é vaga e não entra. Fonte: versão consolidada vigente. Aditivo.</dd>
<dt>Inscrições enviadas</dt><dd>Inscrições com envio concluído e protocolo. Unidade: inscrição, e não pessoa. Inscrições iniciadas e não enviadas não entram. Aditivo; parcial enquanto houver período aberto.</dd>
<dt>Inscrições por vaga</dt><dd>Soma das inscrições nos perfis com vaga imediata dividida pela soma dessas vagas, com uma casa. Perfis só de cadastro de reserva ficam fora dos dois termos. Nunca média das razões dos Editais.</dd>
<dt>Resultados definitivos</dt><dd>Marcos de classificação com resultado definitivo vigente em todas as listas. Resultado preliminar substituído pelo definitivo conta uma vez.</dd>
<dt>Vagas com inscrição classificada e habilitada</dt><dd>Soma das apurações de ocupação vigentes e atualizadas, do último marco de cada perfil. Recorte sem apuração conta como "ainda não apurada"; apuração desatualizada não entra na soma. Não é matrícula nem aceite.</dd>
<dt>Convocações</dt><dd>Convocações vigentes, contadas pela cadeia de cada uma, com o desfecho registrado mais recente. A mesma inscrição chamada duas vezes conta duas convocações.</dd>
<dt>Recursos</dt><dd>Pedidos de recurso, pela situação: não admitido, indeferido, deferido (qualquer decisão que não seja indeferimento) e aguardando.</dd>
<dt>Providência em curso</dt><dd>As do relatório individual: resultado não divulgado ou só preliminar, recurso ou reavaliação pendente, apuração desatualizada, convocação sem desfecho.</dd>
</dl>

<h2>A4. Limitações</h2>
<ul class="compacta">
<li>Fatos não públicos — recursos, convocações, apurações — aparecem no total do conjunto e, nas providências, por Edital, como no relatório individual; nunca por perfil ou por lista. Edital com menos de 5 inscrições enviadas tem o detalhe omitido, e continua nos totais.</li>
<li>As listas reservadas não se somam entre Editais por modalidade, e localidade de polo é texto livre do Edital: nenhuma das duas vira agrupamento.</li>
<li>O GPS não registra homologação, cancelamento ou desistência de inscrição, presença em prova, nem matrícula.</li>
</ul>

<h2>A5. Emissão</h2>
<table class="datas"><tbody>
<tr><td>Emissão</td><td>nº 1 do relatório consolidado da unidade Cefor, registrada na trilha de auditoria com o critério, a relação dos Editais, o instante dos dados e o resumo do arquivo.</td></tr>
<tr><td>Emitido por</td><td>Gestão da unidade (identificação na trilha).</td></tr>
<tr><td>Resumo SHA-256</td><td class="hash">(calculado na emissão — a maquete não o tem)</td></tr>
</tbody></table>
"""

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório consolidado — maquete</title>
<style>{CSS}</style>
</head>
<body>
{folha(1, pagina1)}
{folha(2, pagina2)}
{folha(3, pagina3)}
{folha(4, pagina4)}
{folha(5, pagina5)}
{folha(6, pagina6)}
</body>
</html>
"""

DESTINO.write_text(html, encoding="utf-8")
print(f"vagas={vagas} reservadas={reservadas} inscricoes={inscricoes} razao={dec(razao)}")
print(f"especies={dict(por_especie)} situacoes={dict(por_situacao)}")
print(f"apuradas={apuradas} habilitadas={habilitadas} desatualizadas={desatualizadas} nao_apuradas={nao_apuradas}")
print(f"recursos={rec} convocacoes={conv} pendencias={dict(pendencias)}")
print(f"abaixo={[(e.numero, p.nome) for e, p in abaixo]} envios={dict(envios)}")
