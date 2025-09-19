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
