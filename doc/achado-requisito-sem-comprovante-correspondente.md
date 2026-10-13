# Achado — o requisito de dezesseis Perfis e o comprovante de um só

Encontrado em 12/10/2026, na [análise de linguagem simples](analise-edital-linguagem-simples-2026-10-12.md)
(cenário B, [conferência de equivalência](analise-edital-linguagem-simples-2026-10-12/equivalencia.md), B19),
ao recompor o cenário B da auditoria de 08/10.

> **Registro, não escopo.** A proposta de apresentação reproduz a exigência como o dado a declara e
> **não** a amplia. Priorizar é do usuário.

## O que o documento publica hoje

No cenário B (tutores UAB, 18 Perfis), os Perfis **TP-01 a TP-16** têm o mesmo requisito:

> Residir no município do polo ou em município limítrofe

Mas o documento exigido que comprova esse requisito está declarado **só para o TP-01**:

> Dos candidatos ao perfil TP-01 — Tutor presencial:
> a) Comprovante de residência no município do polo ou em município limítrofe

O PDF de hoje (`analise-edital-linguagem-simples-2026-10-12/atual-B.pdf`, idêntico ao da 068) publica
assim. O candidato de TP-02 a TP-16 precisa atender ao requisito e não é chamado a comprová-lo.

## Por que o sistema deixa passar

- **Requisito e documento não se relacionam.** `PerfilVaga.requirements` é lista de textos
  (`editais/models/perfis.py:20`); `DocumentoExigido` tem destinatário — todos, um Perfil, ou um código
  de Modalidade (044) —, mas nenhum vínculo com o requisito que comprova (`editais/models/documentos.py:21-65`).
  Nada acusa um requisito sem comprovante, nem um comprovante sem requisito.
- **Documento para vários Perfis exige uma declaração por Perfil.** O destinatário é **um** Perfil
  (`perfil` é chave estrangeira, `documentos.py:32`). Exigir o comprovante dos dezesseis seriam
  dezesseis declarações, e o PDF imprimiria dezesseis grupos "Dos candidatos ao perfil TP-xx". O
  recorte transversal da 044 resolve isso para Modalidade, não para Perfil.

## Natureza

No cenário B, a origem provável é a montagem do teste de estresse, que declarou o documento num Perfil
só. Mas o cenário mostra uma **lacuna do produto**: o sistema permite publicar um requisito sem o
comprovante correspondente, e tornaria cara a exigência certa (dezesseis declarações) se o Elaborador a
quisesse.

## Perguntas para quem decide

1. **Aviso na Revisão** quando um grupo de Perfis com o mesmo requisito tem o comprovante declarado em
   só parte deles? A comparação seria por identidade de texto, a mesma da 064 e da 068.
2. **Destinatário "grupo de Perfis"** para o documento exigido, como a 044 fez com o código de
   Modalidade?
3. **Vínculo requisito → comprovante** no modelo, que permitiria ao documento dizer "comprova o
   requisito X"?
