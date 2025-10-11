myDropzone.on("success", function (file, response) {
  Swal.fire({
    icon: "success",
    title: "Registro exitoso",
    text: response.mensaje || "El animal ha sido registrado correctamente.",
    confirmButtonColor: "#28a745",
    confirmButtonText: "postoperatorio"
  }).then(() => {
    window.location.href = "/postoperatorio";
  });
});