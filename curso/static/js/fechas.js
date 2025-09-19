// fechas.js - versión final corregida
document.addEventListener("DOMContentLoaded", function () {
    
  // ---------- FullCalendar ----------
  const calendarEl = document.getElementById("calendar");
  if (calendarEl) {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      locale: "es",
      timeZone: "local",
      events: []
    });
    calendar.render();
    window.calendar = calendar;
  }

  // ---------- elementos del DOM ----------
  const selectPrograma = document.getElementById("id_nombreprograma");
  const inputCodigo = document.getElementById("id_codigoprograma");
  const inputVersion = document.getElementById("id_versionprograma");
  const inputDuracion = document.getElementById("id_duracionprograma");

  const diasCheckboxes = Array.from(document.querySelectorAll("input[name='dias']"));
  const horariosDias = document.getElementById("horarios-dias");
  const tipoHorarioRadios = Array.from(document.querySelectorAll("input[name='tipo_horario']"));
  const horarioGeneral = document.getElementById("horario-general");

  const fechaInicioInput = document.getElementById("id_fechainicio");
  const duracionInput = document.getElementById("id_duracionprograma");
  const horaInicioInput = document.getElementById("id_horario_inicio");
  const horaFinInput = document.getElementById("id_horario_fin");

  const fecha1Input = document.getElementById("id_fecha1");
  const fecha2Input = document.getElementById("id_fecha2");
  const fechaFinInput = document.getElementById("id_fechafin");

  // ---------- fetch para autocompletar programa ----------
  if (selectPrograma) {
    selectPrograma.addEventListener("change", function () {
      const programaId = this.value;
      if (!programaId) return;
      fetch(`/get-programa/${programaId}/`)
        .then(resp => resp.json())
        .then(data => {
          if (!data.error) {
            if (inputCodigo) inputCodigo.value = data.codigo || "";
            if (inputVersion) inputVersion.value = data.version || "";
            if (inputDuracion) inputDuracion.value = data.duracion || "";
            calcularFechas();
          }
        })
        .catch(err => console.error("Error al obtener datos del programa:", err));
    });
  }

  // ---------- helper horas ----------
  function parseHora(hora) {
    if (!hora) return NaN;
    const parts = hora.split(":").map(Number);
    if (parts.length === 0 || Number.isNaN(parts[0])) return NaN;
    const h = parts[0];
    const m = parts[1] || 0;
    return h + (m / 60);
  }

  const dayNumToCode = ["DOM", "LUN", "MAR", "MIE", "JUE", "VIE", "SAB"];
  const codeToDayNum = { "DOM": 0, "LUN": 1, "MAR": 2, "MIE": 3, "JUE": 4, "VIE": 5, "SAB": 6 };

  function getHorasSesionPorDiaCodigo(diaCodigo) {
    const tipo = (document.querySelector("input[name='tipo_horario']:checked") || {}).value || "general";

    if (tipo === "general") {
      if (!horaInicioInput || !horaFinInput || horaInicioInput.disabled || horaFinInput.disabled) return 0;
      const hi = parseHora(horaInicioInput.value);
      const hf = parseHora(horaFinInput.value);
      return Number.isFinite(hf - hi) && hf > hi ? (hf - hi) : 0;
    } else {
      const inicioEl = document.querySelector(`input[name='hora_inicio_${diaCodigo}']`);
      const finEl = document.querySelector(`input[name='hora_fin_${diaCodigo}']`);
      if (!inicioEl || !finEl) return 0;
      const hi = parseHora(inicioEl.value);
      const hf = parseHora(finEl.value);
      return Number.isFinite(hf - hi) && hf > hi ? (hf - hi) : 0;
    }
  }

  function getLabelHorarioPorDia(diaCodigo) {
    const tipo = (document.querySelector("input[name='tipo_horario']:checked") || {}).value || "general";
    if (tipo === "general") {
      if (horaInicioInput.disabled || horaFinInput.disabled) return "";
      return `${horaInicioInput.value || ""} - ${horaFinInput.value || ""}`;
    } else {
      const inicioEl = document.querySelector(`input[name='hora_inicio_${diaCodigo}']`);
      const finEl = document.querySelector(`input[name='hora_fin_${diaCodigo}']`);
      if (!inicioEl || !finEl) return "";
      return `${inicioEl.value || ""} - ${finEl.value || ""}`;
    }
  }

  // ---------- render de inputs horarios ----------
  function renderHorarios() {
    if (!horariosDias) return;
    horariosDias.innerHTML = "";
    const tipo = (document.querySelector("input[name='tipo_horario']:checked") || {}).value || "general";

    if (tipo === "individual") {
        if (horarioGeneral) {
            horarioGeneral.style.display = "none";
            // 🚨 limpiar y deshabilitar inputs generales
            horaInicioInput.value = "";
            horaFinInput.value = "";
            horaInicioInput.removeAttribute("required");
            horaFinInput.removeAttribute("required");
            horaInicioInput.disabled = true;
            horaFinInput.disabled = true;
        }


      diasCheckboxes.forEach(chk => {
        if (chk.checked) {
          const val = (chk.value || "").trim();
          let label = chk.closest("label")?.textContent?.trim() || val;
          horariosDias.insertAdjacentHTML("beforeend",
            `<div class="form-group horario-individual" data-dia="${val}">
                <label>${label}</label>
                <input type="time" name="hora_inicio_${val}" class="hora-ind">
                <input type="time" name="hora_fin_${val}" class="hora-ind">
            </div>`);
        }
      });
    } else {
      if (horarioGeneral) {
        horarioGeneral.style.display = "";
        // ✅ limpiar inputs individuales y reactivar generales
        horariosDias.innerHTML = "";
        horaInicioInput.disabled = false;
        horaFinInput.disabled = false;
        horaInicioInput.setAttribute("required", "required");
        horaFinInput.setAttribute("required", "required");
      }
    }
    calcularFechas();
  }

  // ---------- cálculo de fechas ----------
  function limpiarSalida() {
    if (fecha1Input) fecha1Input.value = "";
    if (fecha2Input) fecha2Input.value = "";
    if (fechaFinInput) fechaFinInput.value = "";
    if (window.calendar) window.calendar.removeAllEvents();
  }

  function calcularFechas() {
    try {
      if (!fechaInicioInput?.value || !duracionInput?.value) {
        limpiarSalida(); return;
      }

      const duracion = Number(duracionInput.value);
      if (!Number.isFinite(duracion) || duracion <= 0) {
        limpiarSalida(); return;
      }

      const diasSemanaNums = diasCheckboxes.filter(chk => chk.checked).map(chk => {
        const v = (chk.value || "").trim().toUpperCase();
        return codeToDayNum[v];
      }).filter(d => typeof d === "number");

      if (!diasSemanaNums.length) {
        limpiarSalida(); return;
      }

      const diasHoras = {};
      let positiveHoras = [];
      diasSemanaNums.forEach(n => {
        const codigo = dayNumToCode[n];
        const h = getHorasSesionPorDiaCodigo(codigo);
        diasHoras[n] = h;
        if (h > 0) positiveHoras.push(h);
      });

      if (!positiveHoras.length) {
        limpiarSalida(); return;
      }

      const minHorasPos = Math.min(...positiveHoras);
      const sesionesEstimadas = Math.ceil(duracion / minHorasPos);
      const maxDiasIter = sesionesEstimadas * 7 + 30;

      let fechaCursor = new Date(fechaInicioInput.value);
      let horasAcum = 0;
      const sesiones = [];

      for (let i = 0; horasAcum < duracion && i < maxDiasIter; i++) {
        const dayNum = fechaCursor.getDay();
        if (diasSemanaNums.includes(dayNum)) {
          const codigo = dayNumToCode[dayNum];
          const horasSesion = diasHoras[dayNum] ?? getHorasSesionPorDiaCodigo(codigo);
          if (horasSesion > 0) {
            sesiones.push({
              fecha: fechaCursor.toISOString().split("T")[0],
              label: getLabelHorarioPorDia(codigo)
            });
            horasAcum += horasSesion;
          }
        }
        fechaCursor.setDate(fechaCursor.getDate() + 1);
      }

      const mesInicio = new Date(fechaInicioInput.value).getMonth();
      const mes1 = sesiones.filter(s => new Date(s.fecha).getMonth() === mesInicio).map(s => s.fecha);
      const mes2 = sesiones.filter(s => new Date(s.fecha).getMonth() !== mesInicio).map(s => s.fecha);

      if (fecha1Input) fecha1Input.value = mes1.join(", ");
      if (fecha2Input) fecha2Input.value = mes2.join(", ");
      if (fechaFinInput) fechaFinInput.value = sesiones.length ? sesiones.at(-1).fecha : "";

      if (window.calendar) {
        window.calendar.removeAllEvents();
        sesiones.forEach(s => {
          const parts = s.fecha.split("-");
          const y = Number(parts[0]), m = Number(parts[1]) - 1, d = Number(parts[2]);
          const dt = new Date(y, m, d);
          window.calendar.addEvent({ title: s.label, start: dt, allDay: true });
        });
      }
    } catch (err) {
      console.error("Error en calcularFechas():", err);
    }
  }

  // ---------- listeners ----------
  if (fechaInicioInput) fechaInicioInput.addEventListener("change", calcularFechas);
  if (duracionInput) duracionInput.addEventListener("input", calcularFechas);
  if (horaInicioInput) horaInicioInput.addEventListener("input", calcularFechas);
  if (horaFinInput) horaFinInput.addEventListener("input", calcularFechas);

  diasCheckboxes.forEach(chk => chk.addEventListener("change", renderHorarios));
  tipoHorarioRadios.forEach(r => r.addEventListener("change", renderHorarios));

  if (horariosDias) {
    horariosDias.addEventListener("input", function (e) {
      if (e.target && e.target.type === "time") calcularFechas();
    });
  }

  renderHorarios();
});
