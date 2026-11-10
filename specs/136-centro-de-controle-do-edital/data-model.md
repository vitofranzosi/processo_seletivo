# Data model: Centro de Controle do Edital

**Nada é persistido.** Todas as estruturas são de apresentação, montadas a cada requisição a partir do
`Andamento` da `127`. Os tipos da `127` (`Andamento`, `PerfilNoAndamento`, `Ponto`, `Celula`,
`Providencia`, `Nivel1`, `Alcance`) são lidos e nunca alterados.

## Andamento da fase (quatro valores)

| Valor | Rótulo | Sinal | Regra numa lista (`agregar`) |
|---|---|---|---|
| `concluida` | Concluída | ✓ | todas as células *Feito* ou *Não se aplica*, ao menos uma *Feito* |
| `nao_se_aplica` | Não se aplica | — | todas *Não se aplica* |
| `nao_iniciada` | Ainda não começou | ○ | todas *Depois* ou *Não se aplica* |
| `em_curso` | Em curso | ◐ | qualquer outro caso |

`juntar` (no Edital), sobre o andamento das listas, ignorando `nao_se_aplica`: todas `concluida` →
`concluida`; todas `nao_iniciada` → `nao_iniciada`; outro caso → `em_curso`; nenhuma que se aplique →
`nao_se_aplica`.

## Macrofase

| Campo | Origem |
|---|---|
| `chave`, `nome`, `pergunta`, `grupo` | `conceitos.FASES` |
| `andamento` | `agregar`/`juntar`, ou a regra própria das fases Edital, Inscrições, Conclusão |
| `resumo` | "1 de 2 listas concluídas", "Publicado · 1 Retificação", "8 inscrições · encerradas" |
| `nota` | Retificação em curso; matrícula fora do GPS |
| `paralela` | frase de R-005, só na Avaliação |
| `perfis` | `[FaseNoPerfil]`: por Perfil, o roteiro e as listas da fase |
| `providencias` | `[ItemDeProvidencia]` desta fase |
| propriedades | `suas`, `de_outros`, `aguardando`, `impedidas`, `espera_ate`, `parada` |

`parada` = em curso e sem providência ("nada a fazer agora").

## FaseNoPerfil

`perfil` (o `PerfilNoAndamento`), `roteiro` (`[PassoDoRoteiro]`), `listas` (`[ListaNaFase]`).

## PassoDoRoteiro

`simples`, `termo`, `curta`, `porque`, `ao_confirmar` (de `conceitos`; a Etapa usa o nome dela como
`simples`), `andamento`, `feitas`, `total` (listas em que se aplica), `unico` (semente e Etapa valem
para todas as listas), `tem_acao` (alguma célula *Pendente* ou *Obsoleto*), `razao` (a primeira razão
de célula *Depois*).

## ListaNaFase

`rotulo` curto, `andamento` da fase nesta lista, `celulas`: `[(nome do passo, Celula)]`.

## ItemDeProvidencia

`p` (a `Providencia` da `127`), `fase_chave`, `fase` (nome), `conceito`, `titulo` (nome simples quando
o ato é jargão; senão o ato da `127`), `no_gps` (o ato da `127`, quando o título é o nome simples),
`paralela`.

## ListaNoCentro / PerfilNoCentro

`ListaNoCentro`: `rotulo`, `curto`, `fases` (`[(chave, andamento)]`, uma por fase por lista),
`concluida`, `atos` (`[(nome da fase, Celula, título)]`, um por fase, a praticar), `espera` (a
primeira célula *Aguarda* ou *Impedido* sem ato a praticar).

`PerfilNoCentro`: `andamento` (o `PerfilNoAndamento`), `listas`, `matricula_fora`.

## Destaque

`item` (`ItemDeProvidencia`), `porque` (frase da regra), `destrava` (nomes simples dos passos).

## Centro

`fases`, `grupos` (`[(rótulo, [Macrofase])]`), `perfis`, `itens` (todas as providências, na ordem do
nível 1), `suas`, `de_outros`, `aguardando`, `impedidas`, `total`, `onde`, `onde_detalhe`,
`destaque`, `sem_destaque`, `papel` (frase do alcance), `ve_a_matriz`.

## Invariantes (testados)

1. Cada item do nível 1 está em exatamente uma fase; `sum(len(f.providencias)) == nivel_1.total`.
2. `bool(f.suas) == any(i.p.grupo == "sua" for i in f.providencias)` — e a marca "sua" do HTML segue
   `f.suas`.
3. Numa lista, `agregar(...) == "concluida"` ⇔ todas as células da fase são *Feito* ou *Não se aplica*
   e ao menos uma é *Feito*.
4. Há no máximo um destaque, e ele é sempre uma providência "sua".
5. Nenhuma estrutura cria URL: toda URL vem da `Providencia`, da `Celula`, das ações do Edital ou dos
   destinos do marco.
