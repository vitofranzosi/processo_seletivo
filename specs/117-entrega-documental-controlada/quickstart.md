# Quickstart: Entrega documental controlada

Roteiro da demonstração no navegador, para depois da implementação. Os dados são fictícios, e os
cenários são os do pedido.

## Preparação

```bash
cd backend && make preparar
```

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8017
```

- Use um **banco próprio**. O cenário vem das fixtures da `115` (moldes 72, 146 e 89), estendidas por
  `montar_cenario_da_formalizacao` (T032).
- **Atores** (pelo seletor de identidade):
  - **Ana**, presidência da comissão;
  - **Gil**, administrador de acessos da unidade;
  - **Rui**, Registro Acadêmico, fora da comissão;
  - **Bia**, Coordenação UAB;
  - **Caio**, auditor;
  - **Duda**, de outra unidade.

## Cenário A — Matrícula, 40 aptos (molde 72/2026)

O Edital pede:

- **na inscrição**: certificado e títulos;
- **na convocação**: identidade, CPF, histórico e comprovação de renda.

São 40 aceites, 6 indeferimentos e 4 sem resposta.

1. Ana abre *Documentos para a formalização* na condução e marca identidade, CPF, histórico e
   certificado, com motivo.
2. Ana marca a renda: a tela avisa que é documento de modalidade de reserva. Ana desmarca.
3. Gil concede o papel Formalização a Rui, em **Acessos**, e o designa para o 72/2026, sem restrição.
4. Rui abre **Formalização** na barra e depois o Edital. Vê:
   - 40 pessoas;
   - 4 documentos cada;
   - o certificado marcado *"enviado na inscrição; sem conferência na convocação"*;
   - nenhuma renda e nenhum título.
5. Rui marca *Selecionar todos* e pede *Exportar selecionados*. A prévia mostra 40 pessoas, 160
   arquivos, nenhum ausente, o tamanho e o alcance. Ele confirma.
6. Abra o ZIP: 40 pastas, 4 PDFs cada e `manifesto.csv`. O resultado é *completo*.
7. Confira com `sha256sum`:
   - três arquivos contra o manifesto;
   - o ZIP contra o histórico da página.
8. Liste o temporário do processo e a raiz privada: nenhum arquivo novo.

## Cenário B — Bolsista (molde 146/2025)

1. Ana define a Ficha/Termo e o certificado. Gil designa Bia, só no Perfil de tutor.
2. Bia visualiza a Ficha e baixa o certificado, que sai como `‹protocolo›-certificado.pdf`.
3. Caio, na trilha do Edital, vê *Documento visualizado* e *Download individual disponibilizado*. Não
   tem botão para abrir.
4. Nenhuma tela diz *bolsa concedida*, *obtido* ou *recebido*.

## Cenário C — Finalidades diferentes

Numa pasta do Cenário A, confira a **ausência** de:

- títulos (classificação);
- renda (reserva).

No molde 89, o certificado da inscrição aproveitado por referência aparece **uma vez**.

## Cenário D — Desfecho sucedido

1. Ana corrige o aceite de uma pessoa já exportada para indeferimento.
2. Rui recarrega a página: a pessoa saiu.
3. A nova prévia de *Selecionar todos* tem 39 pessoas.
4. O histórico continua mostrando a exportação anterior, com 40.

## Cenário E — Controle de acesso

Repita por URL direta e por POST forjado, copiados da sessão de Rui:

| Quem | Tentativa | Esperado |
|---|---|---|
| Bia (Perfil de tutor) | documento de aluno | 404 |
| Bia | POST de exportação com id de aluno na seleção | 404, nada gerado |
| Rui, designação revogada por Gil | a página | 404 |
| Rui, papel revogado e designação vigente | a página | 403, nomeando o papel |
| Ana | a página da formalização / designar | 403 / 403 |
| Gil | designar a si mesmo | recusa de autodesignação |
| Gil | a página da formalização | 403 |
| Duda | qualquer URL | 404 |
| Caio | exportar | 403 |

## Cenário F — Falha operacional

Num Edital de 5 aptos:

1. Pelo shell, apague o arquivo de uma apresentação e acrescente um byte ao de outra.
2. **Antes**, sem a feature, abrir o arquivo apagado na página de documentos da convocação dava erro
   500. Agora a resposta é *"Arquivo indisponível"*, e a trilha registra.
3. A prévia mostra o arquivo ausente.
4. A exportação sai **parcial**, com 3 pastas. O manifesto, o histórico e a tela nomeiam as 2 pessoas
   e o motivo, e a trilha tem `INTEGRIDADE`.
5. Com o limite configurado em 1 MB, a confirmação é recusada antes de ler, mostrando o tamanho por
   pessoa.
6. Com duas abas de Rui confirmando ao mesmo tempo, a segunda recebe *"Uma exportação sua já está
   sendo gerada"*.

## Capturas

Capture a 1280 px e a 375 px:

- a definição, com o aviso;
- a designação em Acessos;
- a página do Edital;
- a prévia;
- o resultado parcial;
- o histórico;
- a recusa de arquivo indisponível.
