"""A fonte de consulta do Edital vigente — Fase A do assistente de dúvidas (070).

**Cada resposta diz de qual versão do Edital ela vem, de qual ato publicado vem cada informação, e o
que é texto do Edital, o que é dado e o que é explicação — e nunca diz mais do que o Edital
publicado diz.**

Nada aqui grava, nada chama serviço externo, e nada lê o rascunho (`FR-1447`, `FR-1449`, `FR-1412`).
O domínio é puro: recebe o conteúdo publicado e devolve a resposta. A aplicação só lê do banco o que
o domínio precisa, e é a porta pela qual a Fase B poderá isolar a inferência (`R-017`).

**O nome é o do produto, e não o de uma plataforma** (`R-001`): `consulta` já nomeia a consulta
pública e histórica de `publicacoes`, e "assistente", na gestão, é o assistente de composição.
"""
