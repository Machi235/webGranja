document.addEventListener("DOMContentLoaded", () => {
  const mensajes = document.querySelectorAll(".flash-message");

  if (mensajes.length === 0) return;

  mensajes.forEach(msg => {
    const tipo = msg.dataset.tipo || "info";
    const texto = msg.dataset.mensaje || "";

    Swal.fire({
      icon: tipo,
      title: texto,
      showConfirmButton: false,
      timer: 2000,
      timerProgressBar: true,
      toast: true,
      position: "top-end"
    });
  });
});

