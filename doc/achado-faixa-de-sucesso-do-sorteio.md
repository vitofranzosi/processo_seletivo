# Achado — a tela do sorteio anuncia sempre o mesmo ato, e ele quase nunca é o que aconteceu

**Data:** 2026-09-10
**Origem:** demonstração do ciclo da `021` pela interface, percorrido como `paulo.presidente` no
Edital de sorteio do `seed_demo`, para responder como o sorteio ficou operacionalmente.
**Natureza:** achado registrado — e **corrigido no mesmo dia**, pelo caminho 2 da lista abaixo.

> **Desfecho, acrescentado em 10/09/2026.** Este achado foi encontrado, no mesmo dia e por sessão
> independente, na exploração de [`descoberta-rito-do-sorteio-2026-09-10.md`](descoberta-rito-do-sorteio-2026-09-10.md)
> — ali é o **E-01**, e a faixa de erro é o **E-02**. Os dois foram corrigidos no PR #97, mesclado
> horas depois deste registro: cada comando passa a declarar o ato que praticou, e a tela escolhe a
> frase por ele. Observar responde *"Números obtidos em…"*; realizar responde *"Sorteio realizado,
> com N participantes na ordem…"*, com a semente e o manifesto; a recusa nomeia qual dos quatro
> comandos falhou.
>
> A última frase deste documento — a de que qualquer caminho pede asserção de tela para os quatro
> — também foi atendida: `backend/tests/interface/test_console_do_sorteio.py` afirma o que a tela
> diz depois de cada comando, e é ele que impede o próximo comando de repetir o defeito.
>
> **O texto abaixo fica como estava**, no presente do indicativo em que foi escrito. Ele descreve o
> sistema no instante em que foi medido, e é isso que um achado registra — reescrevê-lo no passado
> apagaria a única coisa que ele tem para dizer a quem o ler depois: que isto existiu, e como
> ninguém viu.

## O que acontece

A tela do sorteio tem quatro comandos. Os quatro escrevem no **mesmo** lugar da sessão, e a tela
tem **uma** frase para todos:

```html
{% if resultado %}<p class="sucesso" role="status">Relação publicada e congelada,
  com {{ resultado.quantidade }} participante{{ resultado.quantidade|pluralize }}.
  O resumo é <code>{{ resultado.resumo }}</code>.</p>{% endif %}
```
`backend/processo_seletivo/interface/templates/interface/sorteio.html:14`

Os desfechos que os comandos devolvem não têm as mesmas chaves:

| Comando | Chaves do desfecho | O que a faixa exibe |
|---|---|---|
| `publicar_relacao` | `relacao`, `quantidade`, `resumo`, `metodoHash`, `algoritmo` | correto |
| `observar_ocorrencia` | `ocorrencia`, `fonte`, `referencia`, `materialBruto`, … | *"Relação publicada e congelada, com participante. O resumo é ."* |
| `constituir_sorteio` | `sorteio`, `ato`, `relacao`, `quantidade`, `semente`, `manifestoHash` | *"Relação publicada e congelada, com 7 participantes. O resumo é ."* |
| `anular_sorteio` | os mesmos de `constituir_sorteio` | idem |

Observado ao vivo, nesta ordem, na demonstração de 10/09/2026: observar a ocorrência 5926 produziu
a frase com o número em branco; **realizar o sorteio** produziu a frase com `7` — a contagem certa,
sob o anúncio errado.

O terceiro caso é o pior justamente por ser plausível. A faixa é verde, tem `role="status"`, traz o
número correto de participantes, e afirma que o que acabou de acontecer foi a publicação da
relação — no instante em que o certame constituiu a ordem, com a tela transmitida.

A faixa de erro tem a mesma forma: `sorteio.html:13` diz **"Não foi possível publicar:"** para a
recusa de qualquer um dos quatro comandos. Um sorteio recusado pela FR-016 — semente conhecida
sobre relação alterada — é anunciado como falha de publicação.

## Por que

Um canal só para quatro atos. As quatro rotas gravam `request.session["resultado_do_sorteio"]`
(`interface/views.py:4861`, `:4911`, `:4943`, `:4969`), a leitura o consome em `:4843`, e a
mensagem está fixa no template. Nada no caminho distingue qual comando escreveu.

Não é lapso de redação: os desfechos foram desenhados por comando — cada um declara o que o seu ato
produziu — e a tela foi escrita quando só existia o primeiro deles.

## Por que ninguém viu

Há uma asserção sobre essa frase, e ela cobre exatamente o caminho em que a frase é verdadeira:

```
backend/tests/interface/test_relacao_de_habilitados.py:101
assert "Relação publicada e congelada" in corpo
```

Nenhum teste afirma o que a tela diz depois de observar, de sortear ou de anular. A suíte fecha em
verde com três dos quatro anúncios errados.

## O que isto custa

O custo é de credibilidade, e é maior porque a `021` existe para produzir prova pública. A tela do
sorteio é a tela transmitida ao vivo — a D-012 a define como a evidência que a instituição oferece
enquanto o vídeo corre. No segundo em que a ordem é constituída, ela afirma outro ato.

Quem assiste não tem como saber que a frase é genérica. Quem conduz vê a contagem certa e segue.

## Os caminhos, sem escolher nenhum

1. **Uma frase por desfecho, escolhida pelo que o desfecho traz.** O mais barato: o dicionário já
   distingue os quatro (`resumo`, `materialBruto`, `manifestoHash`), e a tela passa a escolher. Não
   toca em domínio nem em rota.
2. **Um discriminador no desfecho** — cada comando declarando o ato que praticou —, e a tela
   traduzindo. Mais explícito, e alcança qualquer superfície futura que leia o mesmo desfecho, não
   só esta tela.
3. **Chaves de sessão distintas por comando.** Resolve o anúncio e também o erro, mas multiplica o
   que a leitura precisa consumir.

Qualquer um dos três pede, junto, asserção de tela para os quatro caminhos — é a ausência dela que
manteve o defeito invisível, e sem ela o próximo comando repete o problema.
