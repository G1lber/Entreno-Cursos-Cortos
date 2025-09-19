// document.addEventListener("DOMContentLoaded", function () {
//  // =========================
//   // 2. CARGAR DATOS DEL PROGRAMA
//   // =========================
//   const selectPrograma = document.getElementById("id_nombreprograma");
//   const inputCodigo = document.getElementById("id_codigoprograma");
//   const inputVersion = document.getElementById("id_versionprograma");
//   const inputDuracion = document.getElementById("id_duracionprograma");

//   if (selectPrograma) {
//     selectPrograma.addEventListener("change", function () {
//       const programaId = this.value;
//       if (programaId) {
//         fetch(`/get-programa/${programaId}/`)
//           .then((response) => response.json())
//           .then((data) => {
//             if (!data.error) {
//               inputCodigo.value = data.codigo || "";
//               inputVersion.value = data.version || "";
//               inputDuracion.value = data.duracion || "";
//             }
//           })
//           .catch((error) => console.error("Error al obtener datos:", error));
//       }
//     });
//   }

// });

document.addEventListener("DOMContentLoaded", function () {
    const areaSelect = document.getElementById("id_area");
    const duracionSelect = document.getElementById("id_duracion_filtro");
    const programaSelect = document.getElementById("id_nombreprograma");

    function cargarProgramas() {
        const area = areaSelect.value;
        const duracion = duracionSelect.value;

        fetch(`/filtrar-programas/?area=${area}&duracion=${duracion}`)
            .then(res => res.json())
            .then(data => {
                programaSelect.innerHTML = '<option value="">---------</option>';
                data.programas.forEach(p => {
                    const option = document.createElement("option");
                    option.value = p.id;
                    option.textContent = `${p.nombre} (v${p.version})`;
                    programaSelect.appendChild(option);
                });
            });
    }

    areaSelect.addEventListener("change", cargarProgramas);
    duracionSelect.addEventListener("change", cargarProgramas);
});
