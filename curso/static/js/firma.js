    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.getElementById('firma');
        const fileLabel = document.querySelector('.firma-input-label');
        
        // Mostrar el nombre del archivo seleccionado
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileLabel.innerHTML = `<i class="bi bi-file-image fa-2x mb-2"></i><br>Archivo seleccionado: ${this.files[0].name}`;
                
                // Mostrar vista previa si es una imagen
                if (this.files[0].type.match('image.*')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Crear o actualizar vista previa
                        let preview = document.querySelector('.firma-preview');
                        if (!preview) {
                            preview = document.createElement('img');
                            preview.className = 'firma-preview mt-3';
                            fileLabel.parentNode.appendChild(preview);
                        }
                        preview.src = e.target.result;
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            } else {
                fileLabel.innerHTML = '<i class="bi bi-cloud-arrow-up fa-2x mb-2"></i><br>Haga clic aquí o arrastre su archivo PNG/JPG';
            }
        });
        
        // Permitir arrastrar y soltar archivos
        const dropZone = document.querySelector('.firma-input-wrapper');
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#39A900';
            this.style.backgroundColor = '#f9fff9';
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#ccc';
            this.style.backgroundColor = '';
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#ccc';
            this.style.backgroundColor = '';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        });
    });