const descripcion = document.getElementById("descripcion");

descripcion.addEventListener("input", () => {
  descripcion.style.height = "auto";          // reinicia la altura
  descripcion.style.height = descripcion.scrollHeight + "px";  // ajusta según el texto

});

//---------------------------------------------------------------------------------------------
  const crearNotificacion = document.querySelector("#crearNotificacion");
  const notificacion = document.querySelector("#notificacion");
  const form =  notificacion.querySelector("form")

  crearNotificacion.addEventListener("click", () => { 
    notificacion.showModal();
  })

  notificacion.addEventListener("close" , () => {
    form.reset();
  })

