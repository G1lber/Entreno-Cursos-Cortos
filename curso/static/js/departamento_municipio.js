document.addEventListener("DOMContentLoaded", function () {
  const selectDepartamento = document.getElementById("id_departamento");
  const selectMunicipio = document.getElementById("id_municipio");

  if (selectDepartamento) {
    selectDepartamento.addEventListener("change", function () {
      const departamentoId = this.value;

      // Limpiar municipios anteriores
      selectMunicipio.innerHTML = '<option value="">Seleccione un municipio</option>';

      if (departamentoId) {
        fetch(`/get-municipios/${departamentoId}/`)
          .then((response) => response.json())
          .then((data) => {
            data.forEach((municipio) => {
              const option = document.createElement("option");
              option.value = municipio.id;
              option.textContent = municipio.nombre;
              selectMunicipio.appendChild(option);
            });
          })
          .catch((error) => console.error("Error cargando municipios:", error));
      }
    });
  }
});
