# A Revisão não mostra a Classificação que a submissão congela

**Encontrado em**: 27/09/2026, no ensaio do [teste operacional assistido](roteiro-teste-operacional-assistido-28-2026.md)
(passo 0,5), contra a `main` em `f6efe0dd`.

**Estado**: **registrado, não corrigido.** Não bloqueia a composição nem a submissão: o ensaio chegou
a *"Nada pendente — o Edital pode ser submetido"*. É achado de conferência, e a decisão de corrigir é
do usuário.

---

## O que se vê

O Edital do ensaio tem a estrutura do 28/2026: 7 Perfis, 3 Modalidades, 18 Eventos e 7 marcos que
ordenam por sorteio, com o método comum declarado no alto da etapa Classificação. Na Revisão, o bloco
*"O que será congelado na submissão"* lista sete grupos: Identificação, Perfis de Vaga, Cronograma,
Etapas de Avaliação, Documentos Exigidos, Anexos e Conteúdo. **Não há grupo de Classificação.** Quem
submete não lê, nessa tela:

- o **método do sorteio** — algoritmo, fonte da semente, ocorrência, instante, normalização e
  substituição;
- os **marcos** de cada Perfil — como a ordem é produzida, a regra de corte, os suplentes, a Etapa
  que o corte alimenta, a faixa seguinte e o recurso;
- os **critérios de desempate**, quando houver.

O documento sabe de tudo isso. A *"Visualizar Edital"* da mesma tela gera o PDF, e lá cada Perfil
traz *"Marcos classificatórios"* com o sorteio, o corte e o recurso. Só a conferência da tela não
traz.

## Por que o guardião não pegou

`interface/revisao.py` promete, na abertura, que *"uma coleção nova aparece na Revisão porque está no
snapshot, e não porque foi lembrada"*. O guardião é
`test_toda_colecao_do_snapshot_esta_declarada_na_conferencia`
(`tests/unit/interface/test_revisao.py`), e ele compara **só as coleções-raiz que são listas de
entidades com `id`**. Dois formatos escapam dele por construção:

| O que escapa | Onde mora no snapshot | Por que o guardião não vê |
|---|---|---|
| Método comum do sorteio | `drawMethod`, na raiz | é um dicionário, e não uma lista |
| Marcos, com corte, recurso e método próprio | `profiles[].classificationMilestones` | é coleção **aninhada** no Perfil |
| Fatos exigidos do candidato | `profiles[].declaredFacts` | idem |

E a leitura do Perfil (`_perfil`, no mesmo arquivo) também é escrita à mão: ela lê vagas, quadro,
cadastro reserva, localidade, requisitos e Modalidades, e **não** lê `callForm` (como a convocação é
comunicada), `vacancyReversion` (a reversão de vaga reservada), descrição, carga horária,
remuneração nem atribuições. A reversão e a forma de comunicar são duas das declarações que mais
pesam na operação, e as duas se corrigem depois só por Retificação.

É a mesma classe de defeito que o arquivo diz ter feito desaparecer, uma camada abaixo: a raiz
passou a ser lida do snapshot, e o interior do Perfil continuou sendo lembrado.

## Por que importa no teste

A `D-G3` e a `035` dizem que o método do sorteio é norma publicada, e que alterá-lo depois exige
Retificação. Na Revisão, que é a última tela antes de submeter, quem elabora não o vê. No 28/2026 a
Classificação é a etapa em que a estimativa do [anexo A](reavaliacao-pos-consolidacao-2026-09-27/anexo-A-composicao.md)
mais oscila (~18 a ~72 interações). Se a pessoa do teste, na Revisão, voltar à Classificação para
conferir o que escreveu, a volta custa interações que a estimativa não previu, e o motivo dela é esta
lacuna, e não a carga cognitiva da etapa. O roteiro manda anotar a volta com o motivo, para que os
dois casos não se somem.

## O que não se decidiu aqui

- **Se a conferência deve mostrar o marco inteiro ou um resumo.** Num Edital de 16 Perfis são 16
  marcos. A dobra por Perfil que o RC-10 pede para as pendências vale também para a conferência.
- **Se o guardião passa a descer nos Perfis.** A alternativa é declarar, ao lado de `COLECOES`, as
  chaves do Perfil que a leitura cobre, e comparar com as chaves do Perfil no snapshot.

Nada foi corrigido. Registro, não escopo.
