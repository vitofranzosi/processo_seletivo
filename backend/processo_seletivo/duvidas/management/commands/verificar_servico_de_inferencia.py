"""A verificação de conexão com o serviço de inferência (071, `R-017`, `FR-1520`).

**Antes de cada rodada e de cada sessão com o setor** (DP-7, opção b). O piloto confere sozinho, a
cada pergunta, só o modelo que respondeu (`FR-1521`); a quantização, o contexto e a GPU mudam no
servidor sem a aplicação saber, e é este comando que os confere contra a configuração. Com
divergência, sai com código 1, e a equipe não roda a rodada nem a sessão.

**Não grava nada** — nem o resultado: pela DP-7 (b), ele vai ao relatório, colado por quem rodou.

**Uma conversa sintética, e só uma**, sem conteúdo de Edital, pela mesma porta das perguntas: é o
corpo real que vai ao serviço. Os tokens que o serviço diz ter lido, contra os do tokenizer, medem o
acréscimo por mensagem do molde de conversa, que a aplicação não reproduz (`R-006`). No serviço
externo ela custa, e por isso só sai quando a chave tem limite de gasto — a única barreira de gasto
do piloto (`FR-1507`).

**O que o serviço não informa fica dito**, na lista "a confirmar com a infraestrutura" — inclusive
se a versão instalada do Ollama aceita `truncate` e `shift`: a API não diz, e um campo desconhecido
é ignorado em silêncio.
"""

from __future__ import annotations

import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from processo_seletivo.duvidas.domain.mensagens import ESQUEMA_DA_SAIDA
from processo_seletivo.duvidas.infrastructure import inferencia, tokens

SINTETICA = (
    {"role": "system", "content": "Você responde a um teste de conexão, no formato pedido."},
    {
        "role": "user",
        "content": "Responda com o tipo FORA_DO_ESCOPO e um trecho de explicação, sem fontes, "
        "que diga apenas: teste de conexão.",
    },
)
A_CONFIRMAR_NO_OLLAMA = (
    "OLLAMA_NUM_PARALLEL, OLLAMA_MAX_QUEUE, OLLAMA_KV_CACHE_TYPE, outros serviços na GPU, modo de "
    "raciocínio em uso, rede, e se a versão instalada aceita truncate e shift"
)
A_CONFIRMAR_NO_OPENROUTER = "a quantização e a revisão do modelo que o provedor serve"


class Command(BaseCommand):
    help = "Confere o serviço de inferência do piloto contra a configuração, sem gravar nada."

    def handle(self, *args, **opcoes):
        servico = settings.ASSISTENTE_SERVICO
        self.divergencias = []
        self.stdout.write(f"Serviço: {servico or '—'} em {settings.ASSISTENTE_ENDERECO or '—'}")
        if servico == inferencia.OLLAMA:
            self._ollama()
        elif servico == inferencia.OPENROUTER:
            self._openrouter()
        elif servico:
            # Com maiúscula ou espaço, o valor existe e não é conhecido: dizer "nenhum serviço"
            # mandava procurar a variável ausente, e não o valor errado (073, `FR-1661`).
            self.divergencias.append(
                f"serviço desconhecido: {servico!r} (ASSISTENTE_SERVICO); os aceitos são "
                f"{inferencia.OLLAMA} e {inferencia.OPENROUTER}, "
                f"e em produção só {inferencia.OLLAMA}"
            )
        else:
            self.divergencias.append("nenhum serviço configurado (ASSISTENTE_SERVICO)")
        self.stdout.write(
            "Divergências: " + ("; ".join(self.divergencias) if self.divergencias else "nenhuma")
        )
        if self.divergencias:
            sys.exit(1)

    # ---- Ollama -----------------------------------------------------------------------------

    def _ollama(self):
        endereco = settings.ASSISTENTE_ENDERECO
        modelo = settings.ASSISTENTE_MODELO
        versao = self._ler(lambda: inferencia.obter(f"{endereco}/api/version"), "a versão")
        if versao is None:
            return
        self.stdout.write(f"Versão do Ollama: {versao.get('version', '—')}")
        instalados = self._ler(lambda: inferencia.obter(f"{endereco}/api/tags"), "os modelos")
        nomes = {item.get("name") for item in (instalados or {}).get("models") or []}
        instalado = modelo in nomes
        self.stdout.write(f"Modelo configurado: {modelo} — instalado: {_sim(instalado)}")
        if not instalado:
            self.divergencias.append(f"o modelo {modelo} não está instalado")
            return
        mostrado = self._ler(
            lambda: inferencia.postar(f"{endereco}/api/show", {"model": modelo}), "o modelo"
        )
        if mostrado is not None:
            self._detalhes(mostrado)
        self._conversa_sintetica()
        # Depois da conversa, que é o que carrega o modelo: antes dela, "não carregado" não diria
        # nada sobre a GPU.
        carregados = self._ler(lambda: inferencia.obter(f"{endereco}/api/ps"), "a ocupação")
        if carregados is not None:
            self._gpu(carregados, modelo)
        self.stdout.write(
            "truncate/shift: "
            + (
                "enviados (ASSISTENTE_OLLAMA_SEM_CORTE)"
                if settings.ASSISTENTE_OLLAMA_SEM_CORTE
                else "não enviados — a conferência da contagem é a única proteção"
            )
        )
        self.stdout.write(f"A confirmar com a infraestrutura: {A_CONFIRMAR_NO_OLLAMA}.")

    def _detalhes(self, mostrado):
        detalhes = mostrado.get("details") or {}
        informacoes = mostrado.get("model_info") or {}
        arquitetura = informacoes.get("general.architecture") or detalhes.get("family") or ""
        contexto = informacoes.get(f"{arquitetura}.context_length")
        quantizacao = detalhes.get("quantization_level") or ""
        self.stdout.write(
            f"  família: {detalhes.get('family') or '—'}   "
            f"parâmetros: {detalhes.get('parameter_size') or '—'}   "
            f"quantização: {quantizacao or '—'}   contexto do modelo: {contexto or '—'}"
        )
        esperada = settings.ASSISTENTE_QUANTIZACAO
        if not esperada:
            self.divergencias.append(
                "a quantização esperada não está configurada (ASSISTENTE_QUANTIZACAO)"
            )
        elif quantizacao.lower() != esperada.lower():
            self.divergencias.append(
                f"a quantização servida é {quantizacao or '—'}, e a configurada, {esperada}"
            )
        if contexto is None:
            self.divergencias.append("o serviço não informou o contexto do modelo")
        elif int(contexto) < settings.ASSISTENTE_CONTEXTO_TOKENS:
            self.divergencias.append(
                f"o contexto do modelo é {contexto}, menor que o configurado "
                f"({settings.ASSISTENTE_CONTEXTO_TOKENS})"
            )

    def _gpu(self, carregados, modelo):
        item = next(
            (item for item in carregados.get("models") or [] if item.get("name") == modelo), None
        )
        if item is None:
            self.stdout.write("Modelo carregado: não")
            self.divergencias.append("o modelo não ficou carregado depois da conversa sintética")
            return
        total, na_gpu = item.get("size") or 0, item.get("size_vram") or 0
        parte = round(100 * na_gpu / total) if total else 0
        gigas = f"{na_gpu / 1e9:.1f}".replace(".", ",")
        self.stdout.write(f"Modelo carregado: sim, {parte}% na GPU ({gigas} GB)")
        if parte < 100:
            self.divergencias.append(f"o modelo está {100 - parte}% na CPU")

    # ---- OpenRouter -------------------------------------------------------------------------

    def _openrouter(self):
        chave = self._ler(
            lambda: inferencia.obter(
                f"{settings.ASSISTENTE_ENDERECO}/key",
                cabecalhos={"Authorization": f"Bearer {settings.ASSISTENTE_CREDENCIAL}"},
            ),
            "a chave",
        )
        limite = None
        if chave is not None:
            dados = chave.get("data") or {}
            limite = dados.get("limit")
            self.stdout.write(
                f"Limite de gasto da chave: {limite if limite is not None else '—'}   "
                f"usado: {dados.get('usage', '—')}"
            )
            if limite is None:
                self.divergencias.append("a chave não tem limite de gasto (FR-1507)")
        self.stdout.write(f"Modelo configurado: {settings.ASSISTENTE_MODELO}")
        if limite is None:
            # A conversa sintética é uma chamada paga como as outras, e sem limite na chave nada
            # limitaria o gasto dela (`FR-1507`).
            self.stdout.write("Conversa sintética: não enviada — a chave não tem limite de gasto")
        else:
            self._conversa_sintetica()
        self.stdout.write(f"A confirmar com a infraestrutura: {A_CONFIRMAR_NO_OPENROUTER}.")

    # ---- os dois ----------------------------------------------------------------------------

    def _conversa_sintetica(self):
        inicio = time.monotonic()
        try:
            devolucao = inferencia.conversar(
                list(SINTETICA), ESQUEMA_DA_SAIDA, inferencia.parametros_configurados()
            )
        except inferencia.FalhaDoServico as falha:
            de_quem = f", pelo provedor {falha.provedor}" if falha.provedor else ""
            self.stdout.write(f"Conversa sintética: falhou — {falha.motivo}{de_quem}")
            self.divergencias.append(f"a conversa sintética falhou ({falha.codigo})")
            return
        segundos = f"{time.monotonic() - inicio:.1f}".replace(".", ",")
        informados = devolucao.tokens_de_entrada
        try:
            texto = sum(tokens.contar_texto(mensagem["content"]) for mensagem in SINTETICA)
        except tokens.SemTokenizer as falta:
            texto = None
            self.divergencias.append(f"sem tokenizer: {falta}")
        self.stdout.write(
            f"Conversa sintética: entrada {informados if informados is not None else '—'} tokens "
            f"({'texto ' + str(texto) if texto is not None else 'sem tokenizer para medir'})  "
            f"saída {devolucao.tokens_de_saida or '—'}  término {devolucao.termino or '—'}  "
            f"{segundos} s"
        )
        if devolucao.provedor:
            configurado = settings.ASSISTENTE_PROVEDOR or "nenhum — o OpenRouter escolhe"
            self.stdout.write(
                f"Provedor que respondeu: {devolucao.provedor} (configurado: {configurado})"
            )
        if texto is not None and informados is not None:
            # Uma chamada só não separa o fixo do por mensagem: a soma é o que ela mede, e o log das
            # trocas, com duas ou mais quantidades de mensagens, separa um do outro (`R-006`).
            medido = informados - texto
            configurado = tokens.acrescimo(len(SINTETICA))
            self.stdout.write(
                f"Acréscimo além do texto: medido {medido} tokens em {len(SINTETICA)} mensagens; "
                f"configurado {configurado} (ASSISTENTE_TOKENS_POR_CHAMADA "
                f"{settings.ASSISTENTE_TOKENS_POR_CHAMADA} + {len(SINTETICA)} × "
                f"ASSISTENTE_TOKENS_POR_MENSAGEM {settings.ASSISTENTE_TOKENS_POR_MENSAGEM})"
            )
            if medido > configurado:
                # Subestimado, a aplicação conta menos do que o serviço lê, e um contexto estourado
                # pode passar pela conferência da contagem (`FR-1482`).
                self.divergencias.append(
                    f"o acréscimo configurado ({configurado}) é menor que o medido ({medido})"
                )
        elif informados is None:
            self.divergencias.append("o serviço não informou os tokens de entrada")
        if devolucao.modelo != settings.ASSISTENTE_MODELO:
            self.divergencias.append(
                f"respondeu o modelo {devolucao.modelo or '—'}, e não o configurado"
            )
        if devolucao.termino != "stop":
            self.divergencias.append(
                f"a conversa sintética terminou por {devolucao.termino or '—'}, e não por stop"
            )

    def _ler(self, ler, o_que):
        try:
            return ler()
        except inferencia.FalhaDoServico as falha:
            self.stdout.write(f"Não foi possível ler {o_que}: {falha.motivo}")
            self.divergencias.append(f"não foi possível ler {o_que} ({falha.codigo})")
            return None


def _sim(valor):
    return "sim" if valor else "não"
