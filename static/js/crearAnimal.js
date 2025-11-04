Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#myDropzone", {
  url: "/registro_animal",
  paramName: "imagen",
  maxFilesize: 2,
  acceptedFiles: ".jpg,.png",
  autoProcessQueue: false,
  uploadMultiple: false,
  maxFiles: 1,
  dictDefaultMessage: "Arrastra la imagen aquí o haz clic para subirla",
  thumbnailWidth:400,
  thumbnailHeight:400
});

myDropzone.on("maxfilesexceeded", function(file){
  this.removeAllFiles();
  this.addFile(file)
});
// Evento para botón de registro
document.getElementById("btnRegistrar").addEventListener("click", function () {
  const form = document.getElementById("miFormulario");
  const requiredFields = ["nombre", "especie", "edad", "salud", "habitat", "observaciones"];
  let isValid = true;

  // Validar campos obligatorios
  requiredFields.forEach(id => {
    const el = document.getElementById(id);
    if (!el.value.trim()) {
      isValid = false;
      el.style.borderColor = "red";
    } else {
      el.style.borderColor = "";
    }
  });

  // Si faltan campos, mostrar ventana de advertencia
  if (!isValid) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Los campos con * son obligatorios, por favor completelos.",
      confirmButtonColor: "#d33",
      confirmButtonText: "Entendido"
    });
    return;
  }

  // Validar que haya imagen
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

  // Adjuntar datos del formulario a Dropzone
  myDropzone.on("sending", function (file, xhr, formData) {
    const formElements = form.querySelectorAll("input, select, textarea");
    formElements.forEach(el => {
      if (el.type === "radio" && !el.checked) return;
      formData.append(el.name, el.value);
    });
  });

  // Procesar la cola (subir imagen y datos)
  myDropzone.processQueue();
});

// Cuando la subida sea exitosa
myDropzone.on("success", function (file, response) {
  Swal.fire({
    icon: "success",
    title: "Registro exitoso",
    text: response.mensaje || "El animal ha sido registrado correctamente.",
    confirmButtonColor: "#28a745",
    confirmButtonText: "Ver animales"
  }).then(() => {
    window.location.href = "/ver_animales";
  });
});

// Cuando ocurra un error durante la subida
myDropzone.on("error", function (file, errorMessage) {
  Swal.fire({
    icon: "error",
    title: "Error",
    text: errorMessage.error || "Ocurrió un error al registrar el animal. Intenta nuevamente.",
    confirmButtonColor: "#d33",
    confirmButtonText: "Reintentar"
  });
});

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
