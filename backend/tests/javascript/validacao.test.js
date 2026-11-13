/* FR-026 da 003 — as regras da tela, executadas de verdade.

   Os testes anteriores procuravam strings no fonte: provavam que a mensagem estava escrita, não
   que ela aparecia na situação certa. Aqui o script roda contra um DOM mínimo e o que se afirma é
   o efeito — qual campo fica inválido, com que mensagem, e se o envio é bloqueado. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Formulario, carregar, linha, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/validacao.js"
);

const PERFIL = { code: "P1", name: "Perfil", immediateVacancies: "1", reserveType: "NONE",
                 modalidades: "" };
const EVENTO = { type: "INSCRICAO", description: "Inscrições", startAt: "2026-09-01T09:00",
                 endAt: "" };

/* O tipo de reserva como `_perfil.html` o renderiza: **três rádios com o mesmo `name`**, na ordem
   de `reservas`, e só o escolhido marcado. A fixture montava um campo único com o valor escolhido
   — e era o primeiro campo com aquele sufixo. O script lia o primeiro, e passava. Na tela, o
   primeiro rádio é sempre `NONE`: "limitado" era inalcançável e estes testes diziam o contrário. */
function reserva(escolhido) {
  return ["NONE", "LIMITED", "UNLIMITED"].map((valor) => ({
    value: valor,
    type: "radio",
    checked: valor === escolhido,
  }));
}

function perfil(campos) {
  const juntos = { ...PERFIL, ...campos };
  return { ...juntos, reserveType: reserva(juntos.reserveType) };
}

function comPerfis(...perfis) {
  return new Formulario(perfis.map((campos, i) => linha("perfil", i, perfil(campos))));
}

function comEventos(...eventos) {
  return new Formulario(eventos.map((campos, i) => linha("evento", i, { ...EVENTO, ...campos })));
}

function validar(formulario) {
  montar({ formulario });
  carregar(SCRIPT);
  formulario.disparar("input");
  return formulario;
}

test("reserva limitada é aceita sem número: ele vem do corte (162)", () => {
  const form = validar(comPerfis({ reserveType: "LIMITED" }));

  assert.equal(form.checkValidity(), true);
  assert.equal(form.disparar("submit").impedido, false);
});

test("nenhuma espécie de reserva pede número", () => {
  for (const especie of ["NONE", "LIMITED", "UNLIMITED"]) {
    assert.equal(validar(comPerfis({ reserveType: especie })).checkValidity(), true, especie);
  }
});

test("vagas negativas são recusadas", () => {
  const form = validar(comPerfis({ immediateVacancies: "-1" }));

  assert.equal(form.mensagemDe("immediateVacancies"), "Vagas imediatas não podem ser negativas.");
});

test("código de Perfil repetido é recusado nos dois Perfis, nomeando o código", () => {
  const form = validar(comPerfis({ code: "P1" }, { code: "P1" }));

  const mensagens = form.elements
    .filter((campo) => campo.name.endsWith("-code"))
    .map((campo) => campo.validationMessage);
  assert.deepEqual(mensagens, [
    "Já há outro Perfil com o código P1.",
    "Já há outro Perfil com o código P1.",
  ]);
});

test("códigos distintos não conflitam", () => {
  const form = validar(comPerfis({ code: "P1" }, { code: "P2" }));

  assert.equal(form.checkValidity(), true);
});

test("modalidade repetida no mesmo Perfil é recusada, com travessão ou hífen", () => {
  for (const separador of ["—", "-"]) {
    const form = validar(
      comPerfis({ modalidades: `AC ${separador} Ampla\nAC ${separador} Duplicada` })
    );
    assert.match(form.mensagemDe("modalidades"), /A modalidade AC aparece mais de uma vez/);
  }
});

test("término anterior ao início é recusado no campo do término", () => {
  const form = validar(
    comEventos({ startAt: "2026-09-10T09:00", endAt: "2026-09-01T09:00" })
  );

  assert.equal(
    form.mensagemDe("endAt"),
    "O término do Evento não pode ser anterior ao início."
  );
});

test("evento pontual, sem término, é aceito", () => {
  const form = validar(comEventos({ endAt: "" }));

  assert.equal(form.mensagemDe("endAt"), "");
  assert.equal(form.checkValidity(), true);
});

test("corrigir o campo limpa a mensagem e a marcação ARIA", () => {
  const form = validar(comPerfis({ immediateVacancies: "-1" }));
  assert.equal(form.checkValidity(), false);

  form.elements.find((campo) => campo.name.endsWith("-immediateVacancies")).value = "3";
  form.disparar("input");

  assert.equal(form.mensagemDe("immediateVacancies"), "");
  assert.equal(form.invalidoEmAria("immediateVacancies"), null);
  assert.equal(form.checkValidity(), true);
  assert.equal(form.disparar("submit").impedido, false);
});

test("linha inserida já inválida é pega no envio, mesmo sem nenhum `input`", () => {
  // É o caso que o ouvinte de `submit` existe para resolver: o HTMX acrescenta a linha e nada
  // dispara `input` até a pessoa digitar.
  const form = comPerfis({});
  montar({ formulario: form });
  carregar(SCRIPT);
  form.linhas.push(linha("perfil", 1, perfil({ immediateVacancies: "-1" })));

  assert.equal(form.disparar("submit").impedido, true);
  // `mensagemDe` acha o primeiro campo com o sufixo; a linha inválida é a segunda.
  const vagasDaLinhaNova = form.elements.find(
    (campo) => campo.name === "perfil-1-immediateVacancies"
  );
  assert.equal(vagasDaLinhaNova.validationMessage, "Vagas imediatas não podem ser negativas.");
});
