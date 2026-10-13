"""As unidades semânticas do catálogo, por chave. O identificador LIB-NNNN é atribuído na ordem
de descoberta (Edital 91, depois 92, depois 01), e a do consolidado por último.

Campos: t título · fam família · cls classificação de reuso · ori origem (A–E) · cx complexidade
preliminar · fonte · fin finalidade · ctx contexto · var variáveis · dep dependências · eq condições
de equivalência · imp o que impede o reuso · obr informações obrigatórias · ordem · trad contexto ao
tradutor · vis elementos visuais · mont montagem · pend pendências · dec decisões humanas · jur
implicação jurídica.
"""

PDF = "backend/processo_seletivo/publicacoes/infrastructure/pdf.py"
VOC = "backend/processo_seletivo/publicacoes/domain/vocabulario_da_regra.py"

FAMILIAS = {
    "ATO": ("Abertura, estrutura e fecho do ato", "A identidade do ato e a navegação no documento."),
    "GER": ("Disposições gerais", "Regras de condução, canais e efeitos gerais do certame, em texto livre."),
    "OFE": ("Oferta, público e certificação", "O que é ofertado e para quem; texto livre."),
    "REQ": ("Requisitos de participação", "Condições que a pessoa precisa cumprir para concorrer."),
    "PER": ("Perfis, vagas e modalidades", "A oferta estruturada: Perfis, quantidades e listas de concorrência."),
    "CLA": ("Classificação", "Como a ordem é produzida, cortada, desempatada e contestada."),
    "INS": ("Inscrição", "Como, quando e quantas vezes se inscrever."),
    "DOC": ("Documentos e anexos", "O que entregar, quem entrega e onde estão os modelos."),
    "AFI": ("Ações afirmativas e acessibilidade", "Verificação da autodeclaração e atendimento à pessoa com deficiência."),
    "ETA": ("Etapas de avaliação", "Fichas das Etapas: caráter, peso, nota, resultado e datas."),
    "CRO": ("Cronograma", "A tabela de Eventos e cada tipo de Evento."),
    "REC": ("Recursos", "Como recorrer, contra o quê e o que não se admite; texto livre."),
    "CON": ("Convocação e matrícula", "Chamada, suplência, matrícula e o Requerimento de Matrícula."),
}

# O que vale para a família inteira, quando a unidade não diz outra coisa. Desde a rodada 2, `vis` lista
# apoios visuais **possíveis**, e `mont` registra fatos que um corte de vídeo precisa respeitar — nenhum
# dos dois decide a solução linguística, que é do profissional de Libras.
PADRAO = {
    "ATO": dict(vis="Possíveis: legenda ou cartela com os dados de identificação.",
                mont="Abre ou fecha o ato; o rodapé se repete por página no papel e não tem conteúdo próprio."),
    "GER": dict(vis="Possíveis: endereços, e-mails e horários também por escrito.",
                mont="Depende do contexto da seção em que está; isolado, perde o tema."),
    "OFE": dict(vis="Possíveis: números (horas, meses) também por escrito.", mont="Depende do contexto da seção."),
    "REQ": dict(vis="Possíveis: a lista de requisitos na tela.",
                mont="Cada requisito é uma condição própria; a lista vale para o Perfil ou o grupo indicado antes dela."),
    "PER": dict(vis="Tabelas pedem decisão de tratamento visual (a tabela na tela, uma linha por vez, ou outra).",
                mont="Tabelas, frases de reversão e de convocação e blocos de Perfil se referem uns aos outros."),
    "CLA": dict(vis="Possíveis: rótulos (Ordem, Corte, Recurso…) e números também por escrito.",
                mont="As frases de um marco formam um bloco: separadas, algumas perdem o referente."),
    "INS": dict(vis="Possíveis: canal, prazos e limites também por escrito.", mont="Depende do contexto da seção."),
    "DOC": dict(vis="Possíveis: nome do documento e alínea também por escrito.",
                mont="O documento vale para o destinatário dito no cabeçalho do grupo; isolado, perde o destinatário."),
    "AFI": dict(vis="Possíveis: termos da política afirmativa também por escrito.",
                mont="Depende da modalidade a que se refere."),
    "ETA": dict(vis="Possíveis: a ficha da Etapa e as datas também por escrito.", mont="Uma Etapa se refere a Eventos e a marcos."),
    "CRO": dict(vis="Tabela de datas: decisão de tratamento visual (a tabela inteira, um Evento por vez, ou outra).",
                mont="Cada Evento se liga a uma Etapa, a um resultado ou a um prazo descrito em outra parte."),
    "REC": dict(vis="Possíveis: canal e prazo também por escrito.", mont="Depende do objeto do recurso, dito antes ou em outra seção."),
    "CON": dict(vis="Possíveis: prazos e canais também por escrito.", mont="Depende do contexto da seção."),
}

DEC_PADRAO = [
    "Limite linguístico do vídeo: se a unidade é gravada sozinha ou só dentro do bloco da seção.",
    "Tradução validada por profissional de Libras antes de qualquer reuso.",
]

U = {}


def u(k, **kw):
    U[k] = kw


# ── ATO ─────────────────────────────────────────────────────────────────────────────────────────
u("orgao", t="Identificação do órgão emissor", fam="ATO", cls="EXATA", ori="A+E", cx="baixa",
  fonte=f"{PDF} — `INSTITUICAO` (l. 979) e `linhas_do_orgao` (l. 985); linhas da Unidade de `unidades/unidades.json`, congeladas na Publicação (060)",
  fin="Dizer qual órgão pratica o ato: Ministério, instituto e unidade.",
  ctx="Primeiras linhas do documento, abaixo do brasão. Igual em todo Edital da mesma Unidade.",
  var=["linhas de cabeçalho da Unidade (aqui, Cefor em duas linhas)"],
  dep=[], eq="Mesma Unidade e mesmas linhas de cabeçalho.",
  imp="Edital de outra Unidade (campus) muda as últimas linhas.",
  obr=["Ministério da Educação", "Instituto Federal do Espírito Santo", "nome da Unidade"],
  ordem="Do órgão mais amplo para o mais específico, como impresso.",
  trad="É cabeçalho institucional, não texto normativo. O brasão é imagem, sem texto alternativo no PDF.",
  vis="Brasão e nomes escritos na tela.", pend=["Decidir se o cabeçalho é sinalizado ou só exibido."])

u("anuncio", t="Anúncio do ato: número, ano e objeto do Edital", fam="ATO", cls="PARAMETRIZÁVEL", ori="A+D", cx="média",
  fonte=f"{PDF} — `anuncio_do_ato` (l. 1013): “EDITAL Nº <número>/<ano> — <título>”, em caixa alta",
  fin="Identificar o ato (número e ano) e dizer o seu objeto.",
  ctx="O número e o ano vêm de campos estruturados; o objeto é o título digitado pelo gestor, que o sistema corta quando repete o próprio número.",
  var=["número", "ano", "título (texto livre)"],
  dep=["Rodapé e verificação de integridade repetem número e ano."],
  eq="Mesma estrutura “Edital nº N/AAAA — objeto”; o objeto só é reutilizável se o título for o mesmo.",
  imp="O título é texto livre e se retifica; a caixa alta muda siglas (“EaD” vira “EAD”).",
  obr=["número e ano", "objeto completo, inclusive curso, modalidade e público"],
  ordem="Ato, depois objeto.",
  trad="A caixa alta é tipografia do documento, não ênfase. Siglas como EaD, UAB e Cefor/Ifes têm grafia própria fora da caixa alta.",
  vis="Número/ano escritos; título escrito por extenso.", pend=["Padronizar a forma de sinalizar “Edital nº N/AAAA”."])

u("descricao", t="Descrição resumida do Edital", fam="ATO", cls="ESPECIALIZADA", ori="D", cx="baixa",
  fonte=f"Campo `Edital.description` (texto livre), impresso por `_cabecalho` ({PDF}, l. 1095)",
  fin="Resumir em uma frase o que o Edital seleciona.",
  ctx="Frase entre o anúncio e o preâmbulo. A auditoria do PDF de 08/10 nota que ela repete o preâmbulo e não tem equivalente nos Editais reais da amostra.",
  var=["texto inteiro"], dep=["Preâmbulo (repete o objeto)."],
  eq="Só com texto idêntico.", imp="Texto próprio de cada Edital.",
  obr=["o objeto da seleção"], ordem="Única frase.",
  trad="É resumo administrativo, sem força normativa própria.",
  pend=["Decidir com a área se a descrição entra no vídeo (ela repete o preâmbulo)."])

u("preambulo", t="Preâmbulo: a autoridade torna pública a abertura", fam="ATO", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Seção textual `apresentacao` (sai sem número e sem título; `_secoes`, pdf.py l. 3378)",
  fin="Dizer quem abre o certame, com que fundamento e para quê.",
  ctx="Fórmula de abertura dos atos do Cefor: autoridade + “no uso de suas atribuições legais” + “torna pública a abertura de …”. O 92/2026 acrescenta um “considerando” com a portaria da CAPES.",
  var=["autoridade", "fundamento (opcional)", "objeto", "ingresso/turma"],
  dep=["Anúncio do ato (objeto)", "Autoridade responsável pelo ato (fecho)"],
  eq="Mesma autoridade, mesmo fundamento e mesmo objeto.",
  imp="Fundamento legal diferente ou objeto diferente mudam o conteúdo jurídico.",
  obr=["autoridade", "ato de tornar pública a abertura", "objeto do certame", "fundamento, quando houver"],
  ordem="Quem, com base em quê, abre o quê.",
  trad="Fórmula jurídica de abertura. “No uso de suas atribuições legais” é fórmula, não informação nova.",
  jur="Fundamenta a competência do ato.")

u("titulo_secao", t="Abertura de seção numerada", fam="ATO", cls="PARAMETRIZÁVEL", ori="A", cx="baixa",
  fonte=f"{PDF} — `_secoes` (l. 3403): “<número>. <TÍTULO DO CATÁLOGO>”; catálogo fixo de 22 seções em `backend/processo_seletivo/editais/domain/secoes.py` (l. 77)",
  fin="Marcar o início de uma seção e dizer do que ela trata.",
  ctx="Os títulos são do catálogo e não se editam; o número é posicional e depende de quais seções saem no Edital (`numeracao`, pdf.py l. 3242).",
  var=["número da seção", "título (um dos 22 do catálogo)"],
  dep=["Toda remissão “item N.M” depende deste número."],
  eq="Mesmo título do catálogo; o número muda de Edital para Edital e numa Retificação que esvazia ou preenche seção.",
  imp="Gravar o número junto com o título amarra o vídeo à numeração daquele Edital.",
  obr=["título da seção", "número (como referência de navegação)"], ordem="Número, título.",
  trad="Os 22 títulos estão em `catalogo/terminologia.md`. São marcos de navegação.",
  vis="Número e título escritos na tela.",
  mont="Gravar o título sem o número, e mostrar o número só por escrito, mantém o vídeo válido quando a numeração muda.",
  pend=["Decidir se o número da seção é sinalizado ou só escrito."])

u("fecho", t="Local e data do ato", fam="ATO", cls="PARAMETRIZÁVEL", ori="A+E", cx="baixa",
  fonte=f"{PDF} — `fecho` (l. 3508): “<local>, <data por extenso>.”",
  fin="Registrar onde e quando o ato foi praticado.",
  ctx="Local da Unidade; data do ato (a da publicação).", var=["local", "data"], dep=[],
  eq="Mesma estrutura; data sempre diferente.", imp="—",
  obr=["local", "data por extenso"], ordem="Local, data.",
  trad="Fecho formal. Em Retificação, a data é a da Retificação.")

u("autoridade", t="Autoridade responsável pelo ato", fam="ATO", cls="PARAMETRIZÁVEL", ori="A+E", cx="baixa",
  fonte=f"{PDF} — `_autoridade` (l. 3517): rótulo “Autoridade responsável pelo ato”, nome, cargo e ato de nomeação congelados na Publicação",
  fin="Dizer quem responde pelo ato.",
  ctx="Registro, não assinatura. Hoje o registro do Cefor pode ter só o cargo (060, FR-1124): o 92/2026 e o 01/2026 saem sem nome.",
  var=["nome (pode faltar)", "cargo", "ato de nomeação (pode faltar)"], dep=["Preâmbulo nomeia a mesma autoridade pelo cargo."],
  eq="Mesma pessoa, cargo e nomeação.", imp="Troca de titular muda o conteúdo.",
  obr=["cargo", "nome, se houver", "ato de nomeação, se houver"], ordem="Rótulo, nome, cargo, nomeação.",
  trad="Nome próprio: datilologia ou sinal pessoal é decisão da equipe e da pessoa.",
  dec=["Uso de sinal pessoal da autoridade."])

u("integridade", t="Verificação de integridade do documento", fam="ATO", cls="PARAMETRIZÁVEL", ori="A", cx="alta",
  fonte=f"{PDF} — `_integridade` (l. 3568): frase fixa, Edital/Processo e “SHA-256 do conteúdo: …”",
  fin="Permitir conferir que o documento corresponde à versão homologada.",
  ctx="Bloco técnico de nota, em corpo pequeno, depois da autoridade. O hash é do conteúdo canônico, não do arquivo.",
  var=["número/ano", "código e título do Processo", "hash"],
  dep=["Rodapé de cada página repete os 16 primeiros caracteres do hash."],
  eq="A frase fixa é idêntica em todo Edital; os valores mudam.", imp="O hash não tem tradução linguística.",
  obr=["que o documento deriva da versão homologada", "identificação do Edital e do Processo"],
  ordem="Frase, identificação, hash.",
  trad="O hash é cadeia técnica; ninguém sinaliza 64 caracteres. O que importa comunicar é a função de conferência.",
  vis="Hash só por escrito.", pend=["Decidir se o bloco entra no vídeo ou fica só no documento escrito."])

u("rodape", t="Rodapé de página (Edital, verificação e paginação)", fam="ATO", cls="PARAMETRIZÁVEL", ori="A", cx="baixa",
  fonte=f"{PDF} — `render_edital_pdf` (l. 3721) e `render_documento` (l. 3751): “Edital N/AAAA · Verificação <16 car.>… — Página X de Y”",
  fin="Orientar a leitura do papel: qual Edital, qual versão e qual página.",
  ctx="Repetido em todas as páginas. É elemento de paginação, sem conteúdo normativo novo.",
  var=["número/ano", "início do hash", "página e total"], dep=["Verificação de integridade."],
  eq="Igual em estrutura; muda a cada página.", imp="Paginação não existe num vídeo.",
  obr=["nenhuma informação normativa própria"], ordem="—",
  trad="Não é conteúdo do ato; é navegação do papel.",
  mont="Recomendação documental: não gravar; no vídeo, a navegação é por seção e por item.",
  pend=["Confirmar com a área que o rodapé fica fora da tradução."])

# ── GER ─────────────────────────────────────────────────────────────────────────────────────────
u("comissao", t="Condução do certame por comissão designada", fam="GER", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seção textual `disposicoes-preliminares` (texto livre)",
  fin="Dizer quem conduz o processo seletivo.",
  ctx="No 91/2026, comissão designada pela Diretora-Geral; no 92/2026, “regido por este Edital e executado pela Comissão… designada por portaria”.",
  var=["autoridade que designa", "forma de designação"], dep=["Casos omissos (a mesma comissão resolve)."],
  eq="Mesma autoridade e mesma forma de designação; o 92 acrescenta a regência pelo Edital.",
  imp="A frase do 92 afirma duas coisas (regência e execução); a do 91, uma.",
  obr=["quem conduz", "quem designa"], ordem="Órgão condutor, autoridade que o designa.",
  trad="“Comissão de Seleção” é termo do glossário.")

u("duvidas", t="Canal de atendimento a dúvidas", fam="GER", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seções textuais `disposicoes-preliminares` (91) e `disposicoes-finais` (92)",
  fin="Dizer por onde a pessoa tira dúvidas sobre o Edital.",
  ctx="No 91, “exclusivamente” por e-mail e com horário; no 92, “poderão ser enviadas” a um e-mail, sem horário.",
  var=["endereço de e-mail", "horário de atendimento", "exclusividade do canal"], dep=[],
  eq="Mesmo canal, mesma exclusividade, mesmo horário.",
  imp="“Exclusivamente” muda a regra: exclui outros canais.",
  obr=["canal", "endereço", "horário, quando houver", "se o canal é exclusivo"], ordem="Canal, endereço, horário.",
  trad="O endereço eletrônico é dado escrito, não se sinaliza letra a letra.",
  vis="E-mail escrito na tela.",
  pend=["Para candidatos surdos, avaliar se há canal acessível (videochamada em Libras) — decisão institucional, fora deste catálogo."])

u("publicacoes_oficiais", t="Local oficial das publicações do certame", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `disposicoes-preliminares` (91)", fin="Dizer onde saem todas as publicações do processo.",
  ctx="Frase que define o “endereço eletrônico do certame”, citado depois em várias seções.",
  var=["endereço (aqui não declarado)"], dep=["Convocação por publicação; inscrição pela internet."],
  eq="Mesma frase.", imp="—", obr=["que todas as publicações saem no endereço do certame"], ordem="Única frase.",
  trad="Define um referente usado no resto do documento.")

u("finalidade_cadastro_reserva", t="Finalidade de cadastro de reserva e convocação conforme a necessidade", fam="GER", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `disposicoes-preliminares` (92, item 1.2)",
  fin="Dizer que a seleção forma cadastro de reserva e que a convocação depende da necessidade.",
  ctx="Explica por que 16 Perfis têm zero vaga imediata.", var=["prazo de validade (remete)"],
  dep=["Quadro de Perfis (vagas 0, cadastro limitado)", "Prazo de validade"],
  eq="Mesma finalidade e mesma condição de convocação.", imp="—",
  obr=["formação de cadastro de reserva", "convocação conforme a necessidade", "durante a validade do Edital"],
  ordem="Finalidade, condição, prazo.", trad="“Cadastro de reserva” é termo do glossário.",
  jur="Afasta expectativa de convocação imediata.")

u("sem_vinculo", t="Ausência de vínculo empregatício do bolsista", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `disposicoes-preliminares` (92, item 1.3)", fin="Dizer que ser bolsista não cria vínculo de emprego.",
  ctx="Típico de seleção de bolsistas (UAB/CAPES).", var=["instituições citadas"], dep=["Remuneração do Perfil (bolsa)."],
  eq="Mesma frase.", imp="—", obr=["não há vínculo empregatício", "com quem (Ifes, CAPES)"], ordem="Única frase.",
  trad="Distinção jurídica entre bolsa e emprego.", jur="Natureza jurídica da relação.")

u("vedacao_acumulo_bolsas", t="Vedação de acúmulo de bolsas", fam="GER", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Seções textuais `disposicoes-preliminares` (92, 1.4) e `requisitos-gerais` (92, 2.3)",
  fin="Proibir acumular a bolsa com outra dos mesmos programas.",
  ctx="O mesmo Edital diz a regra duas vezes, com redações diferentes: como vedação (1.4) e como requisito (2.3).",
  var=["programas de fomento", "período"], dep=["Requisitos gerais."],
  eq="As duas redações não são equivalentes palavra por palavra: 2.3 limita ao “período de atuação”.",
  imp="Gravar uma só para as duas apagaria a diferença de alcance.",
  obr=["a proibição", "quais programas", "o período, quando dito"], ordem="Proibição, alcance.",
  trad="Mesmo conteúdo dito duas vezes; o profissional decide se a segunda remete à primeira.",
  dec=["Se a repetição interna é traduzida duas vezes ou por remissão."], jur="Requisito de elegibilidade.")

u("prazo_validade", t="Prazo de validade do processo seletivo", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `prazo-de-validade` (92)", fin="Dizer por quanto tempo o resultado vale e se pode ser prorrogado.",
  ctx="Conta da publicação do resultado final.", var=["duração", "termo inicial", "prorrogação"],
  dep=["Finalidade de cadastro de reserva."], eq="Mesma duração e mesma prorrogação.", imp="Duração diferente.",
  obr=["duração", "a partir de quando", "prorrogação"], ordem="Duração, início, prorrogação.",
  trad="Números por extenso entre parênteses são redação jurídica; dizer o número uma vez.", jur="Prazo legal do certame.")

u("aceitacao_normas", t="Aceitação das normas pela inscrição", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `disposicoes-finais` (92, 15.1)", fin="Dizer que se inscrever implica aceitar o Edital.",
  ctx="Cláusula muito comum nos Editais reais (ver a sondagem em `viabilidade.md`).", var=[], dep=[],
  eq="Mesma frase.", imp="—", obr=["inscrição implica conhecimento e aceitação das normas"], ordem="Única frase.",
  trad="Cláusula de adesão.", jur="Efeito jurídico da inscrição.")

u("casos_omissos", t="Casos omissos", fam="GER", cls="PARAMETRIZÁVEL", ori="D", cx="baixa",
  fonte="Seção textual `disposicoes-finais`", fin="Dizer quem decide o que o Edital não prevê.",
  ctx="Fórmula fixa com uma variável: a instância ouvida (Diretoria de Ensino no 91; Coordenação UAB no 92).",
  var=["órgão que decide", "órgão ouvido"], dep=["Comissão (seção 1)."],
  eq="Mesmo órgão que decide e mesmo órgão ouvido.", imp="Órgão diferente muda a competência.",
  obr=["quem resolve", "quem é ouvido"], ordem="Situação, quem resolve, quem é ouvido.",
  trad="“Casos omissos” é expressão jurídica: situações que o Edital não regula.", jur="Competência decisória residual.")

# ── OFE ─────────────────────────────────────────────────────────────────────────────────────────
u("oferta_curso", t="Caracterização da oferta do curso", fam="OFE", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `informacoes-gerais` (91)", fin="Explicar como o curso funciona: a distância, com encontros síncronos.",
  ctx="Informação sobre o curso, não sobre a seleção.", var=["modalidade", "ambiente", "atividades obrigatórias"],
  dep=["Carga horária e duração."], eq="Mesmo curso e mesma organização.", imp="Outro curso.",
  obr=["modalidade a distância", "ambiente virtual", "encontros síncronos obrigatórios e para quê"],
  ordem="Modalidade, meio, obrigações.", trad="“Síncrono” e “Ambiente Virtual de Aprendizagem” estão no glossário.")

u("carga_duracao", t="Carga horária e duração do curso", fam="OFE", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `informacoes-gerais` (91)", fin="Dizer a carga horária e a duração prevista.",
  ctx="A carga horária também sai na Tabela 1 (coluna Carga horária), por outro campo.", var=["horas", "meses"],
  dep=["Quadro de Perfis (coluna Carga horária)."], eq="Mesmos números.", imp="Números diferentes.",
  obr=["carga horária", "duração prevista"], ordem="Carga, duração.",
  trad="Dois campos diferentes dizem o mesmo número; uma Retificação pode mudar um e não o outro.")

u("publico_alvo", t="Público-alvo", fam="OFE", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `publico-alvo` (91)", fin="Dizer a quem o curso se destina.", ctx="Frase única.",
  var=["formação exigida"], dep=["Requisitos do Perfil (diploma)."], eq="Mesmo público.", imp="—",
  obr=["quem pode ser aluno"], ordem="Única frase.", trad="Diferente de requisito: é público, mas no 91 coincide com o requisito de diploma.")

u("certificado", t="Condição para o certificado", fam="OFE", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `certificado` (91)", fin="Dizer o que dá direito ao certificado.", ctx="Informação acadêmica posterior à seleção.",
  var=["título conferido", "condições"], dep=[], eq="Mesmo título e mesmas condições.", imp="—",
  obr=["título", "condições de aprovação"], ordem="Direito, condições.", trad="“Trabalho Final de Curso” está no glossário.")

# ── REQ ─────────────────────────────────────────────────────────────────────────────────────────
u("remissao_requisitos_perfil", t="Remissão aos requisitos específicos do Perfil", fam="REQ", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seção textual `requisitos-gerais`", fin="Dizer que, além dos gerais, valem os requisitos do Perfil escolhido.",
  ctx="91: “do polo pretendido, descritos na seção Perfis de Vaga”; 92: “do perfil pretendido, descritos neste Edital”.",
  var=["como o Perfil é chamado (polo, perfil)", "onde estão os requisitos"], dep=["Seção Perfis de Vaga."],
  eq="Mesma remissão.", imp="O 91 chama o Perfil de “polo”; o vocabulário muda o referente.",
  obr=["que os requisitos do Perfil também valem", "onde estão"], ordem="Única frase.",
  trad="Remissão interna: precisa apontar a seção, não o número.")

u("req_nacionalidade", t="Requisito geral: nacionalidade", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `requisitos-gerais` (92, 2.1)", fin="Exigir nacionalidade brasileira ou situação regular de estrangeiro.",
  ctx="Requisito comum em seleção de bolsista.", var=[], dep=[], eq="Mesma frase.", imp="—",
  obr=["brasileiro nato ou naturalizado", "ou estrangeiro em situação regular"], ordem="Única frase.",
  trad="Termos jurídicos de nacionalidade.", jur="Elegibilidade.")

u("req_quitacao", t="Requisito geral: quitação eleitoral e militar", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `requisitos-gerais` (92, 2.2)", fin="Exigir quitação com obrigações eleitorais e, para homens, militares.",
  ctx="No 91 a mesma exigência aparece como documento (certidão de quitação eleitoral).", var=[],
  dep=["Documento: certidão de quitação eleitoral (91)."], eq="Mesma frase.", imp="—",
  obr=["quitação eleitoral", "quitação militar para o sexo masculino"], ordem="Eleitoral, militar.",
  trad="“Sexo masculino” é a redação do texto de origem; não reformular.", jur="Elegibilidade.")

u("req_diploma_graduacao", t="Requisito: diploma de graduação reconhecido pelo MEC", fam="REQ", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (lista de texto livre)",
  fin="Exigir graduação reconhecida pelo MEC.",
  ctx="91 enumera os graus (bacharelado, licenciatura, tecnologia); 92 diz “em qualquer área”.",
  var=["graus aceitos", "área"], dep=["Documento: diploma de graduação."],
  eq="Mesmos graus e mesma área.", imp="Restrição de área ou de grau.",
  obr=["graduação", "reconhecida pelo MEC", "graus ou área, quando ditos"], ordem="Única frase.",
  trad="Requisito de formação.", jur="Elegibilidade.")

u("req_acesso_computador", t="Requisito: acesso a computador com internet", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements`", fin="Exigir meio técnico para o curso a distância.", ctx="Requisito de curso EaD.",
  var=[], dep=[], eq="Mesma frase.", imp="—", obr=["computador", "conexão à internet"], ordem="Única frase.", trad="—")

u("req_graduacao_area", t="Requisito: graduação em áreas específicas", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (92, TD-ADM)", fin="Exigir graduação numa das áreas listadas.", ctx="Requisito do Perfil.",
  var=["áreas"], dep=[], eq="Mesmas áreas.", imp="Áreas diferentes.", obr=["as áreas aceitas"], ordem="Única frase.", trad="—")

u("req_mestrado_graduacao_computacao", t="Requisito: mestrado em qualquer área com graduação em Computação", fam="REQ", cls="INÉDITA", ori="D", cx="média",
  fonte="Campo `PerfilVaga.requirements` (92, TD-INFO-EDU)", fin="Exigir mestrado e, cumulativamente, graduação em Computação ou Informática.",
  ctx="Dois requisitos numa frase.", var=["áreas"], dep=["Documento: diploma de mestrado."],
  eq="Mesma combinação.", imp="Parecida com o requisito de mestrado do 01/2026, mas de alcance diferente.",
  obr=["mestrado em qualquer área", "graduação em Computação ou Informática"], ordem="Mestrado, graduação.", trad="—")

u("req_mestrado_area", t="Requisito: mestrado na área ou em área afim", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (01, DOC-INFO)", fin="Exigir mestrado em Computação ou área afim.",
  ctx="Semelhante na forma ao requisito do TD-INFO-EDU (92), mas outro requisito: ali a área do mestrado é livre.",
  var=["área"], dep=[], eq="Mesma área.", imp="Não equivale ao requisito do 92.", obr=["mestrado", "área ou área afim"], ordem="Única frase.",
  trad="“Área afim” é conceito aberto, decidido pela comissão.")

u("req_experiencia_magisterio", t="Requisito: experiência mínima no magistério", fam="REQ", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Campo `PerfilVaga.requirements` (92: TD-ADM, TD-INFO-EDU e item 3.20)",
  fin="Exigir tempo mínimo de experiência docente.",
  ctx="Três redações no mesmo Edital: “no magistério”, “no magistério superior” e “no magistério do ensino básico ou superior, ou vinculação a programa de pós-graduação…, comprovada por declaração…”.",
  var=["tempo", "nível de ensino", "alternativas", "forma de comprovação"], dep=["Documento: comprovante de experiência."],
  eq="Mesmo tempo, mesmo nível e mesmas alternativas.",
  imp="As três diferem em alcance: não se reutiliza uma pela outra.",
  obr=["tempo mínimo", "nível de ensino", "alternativas e comprovação, quando ditas"], ordem="Tempo, onde, alternativas, comprovação.",
  trad="Diferenças pequenas na letra e grandes na regra.", jur="Elegibilidade.")

u("req_residencia", t="Requisito: residência no município do polo", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (92, 3.20)", fin="Exigir residência no município do polo ou limítrofe.", ctx="Requisito de tutoria presencial.",
  var=[], dep=["Documento: comprovante de residência (só no TP-01 — ver cobertura)."], eq="Mesma frase.", imp="—",
  obr=["município do polo", "ou limítrofe"], ordem="Única frase.", trad="“Limítrofe”: que faz divisa.")

u("req_disponibilidade", t="Requisito: disponibilidade de horas semanais", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (92, 3.20)", fin="Exigir disponibilidade de carga semanal, inclusive aos sábados.", ctx="Requisito de tutoria.",
  var=["horas", "dias"], dep=["Quadro de Perfis (carga horária)", "Documento: declaração de disponibilidade."], eq="Mesmas horas e dias.", imp="—",
  obr=["horas semanais", "inclusive sábados"], ordem="Única frase.", trad="—")

u("req_habilidade_ava", t="Requisito: habilidade com computador e ambiente virtual", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (92, 3.20)", fin="Exigir habilidade com computador e com o Moodle.", ctx="Requisito de tutoria.",
  var=["ambiente"], dep=[], eq="Mesma frase.", imp="—", obr=["computador", "ambiente virtual (Moodle)"], ordem="Única frase.",
  trad="“Moodle” é nome próprio.")

u("req_curso_tecnico", t="Requisito: curso técnico na área", fam="REQ", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `PerfilVaga.requirements` (01, TEC-LAB)", fin="Exigir curso técnico em Informática.", ctx="Requisito do Perfil.",
  var=["área"], dep=[], eq="Mesma área.", imp="—", obr=["curso técnico", "área"], ordem="Única frase.", trad="—")

# ── PER ─────────────────────────────────────────────────────────────────────────────────────────
u("quadro_perfis", t="Quadro de Perfis de vaga (tabela)", fam="PER", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="alta",
  fonte=f"{PDF} — `_quadro_de_perfis` (l. 2055): colunas Perfil, Localidade, Vagas, Cadastro reserva, Carga horária; linha Total",
  fin="Mostrar, lado a lado, cada Perfil, onde fica, quantas vagas imediatas e qual cadastro de reserva.",
  ctx="Só sai com dois ou mais Perfis; com um Perfil, os mesmos dados saem em pares rótulo-valor. Código e nome são digitados; vagas e cadastro, estruturados.",
  var=["número de linhas", "código e nome", "localidade", "vagas", "cadastro (não há / limitado em N / ilimitado)", "carga horária", "total"],
  dep=["Vagas por lista (a soma por linha bate com Vagas)", "Identificação de cada Perfil"],
  eq="Mesma tabela só com os mesmos Perfis e números.", imp="Qualquer número diferente.",
  obr=["cada Perfil", "localidade", "vagas imediatas", "cadastro de reserva", "carga horária", "total"],
  ordem="Linha a linha, na ordem do código; total no fim.",
  trad="Tabela é leitura espacial; em Libras, o arranjo das colunas no espaço de sinalização é decisão do profissional.",
  pend=["Decidir entre sinalizar a tabela inteira ou remeter a ela e sinalizar só a leitura de uma linha-modelo."],
  dec=["Estratégia de tradução de tabelas (todas as famílias com tabela)."])

u("matriz_vagas", t="Vagas por lista de concorrência (matriz)", fam="PER", cls="PARAMETRIZÁVEL", ori="A+B", cx="alta",
  fonte=f"{PDF} — `_tabela_de_vagas` (l. 2717), legenda “Vagas por lista de concorrência” (068)",
  fin="Mostrar como as vagas de cada Perfil se repartem entre ampla concorrência e listas reservadas.",
  ctx="Matriz Perfil × lista (068, D-002). Perfil sem vaga imediata não tem linha (067, ED-12).",
  var=["Perfis com vaga", "listas", "quantidades"], dep=["Quadro de Perfis (coluna Vagas)", "Tabela de modalidades (o que cada sigla é)"],
  eq="Mesmas quantidades e listas.", imp="Números diferentes.",
  obr=["quantas vagas por lista em cada Perfil"], ordem="Perfil a Perfil; ampla primeiro.",
  trad="As siglas das colunas só se entendem com a tabela de modalidades; não traduzir isoladas.")

u("reversao_ausencia", t="Reversão de vagas: ausência de aprovados na reserva", fam="PER", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `FRASE_DA_REVERSAO['ON_EXHAUSTION']` (l. 2320)",
  fin="Dizer o que acontece com vaga reservada quando não há aprovados na reserva.",
  ctx="Texto fixo do sistema, escolhido pela espécie de reversão declarada no Perfil. Sai junto do quadro de vagas; com Perfis em grupos diferentes, ganha “No Perfil X, …”.",
  var=["nenhuma no texto", "alcance: “Nos Perfis …” quando só parte dos Perfis a declara"], dep=["Vagas por lista de concorrência."],
  eq="Texto idêntico em todo Edital que declara essa espécie.",
  imp="A outra espécie (não preenchimento total) é outra regra: não se substitui uma pela outra.",
  obr=["vaga reservada sem aprovado", "vai para a ampla concorrência", "do mesmo Perfil (“respectiva”)"],
  ordem="Condição, consequência.", trad="Regra de cotas: o gatilho é a ausência de aprovados.",
  jur="Destinação de vaga reservada (política de cotas).")

u("reversao_saldo", t="Reversão de vagas: não preenchimento total das reservadas", fam="PER", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `FRASE_DA_REVERSAO['ON_BALANCE']` (l. 2320)",
  fin="Dizer o que acontece com o saldo das vagas reservadas não preenchidas.",
  ctx="Texto fixo do sistema para a segunda espécie de reversão.", var=["alcance, como na outra espécie"],
  dep=["Vagas por lista de concorrência."], eq="Texto idêntico.", imp="Não equivale à reversão por ausência de aprovados.",
  obr=["vagas reservadas não preenchidas", "o saldo vai para a ampla", "do mesmo Perfil"], ordem="Condição, consequência.",
  trad="O gatilho é o saldo, e não a ausência total: a diferença tem efeito jurídico.", jur="Destinação de vaga reservada.")

u("tabela_modalidades", t="Modalidades de concorrência (tabela)", fam="PER", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="alta",
  fonte=f"{PDF} — `_tabela_de_modalidades` (l. 2743) e `_modalidades` (l. 2012): colunas Modalidade, Percentual, Fundamento normativo",
  fin="Dizer quais listas existem, que percentual a lei reserva e com que fundamento.",
  ctx="Agrupada por identidade (068, ED-11): uma tabela para todos os Perfis quando são iguais, uma por Perfil quando diferem (01/2026). Coluna vazia é omitida.",
  var=["siglas e nomes", "percentuais", "fundamentos legais (texto livre)", "Perfil, quando por Perfil"],
  dep=["Vagas por lista (usa as siglas)", "Documentos por modalidade"], eq="Mesmas modalidades, percentuais e fundamentos.",
  imp="Fundamento legal diferente (Resolução CS, Lei 15.142/2025, Lei 12.990/2014) muda a base jurídica.",
  obr=["cada modalidade", "percentual", "fundamento normativo"], ordem="Linha a linha.",
  trad="Os nomes das modalidades são termos do glossário; os fundamentos são citações legais, ditos por escrito.",
  jur="Base legal da reserva de vagas.")

u("convocacao_publicacao", t="Forma de convocação: publicação no endereço eletrônico", fam="PER", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{VOC} — `FORMA_DE_CONVOCACAO_POR_EXTENSO` (l. 52); frase em {PDF} (l. 2662)",
  fin="Dizer como o classificado fica sabendo que foi convocado.", ctx="Texto fixo; sai uma vez quando todos os Perfis declaram a mesma forma.",
  var=["alcance (“Nos Perfis …”)"], dep=["Local oficial das publicações"], eq="Texto idêntico.",
  imp="A forma por mensagem individual é outra regra.", obr=["convocação", "por publicação no endereço do certame"], ordem="Única frase.",
  trad="O ônus de acompanhar a publicação é da pessoa.", jur="Forma de ciência da convocação.")

u("convocacao_mensagem", t="Forma de convocação: mensagem individual", fam="PER", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{VOC} — `FORMA_DE_CONVOCACAO_POR_EXTENSO` (l. 52); frase em {PDF} (l. 2662)",
  fin="Dizer que a convocação chega por mensagem à pessoa.", ctx="Texto fixo do sistema.", var=["alcance"],
  dep=["Convocação textual (92, 12.1)"], eq="Texto idêntico.", imp="Não equivale à convocação por publicação.",
  obr=["convocação", "por mensagem individual"], ordem="Única frase.", trad="—", jur="Forma de ciência da convocação.")

u("identificacao_perfil", t="Identificação do Perfil (código, nome e descrição)", fam="PER", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="média",
  fonte=f"{PDF} — `_identificacao_do_perfil` (l. 2228): “<item> <código> — <nome>” e a descrição",
  fin="Abrir o bloco de um Perfil e dizer qual é.", ctx="O item é posicional (seção.ordem). Código e nome são digitados; a descrição é texto livre.",
  var=["item", "código", "nome", "descrição"], dep=["Linha do Perfil no quadro de Perfis."],
  eq="Mesmo código, nome e descrição.", imp="Códigos (INF-BJN, TP-01) não têm leitura em Libras sem convenção.",
  obr=["qual é o Perfil", "a descrição, quando houver"], ordem="Item, código, nome, descrição.",
  trad="O código é identificador de sistema; o que identifica o Perfil para a pessoa é nome e localidade.",
  dec=["Se o código do Perfil é sinalizado (datilologia), só escrito, ou substituído pelo nome do polo."])

u("remissao_comum", t="Remissão a bloco comum de Perfis", fam="PER", cls="PARAMETRIZÁVEL", ori="C", cx="baixa",
  fonte=f"{PDF} — `_perfis` (l. 2165, 2176, 2181) e `_remissao` (l. 2288): “Atribuições: as descritas no item N.” / “Requisitos: os descritos no item N.” / “Marcos classificatórios: os descritos no item N.”",
  fin="Dizer que aquele conteúdo do Perfil está numa subseção comum.", ctx="Desde a 064 e a 068 o que se repete entre Perfis sai uma vez, e cada Perfil remete a ela.",
  var=["matéria (atribuições, requisitos, marcos)", "número do item"], dep=["Subseção comum correspondente."],
  eq="Mesma matéria; o número muda.", imp="O número é posicional e muda com a quantidade de Perfis.",
  obr=["a matéria", "onde está"], ordem="Rótulo, remissão.",
  trad="Remissão interna. No vídeo, a remissão por número exige navegação.",
  mont="Pode virar instrução de navegação (“veja o bloco comum”) em vez de número.",
  pend=["Decidir como o vídeo trata remissão a item numerado."])

u("titulo_subsecao_comum", t="Título de subseção comum aos Perfis", fam="PER", cls="PARAMETRIZÁVEL", ori="C", cx="média",
  fonte=f"{PDF} — `TITULO_DA_SUBSECAO` (l. 2306) e `_titulo_da_subsecao_comum` (l. 2805)",
  fin="Abrir a subseção que vale para um grupo de Perfis, e dizer quais.",
  ctx="“Requisitos / Atribuições / Marcos classificatórios comuns aos Perfis X, Y e Z”. Os códigos enumerados podem ser 18.",
  var=["matéria", "item", "lista de códigos"], dep=["Remissões de cada Perfil."], eq="Mesma matéria e mesma lista.", imp="Outra lista de Perfis.",
  obr=["a matéria", "a quais Perfis vale"], ordem="Item, matéria, Perfis.",
  trad="Enumerar 18 códigos em sinalização é longo; decidir resumo (“todos os tutores presenciais”) com a área — o resumo é paráfrase e precisa de validação jurídica.",
  dec=["Se a lista de códigos pode ser resumida no vídeo."])

u("atrib_tutoria_distancia", t="Atribuições da tutoria a distância", fam="PER", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Campo `PerfilVaga.duties` (texto livre), impresso por `_atribuicoes` (pdf.py l. 2247)",
  fin="Dizer o que o tutor a distância faz.", ctx="TD-ADM e TD-INFO-EDU dividem três atribuições; o TD-INFO-EDU tem uma quarta. Por diferirem, não se juntaram (064).",
  var=["lista de atribuições"], dep=[], eq="Mesma lista.", imp="A quarta atribuição do TD-INFO-EDU.",
  obr=["cada atribuição"], ordem="Na ordem da lista.",
  trad="As três primeiras são idênticas nos dois Perfis: candidatas a trecho comum, gravado uma vez.")

u("atrib_tutoria_presencial", t="Atribuições da tutoria presencial (comuns aos polos)", fam="PER", cls="INÉDITA", ori="D", cx="média",
  fonte="Campo `PerfilVaga.duties`, consolidado na subseção comum (064)", fin="Dizer o que o tutor presencial faz.",
  ctx="Impresso uma vez para os 16 polos.", var=["lista"], dep=["Título da subseção comum."], eq="Mesma lista.", imp="—",
  obr=["cada atribuição"], ordem="Na ordem da lista.", trad="—")

u("remuneracao_bolsa", t="Remuneração do Perfil", fam="PER", cls="EXATA", ori="B+D", cx="baixa",
  fonte=f"Campo `PerfilVaga.compensation`; “Remuneração: …” em {PDF} (l. 2170)",
  fin="Dizer quanto e como o Perfil é remunerado.", ctx="No 92/2026, a mesma frase sai 18 vezes, uma por Perfil: a consolidação da 068 não alcança a remuneração.",
  var=["valor ou forma"], dep=["Ausência de vínculo empregatício."], eq="Mesmo texto.", imp="Valor diferente.",
  obr=["forma de remuneração", "referência de valor"], ordem="Única frase.",
  trad="Repetição idêntica dentro do Edital: um trecho gravado serve a todos os Perfis.")

u("fatos_declarados", t="Dados exigidos na inscrição", fam="PER", cls="PARAMETRIZÁVEL", ori="A+D", cx="média",
  fonte=f"{PDF} — `_fatos_declarados` (l. 1856): rótulo “Dados exigidos na inscrição” e “• <dado> (<tipo>)”",
  fin="Anunciar quais dados a inscrição vai pedir, e de que tipo.",
  ctx="Os dados alimentam o desempate. No 92/2026 o bloco sai 18 vezes idêntico; no 01/2026, uma.",
  var=["rótulos dos dados", "tipo (data, número inteiro)"], dep=["Critérios de desempate (usam esses dados)."],
  eq="Mesmos dados e tipos.", imp="Dados diferentes.", obr=["cada dado", "o tipo de valor"], ordem="Na ordem impressa.",
  trad="O tipo entre parênteses (“número inteiro”, “data”) é vocabulário do sistema.")

# ── CLA ─────────────────────────────────────────────────────────────────────────────────────────
u("marcos_separadamente", t="Marcos aplicados a cada Perfil separadamente", fam="CLA", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `MARCOS_SEPARADAMENTE` (l. 2316, 068, FR-1347)",
  fin="Evitar que a regra impressa uma vez seja lida como classificação conjunta dos Perfis.",
  ctx="Abre toda subseção comum de marcos. Sem ela, “os 10 primeiros” valeria para os 18 Perfis somados.",
  var=[], dep=["Título da subseção comum de marcos."], eq="Texto idêntico.", imp="—",
  obr=["cada Perfil tem classificação própria", "e resultado próprio"], ordem="Única frase.",
  trad="Frase de alcance: decide o sentido de todas as regras seguintes.", jur="Alcance da regra classificatória.")

u("identificacao_marco", t="Identificação do marco classificatório", fam="CLA", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="média",
  fonte=f"{PDF} — `_marcos` (l. 1696): rótulo “Marcos classificatórios[ — <Perfil>]” e “<código> — <nome>” (l. 1755)",
  fin="Nomear a classificação cujo resultado será publicado.", ctx="O nome do marco é o que a frase de recurso cita entre aspas.",
  var=["código", "nome", "Perfil (fora de subseção comum)"], dep=["Recurso do marco."], eq="Mesmo código e nome.", imp="Outro nome.",
  obr=["nome da classificação"], ordem="Rótulo, código, nome.", trad="“Marco classificatório” é vocabulário do sistema (auditoria de 08/10, §5).",
  dec=["Como sinalizar “marco classificatório”."])

u("ordem_sorteio", t="Forma da ordem: por sorteio", fam="CLA", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `FORMA_DA_ORDEM['POR_SORTEIO']` (l. 1588)", fin="Dizer que a ordem é sorteada.", ctx="Texto fixo; sob sorteio não se imprime combinação, normalização nem arredondamento (067).",
  var=[], dep=["Método do sorteio."], eq="Texto idêntico.", imp="—", obr=["a ordem é por sorteio"], ordem="Rótulo, valor.", trad="—")

u("ordem_pontuacao", t="Forma da ordem: pela pontuação combinada das Etapas", fam="CLA", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `FORMA_DA_ORDEM['POR_PONTUACAO']` (l. 1588)", fin="Dizer que a ordem decorre das notas.", ctx="Texto fixo.",
  var=[], dep=["Regra de cálculo da nota."], eq="Texto idêntico.", imp="—", obr=["a ordem é pela pontuação"], ordem="Rótulo, valor.", trad="—")

u("metodo_sorteio", t="Método do sorteio público", fam="CLA", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="alta",
  fonte=f"{PDF} — `_metodo_do_marco` (l. 1658), `_origem_do_metodo` (l. 1621); rótulos em `CAMPOS_DO_METODO` (`backend/processo_seletivo/editais/domain/perfis.py`, l. 527)",
  fin="Publicar, antes do sorteio, como a semente será obtida, para que qualquer pessoa possa conferir o resultado.",
  ctx="Bloco “Sorteio” com Método, Algoritmo, Fonte, Ocorrência, Quando, Derivação, Semente e Se faltar. Os três últimos são frases digitadas.",
  var=["origem do método (comum/próprio)", "algoritmo", "fonte", "concurso", "data e hora", "derivação", "semente", "substituição"],
  dep=["Evento Sorteio público e Evento Divulgação da ordem no Cronograma", "Habilitação ao sorteio"],
  eq="Mesma fonte, mesma regra de semente e de substituição; concurso e data mudam sempre.",
  imp="Algoritmo e semente não têm equivalente em linguagem comum sem explicação.",
  obr=["que há sorteio público e verificável", "a fonte", "o concurso e a data", "como se forma a semente", "o que vale se faltar"],
  ordem="Origem, algoritmo, fonte, ocorrência, quando, derivação, semente, substituição.",
  trad="Conteúdo técnico de auditoria. A auditoria de 08/10 aponta “Semente” e “Derivação” como vocabulário do sistema.",
  vis="Nome do algoritmo e concurso escritos; um esquema visual (fonte → semente → ordem) ajudaria.",
  pend=["Validar com a área como explicar semente e algoritmo sem alterar a norma."], dec=["Se a explicação conceitual é gravada uma vez e reutilizada."])

u("habilitacao_todas", t="Habilitação ao sorteio: todas as inscrições submetidas", fam="CLA", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `_habilitacao_ao_sorteio` (l. 1552, frase na l. 1579)", fin="Dizer quem participa do sorteio.",
  ctx="Variante da ausência de Etapa de habilitação. A outra variante (“apenas as inscrições habilitadas na Etapa …”) não aparece no corpus.",
  var=[], dep=["Método do sorteio."], eq="Texto idêntico.", imp="A variante com Etapa de habilitação é outra regra.",
  obr=["todas as inscrições enviadas participam"], ordem="Única frase.", trad="—", jur="Universo do sorteio.")

u("calculo_nota", t="Regra de cálculo da nota classificatória", fam="CLA", cls="PARAMETRIZÁVEL", ori="C+D", cx="alta",
  fonte=f"{PDF} — `_combinacao` (l. 1321), `NORMALIZACAO_DO_MARCO` (l. 1277), `_arredondamento` (l. 1337)",
  fin="Dizer como as notas das Etapas se combinam numa nota final, e como ela é arredondada.",
  ctx="Três linhas: Combinação (operação + Etapas com peso), Normalização e Arredondamento. Os nomes das Etapas são digitados.",
  var=["operação", "Etapas e pesos", "normalização", "casas e modo de arredondamento"], dep=["Fichas das Etapas (pesos)."],
  eq="Mesmas Etapas, pesos e arredondamento.", imp="Etapas e pesos diferentes mudam o cálculo.",
  obr=["operação", "quais Etapas e pesos", "normalização", "arredondamento"], ordem="Combinação, normalização, arredondamento.",
  trad="“Normalização: nenhuma” e “meio para cima” são vocabulário técnico (auditoria de 08/10, §5.2).",
  vis="Um esquema da soma ponderada ajuda; números escritos.")

u("recurso_marco", t="Prazo de recurso contra o resultado do marco", fam="CLA", cls="PARAMETRIZÁVEL", ori="C", cx="média",
  fonte=f"{PDF} — `_janela_recursal` (l. 1411) e `prazo_do_recurso` (l. 1373); nomeia o resultado desde a 067 (ED-02)",
  fin="Dizer contra qual resultado se recorre e em quanto tempo.",
  ctx="“Caberá recurso contra o resultado de “<marco>”, no prazo de N (extenso) dias corridos, contados da divulgação desse resultado.” Marco sem declaração não imprime nada; negativa expressa imprime “Não caberá recurso…”.",
  var=["nome do marco", "dias", "dia/dias corridos"], dep=["Identificação do marco", "Eventos de recurso do Cronograma", "Seção Dos Recursos"],
  eq="Mesmo marco e mesmo prazo.", imp="Prazo diferente; nome diferente.",
  obr=["objeto do recurso (qual resultado)", "prazo", "a contar de quando"], ordem="Objeto, prazo, termo inicial.",
  trad="“Dias corridos” tem sentido jurídico próprio. A ausência da frase também é norma: não acrescentar recurso onde o documento cala.",
  jur="Direito de recorrer e prazo decadencial.")

u("corte_quadro", t="Corte pelo quadro de vagas, com suplentes", fam="CLA", cls="PARAMETRIZÁVEL", ori="C", cx="alta",
  fonte=f"{PDF} — `_regra_de_corte` (l. 1455), alvo `FROM_VACANCY_TABLE`",
  fin="Dizer quantos, da ordem, seguem para a Etapa seguinte.",
  ctx="O número não é impresso: é o das vagas do recorte (Perfil e lista). Uma Retificação que mude as vagas muda o efeito sem mudar o texto.",
  var=["Etapa governada", "suplentes"], dep=["Quadro de Perfis e vagas por lista", "Etapa governada"],
  eq="Mesma Etapa e mesmos suplentes.", imp="Traduzir o número no lugar da referência ao quadro.",
  obr=["para qual Etapa", "até o número de vagas do recorte", "quantos suplentes"], ordem="Destino, quantidade, suplentes.",
  trad="“Recorte” é vocabulário do sistema (Perfil + lista). Não concretizar o número de vagas na sinalização: ele muda por Retificação.",
  jur="Quem continua no certame.", dec=["Como sinalizar “recorte”."])

u("corte_fixo", t="Corte com quantidade fixa", fam="CLA", cls="PARAMETRIZÁVEL", ori="C", cx="média",
  fonte=f"{PDF} — `_regra_de_corte` (l. 1455), alvo fixo",
  fin="Dizer quantos primeiros seguem adiante, e se há suplentes.",
  ctx="Com Etapa governada (“Progridem para <Etapa> os N primeiros…, mais S suplentes”) ou sem ela (“Progridem os N primeiros desta ordem.”).",
  var=["N", "Etapa governada (opcional)", "suplentes (opcional)"], dep=["Empate no corte (refere “essa quantidade”)", "Etapa governada"],
  eq="Mesmos N, Etapa e suplentes.", imp="A variante sem Etapa não diz para onde se progride.",
  obr=["quantos", "para onde, quando dito", "suplentes, quando houver"], ordem="Destino, quantidade, suplentes.",
  trad="O número por extenso entre parênteses é redação jurídica.", jur="Quem continua no certame.")

u("empate_excedente", t="Empate no corte: todos os empatados progridem", fam="CLA", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `EMPATE_NO_CORTE['ADMITS_SURPLUS']` (l. 1521)",
  fin="Dizer o que acontece quando há empate na última posição do corte.",
  ctx="Texto fixo, mas dependente: “essa quantidade” é a do Corte imediatamente acima. Sob sorteio não sai.",
  var=[], dep=["Corte (antecedente obrigatório)"], eq="Texto idêntico.",
  imp="Isolado do Corte, perde o referente; a variante estrita diz o contrário.",
  obr=["empate na última posição", "todos os empatados progridem", "mesmo excedendo"], ordem="Condição, consequência.",
  trad="Anáfora: precisa do Corte antes.", mont="Gravar sempre depois do Corte, nunca isolado.", jur="Quem continua no certame.")

u("empate_estrito", t="Empate no corte: a quantidade não é excedida", fam="CLA", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `EMPATE_NO_CORTE['STRICT']` (l. 1521)", fin="Dizer que o empate não aumenta a quantidade do corte.",
  ctx="Texto fixo dependente do Corte, como a outra variante.", var=[], dep=["Corte (antecedente obrigatório)"], eq="Texto idêntico.",
  imp="Isolado do Corte, perde o referente.", obr=["empate na última posição", "a quantidade não é excedida"], ordem="Condição, consequência.",
  trad="Não diz como o empate se resolve: isso está nos critérios de desempate, quando há.", mont="Gravar depois do Corte.", jur="Quem continua no certame.")

u("continuacao_admitida", t="Continuação admitida além do corte", fam="CLA", cls="EXATA", ori="C", cx="média",
  fonte=f"{PDF} — `CONTINUACAO_DO_CORTE['ALLOWED']` (l. 1528)", fin="Dizer que pode haver chamada de mais gente, na mesma ordem.",
  ctx="Texto fixo. A auditoria de 08/10 aponta “Continuação” como vocabulário do sistema.", var=[], dep=["Corte."], eq="Texto idêntico.",
  imp="A variante “Não haverá chamada…” diz o contrário.", obr=["pode haver chamada além do corte", "na mesma ordem"], ordem="Única frase.",
  trad="—", jur="Expectativa de chamada.")

u("continuacao_nao", t="Continuação não admitida", fam="CLA", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `CONTINUACAO_DO_CORTE['NONE']` (l. 1528)", fin="Dizer que não haverá chamada além do corte.",
  ctx="Texto fixo.", var=[], dep=["Corte."], eq="Texto idêntico.", imp="—", obr=["não há chamada além do corte"], ordem="Única frase.",
  trad="—", jur="Expectativa de chamada.")

u("criterios_desempate", t="Critérios de desempate", fam="CLA", cls="PARAMETRIZÁVEL", ori="C+D", cx="alta",
  fonte=f"{PDF} — `_marcos` (l. 1840) e `criterio_com_a_ausencia` em {VOC} (`CRITERIO_DE_DESEMPATE` l. 21, `QUANDO_AUSENTE` l. 26)",
  fin="Dizer, em ordem, como se separam candidatos empatados.",
  ctx="Cada critério combina um tipo (maior/menor valor declarado, maior pontuação na Etapa), um alvo (dado ou Etapa) e o que fazer sem o valor.",
  var=["número de critérios", "tipo", "alvo", "regra de ausência"], dep=["Dados exigidos na inscrição", "Ficha da Etapa"],
  eq="Mesmos critérios, na mesma ordem.", imp="Ordem diferente muda o resultado.",
  obr=["a ordem dos critérios", "o que cada um compara", "o que acontece sem o valor"], ordem="1º, 2º, 3º…",
  trad="“Menor valor declarado em Data de nascimento” quer dizer “quem nasceu primeiro”, mas a paráfrase precisa de validação jurídica antes de ser usada.",
  dec=["Se a paráfrase do critério é admitida."], jur="Ordem final da classificação.")

u("classificacao_sorteio_texto", t="Classificação por sorteio quando inscritos excedem vagas (texto livre)", fam="CLA", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `classificacao` (91)", fin="Dizer, em linguagem corrente, que o sorteio define a ordem quando há mais inscritos que vagas.",
  ctx="Repete em texto livre o que o marco publica. Cláusula muito comum nos Editais reais de curso (sondagem em `viabilidade.md`).",
  var=["remissão ao método"], dep=["Forma da ordem: sorteio", "Método do sorteio"], eq="Mesma frase.",
  imp="Duas fontes da mesma regra: uma Retificação pode mudar uma e não a outra.",
  obr=["condição (mais inscritos que vagas)", "ordem por sorteio", "onde está o método"], ordem="Condição, consequência, remissão.",
  trad="—", jur="Critério de classificação.")

u("analise_sorteados_texto", t="Análise documental dos sorteados até as vagas (texto livre)", fam="CLA", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `classificacao` (91)", fin="Dizer que só os sorteados dentro das vagas e suplentes têm documentos analisados.",
  ctx="Repete o Corte do marco em linguagem corrente.", var=[], dep=["Corte pelo quadro de vagas."], eq="Mesma frase.",
  imp="Duas fontes da mesma regra.", obr=["depois do sorteio", "análise dos documentos", "até as vagas, mais suplentes"], ordem="Momento, ação, alcance.", trad="—")

u("nota_final_titulos", t="Nota final pela prova de títulos (texto livre)", fam="CLA", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `classificacao` (92)", fin="Dizer qual é a nota final e como a lista é apresentada.",
  ctx="Fala em “código de inscrição” — vocabulário que o resto do Edital não usa para o Perfil.", var=[], dep=["Regra de cálculo da nota", "Fase de recursos"],
  eq="Mesma frase.", imp="—", obr=["nota final = prova de títulos", "depois dos recursos", "ordem decrescente", "por código de inscrição"], ordem="Nota, momento, ordenação.",
  trad="“Código de inscrição” aqui parece designar o Perfil (TD-ADM, TP-01…): confirmar com a área.", pend=["Esclarecer “código de inscrição”."])

# ── INS ─────────────────────────────────────────────────────────────────────────────────────────
u("canal_inscricao", t="Canal e período de inscrição", fam="INS", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seção textual `inscricao`", fin="Dizer como e quando se inscrever.",
  ctx="91: “exclusivamente pela internet, no endereço eletrônico do certame”; 92: “exclusivamente pelo sistema de inscrições”. Os dois remetem ao Cronograma.",
  var=["canal", "remissão ao período"], dep=["Evento Período de inscrições."], eq="Mesmo canal.", imp="Canal descrito de outro modo.",
  obr=["canal exclusivo", "período no Cronograma"], ordem="Canal, período.", trad="—")

u("indicacao_perfil_lista", t="Indicação do Perfil e da lista na inscrição", fam="INS", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `inscricao` (91)", fin="Dizer que a pessoa escolhe o polo e a lista de concorrência ao se inscrever.", ctx="—",
  var=[], dep=["Quadro de Perfis", "Tabela de modalidades"], eq="Mesma frase.", imp="—", obr=["indicar o polo", "indicar a lista"], ordem="Única frase.", trad="—")

u("concorrencia_simultanea", t="Concorrência simultânea às vagas reservadas e à ampla", fam="INS", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `inscricao` (91)", fin="Dizer que quem concorre à reserva concorre também à ampla.", ctx="Regra de cotas com efeito sobre a classificação.",
  var=[], dep=["Tabela de modalidades"], eq="Mesma frase.", imp="—", obr=["concorrência dupla", "no mesmo polo"], ordem="Única frase.", trad="—", jur="Política de cotas.")

u("teto", t="Limite de inscrições por candidato", fam="INS", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `teto_de_inscricoes` (l. 3426): “Cada candidato poderá ter apenas 1 inscrição enviada neste Edital.” (com teto maior: “no máximo N inscrições enviadas”)",
  fin="Dizer quantas inscrições cada pessoa pode enviar.", ctx="Acrescentada pelo sistema ao fim da seção Da Inscrição, depois do texto do autor (054, FR-984). Os três Editais usam teto 1.",
  var=["teto (só 1 no corpus)"], dep=["No 92, o item 9 §2 diz a mesma regra com outras palavras."], eq="Texto idêntico com teto 1.",
  imp="Teto maior troca a frase.", obr=["quantas inscrições", "que conta a enviada"], ordem="Única frase.",
  trad="“Enviada”: o rascunho não conta.", jur="Recusa de segunda inscrição.")

u("codigo_unico", t="Concorrência a um único código de inscrição (texto livre)", fam="INS", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `classificacao` (92)", fin="Dizer que a pessoa concorre a um só “código de inscrição”.",
  ctx="Diz com outras palavras a frase gerada do teto.", var=[], dep=["Limite de inscrições."], eq="Mesma frase.",
  imp="Não é a mesma frase do teto: tem outro vocabulário.", obr=["um só código"], ordem="Única frase.", trad="Ver a pendência de “código de inscrição”.")

u("arquivo_documentos", t="Formato e limite do arquivo de documentos", fam="INS", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `inscricao` (92, 4.2)", fin="Dizer em que formato, tamanho e nome o arquivo deve ser enviado.", ctx="—",
  var=["formato", "tamanho", "padrão de nome"], dep=["Documentos exigidos."], eq="Mesmos limites.", imp="—",
  obr=["PDF único", "até 10 MB", "o que vai dentro", "padrão do nome do arquivo"], ordem="Formato, tamanho, conteúdo, nome.",
  trad="O padrão do nome é dado técnico escrito.", vis="Exemplo do nome do arquivo escrito.")

u("sem_conferencia", t="Ausência de conferência na inscrição e responsabilidade do candidato", fam="INS", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `inscricao` (92, 4.3)", fin="Dizer que ninguém confere os documentos no envio e que a responsabilidade é da pessoa.",
  ctx="Cláusula de responsabilidade frequente nos Editais reais.", var=[], dep=[], eq="Mesma frase.", imp="—",
  obr=["sem conferência no envio", "responsabilidade exclusiva do candidato"], ordem="Fato, consequência.", trad="—", jur="Ônus do candidato.")

u("limite_paginas", t="Indeferimento por excesso de páginas", fam="INS", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `inscricao` (92, 4.4)", fin="Dizer que documentação acima de 30 páginas é indeferida sem recurso.", ctx="—",
  var=["número de páginas"], dep=["Formato do arquivo."], eq="Mesmo limite.", imp="—",
  obr=["limite de 30 páginas", "indeferimento", "sem recurso"], ordem="Condição, consequência, vedação.", trad="—", jur="Indeferimento sem recurso.")

# ── DOC ─────────────────────────────────────────────────────────────────────────────────────────
u("doc_cab_todos", t="Documentos exigidos de todos os candidatos (cabeçalho)", fam="DOC", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `_titulo_do_grupo` (l. 3109): “De todos os candidatos:”", fin="Dizer que a lista a seguir vale para todos.",
  ctx="Texto fixo; os documentos agrupam-se por destinatário (`_documentos_exigidos`, l. 3166).", var=[], dep=["Os documentos do grupo."],
  eq="Texto idêntico.", imp="—", obr=["destinatário: todos"], ordem="Antes da lista.", trad="—")

u("doc_cab_perfil", t="Documentos exigidos dos candidatos a um Perfil (cabeçalho)", fam="DOC", cls="PARAMETRIZÁVEL", ori="C+B+D", cx="baixa",
  fonte=f"{PDF} — `_titulo_do_grupo` (l. 3109): “Dos candidatos ao perfil <código — nome>:”", fin="Dizer que a lista vale só para um Perfil.",
  ctx="Texto fixo com o Perfil como variável.", var=["Perfil"], dep=["Os documentos do grupo."], eq="Mesmo Perfil.", imp="Outro Perfil.",
  obr=["destinatário: candidatos daquele Perfil"], ordem="Antes da lista.", trad="—")

u("doc_cab_modalidade", t="Documentos exigidos dos candidatos de uma modalidade (cabeçalho)", fam="DOC", cls="PARAMETRIZÁVEL", ori="C+D", cx="baixa",
  fonte=f"{PDF} — `_titulo_do_grupo` (l. 3109): “Dos candidatos concorrentes na modalidade <nome>:”", fin="Dizer que a lista vale só para quem concorre numa modalidade reservada.",
  ctx="Texto fixo com o nome da modalidade como variável. A auditoria de 08/10 chama este agrupamento de “ponto alto para o candidato”.",
  var=["modalidade"], dep=["Tabela de modalidades."], eq="Mesma modalidade.", imp="Outra modalidade.",
  obr=["destinatário: quem concorre naquela modalidade"], ordem="Antes da lista.", trad="Nomes das modalidades no glossário.")

u("doc_identificacao", t="Documento: identificação com foto", fam="DOC", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Campos `DocumentoExigido.name` e `instructions` (texto livre), em “<alínea>) <nome> — <instruções>”",
  fin="Pedir documento de identidade com foto.", ctx="Mesmo nome nos três Editais; instruções diferentes (o 92 lista os documentos aceitos).",
  var=["instruções"], dep=[], eq="Mesmo nome e mesmas instruções.", imp="Instruções diferentes mudam o que é aceito.",
  obr=["documento com foto", "instruções (frente e verso, formato, aceitos)"], ordem="Nome, instruções.",
  trad="O documento mais recorrente dos Editais reais (sondagem em `viabilidade.md`).")

u("doc_cpf", t="Documento: comprovante de CPF", fam="DOC", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Campo `DocumentoExigido.name`", fin="Pedir comprovante de CPF.", ctx="“de inscrição” (91) e “de situação cadastral” (92) são documentos diferentes.",
  var=["nome do comprovante"], dep=[], eq="Mesmo comprovante.", imp="Os dois nomes não designam o mesmo documento.", obr=["qual comprovante"], ordem="Nome.", trad="—")

u("doc_diploma", t="Documento: diploma de graduação", fam="DOC", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Campos `DocumentoExigido.name` e `instructions`", fin="Pedir o diploma de graduação.",
  ctx="Três instruções diferentes: com declaração de conclusão e histórico (91), só frente e verso (92), diploma ou certidão com histórico (01).",
  var=["instruções", "destinatário (todos ou um Perfil)"], dep=["Requisito de graduação."], eq="Mesmas instruções.", imp="Instruções diferentes aceitam documentos diferentes.",
  obr=["diploma", "o que o substitui, quando dito"], ordem="Nome, instruções.", trad="—")

u("doc_quitacao_eleitoral", t="Documento: certidão de quitação eleitoral", fam="DOC", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `DocumentoExigido.name`", fin="Pedir a certidão de quitação eleitoral.", ctx="—", var=[], dep=[], eq="Mesmo nome.", imp="—", obr=["certidão de quitação eleitoral"], ordem="Nome.", trad="—")

u("doc_nome_social", t="Documento facultativo: requerimento de nome social", fam="DOC", cls="INÉDITA", ori="D+C", cx="baixa",
  fonte="Campo `DocumentoExigido.name`; “(facultativo)” em pdf.py (l. 3202)", fin="Oferecer o pedido de uso do nome social.",
  ctx="“(facultativo)” é acrescentado pelo sistema quando o documento não é obrigatório.", var=[], dep=[], eq="Mesmo nome.", imp="—",
  obr=["requerimento de nome social", "é facultativo"], ordem="Nome, facultatividade.", trad="—")

u("doc_autodeclaracao_etnico", t="Documento: autodeclaração étnico-racial conforme modelo", fam="DOC", cls="PARAMETRIZÁVEL", ori="D", cx="baixa",
  fonte="Campos `DocumentoExigido.name` e `instructions`", fin="Pedir a autodeclaração no modelo do anexo.",
  ctx="O anexo varia: Anexo I (91), Anexo V (92), “Anexo do Edital” sem número (01).", var=["anexo"], dep=["Relação de anexos (o modelo)"],
  eq="Mesmo anexo.", imp="Número do anexo diferente.", obr=["autodeclaração", "qual modelo"], ordem="Nome, modelo.", trad="—")

u("doc_laudo", t="Documento: laudo médico", fam="DOC", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Campos `DocumentoExigido.name` e `instructions`", fin="Pedir laudo médico de quem concorre como pessoa com deficiência.",
  ctx="91: últimos 12 meses, com CID; 92: últimos 12 meses, médico especialista, CID e limitações funcionais.", var=["prazo", "requisitos do laudo"],
  dep=["Modalidade PcD"], eq="Mesmos requisitos.", imp="O 92 exige mais.", obr=["laudo", "validade", "conteúdo exigido"], ordem="Nome, requisitos.",
  trad="“CID” no glossário.")

u("doc_experiencia", t="Documento: comprovante de experiência no magistério", fam="DOC", cls="INÉDITA", ori="D", cx="média",
  fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Dizer como comprovar a experiência.", ctx="Duas formas alternativas.",
  var=[], dep=["Requisito de experiência."], eq="Mesmas formas.", imp="—", obr=["declaração em papel timbrado com dados", "ou carteira de trabalho"], ordem="Primeira forma, alternativa.", trad="—")

u("doc_pontuacao", t="Documentos passíveis de pontuação (facultativo)", fam="DOC", cls="INÉDITA", ori="D+C", cx="média",
  fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Dizer que os documentos para pontuar seguem a ficha do Anexo IV.", ctx="Facultativo.",
  var=[], dep=["Anexo IV", "Etapa Prova de títulos"], eq="Mesma frase.", imp="—", obr=["conforme a ficha", "na ordem dos itens", "facultativo"], ordem="Nome, regra, facultatividade.", trad="—")

u("doc_disponibilidade", t="Documento: declaração de disponibilidade conforme modelo", fam="DOC", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Pedir a declaração de disponibilidade no modelo do Anexo II.", ctx="—",
  var=["anexo"], dep=["Anexo II", "Requisito de disponibilidade"], eq="Mesmo modelo.", imp="—", obr=["declaração", "modelo", "preenchida e assinada"], ordem="Nome, modelo.", trad="—")

u("doc_residencia", t="Documento: comprovante de residência no município do polo", fam="DOC", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `DocumentoExigido.name` (92)", fin="Pedir comprovante de residência.", ctx="Pedido só ao TP-01 no conteúdo da simulação.", var=[], dep=["Requisito de residência."],
  eq="Mesmo nome.", imp="—", obr=["comprovante", "município do polo ou limítrofe"], ordem="Nome.", trad="—")

u("doc_mestrado", t="Documento: diploma de mestrado", fam="DOC", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Campo `DocumentoExigido.name` (92)", fin="Pedir diploma de mestrado.", ctx="—", var=[], dep=["Requisito de mestrado."], eq="Mesmo nome.", imp="—", obr=["diploma de mestrado"], ordem="Nome.", trad="—")

u("doc_autodeclaracao_genero", t="Documento: autodeclaração de identidade de gênero conforme modelo", fam="DOC", cls="INÉDITA", ori="D", cx="média",
  fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Pedir a autodeclaração de quem concorre na modalidade PTT.", ctx="—",
  var=["anexo"], dep=["Modalidade PTT", "Anexo VI"], eq="Mesmo modelo.", imp="—", obr=["autodeclaração", "modelo"], ordem="Nome, modelo.",
  trad="Terminologia de identidade de gênero no glossário; validar com a comunidade surda.")

u("relacao_anexos", t="Relação de anexos do Edital", fam="DOC", cls="PARAMETRIZÁVEL", ori="A+D", cx="média",
  fonte=f"{PDF} — `_anexos` (l. 3138): um rótulo por linha; os arquivos são artefatos à parte (`AnexoEdital`)",
  fin="Dizer quais anexos acompanham o Edital.", ctx="O PDF lista só os rótulos. O conteúdo dos anexos (modelos, fichas, matriz curricular) é outro arquivo e não está neste inventário.",
  var=["rótulos"], dep=["Documentos que citam anexos"], eq="Mesmos anexos.", imp="—",
  obr=["cada anexo pelo rótulo"], ordem="Na ordem.", trad="Os anexos são documentos próprios: traduzi-los é escopo separado.",
  pend=["Inventariar o conteúdo dos anexos (fora do PDF)."], jur="Anexos integram o Edital.")

# ── AFI ─────────────────────────────────────────────────────────────────────────────────────────
u("convocacao_heteroidentificacao", t="Convocação para verificação da autodeclaração (heteroidentificação)", fam="AFI", cls="SEMELHANTE", ori="D", cx="alta",
  fonte="Seção textual `verificacao-autodeclaracao`", fin="Dizer quem passa pela verificação complementar da autodeclaração e como.",
  ctx="91: os sorteados para as vagas de pretos e pardos, por webconferência, em data a divulgar; 92: quem se autodeclarar preto ou pardo, por comissão própria, por webconferência.",
  var=["quem é convocado", "momento", "meio"], dep=["Tabela de modalidades", "Evento de heteroidentificação (92)"],
  eq="Mesmo público, momento e meio.", imp="O público difere (sorteados × todos os autodeclarados).",
  obr=["quem", "procedimento", "meio", "quando"], ordem="Público, procedimento, meio, data.",
  trad="“Heteroidentificação” no glossário. Para candidato surdo, a webconferência envolve acessibilidade comunicacional — registrar, não decidir.",
  jur="Política de cotas raciais.")

u("indeferimento_autodeclaracao", t="Efeito do indeferimento da autodeclaração", fam="AFI", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `verificacao-autodeclaracao` (91)", fin="Dizer que, indeferida a autodeclaração, a pessoa fica só na ampla.",
  ctx="Semelhante ao 6.3 do 92, mas com outro gatilho (indeferimento × não comparecimento).", var=[], dep=["Concorrência simultânea."],
  eq="Mesma frase.", imp="Não equivale ao efeito do não comparecimento.", obr=["indeferimento", "permanece só na ampla"], ordem="Condição, consequência.", trad="—", jur="Política de cotas.")

u("criterio_fenotipico", t="Critério fenotípico exclusivo da verificação", fam="AFI", cls="INÉDITA", ori="D", cx="alta",
  fonte="Seção textual `verificacao-autodeclaracao` (92, 6.2)", fin="Dizer que a comissão só considera o fenótipo.", ctx="—", var=[], dep=["Convocação para verificação."],
  eq="Mesma frase.", imp="—", obr=["só características fenotípicas"], ordem="Única frase.", trad="“Fenotípicas” no glossário.", jur="Critério legal da heteroidentificação.")

u("nao_comparecimento_heteroidentificacao", t="Efeito do não comparecimento à verificação", fam="AFI", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `verificacao-autodeclaracao` (92, 6.3)", fin="Dizer que faltar à verificação tira a pessoa da lista reservada.", ctx="—", var=[], dep=["Concorrência simultânea."],
  eq="Mesma frase.", imp="Não equivale ao efeito do indeferimento.", obr=["não comparecimento", "exclusão da lista reservada", "permanece na ampla"], ordem="Condição, consequência.", trad="—", jur="Política de cotas.")

u("atendimento_especializado", t="Atendimento especializado à pessoa com deficiência", fam="AFI", cls="INÉDITA", ori="D", cx="média",
  fonte="Seção textual `atendimento-pcd` (92)", fin="Dizer como pedir atendimento especializado para participar das etapas.",
  ctx="É a seção que a Retificação do 92/2026 retira. Diz respeito diretamente a quem precisa de intérprete de Libras.",
  var=["onde pedir", "o que indicar"], dep=["Formulário de inscrição"], eq="Mesma frase.", imp="—",
  obr=["quem pode pedir", "onde", "o que indicar"], ordem="Quem, onde, o quê.",
  trad="O próprio público do vídeo em Libras é destinatário desta regra.", jur="Acessibilidade (LBI).")

# ── ETA ─────────────────────────────────────────────────────────────────────────────────────────
u("etapa_decisoria", t="Etapa decisória (ficha)", fam="ETA", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="média",
  fonte=f"{PDF} — `_etapas` (l. 3005): “<item> <nome>”, Caráter, Resultado “<favorável> ou <desfavorável>”, Realização",
  fin="Dizer que Etapa é essa, que caráter tem, quais resultados possíveis e quando ocorre.",
  ctx="Etapa sem nota: decide deferindo ou indeferindo. Realização só sai se a Etapa estiver ligada a um Evento.",
  var=["nome", "caráter", "rótulos do resultado", "período"], dep=["Evento do Cronograma", "Corte que governa a Etapa"],
  eq="Mesmo nome, caráter, rótulos e datas.", imp="Rótulos (Deferida/Indeferida, Habilitado/Não habilitado) diferem.",
  obr=["nome", "caráter", "resultados possíveis", "quando"], ordem="Nome, caráter, resultado, realização.", trad="—")

u("etapa_pontuada", t="Etapa pontuada (ficha)", fam="ETA", cls="PARAMETRIZÁVEL", ori="A+B+D", cx="média",
  fonte=f"{PDF} — `_etapas` (l. 3005): Caráter, Peso, Nota mínima, Pontuação máxima, Avaliações por inscrição, Realização",
  fin="Dizer como a Etapa pontua e quando ocorre.", ctx="As linhas presentes variam com o que a Etapa declara.",
  var=["nome", "caráter", "peso", "nota mínima", "pontuação máxima", "avaliações", "período"], dep=["Regra de cálculo da nota", "Critérios de desempate"],
  eq="Mesmos valores.", imp="Valores diferentes.", obr=["nome", "caráter", "peso", "nota mínima ou máxima, quando houver", "quando"], ordem="Como impresso.",
  trad="“Avaliações por inscrição” é vocabulário do sistema.")

# ── CRO ─────────────────────────────────────────────────────────────────────────────────────────
def ev(k, t, fin, ctx, var=None, dep=None, jur=None, cls="PARAMETRIZÁVEL"):
    u(k, t=t, fam="CRO", cls=cls, ori="B+D", cx="baixa",
      fonte=f"Linha da tabela do Cronograma ({PDF}, `_cronograma`, l. 2967): Nº, descrição do Evento (texto livre), Início, Término e Onde",
      fin=fin, ctx=ctx, var=var or ["descrição (texto livre)", "início", "término", "local"], dep=dep or [],
      eq="Mesmo tipo de Evento; descrição, datas e local quase sempre mudam.", imp="Datas sempre diferentes; descrição digitada diferente.",
      obr=["o que acontece", "quando começa", "quando termina, se termina", "onde, quando dito"], ordem="Evento, início, término, local.",
      trad="Na tabela, as células quebram em várias linhas e a ordem de leitura do PDF intercala as colunas (auditoria de 08/10, §4.5).",
      jur=jur)

u("cronograma_tabela", t="Cronograma: abertura da tabela", fam="CRO", cls="PARAMETRIZÁVEL", ori="A", cx="média",
  fonte=f"{PDF} — `_cronograma` (l. 2967): legenda “Tabela N — Cronograma”; colunas Nº, Evento, Início, Término e, se algum Evento tiver local, Onde",
  fin="Apresentar a tabela de datas do certame.", ctx="A coluna Onde só existe quando algum Evento tem local.", var=["número da tabela", "presença da coluna Onde"],
  dep=["Todos os Eventos."], eq="Mesmas colunas.", imp="—", obr=["que se trata do calendário do certame"], ordem="Legenda, colunas.",
  trad="O número da tabela muda com as tabelas anteriores.")
ev("ev_inscricoes", "Evento: período de inscrições", "Dizer de quando a quando se inscreve.", "Presente nos três Editais. No 01, a descrição traz “isenção de taxa até o 5º dia”.", jur="Prazo de inscrição.")
ev("ev_relacao_sorteio", "Evento: divulgação da relação de participantes do sorteio", "Dizer quando sai a lista de quem participa do sorteio.", "Só em Edital com sorteio.")
ev("ev_sorteio", "Evento: sorteio público", "Dizer quando e onde o sorteio acontece.", "Com local (transmissão).", dep=["Método do sorteio."])
ev("ev_ordem_sorteio", "Evento: divulgação da ordem do sorteio", "Dizer quando sai a ordem sorteada.", "—", dep=["Recurso do marco (conta desta divulgação)."])
ev("ev_analise_documental", "Evento: análise documental", "Dizer quando os documentos são analisados.", "91: dos sorteados; 92: dos requisitos mínimos dos classificados até o corte.", dep=["Etapa decisória."])
ev("ev_resultado_preliminar", "Evento: resultado preliminar", "Dizer quando sai um resultado preliminar.", "De análise documental, prova de títulos ou heteroidentificação; o objeto está na descrição.")
ev("ev_recurso", "Evento: prazo de recurso", "Dizer de quando a quando se recorre.", "91: “Prazo para interposição de recurso”, sem dizer contra o quê; 92: quatro, cada um nomeando o objeto.", dep=["Recurso do marco", "Seção Dos Recursos"], jur="Prazo recursal.")
ev("ev_resultado_final", "Evento: resultado final", "Dizer quando sai o resultado final.", "92: com homologação; 01: “e abertura do prazo recursal”.")
ev("ev_matriculas_homologadas", "Evento: divulgação das matrículas homologadas", "Dizer quando sai a lista de matrículas homologadas.", "—")
ev("ev_inicio_atividades", "Evento: início das aulas", "Dizer quando começam as aulas.", "Com local (ambiente virtual). Data no ano seguinte ao do Edital, o que a submissão avisa.")
ev("ev_publicacao_edital", "Evento: publicação do Edital", "Dizer quando o Edital foi publicado.", "Instante único, sem término.")
ev("ev_impugnacao", "Evento: prazo para impugnação do Edital", "Dizer de quando a quando se pode impugnar o Edital.", "Com local (formulário).", jur="Direito de impugnar o ato.")
ev("ev_homologacao_inscricoes", "Evento: homologação das inscrições", "Dizer quando sai a lista de inscrições homologadas.", "Preliminar e final.")
ev("ev_avaliacao", "Evento: realização de avaliação", "Dizer quando uma avaliação acontece.", "92: prova de títulos (período); 01: prova objetiva (instante, com local na descrição).", dep=["Ficha da Etapa."])
ev("ev_heteroidentificacao", "Evento: verificação da autodeclaração", "Dizer quando e onde ocorre a heteroidentificação.", "Descrição longa, com regra de convocação embutida (48 horas de antecedência).", dep=["Convocação para verificação."])
ev("ev_curso_formacao", "Evento: curso de formação dos convocados", "Dizer quando ocorre a formação de quem não a tem.", "—")
ev("ev_inicio_convocacoes", "Evento: início das convocações", "Dizer a partir de quando se convoca.", "Com local (mensagem individual).", dep=["Forma de convocação."])

# ── REC ─────────────────────────────────────────────────────────────────────────────────────────
u("recurso_texto_canal", t="Recurso: objeto, prazo e canal (texto livre)", fam="REC", cls="SEMELHANTE", ori="D", cx="média",
  fonte="Seção textual `recursos`", fin="Dizer contra o que se recorre, em que prazo e por onde.",
  ctx="91: contra o resultado preliminar da análise documental, pelo sistema; 92: por formulário eletrônico, nos prazos do Cronograma. Convive com a frase de recurso do marco, que trata de outro resultado.",
  var=["objeto", "canal", "prazo (remete ao Cronograma)"], dep=["Recurso do marco", "Eventos de recurso"],
  eq="Mesmo objeto e mesmo canal.", imp="Objetos diferentes.", obr=["objeto", "prazo", "canal exclusivo"], ordem="Objeto, prazo, canal.",
  trad="Atenção: no mesmo Edital há mais de um recurso, contra resultados diferentes.", jur="Direito de recorrer.")

u("recurso_vedacoes", t="Recurso: vedação de outros canais e de recurso fora do prazo", fam="REC", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seção textual `recursos`", fin="Dizer que recurso por outro meio ou fora do prazo não é aceito.",
  ctx="91: e-mail ou fora do prazo; 92: Correios, e-mail ou outra forma, com remissão ao item 11.1 digitado.", var=["canais vedados", "remissão"],
  dep=["Recurso: canal"], eq="Mesmos canais vedados.", imp="A remissão a número digitado quebra quando a numeração muda.",
  obr=["canais não aceitos", "fora do prazo não é aceito"], ordem="Vedação, alcance.", trad="Cláusula frequente nos Editais reais.", jur="Admissibilidade do recurso.")

u("recurso_sem_documentos", t="Vedação de envio de documentos na fase recursal", fam="REC", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `recursos` (92, 11.2)", fin="Dizer que não se juntam documentos ao recurso.", ctx="—", var=[], dep=[], eq="Mesma frase.", imp="—",
  obr=["sem documentos novos no recurso"], ordem="Única frase.", trad="—", jur="Admissibilidade do recurso.")

# ── CON ─────────────────────────────────────────────────────────────────────────────────────────
u("convocacao_suplentes", t="Convocação de suplentes em caso de desistência", fam="CON", cls="SEMELHANTE", ori="D", cx="baixa",
  fonte="Seção textual `convocacao`", fin="Dizer que desistências abrem vaga ao próximo da ordem.",
  ctx="91: suplentes na ordem do sorteio, por publicação; 92: quem não se manifesta é desistente e substituído pelo próximo do mesmo código.",
  var=["gatilho", "forma"], dep=["Forma de convocação", "Continuação"], eq="Mesmo gatilho e forma.", imp="Gatilhos diferentes.",
  obr=["gatilho", "quem é chamado", "como"], ordem="Gatilho, consequência, forma.", trad="—", jur="Ordem de chamada.")

u("convocacao_manifestacao", t="Convocação por mensagem e prazo de manifestação", fam="CON", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `convocacao` (92, 12.1)", fin="Dizer como chega a convocação e quanto tempo há para responder.", ctx="Repete a frase gerada da forma de convocação e acrescenta o prazo.",
  var=["prazo", "canal"], dep=["Forma de convocação: mensagem individual"], eq="Mesmo prazo.", imp="—",
  obr=["mensagem ao e-mail da inscrição", "2 dias úteis", "contados do envio"], ordem="Canal, prazo, termo inicial.",
  trad="“Dias úteis” (aqui) e “dias corridos” (no recurso) são regras diferentes.", jur="Prazo de manifestação.")

u("matricula_documentacao", t="Matrícula a partir da documentação da inscrição", fam="CON", cls="INÉDITA", ori="D", cx="baixa",
  fonte="Seção textual `matricula` (91)", fin="Dizer que a matrícula usa os documentos já enviados, sem ida presencial.", ctx="—", var=[], dep=["Requerimento de Matrícula."],
  eq="Mesma frase.", imp="—", obr=["matrícula pela documentação da inscrição", "sem comparecimento"], ordem="Única frase.", trad="—")

u("requerimento_momento", t="Momento de envio do Requerimento de Matrícula", fam="CON", cls="EXATA", ori="C", cx="baixa",
  fonte=f"{PDF} — `requerimento_de_matricula` (l. 3460): “O Requerimento de Matrícula será enviado no ato da inscrição.” (a variante “quando o candidato for convocado” não aparece no corpus)",
  fin="Dizer quando o Requerimento de Matrícula é enviado.", ctx="Acrescentada pelo sistema à seção Da Matrícula.", var=["momento (só “no ato da inscrição” no corpus)"],
  dep=["Declaração do Requerimento"], eq="Texto idêntico com o mesmo momento.", imp="O outro momento troca a frase.",
  obr=["o que se envia", "quando"], ordem="Única frase.", trad="—")

u("declaracao_requerimento", t="Declaração de veracidade do Requerimento de Matrícula", fam="CON", cls="SEMELHANTE", ori="C+D", cx="média",
  fonte=f"{PDF} — `requerimento_de_matricula` (l. 3460): “Ao enviá-lo, o candidato declarará:” e o texto de `matriculationRequest.declarationText`",
  fin="Publicar o texto que a pessoa vai declarar ao enviar o Requerimento.",
  ctx="A frase de introdução é fixa; a declaração é texto livre sem padrão no sistema (validação recusa vazio). O portal exibe o mesmo texto para aceite e guarda o hash do que foi exibido.",
  var=["texto da declaração"], dep=["Momento do Requerimento"], eq="Texto idêntico.",
  imp="91 e 01 diferem em “Lei”/“lei” e em “a inexatidão ou a falsidade”.",
  obr=["que a pessoa declara", "o conteúdo integral da declaração"], ordem="Introdução, declaração.",
  trad="Declaração sob as penas da lei: o vídeo em Libras não substitui o aceite do texto escrito; o hash guardado é do texto em português.",
  jur="Declaração com efeito penal e de cancelamento de matrícula.", dec=["Se o vídeo da declaração é exibido no ato do aceite, no portal."])

# ── Unidade descoberta nas Retificações ─────────────────────────────────────────────────────────
u("consolidacao", t="Marca de versão consolidada", fam="ATO", cls="PARAMETRIZÁVEL", ori="A", cx="média",
  fonte=f"{PDF} — `marca_de_consolidacao` (l. 1039): “Versão consolidada. Publicado em …; retificado em …[, com vigência a partir de …].”",
  fin="Dizer que o documento é a versão consolidada, e as datas da publicação, das Retificações e da vigência.",
  ctx="Só no documento de Retificação, logo abaixo do anúncio. Lista as Retificações da versão-base mais a do ato.",
  var=["data da publicação", "datas das Retificações", "vigência futura (opcional)"], dep=["Anúncio do ato."],
  eq="Mesmas datas.", imp="Datas sempre diferentes.", obr=["que é versão consolidada", "datas", "vigência, quando futura"], ordem="Natureza, datas, vigência.",
  trad="Distinguir “retificado em” (publicação) de “vigência a partir de” (efeito).", jur="Qual versão vale e desde quando.")

ORDEM_RETIFICACAO = ["consolidacao"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════
# RODADA 2 (2026-10-11) — correções da revisão crítica da rodada 1
# ═════════════════════════════════════════════════════════════════════════════════════════════════
#
# Critério que a rodada 1 enunciou e não aplicou por inteiro, agora aplicado a todas as unidades:
# **diferença de destinatário, de modalidade normativa (obrigação, possibilidade, proibição), de condição
# ou de consequência é outra unidade**; diferença só de redação, com o mesmo efeito, é a mesma unidade
# (`SEMELHANTE`), e a equivalência fica a confirmar. Nada se apaga: a unidade desdobrada fica no
# catálogo, com as ocorrências que tinha na versão 1 e o apontamento para as que a sucedem.

R2 = "2026-10-11 (rodada 2)"


def corrigir(k, hist, **campos):
    """Altera campos da unidade e registra a correção no histórico dela."""
    U[k].update(campos)
    U[k].setdefault("hist", []).append(f"{R2} — {hist}")


def desdobrar(k, filhas, v1, motivo):
    U[k].update(status="desdobrada", desdobrada_em=filhas, v1_ocorrencias=v1)
    U[k].setdefault("hist", []).append(f"{R2} — desdobrada: {motivo}")


def filha(k, pai, **kw):
    u(k, **kw)
    U[k]["origem_de"] = pai
    U[k]["hist"] = [f"{R2} — criada no desdobramento de {pai}."]


# ── Desdobramentos ───────────────────────────────────────────────────────────────────────────────
desdobrar("req_experiencia_magisterio",
          ["req_exp_magisterio", "req_exp_magisterio_superior", "req_exp_basico_superior_ou_pos"],
          ["E92-026", "E92-033", "E92-136"],
          "as três redações são três condições de elegibilidade diferentes (nível de ensino; alternativa por "
          "vínculo a pós-graduação; forma de comprovação), e a rodada 1 as agrupava por ocuparem a mesma posição.")
for k, t_, quem, txt, extra in [
    ("req_exp_magisterio", "Requisito: experiência mínima no magistério (sem nível de ensino)", "TD-ADM",
     "um ano no magistério, sem restringir o nível", []),
    ("req_exp_magisterio_superior", "Requisito: experiência mínima no magistério superior", "TD-INFO-EDU",
     "um ano no magistério superior", []),
    ("req_exp_basico_superior_ou_pos", "Requisito: experiência no magistério básico ou superior, ou vínculo a pós-graduação, comprovada por declaração",
     "Perfis TP-01 a TP-16 (subseção 3.20)",
     "um ano no magistério do ensino básico ou superior, ou vinculação a programa de pós-graduação, conforme as portarias CAPES citadas, comprovada por declaração em papel timbrado",
     ["comprovação por declaração da instituição em papel timbrado"]),
]:
    filha(k, "req_experiencia_magisterio", t=t_, fam="REQ", cls="INÉDITA", ori="D", cx="média" if not extra else "alta",
          fonte="Campo `PerfilVaga.requirements` (texto livre)",
          fin=f"Exigir, de quem concorre a {quem}, {txt}.",
          ctx="Uma das três redações de experiência do 92/2026, cada uma para um grupo de Perfis. Relacionada às outras duas, sem equivalência.",
          var=["condição: tempo mínimo", "condição: nível de ensino e alternativas"] + [f"condição: {x}" for x in extra],
          dep=["Documento: comprovante de experiência no magistério (LIB-0098)."],
          eq="Mesmo tempo, mesmo nível, mesmas alternativas e mesma forma de comprovação.",
          imp="As outras redações de experiência são outras condições.",
          obr=["tempo mínimo", "nível de ensino ou alternativa", *extra], ordem="Como no texto de origem.",
          trad="Requisito de elegibilidade: quem não o cumpre não pode concorrer àquele Perfil.", jur="Elegibilidade.")

desdobrar("convocacao_suplentes", ["conv_suplentes_desistencia", "conv_nao_manifestacao_desistente"],
          ["E91-087", "E92-212"],
          "no 91 a regra é chamar suplentes quando há desistência; no 92 a regra cria uma consequência — quem não "
          "se manifesta no prazo é considerado desistente — e só depois a substituição. Consequências diferentes.")
filha("conv_suplentes_desistencia", "convocacao_suplentes", t="Convocação de suplentes quando há desistência", fam="CON",
      cls="INÉDITA", ori="D", cx="baixa", fonte="Seção textual `convocacao` (91)",
      fin="Dizer que, havendo desistência, os suplentes são chamados na ordem do sorteio, por publicação.",
      ctx="Não define o que é desistência nem prazo de resposta.", var=["condição: ordem de chamada", "forma"],
      dep=["Forma de convocação: publicação (LIB-0017)", "Continuação admitida (LIB-0030)"], eq="Mesmo gatilho, ordem e forma.",
      imp="A regra do 92 (desistência presumida) é outra.", obr=["gatilho: desistência", "quem é chamado: suplentes", "em que ordem", "como"],
      ordem="Gatilho, consequência, forma.", trad="—", jur="Ordem de chamada.")
filha("conv_nao_manifestacao_desistente", "convocacao_suplentes", t="Não manifestação no prazo: desistência presumida e substituição",
      fam="CON", cls="INÉDITA", ori="D", cx="média", fonte="Seção textual `convocacao` (92, 12.2)",
      fin="Dizer que quem não responde no prazo é considerado desistente e substituído pelo próximo do mesmo código.",
      ctx="Depende do prazo de manifestação dito no 12.1 (LIB-0119).", var=["condição: prazo (remete ao 12.1)", "quem substitui"],
      dep=["Convocação por mensagem e prazo de manifestação (LIB-0119)"], eq="Mesma consequência e mesmo substituto.",
      imp="A regra do 91 não presume desistência.", obr=["condição: não se manifestar no prazo", "consequência: considerado desistente", "substituição pelo próximo do mesmo código"],
      ordem="Condição, consequência, substituição.", trad="“Código de inscrição” — ver pendência de LIB-0109.", jur="Perda da vaga por omissão.")

desdobrar("declaracao_requerimento", ["decl_falsidade", "decl_inexatidao_falsidade"], ["E91-091", "E01-048"],
          "o 01 acrescenta a inexatidão como causa de cancelamento da matrícula; a consequência alcança mais "
          "situações do que no 91. A frase de introdução, fixa, continua igual nas duas.")
for k, t_, causa, _ed, _linha in [("decl_falsidade", "Declaração de veracidade do Requerimento: cancelamento por falsidade", "a falsidade", "91", "14"),
                                ("decl_inexatidao_falsidade", "Declaração de veracidade do Requerimento: cancelamento por inexatidão ou falsidade", "a inexatidão ou a falsidade", "01", "6")]:
    filha(k, "declaracao_requerimento", t=t_, fam="CON", cls="INÉDITA", ori="C+D", cx="média",
          fonte="`requerimento_de_matricula` (pdf.py, l. 3460): “Ao enviá-lo, o candidato declarará:” + `matriculationRequest.declarationText`",
          fin=f"Publicar o que a pessoa declara ao enviar o Requerimento, e que {causa} de qualquer informação cancela a matrícula a qualquer tempo.",
          ctx="A introdução é fixa; a declaração é texto livre sem padrão no sistema. O portal guarda o hash do texto em português aceito.",
          var=["condição: causas de cancelamento"], dep=["Momento do Requerimento (LIB-0064)"], eq="Mesmas causas e mesma consequência.",
          imp="Outra lista de causas é outra declaração.", obr=["o que se declara", f"causa: {causa}", "consequência: cancelamento a qualquer tempo"],
          ordem="Introdução, declaração.", trad="Declaração sob as penas da lei; o vídeo não substitui o aceite do texto escrito.",
          jur="Efeito penal e de cancelamento.", dec=["Estatuto do vídeo da declaração frente ao texto aceito no portal."])

desdobrar("vedacao_acumulo_bolsas", ["vedacao_acumulo", "req_sem_outra_bolsa"], ["E92-010", "E92-014"],
          "1.4 é uma proibição geral; 2.3 é requisito de elegibilidade limitado ao período de atuação. "
          "Natureza e alcance diferentes, ainda que no mesmo tema.")
filha("vedacao_acumulo", "vedacao_acumulo_bolsas", t="Vedação de acúmulo de bolsas CAPES e FNDE", fam="GER", cls="INÉDITA", ori="D", cx="média",
      fonte="Seção textual `disposicoes-preliminares` (92, 1.4)", fin="Proibir o acúmulo de bolsas dos programas de fomento da CAPES e do FNDE.",
      ctx="Proibição, sem limite de período.", var=["programas"], dep=["Requisito: não ter outra bolsa no período (LIB-0137)"],
      eq="Mesma proibição e mesmo alcance.", imp="O 2.3 é requisito com outro alcance.", obr=["é vedado acumular", "quais programas"],
      ordem="Única frase.", trad="—", jur="Proibição.")
filha("req_sem_outra_bolsa", "vedacao_acumulo_bolsas", t="Requisito geral: não ter outra bolsa CAPES ou FNDE no período de atuação", fam="REQ",
      cls="INÉDITA", ori="D", cx="média", fonte="Seção textual `requisitos-gerais` (92, 2.3)",
      fin="Exigir, para participar, que a pessoa não tenha vínculo com outra bolsa da CAPES ou do FNDE no período de atuação.",
      ctx="Requisito de participação; o 1.4 diz a proibição geral.", var=["programas", "condição: período"],
      dep=["Vedação de acúmulo (LIB-0136)"], eq="Mesmo requisito e mesmo período.", imp="A vedação do 1.4 não é requisito.",
      obr=["não possuir vínculo com outra bolsa", "CAPES ou FNDE", "no período de atuação"], ordem="Única frase.", trad="—", jur="Elegibilidade.")

desdobrar("duvidas", ["duvidas_canal_exclusivo", "duvidas_canal_facultativo"], ["E91-008", "E92-220"],
          "no 91 o canal é exclusivo e tem horário (obrigação de usar aquele canal); no 92 é uma possibilidade. "
          "Modalidades normativas diferentes.")
filha("duvidas_canal_exclusivo", "duvidas", t="Canal exclusivo de esclarecimento de dúvidas, com horário", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
      fonte="Seção textual `disposicoes-preliminares` (91)", fin="Dizer que dúvidas são esclarecidas só por um e-mail, em dias e horários definidos.",
      ctx="“Exclusivamente” exclui outros canais.", var=["endereço", "dias e horário"], dep=[], eq="Mesmo canal, exclusividade e horário.",
      imp="O canal facultativo do 92 é outra regra.", obr=["canal único", "endereço", "dias e horário"], ordem="Canal, endereço, horário.",
      trad="—", pend=["Para candidatos surdos, se há canal acessível (videochamada em Libras) é decisão institucional, fora deste catálogo."])
filha("duvidas_canal_facultativo", "duvidas", t="Canal facultativo para envio de dúvidas", fam="GER", cls="INÉDITA", ori="D", cx="baixa",
      fonte="Seção textual `disposicoes-finais` (92, 15.3)", fin="Dizer que dúvidas podem ser enviadas a um e-mail.",
      ctx="“Poderão” é possibilidade, sem exclusividade nem horário.", var=["endereço"], dep=[], eq="Mesmo canal, sem exclusividade.",
      imp="O canal exclusivo do 91 é outra regra.", obr=["possibilidade de enviar dúvidas", "endereço"], ordem="Única frase.", trad="—")

desdobrar("doc_laudo", ["laudo_cid", "laudo_especialista_limitacoes"], ["E91-062", "E92-171"],
          "o 92 exige laudo de médico especialista e a descrição das limitações funcionais; um laudo válido no "
          "91 pode não valer no 92. Condições de validade diferentes.")
filha("laudo_cid", "doc_laudo", t="Documento: laudo médico recente com CID", fam="DOC", cls="INÉDITA", ori="D", cx="média",
      fonte="Campos `DocumentoExigido.name` e `instructions` (91)", fin="Pedir laudo dos últimos 12 meses, com o código da CID.",
      ctx="Para quem concorre como pessoa com deficiência.", var=["condição: validade", "condição: conteúdo exigido"], dep=["Modalidade PcD"],
      eq="Mesma validade e mesmo conteúdo.", imp="O laudo do 92 exige mais.", obr=["laudo", "últimos 12 meses", "código da CID"], ordem="Nome, requisitos.", trad="—")
filha("laudo_especialista_limitacoes", "doc_laudo", t="Documento: laudo de especialista com CID e limitações funcionais", fam="DOC", cls="INÉDITA", ori="D", cx="média",
      fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Pedir laudo de médico especialista, dos últimos 12 meses, com CID e descrição das limitações funcionais.",
      ctx="Para quem concorre como pessoa com deficiência.", var=["condição: validade", "condição: emissor", "condição: conteúdo exigido"], dep=["Modalidade PcD"],
      eq="Mesmos requisitos.", imp="O laudo do 91 é menos exigente.", obr=["laudo", "médico especialista", "últimos 12 meses", "CID", "limitações funcionais"], ordem="Nome, requisitos.", trad="—")

desdobrar("doc_diploma", ["diploma_ou_conclusao", "diploma_sem_substituto"], ["E91-056", "E92-160", "E01-034"],
          "o 91 e o 01 aceitam documento de conclusão com histórico no lugar do diploma; o 92 pede só o "
          "diploma. Quem ainda não tem diploma pode concorrer num caso e não no outro.")
filha("diploma_ou_conclusao", "doc_diploma", t="Documento: diploma de graduação ou documento de conclusão com histórico", fam="DOC", cls="SEMELHANTE", ori="D", cx="baixa",
      fonte="Campos `DocumentoExigido.name` e `instructions` (91, 01)", fin="Pedir o diploma, admitindo documento de conclusão acompanhado do histórico.",
      ctx="91: “Frente e verso, ou declaração de conclusão acompanhada do histórico”, para todos. 01: “Diploma ou certidão de conclusão, com histórico”, para o Perfil DOC-INFO.",
      var=["nome do documento substituto", "destinatário (no cabeçalho do grupo)"], dep=["Requisito de graduação"],
      eq="**Equivalência a confirmar com a área:** “declaração de conclusão” e “certidão de conclusão” designam, provavelmente, o mesmo tipo de documento; “frente e verso” é forma de envio.",
      imp="Se a área disser que declaração e certidão não se equivalem, as duas ocorrências se separam.",
      obr=["diploma", "documento de conclusão admitido", "com histórico"], ordem="Nome, substituto.", trad="—")
filha("diploma_sem_substituto", "doc_diploma", t="Documento: diploma de graduação, sem substituto", fam="DOC", cls="INÉDITA", ori="D", cx="baixa",
      fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Pedir o diploma de graduação, frente e verso.",
      ctx="Não admite documento de conclusão.", var=[], dep=["Requisito de graduação"], eq="Mesma exigência.",
      imp="Os documentos que admitem conclusão são outra regra.", obr=["diploma", "frente e verso"], ordem="Nome, forma.", trad="—")

desdobrar("doc_identificacao", ["identificacao_envio", "identificacao_documentos_aceitos"], ["E91-054", "E92-158", "E01-032"],
          "o 92 enumera os documentos de identificação aceitos e exige legibilidade; o 91 e o 01 só dizem a "
          "forma de envio. A lista fechada recusa documentos que os outros aceitariam.")
filha("identificacao_envio", "doc_identificacao", t="Documento: identificação com foto (forma de envio)", fam="DOC", cls="SEMELHANTE", ori="D", cx="baixa",
      fonte="Campos `DocumentoExigido.name` e `instructions` (91, 01)", fin="Pedir documento de identificação com foto, frente e verso em arquivo único.",
      ctx="91 acrescenta “em PDF”.", var=["formato do arquivo"], dep=[],
      eq="**Equivalência provável:** a diferença é o formato do arquivo, que o sistema de inscrição pode impor por si; confirmar.",
      imp="Se o formato for exigência própria do edital, as ocorrências diferem.", obr=["documento com foto", "frente e verso", "arquivo único"], ordem="Nome, forma.", trad="—")
filha("identificacao_documentos_aceitos", "doc_identificacao", t="Documento: identificação com foto, entre os documentos enumerados", fam="DOC", cls="INÉDITA", ori="D", cx="média",
      fonte="Campos `DocumentoExigido.name` e `instructions` (92)", fin="Pedir um dos documentos de identificação listados, legível e sem cortes.",
      ctx="Lista fechada: Carteira de Identidade, CNH, carteira de conselho profissional, passaporte.", var=["condição: lista de documentos aceitos"], dep=[],
      eq="Mesma lista.", imp="Lista diferente é outra condição.", obr=["documentos aceitos", "frente e verso", "legível e sem cortes"], ordem="Nome, lista, forma.", trad="—")

desdobrar("recurso_texto_canal", ["recurso_analise_documental_texto", "recurso_canal_geral"], ["E91-084", "E92-207"],
          "o 91 diz contra qual resultado se recorre (análise documental preliminar) e por onde; o 92 diz o canal "
          "de todos os recursos. Objetos diferentes não se fundem em “o recurso do edital”.")
filha("recurso_analise_documental_texto", "recurso_texto_canal", t="Recurso contra o resultado preliminar da análise documental: prazo e canal", fam="REC",
      cls="INÉDITA", ori="D", cx="média", fonte="Seção textual `recursos` (91)",
      fin="Dizer que cabe recurso contra o resultado preliminar da análise documental, no prazo do Cronograma, só pelo sistema de inscrição.",
      ctx="Outro objeto que o recurso do marco (contra a ordem do sorteio).", var=["condição: objeto", "canal", "prazo (remete ao Cronograma)"],
      dep=["Evento: prazo de recurso (LIB-0056)", "Recurso do marco (LIB-0028)"], eq="Mesmo objeto, prazo e canal.",
      imp="Recurso contra outro resultado é outra unidade.", obr=["objeto: resultado preliminar da análise documental", "prazo no Cronograma", "canal exclusivo: sistema de inscrição"],
      ordem="Objeto, prazo, canal.", trad="—", jur="Direito de recorrer.")
filha("recurso_canal_geral", "recurso_texto_canal", t="Canal e prazos de todos os recursos (formulário eletrônico)", fam="REC", cls="INÉDITA", ori="D", cx="média",
      fonte="Seção textual `recursos` (92, 11.1)", fin="Dizer que todo recurso se interpõe só por formulário eletrônico, nos prazos do Cronograma.",
      ctx="Vale para os quatro Eventos de recurso e para o recurso do marco.", var=["canal", "prazos (remete ao Cronograma)"],
      dep=["Eventos de recurso (LIB-0056)", "Recurso do marco (LIB-0028)"], eq="Mesmo canal para todos os recursos.",
      imp="Um texto que diga o objeto é outra unidade.", obr=["canal exclusivo: formulário eletrônico", "link na página do processo", "prazos do Cronograma"],
      ordem="Canal, onde está, prazos.", trad="—", jur="Admissibilidade do recurso.")

desdobrar("recurso_vedacoes", ["recurso_vedacao_email_prazo", "recurso_vedacao_outras_formas"], ["E91-085", "E92-209"],
          "o 91 veda e-mail e recurso fora do prazo; o 92 veda qualquer forma diferente da prevista e não fala em "
          "prazo nesse item. Alcances diferentes.")
filha("recurso_vedacao_email_prazo", "recurso_vedacoes", t="Recurso: não se aceitam por e-mail nem fora do prazo", fam="REC", cls="INÉDITA", ori="D", cx="baixa",
      fonte="Seção textual `recursos` (91)", fin="Dizer que recurso por e-mail ou fora do prazo não é aceito.", ctx="—", var=[], dep=["Recurso contra a análise documental (LIB-0132)"],
      eq="Mesmas vedações.", imp="—", obr=["e-mail não", "fora do prazo não"], ordem="Única frase.", trad="—", jur="Admissibilidade.")
filha("recurso_vedacao_outras_formas", "recurso_vedacoes", t="Recurso: não se aceita forma diferente da prevista", fam="REC", cls="INÉDITA", ori="D", cx="baixa",
      fonte="Seção textual `recursos` (92, 11.3)", fin="Dizer que recurso por Correios, e-mail ou outra forma diferente da prevista no item 11.1 não é aceito.",
      ctx="Remete a número digitado (11.1), que a Retificação do 92 deixa apontando para lugar errado.", var=["condição: remissão ao canal"],
      dep=["Canal de todos os recursos (LIB-0148)"], eq="Mesma vedação e mesma remissão.", imp="—",
      obr=["Correios, e-mail ou outra forma não", "só a forma prevista"], ordem="Única frase.", trad="—", jur="Admissibilidade.")

desdobrar("convocacao_heteroidentificacao", ["hetero_sorteados", "hetero_autodeclarados"], ["E91-064", "E92-175"],
          "o 91 convoca só os sorteados para vagas reservadas a pretos e pardos; o 92 submete todos os "
          "autodeclarados pretos ou pardos, por comissão própria. Destinatários diferentes.")
filha("hetero_sorteados", "convocacao_heteroidentificacao", t="Verificação da autodeclaração: só os sorteados para vagas reservadas", fam="AFI", cls="INÉDITA", ori="D", cx="alta",
      fonte="Seção textual `verificacao-autodeclaracao` (91)", fin="Dizer que os sorteados para vagas reservadas a pretos e pardos são convocados à verificação, por webconferência, em data a divulgar.",
      ctx="A modalidade da Tabela 3 é PPI (pretos, pardos e indígenas); o texto fala em pretos e pardos. Diferença registrada, não harmonizada.",
      var=["condição: destinatários", "meio", "data (a divulgar)"], dep=["Tabela de modalidades (LIB-0016)", "Efeito do indeferimento (LIB-0045)"],
      eq="Mesmo público, meio e momento.", imp="O público do 92 é outro.", obr=["quem: sorteados para vagas reservadas", "procedimento", "meio", "data a divulgar"],
      ordem="Público, procedimento, meio, data.", trad="—", jur="Política de cotas raciais.",
      pend=["Perguntar à área se indígenas também passam pela verificação (o texto não os nomeia)."])
filha("hetero_autodeclarados", "convocacao_heteroidentificacao", t="Heteroidentificação de todos os autodeclarados pretos ou pardos", fam="AFI", cls="INÉDITA", ori="D", cx="alta",
      fonte="Seção textual `verificacao-autodeclaracao` (92, 6.1)", fin="Dizer que quem se autodeclara preto ou pardo passa por heteroidentificação, por comissão designada, por webconferência.",
      ctx="Datas no Evento 10 do Cronograma, que embute a regra da convocação com 48 horas de antecedência.", var=["condição: destinatários", "meio"],
      dep=["Antecedência da convocação (LIB-0147)", "Critério fenotípico (LIB-0105)", "Não comparecimento (LIB-0106)"],
      eq="Mesmo público e meio.", imp="O público do 91 é outro.", obr=["quem: autodeclarados pretos ou pardos", "procedimento por comissão", "webconferência"],
      ordem="Público, procedimento, meio.", trad="—", jur="Política de cotas raciais.")

desdobrar("atrib_tutoria_distancia", ["atrib_td_tres", "atrib_td_quatro"], ["E92-023", "E92-030"],
          "o TD-INFO-EDU tem uma obrigação a mais (orientar o Trabalho Final de Curso). As três atribuições "
          "comuns ficam registradas como texto igual nas duas.")
for k, t_, perfil, extra in [("atrib_td_tres", "Atribuições da tutoria a distância (três atribuições)", "TD-ADM", ""),
                             ("atrib_td_quatro", "Atribuições da tutoria a distância com orientação de TFC (quatro atribuições)", "TD-INFO-EDU",
                              " e, a mais, orientar o Trabalho Final de Curso sob supervisão")]:
    filha(k, "atrib_tutoria_distancia", t=t_, fam="PER", cls="INÉDITA", ori="D", cx="média",
          fonte="Campo `PerfilVaga.duties` (texto livre), `_atribuicoes` (pdf.py, l. 2247)",
          fin=f"Dizer o que faz o tutor a distância do {perfil}: mediar conteúdos, corrigir atividades no AVA, participar de webconferências{extra}.",
          ctx="As três primeiras atribuições têm texto idêntico nos dois Perfis TD.", var=["lista de atribuições"],
          dep=["Identificação do Perfil (LIB-0018)"], eq="Mesma lista.", imp="Lista com outra obrigação.",
          obr=["cada atribuição"], ordem="Na ordem da lista.",
          trad="Se as três atribuições comuns admitem a mesma solução tradutória nos dois Perfis é pergunta para o profissional.")

# ── Regras embutidas em descrições de Evento ─────────────────────────────────────────────────────
u("isencao_taxa_embutida", t="Isenção de taxa de inscrição até o 5º dia (regra na descrição de Evento)", fam="INS", cls="INÉDITA", ori="D", cx="média",
  fonte="Campo `EventoCronograma.description` (texto livre), Evento 1 do 01/2026",
  fin="Dizer que há isenção de taxa de inscrição até o 5º dia do período.",
  ctx="A regra existe só como texto dentro da descrição de um Evento. O sistema não modela taxa de inscrição, e o Edital não diz em nenhum outro lugar se há taxa, quanto é, quem é isento nem como se pede a isenção.",
  var=["condição: prazo da isenção"], dep=["Evento: período de inscrições (LIB-0050)"], eq="Mesma regra.", imp="—",
  obr=["há isenção de taxa", "até o 5º dia"], ordem="Única informação.",
  trad="Não é parte da data do Evento: é outra regra, com prazo próprio.", jur="Custo de participação.",
  pend=["Perguntar à área: há taxa? A isenção é para todos ou só para quem pede? “5º dia” é contado de quando?"])
U["isencao_taxa_embutida"]["hist"] = [f"{R2} — criada: a rodada 1 tratava a regra como parte da descrição do Evento (LIB-0050)."]
u("antecedencia_hetero_embutida", t="Convocação para a heteroidentificação com 48 horas de antecedência (regra na descrição de Evento)", fam="AFI",
  cls="INÉDITA", ori="D", cx="média", fonte="Campo `EventoCronograma.description` (texto livre), Evento 10 do 92/2026",
  fin="Dizer que a convocação individual para a verificação sai por e-mail com 48 horas de antecedência.",
  ctx="A regra está só na descrição do Evento; a seção 6 não a repete.", var=["condição: antecedência", "canal"],
  dep=["Heteroidentificação de todos os autodeclarados (LIB-0146)", "Evento: verificação da autodeclaração (LIB-0115)"], eq="Mesma regra.", imp="—",
  obr=["convocação individual", "por e-mail", "48 horas antes"], ordem="Única informação.", trad="—", jur="Ciência da convocação.")
U["antecedencia_hetero_embutida"]["hist"] = [f"{R2} — criada: regra embutida que a rodada 1 tratava como descrição do Evento (LIB-0115)."]
u("abertura_recurso_embutida", t="Abertura de prazo recursal anunciada na descrição de Evento", fam="REC", cls="INÉDITA", ori="D", cx="média",
  fonte="Campo `EventoCronograma.description` (texto livre), Evento 3 do 01/2026",
  fin="Dizer que, com o resultado final, se abre um prazo recursal.",
  ctx="O Evento não diz contra qual resultado, nem até quando. O marco DOC-INFO publica recurso de 5 dias contra “Classificação final”; o marco TEC-LAB não declara recurso.",
  var=["objeto (não dito)"], dep=["Prazo de recurso do marco (LIB-0028)", "Evento: resultado final (LIB-0057)"], eq="—", imp="—",
  obr=["que o prazo recursal se abre com o resultado final"], ordem="Única informação.", trad="—", jur="Direito de recorrer.",
  pend=["Perguntar à área: a abertura vale para os dois Perfis, ou só para o DOC-INFO, cujo marco declara recurso?"])
U["abertura_recurso_embutida"]["hist"] = [f"{R2} — criada: regra embutida que a rodada 1 tratava como descrição do Evento (LIB-0057)."]

# ── Prescrições linguísticas retiradas ───────────────────────────────────────────────────────────
corrigir("corte_quadro", "retirada a orientação “Não concretizar o número de vagas na sinalização”, que prescrevia solução linguística para proteger o reuso.",
         trad="“Recorte” é vocabulário do sistema (Perfil + lista). O número de vagas não está na frase: vem das Tabelas 1 e 2, e muda por Retificação. Se a tradução explicita o número, ganha concretude e passa a depender de cada versão; se remete às tabelas, depende delas. A escolha é do profissional.")
corrigir("titulo_secao", "retirada a orientação “Gravar o título sem o número”, que decidia a navegação do vídeo para favorecer o reuso.",
         mont="O número da seção é posicional e muda por Retificação; o título é fixo. Como o vídeo navega — por número, por título, ou dos dois modos — é decisão de produção e de tradução.")
corrigir("remissao_comum", "retirada a sugestão de trocar a remissão por instrução de navegação.",
         mont="Remete a um item que está em outro ponto do documento; a forma de remeter num vídeo é decisão de produção e de tradução.")
corrigir("empate_excedente", "a observação “Gravar sempre depois do Corte, nunca isolado” passou a registrar a dependência, sem decidir o limite do vídeo.",
         mont="Depende do Corte imediatamente anterior (“essa quantidade”). Onde começa e termina o vídeo é decisão do profissional.")
corrigir("empate_estrito", "idem LIB-0093.", mont="Depende do Corte imediatamente anterior. Onde começa e termina o vídeo é decisão do profissional.")
corrigir("integridade", "retirada a afirmação de que o hash não se sinaliza.",
         trad="O hash é cadeia técnica de 64 caracteres, que serve à conferência. Se ele aparece no vídeo, e como, é decisão de produção.",
         vis="Possíveis: o hash por escrito.")
corrigir("rodape", "retirada a recomendação de não gravar; virou pendência.",
         mont="Repete-se por página; não tem conteúdo normativo próprio.", pend=["Decidir com a área se o rodapé entra na tradução."])
corrigir("tabela_modalidades", "retirada a orientação de dizer os fundamentos “por escrito”.",
         trad="Os nomes das modalidades são termos do glossário; os fundamentos são citações legais longas.",
         var=["siglas e nomes", "condição: percentuais", "condição: fundamentos legais (texto livre)", "Perfil, quando por Perfil"])
corrigir("remissao_requisitos_perfil", "retirada a orientação de apontar a seção “não o número”; a diferença de vocabulário (polo × perfil) passou a ser tratada como equivalência provável.",
         trad="Remissão interna, pelo nome da seção.",
         eq="**Equivalência provável:** “do polo pretendido” (91) e “do perfil pretendido” (92) designam o mesmo — o Perfil escolhido —, com vocabulário diferente; confirmar.",
         imp="Nenhum identificado; a diferença é de vocabulário.")
corrigir("remuneracao_bolsa", "retirada a afirmação de que um trecho gravado serve a todos os Perfis.",
         trad="Repetição textual idêntica, 18 vezes no mesmo edital. Se uma mesma solução — e uma mesma gravação — serve a todas é decisão do profissional.")
corrigir("arquivo_documentos", "retirada a orientação de tratar o padrão de nome “por escrito”.", trad="O padrão do nome do arquivo é dado técnico.")

# ── Diferença de redação tratada como diferença de sentido ───────────────────────────────────────
corrigir("canal_inscricao", "o impedimento “canal descrito de outro modo” virou equivalência a confirmar.",
         eq="**Equivalência a confirmar com a área:** “exclusivamente pela internet, no endereço eletrônico do certame” (91) e “exclusivamente pelo sistema de inscrições” (92) podem designar o mesmo procedimento — a inscrição no sistema, pela internet — ou não.",
         imp="Se a área confirmar que são canais diferentes.", pend=["Confirmar com a área se os dois canais são o mesmo procedimento."])
corrigir("req_diploma_graduacao", "a diferença de redação passou a ser tratada como equivalência provável.",
         eq="**Equivalência provável:** “bacharelado, licenciatura ou tecnologia” (91) e “em qualquer área” (92) parecem admitir a mesma graduação; confirmar.",
         imp="Se a área disser que um dos textos restringe grau ou área.")
corrigir("doc_cpf", "deixou de afirmar que os dois comprovantes são documentos diferentes; a equivalência fica a confirmar.",
         ctx="“Comprovante de inscrição no CPF” (91) e “Comprovante de situação cadastral no CPF” (92) são nomes de documentos da Receita Federal que podem ou não ser aceitos um pelo outro.",
         eq="**Equivalência a confirmar com a área:** se o edital aceita qualquer comprovante que identifique o CPF.",
         imp="Se a área exigir o documento nomeado.")
corrigir("comissao", "registrada a parte comum.",
         eq="A condução por comissão designada pela Diretora-Geral é comum aos dois; o 92 acrescenta a regência pelo Edital, que é informação a mais, e não contradição.")

# ── Ausência de cláusula, proibição expressa e direitos fora do edital ──────────────────────────
corrigir("recurso_marco", "a frase “a ausência da frase também é norma” podia ser lida como proibição; passou a distinguir os três casos.",
         trad="Três situações diferentes: (1) prazo declarado, a frase observada; (2) **negativa expressa** — “Não caberá recurso contra o resultado de …”, que o compositor só imprime quando o marco a declara (variante não observada no corpus); (3) **ausência de declaração** — o compositor não imprime nada, e isso não equivale a proibição: as vias que a lei dá fora do edital continuam (`_janela_recursal`, pdf.py l. 1411; Lei nº 9.784/1999, arts. 56 e 59, cuja aplicação a cada certame é questão jurídica). Não acrescentar recurso onde o edital cala, nem dizer que não há.",
         var=["nome do marco", "condição: admite ou não", "condição: dias", "dia/dias corridos"])
corrigir("atendimento_especializado", "a implicação jurídica passou a citar a fonte legal por tipo de certame e a distinguir cláusula do edital de direito previsto em lei.",
         jur="Acessibilidade. Para ingresso em curso, a LBI (Lei nº 13.146/2015), art. 30, II a V, prevê campos de acessibilidade no formulário, provas acessíveis, recursos de acessibilidade e dilação de tempo; para concurso e seleção da Lei nº 8.745/1993, o Decreto nº 9.508/2018, art. 4º. Retirar a cláusula do edital não suprime direito previsto em lei; qual norma alcança uma seleção de bolsistas é questão jurídica (ver auditoria, §13).")
corrigir("indeferimento_autodeclaracao", "explicitado que esta e LIB-0106 são condições diferentes com a mesma consequência.",
         ctx="Semelhante ao 6.3 do 92 na consequência (permanecer só na ampla), com outro gatilho (indeferimento × não comparecimento): duas condições, duas unidades.")

# ── Variáveis de valor e de condição ─────────────────────────────────────────────────────────────
# Uma variável de **condição** muda a regra (eliminatória ou não; admite recurso ou não); uma de **valor**
# muda o dado (a data, o número). Reaproveitar com variável de condição diferente não é reaproveitar.
for k, var in {
    "quadro_perfis": ["número de linhas", "código e nome", "localidade", "vagas", "condição: tipo de cadastro (não há / limitado em N / ilimitado)", "carga horária", "total"],
    "corte_quadro": ["condição: Etapa governada", "condição: suplentes"],
    "corte_fixo": ["condição: N", "condição: Etapa governada (opcional)", "condição: suplentes (opcional)"],
    "etapa_decisoria": ["nome", "condição: caráter", "rótulos do resultado", "período"],
    "etapa_pontuada": ["nome", "condição: caráter", "condição: peso", "condição: nota mínima", "pontuação máxima", "avaliações", "período"],
    "teto": ["condição: teto (só 1 no corpus)"],
    "doc_cab_perfil": ["condição: Perfil"],
    "doc_cab_modalidade": ["condição: modalidade"],
    "ev_recurso": ["condição: objeto do recurso (na descrição)", "início", "término", "local"],
    "calculo_nota": ["condição: operação", "condição: Etapas e pesos", "condição: normalização", "condição: casas e modo de arredondamento"],
    "criterios_desempate": ["condição: número de critérios", "condição: tipo", "condição: alvo", "condição: regra de ausência"],
    "fatos_declarados": ["rótulos dos dados", "tipo (data, número inteiro)"],
    "matriz_vagas": ["Perfis com vaga", "listas", "condição: quantidades"],
}.items():
    corrigir(k, "variáveis separadas entre valor e condição.", var=var)
corrigir("ev_inscricoes", "a isenção de taxa do 01/2026, que estava como parte da descrição, virou unidade própria (LIB-0152).",
         ctx="Presente nos três Editais. No 01, a descrição traz também uma regra de isenção de taxa, tratada em LIB-0152.")
corrigir("ev_resultado_final", "a abertura de prazo recursal do 01/2026 virou unidade própria (LIB-0153).",
         ctx="92: com homologação; 01: com “abertura do prazo recursal”, tratada em LIB-0153.")
corrigir("ev_heteroidentificacao", "a antecedência de 48 horas virou unidade própria (LIB-0147).",
         ctx="Descrição longa; a regra de convocação com 48 horas de antecedência está em LIB-0147.")

# ── Apoios visuais reescritos como possibilidades ───────────────────────────────────────────────
# A varredura da rodada 2 achou estes `vis` escritos como afirmação (“escritos na tela”): eram escolhas de
# apresentação. Passam a listar possibilidades, que a produção e o profissional decidem.
for k, vis in {
    "orgao": "Possíveis: o brasão e os nomes também por escrito.",
    "anuncio": "Possíveis: número, ano e título também por escrito.",
    "titulo_secao": "Possíveis: número e título também por escrito.",
    "duvidas": "Possíveis: o e-mail também por escrito.",
    "metodo_sorteio": "Possíveis: nome do algoritmo e concurso também por escrito; um esquema visual (fonte → semente → ordem).",
    "calculo_nota": "Possíveis: um esquema da soma ponderada; os números também por escrito.",
    "arquivo_documentos": "Possíveis: um exemplo do nome do arquivo, por escrito.",
}.items():
    corrigir(k, "o apoio visual, escrito como afirmação, passou a possibilidade.", vis=vis)


# ═════════════════════════════════════════════════════════════════════════════════════════════════
# RODADA 3 (2026-10-11) — editais REAIS 28/2026 e 59/2026 (documentos oficiais do Cefor/Ifes)
# ═════════════════════════════════════════════════════════════════════════════════════════════════
# Texto livre de edital real (origem D, documento externo ao sistema). A classificação reflete o que os
# cinco editais mostram depois desta rodada; o critério de desdobramento é o da rodada 2.

R3 = "2026-10-11 (rodada 3)"
FAMILIAS["ANX"] = ("Anexos: formulários, declarações e termos", "Os modelos que o candidato preenche e assina; nos editais reais, dentro do PDF.")
PADRAO["ANX"] = dict(vis="Possíveis: o formulário na tela, campo a campo.",
                     mont="O formulário se preenche; a declaração se assina: são atos diferentes do candidato.")
FONTE_REAL = "PDF oficial do edital real, em `editais/<edital>/fonte/` (documento do Cefor/Ifes, escrito fora do sistema)"
# O padrão da família CLA fala dos marcos do sistema; nos editais reais, a classificação é texto corrido.
MONT_REAL = {"CLA": "As cláusulas do sorteio se referem umas às outras (ordem, análise, substituição): separadas, algumas perdem o referente."}


def real(k, t, fam, fin, obr, cls="INÉDITA", cx="média", ctx="", var=None, dep=None, jur=None, pend=None,
         eq="Mesmo texto, ou mesmo efeito confirmado pela área.", imp="Outro destinatário, condição ou consequência.",
         trad="", ordem="Como no texto de origem."):
    u(k, t=t, fam=fam, cls=cls, ori="D", cx=cx, fonte=FONTE_REAL, fin=fin, ctx=ctx or "Cláusula de edital real do Cefor.",
      var=var or [], dep=dep or [], eq=eq, imp=imp, obr=obr, ordem=ordem, trad=trad, jur=jur, pend=pend or [])
    if fam in MONT_REAL:
        U[k]["mont"] = MONT_REAL[fam]
    U[k]["hist"] = [f"{R3} — criada a partir dos editais reais."]


# ── Oferta e curso ───────────────────────────────────────────────────────────────────────────────
real("matriz_curricular", "Matriz curricular do curso (quadro)", "OFE", "Mostrar os componentes do curso, a natureza e a carga horária de cada um.",
     ["componentes", "obrigatório ou optativo, a distância ou presencial", "carga horária", "total"], cls="PARAMETRIZÁVEL", cx="alta",
     ctx="28: tabela por semestre e módulo; 59: ementa pelo Quadro Europeu Comum de Referência (A1).", var=["componentes", "cargas"])
real("objetivo_curso", "Objetivo e fundamentos do curso", "OFE", "Dizer para que serve o curso e em que se fundamenta.", ["objetivo", "fundamentos, quando ditos"],
     cls="ESPECIALIZADA", ctx="Conteúdo próprio de cada curso. O 59 cita as Leis 10.098/2000, 10.436/2002 e 13.146/2015 e os Decretos 5.626/2005 e 9.656/2018.")
real("metodologia_curso", "Metodologia das aulas", "OFE", "Dizer como as aulas se organizam.", ["forma das aulas", "o que o aluno poderá fazer"], cx="baixa")
real("inicio_curso_no_cronograma", "Início do curso indicado no Cronograma", "OFE", "Remeter o início do curso ao Anexo I.", ["onde está a data"], cx="baixa")
real("certificado_nota_minima", "Condição para o certificado: aprovação com nota mínima", "OFE", "Dizer que só recebe certificado quem é aprovado em todos os componentes com nota final ≥ 60.",
     ["aprovação em todos os componentes", "nota final mínima de 60"], cls="EXATA", cx="baixa", jur="Direito ao certificado.")
real("certificado_envio_email_60", "Envio do certificado por e-mail em até 60 dias", "OFE", "Dizer quando e como o certificado chega.", ["e-mail", "até 60 dias", "contato se não chegar"], cx="baixa")
real("certificado_confeccao_180", "Confecção do certificado em até 180 dias", "OFE", "Dizer o prazo de confecção e quem define o envio.", ["até 180 dias", "envio definido pela secretaria"], cx="baixa")
real("certificado_segunda_via", "Dúvidas e segunda via do certificado", "OFE", "Dizer a quem pedir segunda via.", ["secretaria acadêmica"], cx="baixa")
real("reprovacao_desligamento", "Reprovação em componente: desligamento sem dependência", "OFE", "Dizer que a reprovação desliga o aluno e que o retorno é só por novo processo.",
     ["não prossegue", "sem dependência", "matrícula cancelada", "retorno só por novo processo"], cls="EXATA", jur="Desligamento.")

# ── Requisitos ───────────────────────────────────────────────────────────────────────────────────
real("req_ler_edital", "Requisito: ler atentamente o edital", "REQ", "Pôr a leitura do edital como requisito.", ["ler o edital"], cls="SEMELHANTE", cx="baixa",
     ctx="28: “este edital”; 59: “o edital”, depois de “Para participar deste edital, o candidato deverá atender aos seguintes requisitos:”.",
     eq="**Equivalência provável:** a diferença é a frase de introdução do 59.")
real("req_conhecimento_informatica", "Requisito: conhecimentos intermediários de Informática", "REQ", "Exigir conhecimento intermediário de Informática.", ["nível intermediário"], cx="baixa",
     pend=["Como se comprova o nível intermediário?"])
real("req_ensino_medio", "Requisito: ensino médio completo", "REQ", "Exigir ensino médio completo.", ["ensino médio completo"], cx="baixa", jur="Elegibilidade.")
real("req_disponibilidade_presencial", "Requisito: disponibilidade para aulas presenciais semanais", "REQ", "Exigir disponibilidade para as aulas presenciais.", ["aulas presenciais", "semanalmente"], cx="baixa")
real("req_habilidade_computador", "Requisito: habilidade no uso do computador", "REQ", "Exigir habilidade no uso do computador.", ["habilidade com computador"], cx="baixa",
     ctx="Diferente do requisito do 92/2026 (LIB-0089), que inclui o Moodle.")
real("publico_alvo_ensino_medio", "Público-alvo: quem tem ensino médio completo", "OFE", "Dizer a quem o curso se destina.", ["ensino médio completo", "desejável (não obrigatório): Libras Básico A1"],
     cx="baixa", pend=["“Desejável possuir o Curso Libras Básico - Nível A1” num curso de nível A1: confirmar com a área."])

# ── Perfis e vagas ───────────────────────────────────────────────────────────────────────────────
real("total_vagas", "Total de vagas e onde está a distribuição", "PER", "Dizer quantas vagas há e onde estão distribuídas.", ["total", "remissão ao quadro"], cls="PARAMETRIZÁVEL", cx="baixa",
     var=["total", "remissão"], dep=["Quadro de distribuição de vagas."])
real("definicao_ppi_ibge", "Definição de PPI pelas categorias do IBGE", "AFI", "Dizer que as categorias preto, pardo e indígena seguem o IBGE.", ["categorias do IBGE"], cx="média")
real("definicao_pcd_lbi", "Definição de pessoa com deficiência pela LBI", "AFI", "Definir pessoa com deficiência e citar as normas das categorias.", ["impedimento de longo prazo", "barreiras", "normas citadas"],
     cx="alta", jur="Definição legal.")
real("definicao_pcd_normas", "Normas que definem quem é pessoa com deficiência no certame", "AFI", "Enumerar as normas aplicáveis (LBI, Decreto 3.298, TEA, visão monocular, deficiência auditiva unilateral).",
     ["normas citadas"], cx="alta", jur="Elegibilidade à reserva.")
real("elegibilidade_pcd_categorias", "Categorias de deficiência elegíveis à reserva (definições legais)", "AFI", "Definir cada categoria de deficiência elegível.",
     ["cada categoria e a sua definição"], cls="ESPECIALIZADA", cx="alta",
     ctx="Transcrição de definições legais, no corpo do edital (7.3) e no formulário do Anexo IV, com redações diferentes. A alínea b) trata da pessoa surda ou com deficiência auditiva.",
     jur="Elegibilidade à reserva.", trad="Definições médico-legais extensas; a categoria da pessoa surda pede atenção própria da equipe e da comunidade surda.")

# ── Inscrição ────────────────────────────────────────────────────────────────────────────────────
real("acordo_com_edital", "Inscrição pressupõe acordo com o edital", "INS", "Dizer que, para se inscrever, é preciso concordar com o edital e cumprir as exigências.", ["acordo com o edital", "atender aos requisitos"],
     cls="SEMELHANTE", cx="baixa", ctx="28 e 59 com redação quase idêntica (“atender as” × “atender às”).", eq="**Equivalência provável:** diferença de crase.")
real("cadastro_govbr", "Cadastro no Gov.br para a inscrição", "INS", "Dizer que a inscrição passa pelo cadastro no Gov.br.", ["direcionamento ao Gov.br", "cadastro ou atualização"], cx="baixa")
real("email_caixa_baixa", "E-mail do Gov.br em letras minúsculas", "INS", "Dizer que o e-mail do cadastro tem de estar em minúsculas, sob pena de não conseguir se inscrever.",
     ["e-mail em minúsculas", "sem isso, não há inscrição"], cx="baixa")
real("envio_documentos_formato", "Envio dos documentos: PDF de até 7 MB por campo, legível e sem cortes", "INS", "Dizer como os documentos são enviados e em que estado.",
     ["PDF", "até 7 MB", "campo específico de cada documento", "sem rasuras, nítidos, sem cortes, do original"], cls="EXATA", cx="média",
     ctx="Diferente do 92/2026 (LIB-0095: PDF único de até 10 MB).", jur="Validade da inscrição.")
real("confirmar_inscricao", "Confirmar a inscrição no formulário", "INS", "Dizer que a inscrição só se efetiva ao clicar em confirmar.", ["preencher", "anexar", "clicar em confirmar"],
     cls="SEMELHANTE", cx="baixa", ctx="28 (5.7) fala em “único arquivo pdf”, contradizendo o 5.4; 28 (5.8) repete sem a menção; 59 fala em campo específico.",
     pend=["Arquivo único ou um arquivo por campo? (28)"])
real("comprovante_inscricao", "Imprimir e salvar o comprovante de inscrição", "INS", "Dizer para imprimir e salvar o comprovante.", ["imprimir comprovante", "salvar"], cx="baixa")
real("responsabilidade_preenchimento", "Responsabilidade do candidato pelo preenchimento e pelo envio", "INS", "Dizer que preencher e enviar corretamente é responsabilidade do candidato.",
     ["preenchimento correto", "envio dos documentos"], cx="baixa")
real("responsabilidade_informacoes", "Informações de inteira responsabilidade do candidato, sob as penas da lei", "INS", "Dizer que o candidato responde pelas informações, inclusive penalmente.",
     ["responsabilidade do candidato", "punições previstas em lei"], cls="EXATA", cx="baixa", jur="Responsabilidade penal.")
real("isencao_responsabilidade_tecnica", "O Cefor não responde por erro de preenchimento ou falha técnica", "INS", "Isentar a instituição de prejuízos por preenchimento incorreto ou falha técnica.",
     ["erro de preenchimento", "falha técnica ou de comunicação"], cls="SEMELHANTE", cx="média", ctx="Cláusula das mais difundidas nos editais reais (sondagem).", jur="Risco do candidato.")
real("indeferimento_dados_incompletos_sem_recurso", "Indeferimento por dados incompletos ou arquivo com problema, sem recurso", "INS",
     "Dizer que inscrição com dados incompletos ou arquivo ilegível é indeferida, sem recurso.", ["dados incompletos ou arquivo com problema", "indeferimento", "sem possibilidade de recurso"],
     cls="SEMELHANTE", cx="média", ctx="59 acrescenta “(externo ao Cefor)”.", jur="Proibição expressa de recurso.")
real("vedacao_documentos_ilegiveis", "Documentos cortados ou ilegíveis não são aceitos", "INS", "Dizer que não se aceitam documentos cortados, ilegíveis ou mal digitalizados.", ["cortados", "ilegíveis", "digitalização inadequada"], cx="baixa")
real("indeferimento_formato_documentos", "Indeferimento por documento fora do formato ou inválido", "INS", "Dizer que documentos fora de PDF, incompletos, ilegíveis, rasurados ou vencidos indeferem a inscrição.",
     ["fora do PDF", "incompletos, ilegíveis, rasurados", "fora da validade"], cls="SEMELHANTE", cx="média", jur="Indeferimento.")
real("vedacao_inscricao_email", "Não se aceita inscrição nem documento por e-mail", "INS", "Proibir inscrição e envio de documentos por e-mail.", ["e-mail não"], cls="SEMELHANTE", cx="baixa", jur="Proibição.")
real("termo_lgpd", "Ler o termo de consentimento de dados e marcar a opção", "INS", "Pedir a leitura do termo de dados pessoais e a marcação da opção no formulário.", ["ler o termo", "marcar a opção"],
     cls="PARAMETRIZÁVEL", cx="baixa", var=["número do anexo"], pend=["59 cita o Anexo III, que não está no PDF."])
real("colacao_grau_pendente", "Inscrição com declaração de colação de grau futura", "INS", "Permitir a inscrição de quem ainda não colou grau, com declaração da data de colação anterior ao início do curso.",
     ["declaração da instituição", "data da colação", "antes do início do curso"], jur="Elegibilidade condicional.")
real("comprovacao_colacao_30_dias", "Comprovar o término da graduação em até 30 dias do início", "INS", "Dizer o prazo para comprovar a conclusão.", ["até 30 dias após o início"], jur="Condição posterior.")
real("revalidacao_estrangeiros", "Diplomas estrangeiros revalidados e traduzidos", "DOC", "Exigir revalidação e tradução juramentada de diplomas do exterior.", ["revalidação", "tradução juramentada"],
     cls="SEMELHANTE", cx="média", ctx="28: alínea e e outros diplomas; 59: alínea e, outros diplomas e certificados.")
real("traducao_juramentada", "Documentos estrangeiros com tradução juramentada", "DOC", "Exigir tradução juramentada de todo documento emitido fora do Brasil.", ["tradução juramentada"], cls="SEMELHANTE", cx="baixa")

# ── Documentos ───────────────────────────────────────────────────────────────────────────────────
real("identificacao_lista_cefor", "Documento: identificação entre os documentos enumerados pelo Cefor", "DOC", "Pedir um dos documentos de identificação listados.",
     ["documentos aceitos", "frente e verso", "foto e impressão digital"], cls="EXATA", cx="média",
     ctx="Lista diferente da do 92/2026 (LIB-0143). A cláusula mais difundida nos editais reais da sondagem.")
real("doc_quitacao_ou_votacao", "Documento: comprovante de votação ou certidão de quitação eleitoral", "DOC", "Pedir prova de quitação eleitoral, por comprovante de votação de 2024 ou certidão.",
     ["comprovante de votação 2024 ou certidão", "onde emitir"], cls="SEMELHANTE", cx="baixa", ctx="Aceita mais do que a certidão do 91/2026 (LIB-0039).")
real("doc_certidao_nascimento_casamento", "Documento: certidão de nascimento ou casamento", "DOC", "Pedir certidão de nascimento ou casamento.", ["nascimento ou casamento"], cx="baixa")
real("doc_certidao_civil_uniao_estavel", "Documento: certidão de nascimento, casamento ou averbação; união estável exige nascimento", "DOC",
     "Pedir certidão civil e dizer que quem envia declaração de união estável precisa da certidão de nascimento.", ["nascimento, casamento ou averbação", "união estável → certidão de nascimento"], cx="média")
real("doc_ensino_medio", "Documento: comprovação do ensino médio completo", "DOC", "Pedir declaração ou histórico do ensino médio.", ["declaração ou histórico"], cx="baixa")
real("doc_militar", "Documento: situação militar, para candidatos do sexo masculino", "DOC", "Pedir o documento militar conforme a idade.", ["alistamento (17 anos)", "reservista, dispensa ou isenção (18+)", "militar da ativa"],
     cls="EXATA", cx="média", trad="“Sexo masculino” é a redação do texto de origem.")
real("diploma_conclusao_ou_colacao", "Documento: diploma, declaração de conclusão com histórico, ou declaração da data de colação", "DOC",
     "Pedir o diploma, admitindo declaração de conclusão com histórico ou de colação futura.", ["diploma completo e legível", "ou declaração de conclusão com histórico", "ou declaração da data de colação (5.14)"],
     cx="média", ctx="Admite mais do que LIB-0129.")
real("doc_requerimento_anexo", "Documento: Requerimento de Matrícula (anexo) preenchido, com a declaração marcada", "DOC", "Pedir o Requerimento preenchido, com o termo de veracidade.",
     ["Anexo II", "termo de veracidade marcado", "incompleto ou incorreto → indeferimento"], cx="média", jur="Indeferimento.")
real("doc_requerimento_sem_recurso", "Documento: Requerimento de Matrícula; preenchimento incorreto indefere sem recurso", "DOC", "Pedir o Requerimento e dizer que o erro de preenchimento indefere, sem recurso.",
     ["Anexo II", "termo de veracidade", "indeferimento sem recurso"], cx="média", ctx="Difere de LIB do 28 pela proibição expressa de recurso.", jur="Proibição expressa de recurso.")
real("doc_declaracao_comunidade_indigena", "Documento: declaração de pertencimento da comunidade indígena", "DOC", "Pedir a declaração da comunidade, assinada por cacique ou vice e duas lideranças, com contatos.",
     ["Anexo V", "assinaturas exigidas", "contatos para verificação"], cx="alta", jur="Política de cotas.")
real("doc_funai_residencia", "Documento: declaração da Funai ou comprovante de residência em comunidade indígena", "DOC", "Pedir prova de residência em comunidade indígena.", ["Funai ou comprovante"], cx="média")
real("laudo_especialista_detalhado", "Documento: laudo de especialista com espécie, grau, CID, causa e dados do médico", "DOC",
     "Pedir laudo detalhado, dos últimos 12 meses, com identificação do médico.", ["espécie e grau", "CID", "provável causa", "12 meses", "nome, carimbo, CRM"], cx="alta",
     ctx="Mais exigente que LIB-0130 e LIB-0145.", jur="Elegibilidade à reserva.")
real("doc_autodeclaracao_pcd", "Documento: autodeclaração de pessoa com deficiência (anexo)", "DOC", "Pedir a autodeclaração PcD.", ["Anexo IV"], cx="baixa")

# ── Verificação da autodeclaração ───────────────────────────────────────────────────────────────
real("verificacao_etapa_obrigatoria_ppi", "Verificação da autodeclaração como etapa obrigatória para PPI", "AFI", "Dizer que a verificação é obrigatória para as vagas PPI.", ["etapa obrigatória", "PPI"], jur="Cotas raciais.")
real("clva_competencia_meios", "Competência da comissão local e meios da verificação", "AFI", "Dizer quem verifica e como: videoconferência (pretos e pardos) ou análise documental (indígenas).",
     ["CLVA", "videoconferência", "análise documental"], cx="média")
real("clva_comunicacoes_listagem", "Comunicações da comissão por listagem de deferidos e indeferidos", "AFI", "Dizer como a comissão comunica os resultados.", ["atos vinculados ao edital", "listagem geral"], cx="média")
real("recurso_cpva_instancia", "Recurso contra a comissão local, julgado pela comissão permanente", "REC", "Dizer que os recursos contra a CLVA vão à CPVA, instância recursal.", ["recursos fundamentados", "CPVA"],
     cx="média", jur="Instância recursal.")
real("videoconferencia_pandemia", "Videoconferência justificada pela pandemia", "AFI", "Dizer que a verificação é por videoconferência (Plataforma RNP).", ["videoconferência", "RNP"],
     cx="baixa", pend=["A justificativa da pandemia está desatualizada; a regra que vale é a videoconferência?"])
real("protocolos_seguranca", "Protocolos de segurança na verificação", "AFI", "Dizer que a verificação segue os protocolos vigentes.", ["protocolos vigentes"], cx="baixa")
real("heteroidentificacao_resolucao_61", "Heteroidentificação conforme a Resolução CS 61/2019", "AFI", "Citar a norma da heteroidentificação.", ["Resolução CS 61/2019"], cx="média", jur="Fundamento.")
real("reverificacao_qualquer_tempo", "Nova verificação a qualquer tempo, com perda do vínculo", "AFI", "Dizer que o cotista pode ser verificado de novo a qualquer tempo, com perda do vínculo se houver irregularidade.",
     ["a qualquer tempo", "denúncia ou de ofício", "perda do vínculo", "sanções penais"], cx="alta", jur="Perda do vínculo.")
real("titulo_subsecao_livre", "Título de subseção do texto livre", "ATO", "Abrir uma subseção do edital.", ["título"], cls="PARAMETRIZÁVEL", cx="baixa", var=["número", "título"])
real("hetero_menor_responsavel", "Heteroidentificação de menor: responsável presente", "AFI", "Exigir o responsável como observador, se o candidato for menor.", ["menor de 18", "responsável presente"], cx="baixa")
real("hetero_acompanhamento_servidor", "Acompanhamento por servidor na falta do responsável", "AFI", "Garantir acompanhamento por servidor indicado.", ["direito a acompanhamento"], cx="baixa")
real("hetero_documento_identificacao", "Documento original com foto na entrevista", "AFI", "Exigir documento de identificação original com foto.", ["original", "com foto e número"], cx="baixa")
real("hetero_requisitos_tecnicos", "Requisitos técnicos para a entrevista por videoconferência", "AFI", "Listar equipamento e programas necessários.", ["computador ou smartphone", "câmera, microfone, som", "conexão mínima", "navegadores"],
     cx="média", pend=["Pede o Adobe Flash Player, descontinuado."])
real("hetero_iluminacao", "Iluminação adequada na entrevista", "AFI", "Exigir boa iluminação.", ["boa iluminação"], cx="baixa")
real("hetero_vestimenta", "Roupas sem estampa e sem acessórios na entrevista", "AFI", "Proibir estampas e acessórios que dificultem a verificação.", ["sem estampas", "sem boné, chapéu ou acessórios"], cx="baixa")
real("hetero_maquiagem", "Sem maquiagem na entrevista", "AFI", "Proibir maquiagem, sob risco de indeferimento.", ["sem maquiagem", "pode levar ao indeferimento"], cx="baixa", jur="Indeferimento.")
real("hetero_antecedencia_sala", "Acessar a sala até 5 minutos antes", "AFI", "Dizer quando acessar a sala.", ["até 5 minutos antes"], cx="baixa")
real("hetero_passos_acesso", "Passos para entrar e configurar a sala de videoconferência", "AFI", "Explicar o acesso e a configuração de câmera e microfone.", ["conferir dispositivos", "acessar o link", "identificar-se", "habilitar câmera e microfone"],
     cls="ESPECIALIZADA", cx="alta", ctx="Instrução operacional da plataforma, em dois blocos (I e II).")
real("hetero_falha_conexao_candidato", "Falha de conexão do candidato: três tentativas e entrevista pendente", "AFI", "Dizer o que acontece se o candidato não conseguir conectar.", ["três tentativas", "pendente", "print da tela"], cx="média")
real("hetero_descontinuidade_conexao", "Queda de conexão de mais de 10 minutos: entrevista cancelada", "AFI", "Dizer o que acontece com queda longa.", ["mais de 10 minutos", "cancelada", "reagendada se falha do sistema"], cx="média")
real("hetero_justificativa_24h", "Justificar a ausência em até 24 horas, com o print", "AFI", "Dizer o prazo e a forma da justificativa.", ["e-mail", "até 24 horas", "print anexado"], cx="média")
real("hetero_nova_convocacao", "Nova convocação só com justificativa", "AFI", "Dizer que só há nova convocação com justificativa aceita.", ["justificativa conforme 6.9.10"], cx="baixa")
real("hetero_gravacao", "Entrevista gravada em áudio e vídeo", "AFI", "Dizer que a entrevista é gravada.", ["áudio e vídeo"], cx="baixa")
real("hetero_indeferimento_hipoteses", "Hipóteses de indeferimento da autodeclaração de preto ou pardo", "AFI", "Listar quando a autodeclaração é indeferida.",
     ["formulário incorreto", "não comparecer", "recusar orientações", "ausência unânime de características fenotípicas", "recusar ser filmado"], cx="alta", jur="Cotas raciais.")
real("indeferimento_fenotipo_mantem_ac", "Indeferido pela ausência de características fenotípicas permanece na ampla", "AFI",
     "Dizer que o indeferido por fenótipo continua deferido na ampla concorrência.", ["só no indeferimento por fenótipo", "mantido na ampla"], cx="média",
     ctx="Condição mais estreita que LIB-0045 (qualquer indeferimento).", jur="Cotas raciais.")
real("verificacao_indigena_documental", "Verificação do candidato indígena por análise documental", "AFI", "Dizer que a verificação do indígena é documental.", ["análise documental", "pertencimento étnico"], cx="média")
real("indigena_documentacao_inscricao", "Documentação do indígena entregue na inscrição", "AFI", "Exigir toda a documentação do indígena no ato da inscrição.", ["no momento da inscrição"], cx="baixa",
     pend=["Remete aos “itens 5.2 e 6”; a documentação está no 5.4, alínea i."])
real("verificacao_indigena_resultado", "Resultado da verificação do indígena em listagem", "AFI", "Dizer como sai o resultado.", ["CLVA", "deferido ou indeferido", "listagem"], cx="baixa")
real("indigena_indeferimento_hipoteses", "Hipóteses de indeferimento da autodeclaração indígena", "AFI", "Listar quando a autodeclaração indígena é indeferida.", ["formulário incorreto", "documentos faltando", "meios fraudulentos"],
     cx="média", pend=["Cita o Anexo IV (PcD) como formulário do indígena."], jur="Cotas.")
real("verificacao_pcd_equipe", "Verificação da pessoa com deficiência por equipe multiprofissional", "AFI", "Dizer quem verifica a elegibilidade PcD.", ["equipe multiprofissional e interdisciplinar"], cx="média")

# ── Seleção por sorteio ──────────────────────────────────────────────────────────────────────────
real("presenca_sorteio_facultativa", "A presença no sorteio não é obrigatória", "CLA", "Dizer que o candidato não precisa acompanhar o sorteio.", ["presença não obrigatória"], cls="SEMELHANTE", cx="baixa",
     ctx="Dito no 8.1/6.1 e, no 59, também no 6.5.")
real("software_sorteio_semente", "Software do sorteio e campo “Semente utilizada”", "CLA", "Explicar o software e onde conferir a semente.", ["software usado por outros institutos", "aleatoriedade", "campo “Semente utilizada”"],
     cls="SEMELHANTE", cx="alta", ctx="Outra forma de dizer o que LIB-0026 publica de modo estruturado.", trad="Conceito técnico de semente: ver LIB-0026.")
real("analise_sorteados_substituicao", "Análise dos sorteados até as vagas, com substituição do indeferido pelo próximo", "CLA",
     "Dizer que se analisam os documentos dos primeiros sorteados até as vagas e que o indeferido é substituído pelo próximo da ordem.",
     ["ordem pelo sorteio", "análise até o limite de vagas", "indeferido → próximo da ordem"], cls="EXATA", cx="média", jur="Quem ocupa a vaga.")
real("lista_habilitados_sorteio", "Lista de habilitados ao sorteio dois dias antes", "CLA", "Dizer quando sai a lista e quem está habilitado.",
     ["dois dias antes", "habilitado: inscrição com dados completos e documentação do 5.4", "número de cada candidato"], cls="SEMELHANTE", cx="média",
     ctx="O universo difere do de LIB-0027 (todas as inscrições submetidas): aqui só as com documentação completa.", jur="Universo do sorteio.")
real("realizacao_sorteio_online", "Sorteio on-line, transmitido e gravado", "CLA", "Dizer como e onde o sorteio é realizado.", ["dois servidores", "on-line", "YouTube", "gravado"], cls="SEMELHANTE", cx="baixa")
real("realizacao_sorteio_salao", "Sorteio no salão de reuniões do Cefor, gravado", "CLA", "Dizer que o sorteio é presencial no Cefor e gravado.", ["dois servidores", "salão de reuniões", "gravado"], cx="baixa",
     pend=["O 6.6 diz que o sorteio é on-line: presencial, on-line ou os dois?"])
real("homologacao_apos_analise_matricula", "Homologação após a análise; documento irregular impede a matrícula", "CLA", "Dizer que a classificação só se homologa após a análise e que irregularidade impede a matrícula.",
     ["homologação depende da análise", "matrícula não efetivada", "vaga para o próximo"], cx="média")
real("homologacao_apos_analise_indeferimento", "Homologação após a análise; documento irregular indefere a inscrição", "CLA", "Dizer que irregularidade indefere a inscrição.",
     ["homologação depende da análise", "inscrição indeferida", "vaga para o próximo"], cx="média", ctx="Consequência diferente da do 28 (8.6).")
real("sorteio_ampla_depois_reservas", "Sorteio da ampla primeiro, com todos; depois o das reservas", "CLA", "Dizer a ordem dos sorteios e a concorrência simultânea.",
     ["todos no sorteio da ampla", "depois as reservas", "Resolução CS 10/2017"], cx="alta", jur="Cotas.")
real("sorteado_duas_listas", "Sorteado nas duas listas fica na ampla", "CLA", "Dizer que quem é sorteado nas duas listas é classificado na ampla.", ["classificado na ampla"], cx="média", jur="Cotas.")
real("substituicao_vaga_reservada", "Vaga reservada de desistente vai ao próximo autodeclarado", "CLA", "Dizer quem ocupa a vaga reservada de quem desiste.", ["próximo autodeclarado sorteado"], cx="média", jur="Cotas.")
real("autodeclarados_na_ampla_nao_computados", "Autodeclarados sorteados na ampla não contam nas reservadas", "CLA", "Dizer que o cotista classificado na ampla libera a vaga reservada.", ["não computados nas reservadas", "vaga ao próximo autodeclarado"],
     cx="média", jur="Cotas.")
real("suplentes_analise_documentos", "Análise dos documentos dos suplentes, por código de vaga", "CLA", "Dizer quantos suplentes têm documentos analisados.", ["até N suplentes por código de vaga", "chamada imediata em caso de desistência"],
     cls="PARAMETRIZÁVEL", cx="média", var=["condição: número de suplentes (15 no 28, 30 no 59)"])
real("recurso_suplentes_documentacao", "Recurso do suplente com documentação indeferida", "REC", "Dizer que o suplente indeferido pode recorrer no prazo do Cronograma.", ["possibilidade de recurso", "prazo do Cronograma"],
     cls="EXATA", cx="baixa", jur="Direito de recorrer.")
real("suplentes_nova_turma", "Suplentes podem ser chamados para nova turma na validade", "CON", "Dizer que, havendo nova oferta na validade, suplentes podem compor a turma.", ["nova oferta", "convocação publicada", "cabe ao candidato acompanhar"], cx="média")

# ── Recursos ─────────────────────────────────────────────────────────────────────────────────────
real("recurso_somente_resultado_preliminar", "Recurso somente contra o resultado preliminar", "REC", "Limitar o recurso ao resultado preliminar.", ["só o resultado preliminar"], cx="média",
     jur="Restrição expressa (proibição para os demais atos).", ctx="Os atos não listados ficam sem recurso **por cláusula expressa**, diferente de ausência.")
real("recurso_somente_verificacao_e_documentacao", "Recurso somente contra a verificação da autodeclaração e o resultado preliminar da documentação", "REC",
     "Limitar o recurso a dois atos.", ["verificação da autodeclaração", "resultado preliminar da análise da documentação"], cx="média", jur="Restrição expressa.",
     pend=["O 8.12 e o Cronograma preveem recurso dos suplentes: cabem na restrição do 9.1?"])
real("recurso_nao_garante", "O recurso não garante alteração do resultado", "REC", "Dizer que recorrer não garante mudança, e que equívocos verificados serão retificados.", ["não garante", "equívocos retificados"], cls="EXATA", cx="baixa")
real("recurso_exige_fundamentacao", "Recurso sem fundamentação é indeferido", "REC", "Exigir fundamentação no recurso.", ["sem fundamentação → indeferido"], cls="EXATA", cx="baixa", jur="Admissibilidade.")
real("recurso_fora_prazo", "Recurso fora do prazo não é aceito", "REC", "Recusar recurso intempestivo.", ["fora do prazo não"], cls="EXATA", cx="baixa", jur="Admissibilidade.")
real("resultado_recurso_publicacao", "Onde sai o resultado do recurso", "REC", "Dizer onde se publica o resultado dos recursos.", ["sítios do Ifes e do Cefor", "conforme o Cronograma"], cls="SEMELHANTE", cx="baixa")

# ── Matrícula e acesso ───────────────────────────────────────────────────────────────────────────
real("matricula_so_homologada", "Só se efetiva a matrícula homologada", "CON", "Dizer que só a matrícula homologada se efetiva.", ["situação “matrícula homologada”"], cls="EXATA", cx="baixa")
real("cancelamento_documentacao_falsa", "Cancelamento por documentação falsa, com responsabilização", "CON", "Dizer que documento falso cancela a matrícula e gera responsabilidade legal.", ["falsa ou adulterada", "cancelamento", "responder legalmente"],
     cls="EXATA", cx="baixa", jur="Responsabilidade penal.")
real("cancelamento_sem_verificacao", "Cancelamento de quem não participa da verificação", "CON", "Dizer que faltar à verificação convocada cancela a matrícula.", ["não participar quando convocado", "cancelamento"], cx="baixa")
real("matriculas_nao_aceitas_canceladas", "Matrículas não aceitas são canceladas", "CON", "Dizer que matrícula não aceita é cancelada definitivamente.", ["cancelamento automático e definitivo"], cls="SEMELHANTE", cx="baixa")
real("vedacao_matricula_simultanea_especializacao", "Vedação de matrícula simultânea em mais de dois cursos de especialização", "CON", "Proibir matrícula simultânea, com as normas citadas.", ["mais de dois cursos de especialização", "Portaria 1.466/2011", "Resolução CS 59/2011"],
     cx="média", pend=["Contradiz o 10.4, II (“mais de um”)."], jur="Vedação.")
real("vedacao_matricula_simultanea_ifes", "Vedação de matrícula simultânea no Ifes por nível de curso", "CON", "Listar os casos em que não se pode ter duas matrículas.", ["stricto sensu", "especialização", "graduação", "técnico"], cx="média", jur="Vedação.")
real("matricula_simultanea_excecoes", "Matrícula simultânea: limite de dois cursos e exceções", "CON", "Dizer o limite e as exceções (extensão, aperfeiçoamento, FIC).", ["mais de dois cursos não", "exceções"], cx="média")
real("opcao_entre_cursos", "Quem já está matriculado deve optar", "CON", "Exigir a opção por um curso.", ["optar"], cx="baixa")
real("desligamento_outro_lato_sensu", "Desligamento automático de outro lato sensu ao optar", "CON", "Dizer que a matrícula no novo curso desliga do anterior.", ["desligamento automático"], cx="baixa", jur="Perda de vínculo.")
real("regularizacao_indeferidos", "Convocação de indeferidos para regularizar, se sobrarem vagas", "CON", "Dizer que a Administração pode chamar indeferidos para regularizar.", ["se sobrarem vagas", "ordem do sorteio", "regularização"], cls="EXATA", cx="média")
real("regularizacao_prazo_email", "Prazo de 2 dias úteis para regularizar, a partir do e-mail", "CON", "Dizer o prazo e a consequência de não regularizar.", ["e-mail", "2 dias úteis", "próximo suplente"], cls="SEMELHANTE", cx="média", jur="Prazo.")
real("desistencia_nao_comparecimento_aulas", "Falta na primeira semana sem justificativa: desistência", "CON", "Dizer que faltar à primeira semana cancela a matrícula.", ["primeira semana", "sem justificativa legal", "cancelamento", "suplente chamado"], cx="média", jur="Perda da vaga.")
real("desistencia_nao_acesso_ava", "Sem acesso ao AVA em 5 dias: desistência", "CON", "Dizer que não acessar a primeira disciplina em 5 dias cancela a matrícula.", ["5 dias corridos", "cancelamento", "suplente chamado"], cx="média", jur="Perda da vaga.")
real("envio_login_senha", "Login e senha por e-mail até um dia antes do curso", "CON", "Dizer quando chegam os dados de acesso.", ["e-mail", "até 1 dia antes"], cx="baixa")
real("contato_sem_login", "Contato se o login não chegar", "CON", "Dizer a quem escrever.", ["e-mail de contato"], cx="baixa")
real("responsabilidade_email", "Responsabilidade de acompanhar o e-mail, inclusive o spam", "CON", "Dizer que acompanhar o e-mail é dever do aluno.", ["e-mail do Anexo II", "caixa de spam"], cx="baixa")
real("aluno_apos_homologacao", "Depois da homologação, a pessoa é aluna e muda de atendimento", "CON", "Dizer quem atende depois da homologação.", ["aluno oficialmente", "coordenação ou secretaria"], cx="baixa")
real("atendimento_pos_selecao", "Assuntos acadêmicos com a coordenação ou a secretaria", "CON", "Dizer a quem levar senha, certificação e documentos.", ["coordenação ou secretaria"], cx="baixa")
real("declaracoes_secretaria", "Declarações de matrícula, frequência ou conclusão", "CON", "Dizer onde pedir declarações e que o prazo varia.", ["onde pedir", "prazo variável"], cls="SEMELHANTE", cx="baixa", ctx="Dita duas vezes no 28 (12.5 e 13.5).")
real("encerramento_selecao", "Fim da atuação da equipe de seleção", "CON", "Dizer quando a seleção encerra e o que continua com ela.", ["após a lista de matriculados", "questões operacionais com a coordenação"], cx="baixa")
real("entrevista_napne", "Entrevista com o Napne para o candidato PcD classificado", "AFI", "Dizer que o classificado PcD faz entrevista para identificar o atendimento de que precisa.",
     ["classificado PcD", "Napne", "antes do início", "agendamento pelo Napne"], cx="média",
     ctx="É onde o edital trata do atendimento específico — inclusive, em tese, de quem precisa de intérprete de Libras.", jur="Acessibilidade.")
real("contato_napne", "Procurar o Napne se não houver contato", "AFI", "Dizer o que fazer se o Napne não contatar.", ["e-mail do Napne"], cx="baixa")

# ── Disposições finais ──────────────────────────────────────────────────────────────────────────
real("inexatidao_eliminacao", "Inexatidão de informação elimina e anula os atos", "GER", "Dizer que informação inexata elimina o candidato, mesmo depois.", ["ainda que depois", "eliminação", "nulidade dos atos"], cls="EXATA", cx="média", jur="Eliminação.")
real("fraude_verificacao", "Convocação para verificação em caso de denúncia de fraude", "GER", "Dizer que, havendo denúncia, o candidato pode ser convocado, com contraditório.", ["denúncia ou suspeita", "contraditório e ampla defesa", "a qualquer tempo"], cls="EXATA", cx="média", jur="Processo.")
real("fraude_perda_vaga", "Fraude implica perda da vaga e penalidades", "GER", "Dizer a consequência da fraude.", ["perda da vaga", "penalidades", "mesmo após a matrícula"], cls="EXATA", cx="baixa", jur="Sanção.")
real("gratuidade_mensalidades", "Sem mensalidades", "GER", "Dizer que não há mensalidade.", ["sem encargos de mensalidade"], cls="EXATA", cx="baixa")
real("vigencia_edital", "Vigência do edital a partir da publicação", "GER", "Dizer quando o edital vigora e que vale só para este processo.", ["a partir da publicação", "só este processo", "revogadas as disposições em contrário"], cls="EXATA", cx="baixa",
     ctx="O 59 o diz duas vezes (10.7 e 10.9).")
real("conhecimento_normas_anexos", "Conhecer as normas e os anexos antes de se inscrever", "GER", "Exigir que o candidato conheça o edital e os anexos.", ["edital e anexos", "não pode alegar desconhecimento"], cx="baixa",
     pend=["Chama o curso de “Libras Básico - Nível A2”."])
real("cumprimento_prazos_desclassificacao", "Prazos do Cronograma, sob pena de desclassificação", "GER", "Dizer que perder prazo desclassifica.", ["cumprir prazos", "desclassificação"], cx="baixa", jur="Desclassificação.")
real("cessao_imagem_inscricao", "Cessão de imagem e voz ao se inscrever", "GER", "Dizer que a inscrição autoriza o uso de imagem e voz para fins educacionais.", ["ao se inscrever", "imagem e voz", "total, não exclusivo, definitivo e gratuito"], cx="média",
     jur="Direito de imagem.", pend=["Cessão definitiva pela simples inscrição: questão jurídica."])
real("cessao_imagem_matricula", "Cessão de imagem e voz do aluno matriculado", "GER", "Dizer que o aluno cede imagem e voz para fins educacionais.", ["aluno matriculado", "imagem e voz", "gratuito"], cx="média", jur="Direito de imagem.")
real("cessao_imagem_prazo", "Prazo indeterminado da cessão, salvo notificação", "GER", "Dizer o prazo da cessão e como encerrá-la.", ["prazo indeterminado", "notificação com 90 dias"], cx="baixa", jur="Direito de imagem.")

# ── Cronograma ───────────────────────────────────────────────────────────────────────────────────
for k, t_, fin in [("ev_situacao_inscricao", "Evento: publicação da situação das inscrições", "Dizer quando sai a situação das inscrições."),
                   ("ev_link_transmissao_sorteio", "Evento: link da transmissão ou da gravação do sorteio", "Dizer quando se publica o link do sorteio."),
                   ("ev_resultado_recursos", "Evento: resultado dos recursos", "Dizer quando sai o resultado dos recursos."),
                   ("ev_convocacao_heteroidentificacao", "Evento: publicação da convocação para a verificação", "Dizer quando sai a convocação para a verificação."),
                   ("ev_aula_inaugural", "Evento: aula inaugural", "Dizer quando é a aula inaugural.")]:
    ev(k, t_, fin, "Evento de cronograma de edital real.")
    U[k].update(ori="D", fonte=FONTE_REAL + ", Anexo I (Cronograma)")
    U[k]["hist"] = [f"{R3} — criada a partir dos editais reais."]

# ── Anexos ───────────────────────────────────────────────────────────────────────────────────────
real("identificacao_anexo", "Identificação do edital no alto do anexo", "ATO", "Repetir o número e o objeto do edital no anexo.", ["número e objeto"], cx="baixa")
real("cabecalho_institucional_anexo", "Cabeçalho ou rodapé institucional de anexo", "ANX", "Identificar a instituição e o endereço no anexo.", ["instituição", "endereço e telefone"], cls="SEMELHANTE", cx="baixa")
real("requerimento_formulario_campos", "Requerimento de Matrícula: campos do formulário", "ANX", "Pedir os dados pessoais e socioeconômicos para a matrícula.",
     ["cada campo", "sem abreviaturas"], cls="EXATA", cx="alta", ctx="Pede, entre outros, cor/raça, renda familiar, tipo sanguíneo e necessidades educacionais especiais.",
     trad="Formulário: traduzir o que cada campo pede, não preenchê-lo.", pend=["Por que cada dado é pedido (LGPD) não está dito no formulário."])
real("requerimento_pedido_matricula", "Requerimento: o pedido de matrícula no curso", "ANX", "Fazer o pedido formal de matrícula no curso.", ["nome do curso"], cls="PARAMETRIZÁVEL", cx="baixa",
     var=["nome do curso"], pend=["No 59, o curso aparece como “Libras Básico - Nível A2”."])
real("decl_requerimento_anexo", "Declaração de veracidade do Requerimento (anexo), com autorização de averiguação", "ANX",
     "Declarar a veracidade das informações e documentos, a ciência do cancelamento e autorizar a averiguação.",
     ["autenticidade e veracidade", "omissão ou falsidade → cancelamento a qualquer tempo", "autorização de averiguação", "responsabilidade legal"],
     cls="EXATA", cx="alta", ctx="Outra declaração que as do sistema (LIB-0135, LIB-0154): inclui omissão, divergência e autorização de averiguação.", jur="Efeito penal.")
real("autodeclaracao_etnico_formulario", "Autodeclaração étnico-racial: identificação e opção", "ANX", "Declarar-se preto, pardo ou indígena e dizer o critério.", ["dados", "opção única", "critério: características fenotípicas"],
     cx="alta", jur="Cotas.")
real("autodeclaracao_ciencia_falsidade", "Autodeclaração: ciência das consequências da falsidade", "ANX", "Declarar ciência de que a falsidade exclui do processo ou cancela a matrícula.", ["exclusão", "cancelamento", "sanções penais"], cx="alta", jur="Efeito penal.")
real("autodeclaracao_convocacao_qualquer_tempo", "Autodeclaração: ciência de convocação a qualquer tempo", "ANX", "Declarar ciência de poder ser convocado para verificação.", ["a qualquer tempo"], cx="baixa")
real("autodeclaracao_pcd_formulario", "Autodeclaração PcD: identificação e CID", "ANX", "Declarar a deficiência, com o CID do laudo.", ["dados", "CID"], cx="média")
real("autodeclaracao_pcd_laudo", "Autodeclaração PcD: o laudo atesta espécie e grau", "ANX", "Vincular a declaração ao laudo.", ["laudo com CID", "espécie e grau"], cx="baixa")
real("declaracao_pertencimento_formulario", "Declaração de pertencimento étnico (formulário da comunidade)", "ANX", "Fazer a comunidade declarar o pertencimento do estudante.", ["comunidade", "laços", "assinaturas de lideranças e do cacique"], cx="alta", jur="Cotas.")
for k, t_, fin, obr in [
    ("lgpd_finalidade_termo", "Termo de dados: o que o documento registra", "Dizer que o termo registra o consentimento para finalidade específica, conforme a LGPD.", ["consentimento livre, informado e inequívoco", "LGPD"]),
    ("lgpd_consentimento", "Termo de dados: a opção de consentir", "Registrar o consentimento e o que o controlador poderá fazer.", ["quem consente", "operações de tratamento"]),
    ("lgpd_nao_consentimento", "Termo de dados: a opção de não consentir", "Registrar a recusa do consentimento.", ["quem não consente"]),
    ("lgpd_dados", "Termo de dados: quais dados", "Listar os dados tratados.", ["requerimento", "usuário e senha", "imagem e voz", "comunicações"]),
    ("lgpd_finalidades", "Termo de dados: para quê", "Listar as finalidades.", ["relacionamento acadêmico", "pesquisa", "contratos", "serviços"]),
    ("lgpd_compartilhamento", "Termo de dados: compartilhamento", "Autorizar o compartilhamento necessário.", ["outros agentes", "finalidades"]),
    ("lgpd_seguranca", "Termo de dados: segurança e incidentes", "Dizer as obrigações de segurança e de comunicar incidentes.", ["medidas de segurança", "comunicação à ANPD"]),
    ("lgpd_termino", "Termo de dados: término e eliminação", "Dizer quanto tempo os dados ficam e como pedir eliminação.", ["enquanto pertinentes", "pedido de eliminação"]),
    ("lgpd_direitos", "Termo de dados: direitos do titular", "Listar os direitos do titular.", ["nove direitos"]),
    ("lgpd_revogacao", "Termo de dados: revogação do consentimento", "Dizer como revogar.", ["a qualquer momento", "e-mail ou correspondência"]),
    ("lgpd_nao_consentimento_matricula", "Termo de dados: recusar não anula o direito à matrícula", "Dizer que não consentir não tira o direito à matrícula.", ["direito à matrícula mantido"]),
]:
    real(k, t_, "ANX", fin, obr, cx="média", ctx="Termo institucional do Ifes, anexo do edital; texto padrão provável entre editais.", jur="LGPD.")

real("local_data_assinatura", "Local, data e assinatura do formulário", "ANX", "Fechar o formulário com o lugar, a data e a assinatura de quem declara.",
     ["local", "data", "assinatura, quando há campo"], cls="PARAMETRIZÁVEL", cx="baixa", var=["ano impresso ou em branco", "condição: campo de assinatura"],
     ctx="Campos em branco. No 59, sem campo de assinatura no Requerimento.")
U["vigencia_edital"].update(cls="SEMELHANTE", eq="**Equivalência provável:** as três ocorrências diferem só na inicial de “Edital”; o 59 repete a cláusula (10.7 e 10.9).")
for k in ("identificacao_lista_cefor", "doc_militar"):
    U[k].update(cls="SEMELHANTE", eq="**Equivalência provável:** 28 e 59 diferem só na pontuação final (“;” × “.” ou nenhuma).")

# ── Unidades anteriores que os editais reais alcançaram ─────────────────────────────────────────
# Uma frase do sistema com o mesmo sentido de uma cláusula real deixa de ser EXATA: passa a SEMELHANTE,
# com a equivalência a confirmar. O texto do sistema, em vários casos, foi calibrado nos próprios editais
# do Cefor (a auditoria do PDF de 08/10 calibrou o cenário A no 28/2026).
for k, cls in {
    "reversao_ausencia": "SEMELHANTE", "ordem_sorteio": "SEMELHANTE", "publicacoes_oficiais": "SEMELHANTE", "publico_alvo": "SEMELHANTE",
    "oferta_curso": "SEMELHANTE", "carga_duracao": "PARAMETRIZÁVEL", "concorrencia_simultanea": "SEMELHANTE", "indicacao_perfil_lista": "SEMELHANTE",
    "classificacao_sorteio_texto": "SEMELHANTE", "matricula_documentacao": "SEMELHANTE", "conv_suplentes_desistencia": "SEMELHANTE",
    "hetero_autodeclarados": "SEMELHANTE", "criterio_fenotipico": "SEMELHANTE", "indeferimento_autodeclaracao": "SEMELHANTE",
    "nao_comparecimento_heteroidentificacao": "SEMELHANTE", "prazo_validade": "PARAMETRIZÁVEL", "recurso_canal_geral": "SEMELHANTE",
    "recurso_vedacao_outras_formas": "SEMELHANTE", "aceitacao_normas": "SEMELHANTE", "duvidas_canal_exclusivo": "PARAMETRIZÁVEL",
    "req_acesso_computador": "SEMELHANTE",
}.items():
    antes = U[k]["cls"]
    corrigir(k, f"{R3}: ganhou ocorrência em edital real com outra redação; classificação {antes} → {cls}, equivalência a confirmar.",
             cls=cls, eq=(U[k].get("eq") or "") + " **Rodada 3:** a ocorrência do edital real tem outra redação; a equivalência fica a confirmar.")
    U[k]["hist"][-1] = U[k]["hist"][-1].replace(f"{R2} — {R3}: ", f"{R3} — ")
corrigir("titulo_secao", "nos editais reais, o título é livre e não segue o catálogo de 22 seções.",
         ctx=U["titulo_secao"]["ctx"] + " Nos editais reais, o título é texto livre (“DAS VAGAS”, “RECURSO”…), sem catálogo.")
U["titulo_secao"]["hist"][-1] = U["titulo_secao"]["hist"][-1].replace(R2, R3)
