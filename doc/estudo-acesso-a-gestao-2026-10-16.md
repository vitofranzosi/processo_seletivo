# Estudo da entrada na gestão — 16/10/2026

> **Desdobramento.** O responsável pelo produto escolheu o conceito A no mesmo dia, e a etapa 1 da
> §7 virou a feature [`075`](../specs/075-entrada-da-gestao/spec.md), com o produto renomeado para
> *Gestão de Processos Seletivos (GPS)*. Os protótipos descritos abaixo saíram nela; o que segue é
> o registro do estudo como ele foi feito.

Primeira rodada do redesign do acesso: auditoria do que existe, proposta de navegação e três
protótipos navegáveis. **Nada do comportamento atual mudou.** A tela de `/gestao/identificar`, o
portal e a gestão continuam como estavam; os protótipos moram em rotas próprias, atrás da mesma
chave do seletor de identidade.

## Como abrir

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_redesign_acesso DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8076
```

É a entrada `redesign-acesso` do `.claude/launch.json`. O banco `ps_redesign_acesso` é um
`seed_demo` limpo, preparado em 16/10 (migrate, `sincronizar_unidades`, `seed_demo`).

| O quê | Endereço |
|---|---|
| Índice e comparação | `/gestao/prototipos/acesso/` |
| Conceito A, B ou C | `/gestao/prototipos/acesso/a/` (`b/`, `c/`) |
| Prévia com a autenticação institucional | `…/a/?modo=institucional` |
| Escolha de identidades | `…/a/demonstracao` |
| Shell da gestão (depois de entrar) | `…/a/gestao` |
| Portal com a porta da gestão | `/gestao/prototipos/acesso/portal?conceito=a` |

Toda página tem, embaixo, a barra escura **Protótipo**: ela troca de conceito e de tela, e não faz
parte de nenhum desenho.

**Entrar por um protótipo é entrar de verdade.** A ação chama `identidade.identificar`, a mesma
função da tela atual, e a sessão é a da gestão: depois de escolher `gustavo.gestor` num protótipo,
`/gestao/` mostra a gestão atual com ele. É de propósito — prova que a apresentação muda sem que o
mecanismo mude.

## 1. Diagnóstico

### Navegação

| | Achado | Evidência |
|---|---|---|
| N1 | Nenhum link público leva à gestão. A raiz manda o navegador à vitrine, e o cabeçalho do portal só oferece "Entrar", que é do candidato. Para chegar à gestão é preciso saber o endereço. | `shared/api/operacional.py` (`IndexView`); `portal/templates/portal/base.html:952-994` |
| N2 | "Entrar" não diz para onde leva. Quem gere entende que é seu, e cai no código por e-mail do candidato. | idem |
| N3 | Depois de identificar-se, a pessoa vai sempre à lista de Processos ou a Minhas Etapas — nunca à página que pediu. São **90** redirecionamentos para a identificação, e nenhum guarda o destino (79 em `views.py`, 9 em `avisos.py`, 1 em `duvidas.py`, 1 em `assistente.py`). Um link de Edital mandado por mensagem perde o Edital. | `interface/views.py:643-646` e as chamadas `redirect(reverse("interface:identificar"))` |
| N4 | "Sair" volta à identificação. Fora do desenvolvimento, isso é a página 503. | `interface/views.py:673-675` |
| N5 | O cabeçalho da gestão tem um link só, "Minhas Etapas". Visão Geral, Autoridades e Modelos de aviso são botões dentro da lista de Processos; de qualquer outra tela, o único caminho até elas é a marca. | `interface/templates/interface/base.html:1311-1327`, `lista.html` |
| N6 | O produto tem dois nomes: "Seleções" no portal, "Processos Seletivos" na gestão. | os dois `base.html` |

### Apresentação

| | Achado | Evidência |
|---|---|---|
| V1 | A tela de identificação é uma página operacional comum — a mesma base, o mesmo cabeçalho, um formulário de nome e oito caixas de seleção — e expõe os códigos de permissão (`edital:elaborar, edital:submeter…`) ao lado de cada papel. O campo vem com o exemplo `ana.elaboradora`. | `interface/templates/interface/identificar.html` |
| V2 | A página 503 sem autenticação é um aviso de erro sem desenho próprio. Em produção, é a primeira coisa que a equipe veria. | `interface/templates/interface/sem_autenticacao.html` |
| V3 | A gestão declara "Open Sans" e nunca a carrega — não há `@font-face` nem `<link>` —, de modo que o texto sai em Segoe UI no Windows e na fonte do sistema no macOS. Não há sistema de ícones. A única biblioteca de frente é o htmx. | `interface/templates/interface/base.html:10` |
| V4 | O que se aproveita: os tokens compartilhados, com contraste conferido (`shared/_tokens.css.html`); o link de salto que move o foco; o `:focus-visible`; e os guardiões de acessibilidade, largura e estáticos que varrem os templates. Os protótipos usam os mesmos tokens e passam pelos mesmos guardiões. | `tests/interface/test_acessibilidade.py`, `test_larguras.py`, `test_estaticos.py` |

### Arquitetura e autenticação

| | Achado | Evidência |
|---|---|---|
| A1 | **A fronteira de autenticação já existe.** `interface/identidade.py` se apresenta como o único módulo que muda quando o diretório chegar: `ator_da_sessao`, `identificar`, `encerrar`, `seletor_disponivel`. As views não sabem de onde vem a identidade. | `interface/identidade.py:1-9` |
| A2 | A autorização está separada da identidade: `PAPEIS` mapeia papel para permissões, o `Actor` só carrega permissões, e presidir e avaliar vêm do **vínculo** com a comissão, conferido objeto a objeto — não são papéis, e a tela atual diz isso. | `interface/identidade.py:20-126`; `comissoes/application/selectors.py:328` |
| A3 | A guarda do seletor está no servidor: `identificar` responde 503 sem a chave, e `production.py` recusa subir com ela ligada. | `interface/views.py:629-630`; `config/settings/production.py:92-96` |
| A4 | **Registro, não correção.** `ator_da_sessao` não confere a chave nem a origem da identidade. Uma sessão aberta pelo seletor sobrevive se a chave for desligada no mesmo banco de sessões. Em produção a chave nunca liga, então o caminho exige copiar a tabela de sessões de um ambiente para outro; o risco é baixo, mas a defesa é uma linha: gravar a origem (`"demonstracao"`) na sessão e recusá-la quando a chave estiver desligada. | `interface/identidade.py:133-138` |
| A5 | A auditoria grava o nome escolhido (`RegistroAuditoria.actor_subject`), e não o método. Com a demonstração fora de produção isso basta; quando o diretório chegar, o sujeito passa a ser o identificador dele. | `auditoria/models.py:9` |
| A6 | O usuário escolheu LDAP em 28/08 (auditoria de 15/10). Se for *bind* direto, o acesso definitivo terá usuário e senha **nesta página**; se houver SSO na frente, será um botão que redireciona. O componente de método tem de comportar os dois. Os protótipos mostram o botão e **não** desenham formulário de senha fictício. | `doc/auditoria-de-consolidacao-2026-10-15.md:44` |

## 2. Navegação proposta

```
Candidato   /  →  Vitrine  →  "Minhas inscrições"  →  código por e-mail  →  Minhas inscrições
Equipe         Vitrine  →  "Área de gestão"  →  Acesso à gestão  →  método  →  destino pedido
Link direto    /gestao/editais/…  →  (sem identidade)  →  Acesso ?proximo=…  →  o Edital
```

- **A raiz continua no portal.** Quem digita o endereço procura vaga; a vitrine não muda.
- **"Minhas inscrições" no lugar de "Entrar".** Leva ao mesmo lugar que "Entrar" já levava — à área
  com sessão, à porta sem ela —, nomeado pelo que a pessoa encontra do outro lado.
- **"Área de gestão" ao lado, mais quieta.** Separada por um filete, sem fundo, com cadeado. No
  celular desce para a segunda linha do cabeçalho em vez de sumir.
- **A página de acesso devolve o candidato perdido**: "Procura suas inscrições?" leva ao portal.
- **O acesso guarda o destino** (`?proximo=`, conferido por `url_has_allowed_host_and_scheme`). Os
  protótipos não implementam isso; é a mudança de maior efeito prático da lista e entra na primeira
  feature.

O protótipo do cabeçalho é a vitrine real com o cabeçalho trocado (`prototipo-acesso-portal`), a
mesma costura do protótipo do assistente.

## 3. Os três conceitos

Os três usam os mesmos tokens, os mesmos dados e o mesmo formulário avançado — a comparação é de
composição, e não de paleta.

**A — Institucional.** Duas colunas: à esquerda, em verde profundo, o nome do produto, a frase de
posicionamento e o ciclo do certame (Edital → Inscrições → Avaliação → Recursos → Resultado); à
direita, em branco, "Bem-vindo à gestão" e um botão. A coluna verde fica presa ao rolar. As
identidades vêm em duas listas — comissões e responsabilidades — com avatar, vínculo e ação. No
celular, a coluna vira uma faixa. **Shell:** barra lateral branca agrupada em *Trabalho* e
*Unidade*, seção atual em verde-claro com filete, pessoa e saída no pé, cabeçalho de contexto com
o caminho e "Trocar identidade".

**B — Essencial.** Uma coluna estreita, sem cartão, com a ação escura; o verde fica no símbolo e
no foco. As identidades entram numa **paleta de comando**: busca no topo, grupos, ↑ ↓ e Enter, Esc
para voltar — e sem JavaScript, a lista inteira continua enviando. **Shell:** barra lateral cinza,
itens baixos, a seção atual como superfície branca elevada; conta no topo da barra, num menu;
conteúdo em lista, sem cartões.

**C — Editorial.** "Processos Seletivos" em serifa, tamanho de capa, e o ciclo como índice
numerado 01–04; o acesso é um bloco verde à direita. As identidades viram **crachás**, com o
vínculo na faixa do topo. **Shell:** sem barra lateral — seções numa faixa verde no topo, contexto
numa faixa clara abaixo, títulos em serifa.

Em todos: o selo de ambiente diz onde a pessoa está antes de ela escolher quem é; nenhum código de
permissão aparece (cada responsabilidade leva uma descrição); presidência e avaliação continuam
sendo vínculo, e não papel; o nome e as responsabilidades livres ficam em **Opções avançadas de
demonstração**, fechado.

**Dados reais.** As comissões vêm de `identidades_com_trabalho` (no banco do estudo: `paulo.presidente`
preside PS-DEMO-2026; `joana.avaliadora` e `otavio.avaliador` têm 3 Etapas cada). Cada
responsabilidade sugere o nome de quem mais a exerceu na trilha de auditoria (`ana.elaboradora`,
`bruno.homologador`, `carla.publicadora`, `gustavo.gestor`); as que ninguém exerceu usam
`demo.<papel>`, que se denuncia na auditoria. O shell mostra só os Processos, Editais e Etapas que o
ator alcança, e a navegação só as seções que a autorização permitiria — o mesmo critério dos links
condicionados da lista atual.

## 4. Avaliação

De 1 a 3.

| Critério | A · Institucional | B · Essencial | C · Editorial |
|---|---|---|---|
| Qualidade visual | 3 | 3 — precisa, mas perto do genérico | 3 — a mais marcante |
| Identidade institucional | 3 | 1 — poderia ser de qualquer órgão | 3 — puxada para produto |
| Clareza | 3 | 3 | 2 — a capa disputa com a entrada |
| Usabilidade da demonstração | 3 | 3 — a melhor com muitas identidades | 2 — mais rolagem para 11 crachás |
| Continuidade com o shell | 3 — barra lateral comporta as seções que virão | 3 | 2 — faixa de topo esgota em ~6 seções |
| Responsividade | 3 | 3 | 2 — página longa; navegação rola de lado |
| Acessibilidade | 3 | 2 — a paleta rende mais com teclado e script | 2 — nomes acessíveis longos nos crachás |
| Viabilidade técnica | 3 | 3 | 2 — a serifa do sistema varia por plataforma |
| Manutenibilidade | 2 — a coluna institucional tem texto a manter | 3 | 1 — capa e índice a manter |

### Recomendação

**A, com duas coisas de B**: o campo de busca sobre a lista de identidades quando ela passar de
oito entradas, e a densidade das linhas de tabela no shell.

- A identidade institucional fica concentrada na única tela em que ela importa — a porta. O shell
  que deriva de A é quieto: barra lateral branca, verde só na seção atual. É o que sustenta o uso
  de oito horas por dia.
- A barra lateral comporta o crescimento: hoje são cinco seções, e cada feature de configuração
  acrescenta uma.
- A troca para a autenticação institucional mexe num componente só — o método de acesso — e a
  coluna da direita comporta tanto o botão do SSO quanto os dois campos do LDAP.
- B sozinho é o mais barato e o mais genérico: tiraria do Ifes a única tela em que a marca
  apareceria. C é o mais memorável e o mais caro de manter, e a navegação em faixa não escala.

## 5. Separação entre interface, autenticação e autorização

A separação existe (A1, A2), e o que falta é pouco:

1. **Interface.** Uma página de acesso com um *lugar* para o método, alimentado por uma lista que a
   view recebe — `["demonstracao"]` hoje, `["institucional"]` depois. Sem método disponível, a
   mesma página diz que o acesso não está configurado, no lugar da 503 atual.
2. **Autenticação.** `identidade.py` ganha `metodos_disponiveis()`. O que é só da demonstração — as
   identidades com trabalho, os nomes sugeridos, o formulário livre — sai para um módulo
   `interface/demonstracao.py`, ligado apenas com a chave, para sair inteiro quando o diretório
   chegar. A sessão passa a gravar a origem (A4).
3. **Autorização.** `PAPEIS` não muda de semântica. Ganha a descrição de cada papel — terceiro
   elemento da tupla ou mapa à parte —, com um guardião que cobre todo papel novo. No protótipo as
   descrições moram em `prototipo_do_acesso.py`, para não tocar a fronteira antes da aprovação.

Nenhuma integração institucional fictícia foi escrita.

## 6. Continuidade visual

Componentes compartilhados que a direção pede, todos sem dependência nova:

| Componente | Nos protótipos | Observação |
|---|---|---|
| Shell (barra lateral + cabeçalho de contexto) | `a_gestao.html` | envolve o `<main>` atual; o conteúdo das telas não precisa mudar no primeiro passo |
| Ícones | sprite SVG inline em `_base.html` (25 símbolos) | traço único, `currentColor`, sem biblioteca |
| Selo de ambiente | `.selo-ambiente` | some quando não houver demonstração |
| Pastilha de situação | `.situacao` | os mesmos pares de cor de hoje |
| Avatar de iniciais | `.a-avatar` | |
| Linha de identidade / item de lista | `.a-identidade` | serve também para listas da gestão |
| Estado vazio | `.g-vazio` | com ação, e não só aviso |
| Tabela que empilha no celular | regra em `_base.html` | número e situação em cima, título embaixo |

Nenhuma métrica ou gráfico foi inventado. Os números do shell ("2 Processos · 4 Editais") são
contagens do que o ator alcança.

## 7. Sequência sugerida

Cada item é uma feature própria em `specs/`, conforme a Constituição.

1. **Entrada da gestão.** A página de acesso do conceito escolhido, no lugar de `identificar`;
   `?proximo=` nos 90 redirecionamentos (um auxiliar único, e não 90 edições à mão); "Sair" para o
   acesso; a página sem método; "Minhas inscrições" e "Área de gestão" no cabeçalho do portal; a
   origem na sessão (A4). Os protótipos saem nesta feature.
2. **Shell da gestão.** Barra lateral e cabeçalho de contexto em `base.html`, sem mexer no conteúdo.
   As seções que hoje são botões da lista ganham lugar na barra, condicionadas à capacidade.
3. **Autenticação institucional.** Depende da TI e da escolha entre *bind* LDAP e SSO (A6). Mexe no
   método de acesso e em `identidade.py`, e em nada mais.
4. **Modernização por tela**, incremental, começando pelas de uso diário (lista, Minhas Etapas,
   Mesa).

### Riscos

- `interface/base.html` tem 1336 linhas de CSS inline e é coberto por guardiões que leem o
  cabeçalho (link de salto, larguras). O shell precisa entrar sem reescrever a folha.
- Varreduras de vocabulário e de classes leem os templates de topo da gestão; tela nova precisa de
  regra na folha para cada classe (memória "classe no template exige regra na folha").
- O `?proximo=` é redirecionamento aberto se não for conferido.

## 8. Decisões que são do usuário

1. Qual conceito seguir — ou outra combinação.
2. Se "Área de gestão" aparece no portal **em produção** antes da autenticação existir. Hoje ela
   levaria à página sem método. A alternativa é condicioná-la a haver método disponível.
3. Um nome só para o produto: "Processos Seletivos" (gestão) ou "Seleções" (portal).
4. A marca oficial do Ifes na coluna institucional. O símbolo dos protótipos é um marcador de lugar,
   e não a marca: a do Instituto vem do manual de identidade visual da Rede Federal.
5. LDAP direto ou SSO na frente — muda o componente de método (A6).

## 9. Limites deste estudo

- Ninguém de fora usou os protótipos. A avaliação é de quem os fez.
- Não houve teste com leitor de tela; o teclado foi conferido na paleta do conceito B e no
  formulário avançado.
- A serifa do conceito C é a do sistema operacional; no Windows ela cai em Palatino ou Georgia, e só
  o macOS foi visto.
- As miniaturas do índice são `iframe` escalados, sem interação.
- Arquivos: `backend/processo_seletivo/interface/prototipo_do_acesso.py`,
  `backend/processo_seletivo/interface/templates/interface/prototipo_acesso/`,
  `backend/tests/interface/test_prototipo_do_acesso.py`, as rotas em `interface/urls.py` e a
  entrada `redesign-acesso` do `.claude/launch.json`.
