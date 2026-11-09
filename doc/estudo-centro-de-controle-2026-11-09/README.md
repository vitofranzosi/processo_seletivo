# Estudo — Centro de Controle do Edital (2026-11-09)

**Pergunta:** o operador consegue, olhando um Edital publicado, saber onde a seleção está, o que já
aconteceu, o que precisa fazer agora e o que vem depois?

**Resposta curta:** hoje, não em palavras. O GPS **já deriva** quase tudo o que precisa: a 127 lê os
atos e dá, para cada ponto da jornada em cada lista, uma de sete situações, com responsável, prazo e
razão. O que falta é **dizer**: agrupar isso em fases compreensíveis, separar a operação da
administração, e explicar no lugar da decisão.

O protótipo faz isso **sem dado novo, sem estado persistido e sem regra de disponibilidade nova**. São
só duas regras puras de agregação sobre o `Andamento` existente.

## Entregas

1. [Auditoria da experiência atual](01-auditoria.md): 8 hipóteses verificadas, 12 achados
   (A-01 a A-12), e a separação entre defeito da fixture e defeito da aplicação.
2. [Mapa real da jornada](02-mapa-da-jornada.md): 8 macrofases, a matriz de 24 marcos, as variações por
   modalidade, os escopos e as lacunas de derivação (G-1 a G-8).
3. [Arquitetura de informação](03-arquitetura-de-informacao.md): quatro camadas, os critérios de
   exibição e a pedagogia integrada.
4. [Protótipos navegáveis](04-prototipos.md): como rodar; os cinco cenários; 34 capturas em
   [`capturas/`](capturas/).
5. [Avaliação comparativa](05-avaliacao-comparativa.md): 12 tarefas medidas por Playwright, os riscos
   e o que não foi validado.
6. [Plano de implementação](06-plano-de-implementacao.md): as specs C1 a C6; o MVP = C3 → C1 → C2.
7. [Rodada de refinamento, versão 2 do protótipo](07-refinamento.md): o andamento da fase separado das
   providências, nomes simples nos passos, o critério do destaque, menos texto à vista e o mapa em três
   grupos. Inclui as peças existentes reutilizadas e as novas.
8. [Plano de produção](08-plano-de-producao.md): a versão 2 aprovada para implementação incremental em
   09/11; as decisões pendentes classificadas, as specs 135 a 138, os critérios de aceite, a sequência e
   a validação com operadores.

## Recomendação crítica

**Adotar.** Uma trilha de oito macrofases que **pode ter várias fases acesas ao mesmo tempo**, sobre o
detalhe do Edital publicado (não numa página nova), com quatro camadas nesta ordem:
- onde estamos e a jornada;
- o que fazer agora, ao lado do detalhe da fase escolhida;
- onde cada lista está;
- administração e histórico.

A macrofase é um **rótulo de apresentação** sobre os pontos que a 127 já deriva. Não é coluna, nem
estado, nem "a" fase do Edital.

**Substituir ou reorganizar.**
- O selo "Publicado" como única resposta de estado, que passa a ter rótulo de "situação
  administrativa".
- A ordem das seções: o andamento sobe, e o histórico e a validação descem.
- Encerrar e Cancelar saem de "O que fazer agora".
- O "O que fazer agora" do Processo, que contradiz os Editais.
- A matriz por lista deixa de ser a única forma de ver as listas. Ela continua, recolhida.

**Implementar primeiro: C3, depois C1 e C2.** A C3 corrige três defeitos de derivação e de texto
(lista vazia, preliminar publicado, espera que oferece o que já foi feito), e dá para fazê-la já. Ela
vem primeiro porque o destaque de "sua próxima ação" **depende** dela: no C08, o protótipo destacou a
ordem de uma lista sem inscritos.

**Não fazer.** Motor de workflow, "fase atual" persistida, percentual, próximo passo único por
prioridade.

**O que esta proposta revisita.** A 127 deixou de fora a barra de fases, o percentual e o "próximo passo" único
(seção "Fica fora" da spec, e FR-4051), e tirou a trilha depois da publicação (D-002). O estudo de 06/11
recusou a barra de seis momentos. A recusa tinha uma razão: o Edital **não
tem** uma etapa atual, e uma barra única mentiria. A proposta conserva a razão e muda a forma:
- várias fases acesas ao mesmo tempo;
- a situação de cada uma diz "1 de 2 listas";
- nenhuma é eleita "a próxima".

Mesmo assim, é a mesma pergunta respondida de outro jeito, e **a decisão é sua** (D-1).

## Decisões que precisam ser tomadas antes das specs

Em 09/11 o usuário aprovou o conceito e a direção arquitetural, e pediu uma rodada de refinamento
([07](07-refinamento.md)). Duas decisões ficaram tomadas, e as demais seguem pendentes.


| # | Decisão | Opções | O que o estudo sugere |
|---|---|---|---|
| D-1 | Aceitar macrofases como apresentação sobre os pontos da 127 | (a) sim, várias acesas ao mesmo tempo; (b) manter a recusa da 127 | **Decidida em 09/11: (a)**, pela aprovação do conceito |
| D-2 | Onde mora o Centro de Controle | (a) o próprio detalhe do Edital publicado; (b) uma página nova | (a), coerente com D-001 da 104 |
| D-3 | Os nomes das oito fases | Os do protótipo: Edital, Inscrições, Avaliação, Classificação, Resultado e recursos, Vagas, Convocação, Conclusão — ou outros | Validar "Vagas" com operadores |
| D-4 | Quando destacar "Sua próxima ação" | (a) só com exatamente uma providência sua; (b) nunca; (c) por prioridade; (d) a da versão 2: uma só, **ou** a única que destrava passos seguintes quando as outras são paralelas | (d), depois da C3 |
| D-5 | Observar a extração antes de congelar todas as relações | (a) o comando recusa; (b) confirmação em duas fases; (c) só alertar | Decisão de domínio; o estudo não escolhe |
| D-6 | Quem vê o detalhe por lista | (a) quem conduz ou audita (D-004 da 127); (b) também quem publica | (a) |
| D-7 | Quem aprova os textos pedagógicos, e se vão a produção antes de teste com operadores | — | Fonte única no código; teste com 3 a 5 operadores antes |
| D-8 | O "O que fazer agora" do Processo | (a) some, e o Processo agrega os Editais; (b) soma as providências dos Editais | **Decidida em 09/11: (a)**. O Processo agrega; o Centro de Controle é do Edital |

## Achados fora do MVP

Registro, e não escopo:
- **A-03.** A tela do sorteio oferece observar a extração antes do congelamento. Vira a C6 só com a D-5.
- **A-10.** "Próximos marcos" lê só o cronograma declarado. Entra na C5, e não no MVP.
- **Catálogo da 134.** Nenhum cenário termina concluído; nenhum tem dois Perfis, dois Editais no
  Processo, vários marcos, recurso interposto nem Retificação em curso. Esses casos ficaram **sem
  verificação com dado real**.

## Limitações
- **Nenhum teste com pessoas.** As evidências são inspeção heurística e medição automatizada.
- **Os cenários são os da 134, rodada 1, num banco local** (`ps_cc_centro`), e não os da homologação:
  o pedido cita o `SIM-TREINAMENTO-006-R3`, e aqui o C06 é a rodada 1. O gerador é o mesmo, e o
  estado de partida também; os números de concurso e as datas diferem.
- **A situação 5 do pedido (seleção concluída) é fixture**, dita na tela. Não confundir com o C05, cenário real "Avaliação pendente".
- **O protótipo não pratica ato nenhum.** Os botões levam às telas reais do mesmo servidor.
