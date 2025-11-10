Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#myDropzone", {
  url: "#", // solo para mostrar la interfaz
  paramName: "imagen",
  maxFilesize: 2,
  acceptedFiles: ".jpg,.png",
  autoProcessQueue: false, // no sube nada automáticamente
  uploadMultiple: false,
  maxFiles: 1,
  dictDefaultMessage: "Arrastra la imagen o haz clic para subirla",
  thumbnailWidth:400,
  thumbnailHeight:400
});

myDropzone.on("maxfilesexceeded", function(file){
  this.removeAllFiles();
  this.addFile(file)
});

function validar() {
  const form = document.getElementById('miFormulario');
  const nombre = document.getElementById('nombre').value.trim();
  const especie = document.getElementById('especie').value.trim();
  const edad = document.getElementById('edad').value.trim();
  const salud = document.getElementById('salud').value.trim();
  const habitat = document.getElementById('habitat').value.trim();
  const observaciones = document.getElementById('observaciones').value.trim();

  // Validar campos vacíos
  if (!nombre || !especie || !edad || !salud || !habitat || !observaciones) {
    Swal.fire({
      icon: 'error',
      title: 'Campos incompletos',
      text: 'Por favor, completa todos los campos obligatorios marcados con *',
      confirmButtonColor: '#d33'
    });
    return;
  }

  // Validar que haya imagen
  if (myDropzone.getAcceptedFiles().length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Imagen requerida",
      text: "Debes subir una imagen del animal antes de registrarlo.",
      confirmButtonColor: "#d33"
    });
    return;
  }

  // Crear FormData con todos los campos e imagen
  const formData = new FormData(form);
  myDropzone.getAcceptedFiles().forEach(file => {
    formData.append("imagen", file);
  });

  // Enviar al backend
  fetch("/registro_animal", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    console.log(data); // 👈 para verificar qué llega del backen
    Swal.fire({
      icon: "success",
      title: data.message,
      showConfirmButton: false,
      timer: 2000,
      timerProgressBar: true
    }).then(() =>  {
        window.location.href = "/ver_animales";
      });
  })
  .catch(error => {
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: "No se pudo conectar con el servidor."
    });
    console.error(error);
  });
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
