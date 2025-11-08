const myDropzone = new Dropzone("#myDropzone", {
  url: "/registro_animal",
  paramName: "imagen",
  maxFilesize: 2,
  acceptedFiles: ".jpg,.png",
  autoProcessQueue: false,
  uploadMultiple: false,
  maxFiles: 1
});

// Agregar datos del formulario al enviar Dropzone
myDropzone.on("sending", function (file, xhr, formData) {
  const form = document.getElementById("miFormulario");
  const formElements = form.querySelectorAll("input, select, textarea");
  formElements.forEach(el => {
    if (el.type === "radio" && !el.checked) return;
    formData.append(el.name, el.value);
  });
});

function validar() {
  const form = document.getElementById('miFormulario');
  let nombre = document.getElementById('nombre').value.trim();
  let especie = document.getElementById('especie').value.trim();
  let edad = document.getElementById('edad').value.trim();
  let salud = document.getElementById('salud').value.trim();
  let habitat = document.getElementById('habitat').value.trim();
  let observaciones = document.getElementById('observaciones').value.trim();

  if (!nombre || !especie || !edad || !salud || !habitat || !observaciones) {
    Swal.fire({
      icon: 'error',
      title: 'Campos incompletos',
      text: 'Por favor, completa todos los campos obligatorios marcados con *',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#d33'
    });
    return;
  }

  if (myDropzone.getAcceptedFiles().length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Imagen requerida",
      text: "Debes subir una imagen del animal antes de registrarlo.",
      confirmButtonColor: "#d33",
      confirmButtonText: "Entendido"
    });
    return;
  }

  myDropzone.processQueue(); // aquí se envía todo ✅


// Escucha el clic del botón
document.getElementById('miFormulario').submit(); 
}

function vaciarFormulario() {
      // selecciona todos los inputs dentro del formulario
      document.querySelectorAll("#miFormulario input").forEach(input => {
        // borra lo que el usuario escribió
        input.value = "";
      });
  
       document.querySelectorAll("#miFormulario select").forEach(select => {
        // borra lo que el usuario escribió
        select.selectedIndex = 0;
      });

      document.querySelectorAll("#miFormulario textarea").forEach(textarea => {
        // borra lo que el usuario escribió
        textarea.value = "";
      });
    }

const hoy = new
Date(). toISOString().split("T")[0];
document.getElementById("nacimiento").setAttribute("max", hoy);
document.getElementById("ingreso").setAttribute("max", hoy);
