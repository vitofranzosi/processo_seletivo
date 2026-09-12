# Ferramentas de captura — saída de S-00, entrada de S-01

Dois arquivos, sem dependência nenhuma além do Node e do Chrome instalado.

- **`cdp.mjs`** — dirige o Chrome sem interface pelo protocolo de depuração. O que importa aqui é
  `recorte()`: ele corta por **seletor**, com faixa de contexto acima, e **emite as coordenadas dos
  retângulos de anotação em porcentagem da imagem**, a partir do mesmo DOM que recortou. Essas
  coordenadas vão direto para o atributo `data-alvos` da figura no HTML. Não estime coordenadas à
  mão: custou três iterações na primeira captura do piloto e zero nas onze seguintes.
- **`smtp.mjs`** — uma caixa de correio local que recebe o e-mail do código de acesso do candidato e
  devolve os seis dígitos. Sem ela a jornada do candidato não se automatiza, porque o mecanismo
  padrão de e-mail imprime o código no terminal do servidor, de onde um roteiro não o lê.

## Como usar

Suba o servidor com uma entrada própria no `.claude/launch.json` — banco exclusivo da sessão,
`INTERFACE_SELETOR_IDENTIDADE=true`, `LC_ALL=en_US.UTF-8`, `DB_USER`, e o mecanismo de e-mail
apontando para a caixa local:

```
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1035
EMAIL_USE_TLS=false
```

Depois, um roteiro por bloco de capturas:

```js
import { abrir } from './cdp.mjs';
import { caixaDeCorreio } from './smtp.mjs';

const correio = caixaDeCorreio();
const p = await abrir({ perfil: '/tmp/chrome-candidata', limpar: true });
await p.viewport(1000, 1200);            // 375, 812, true → celular
await p.ir('http://localhost:8033/selecoes/');
await p.recorte('capturas/SS-032.png', {
  de: 'main h1', ate: 'main article', contexto: 24, margem: 22, margemBaixo: 8,
  alvos: [{ sel: 'a.documento', n: 1 }, { sel: 'p.situacao', n: 2 }],
});
p.fechar();
```

A chamada imprime `alvos: [[x,y,largura,altura,n], …]` — cole no `data-alvos` do `<span
class="quadro">` da figura correspondente.

## Cuidados que custaram tempo no piloto

- **Um pedido de código por candidato.** Pedir outro código para o mesmo e-mail é recusado por cerca
  de um minuto. Faça a jornada inteira de cada pessoa num roteiro só.
- **O perfil do Chrome guarda a sessão entre execuções.** Use `{ perfil: '…', limpar: true }` para
  cada persona, e um perfil por persona — inclusive um sem sessão nenhuma para as capturas do
  público anônimo.
- **`deviceScaleFactor: 2` mais `clip.scale: 2` multiplicam.** O arquivo sai a 4× do tamanho em
  pixels CSS; reduza pela metade depois (`sips -Z`), que é o que dá o 2× do §1 do inventário.
- **Painel de navegador oculto tem viewport zero.** Se um clique "não acerta nada", não é defeito do
  produto.
