# Estudo dos cronogramas — revisão de 01/11/2026

Três POCs de leitura para a lista de períodos da Agenda dos Editais, comparadas com a interface
atual. Nada da aplicação foi alterado.

- [Relatório: diagnóstico, medições, comparação e recomendação](relatorio.md).
- [POCs](prototipo/index.html): **C** faixa por Edital, **A** Gantt por evento, **B** cartões, e a
  agenda atual (Mês e Próximos) renderizada pelos templates de produção.
- [Capturas](capturas/) e [medidas](capturas/medidas.json).

## Abrir

Abra `prototipo/index.html` no navegador, com dois cliques. Não precisa de servidor, banco nem
instalação: os dados estão em `prototipo/dados.js`. Os parâmetros ficam no endereço
(`?visao=c&cenario=denso&mes=2026-12`), e "Cenário e filtros" os muda.

## Regenerar

De `backend/`, com o grupo `navegador` instalado e o banco de demonstração `ps_demo_101`:

```bash
DB_NAME=ps_demo_101 DB_USER="$USER" DB_RUNTIME_USER="$USER" DB_RUNTIME_PASSWORD='' LC_ALL=en_US.UTF-8 .venv/bin/python ../doc/estudo-cronogramas-revisao-2026-11-01/exportar_dados.py
```

```bash
.venv/bin/python ../doc/estudo-cronogramas-revisao-2026-11-01/capturar.py
```

O exportador só aceita o `ps_demo_101` e lê em transação `READ ONLY`; os 16 casos de teste existem
só em memória. O capturador abre as páginas num Chromium sem janela, grava as capturas e o
`medidas.json`, e termina com erro se algum marco ou barra cair fora da coluna do seu dia ou se o
console registrar erro.

`tokens.css`, `base-atual.css` e `agenda-atual.css` são cópias das folhas do produto, gravadas pelo
exportador para que as páginas atuais renderizem sem o Django.
