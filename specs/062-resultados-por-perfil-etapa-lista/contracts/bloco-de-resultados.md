# Contrato: o bloco "Resultados divulgados" da página pública do Edital

É o contrato de tela que os testes leem. Nomes de classe e de identificador são os que os testes
localizam; o resto da marcação é livre.

## Estrutura

```text
section.resultados[.em-destaque]  aria-labelledby="resultados-titulo"
  h2#resultados-titulo  "Resultados divulgados"
  div.resultados-do-perfil                       (um por Perfil, na ordem de FR-1149)
    h3  <nome do Perfil>
    div.resultados-da-etapa                      (um por etapa, na ordem de FR-1150)
      h4  <nome do marco gravado>
      ul.listas-da-etapa
        li.lista-divulgada                       (um por lista, na ordem de FR-1151)
          a[href=/selecoes/resultados/<id>/]
            <nome da lista>
            span.oculto  " — <etapa> — <Perfil>"
          span.meta  "<natureza> · publicado em dd/mm/aaaa"
          span.prazo-recursal  "recurso até dd/mm/aaaa às HHhMM"    (só se aberto)
      details.publicacoes-anteriores             (só se a etapa tiver sucedida)
        summary  "Publicações anteriores (<total da etapa>)"
        ul
          li                                     (agrupado por lista, mais recente primeiro)
            a[href=/selecoes/resultados/<id>/]
              <nome da lista>
              span.oculto  " — <natureza>, publicado em dd/mm/aaaa — <etapa> — <Perfil>"
            span.meta  "<natureza> · publicado em dd/mm/aaaa · sucedido"
  aside.convite-da-situacao                      (FR-1160 a FR-1163; ausente quando não se aplica)
    p  "Participou deste processo seletivo?"
    p  "Consulte sua classificação e situação individual."
    a  "Entrar para ver minha situação"  → /selecoes/acesso?destino=/selecoes/<edital>/
       ou "Ver minha situação"           → /selecoes/inscricoes/<id>/   (uma inscrição enviada)
       ou "Ver minhas inscrições"        → /selecoes/inscricoes/        (mais de uma)
```

## Invariantes que os testes cobram

- Nenhum par de `a` dentro de `section.resultados` tem o mesmo nome acessível (texto visível +
  `span.oculto`) e `href` diferente (`UX-152`, `SC-444`).
- O nome acessível de todo `a` do bloco começa pelo texto visível dele.
- `span.meta` com a natureza só aparece dentro de `li.lista-divulgada` ou de item do histórico;
  `h4` e `h3` não contêm natureza nem data (`FR-1155`).
- Um `details.publicacoes-anteriores` no máximo por `div.resultados-da-etapa` (`SC-446`).
- O `aside.convite-da-situacao` é filho direto da `section`, depois de todos os
  `div.resultados-do-perfil` (D-002 da spec).
- A volta depois da identificação com `destino` igual à página do Edital leva à página do Edital,
  na âncora `#resultados-titulo` (D-007).
