const filtro = document.getElementById("filtroArea");
const tabla = document.getElementById("data");

filtro.addEventListener('change', () => {
    const valor = filtro.value.toLowerCase();
    const filas = tabla.getElementsByTagName('tr');

    for (let i = 0; i < filas.length; i++) {
        const area = filas[i].getElementsByTagName('td')[1].textContent.toLowerCase();
        if (valor === "" || area === valor) {
            filas[i].style.display = "";
        } else {
            filas[i].style.display = "none";
        }
    }
});

//----------------------------------------------------------------------------------------------------------
  const crearHorario = document.querySelector("#crearHorario");
  const nuevoHorario = document.querySelector("#nuevoHorario");
  const cerrarHorario = document.querySelector("#cerrarHorario");
  const form =  nuevoHorario.querySelector("form")

  crearHorario.addEventListener("click", () => { 
    nuevoHorario.showModal();
  })

  nuevoHorario.addEventListener("close", ()=>{
    form.reset();
  })

  cerrarHorario.addEventListener("click", ()=>{
    nuevoHorario.close();
  })

//----------------------------------------------------------------------------------------------------------

 const crearTurno = document.querySelector("#crearTurno");
 const nuevoTurno = document.querySelector("#nuevoTurno");
 const cerrarTurno = document.querySelector("#cerrarTurno");
  const form2 =  nuevoTurno.querySelector("form")

  crearTurno.addEventListener("click", () => { 
    nuevoTurno.showModal();
  })

  nuevoTurno.addEventListener("close", ()=>{
    form2.reset();
  })

  cerrarTurno.addEventListener("click", ()=>{
    nuevoTurno.close();
  })

//----------------------------------------------------------------------------------------------------------

const botonEditar = document.querySelectorAll(".botonEditar");
const editarAsignacionTurno = document.querySelector("#editarAsignacionTurno");
const cerrarEditarHorario = document.querySelector("#cerrarEditarHorario");

botonEditar.forEach(boton => {
  boton.addEventListener("click", () => {

    const id = boton.dataset.id;
    const empleado = boton.dataset.empleado;
    const turno = boton.dataset.turno;

    document.querySelector("#idUsuarioturno").value = id
    document.querySelector("#empleado").value = empleado
    
    const selectTurno = document.querySelector("#turno");
    selectTurno.value = turno;

    editarAsignacionTurno.showModal();
})
})

editarAsignacionTurno.addEventListener("close", () =>{
  form.reset();

})
cerrarEditarHorario.addEventListener("click", ()=>{
  editarAsignacionTurno.close();
})

//----------------------------------------------------------------------------------------------------------

 const verTurnos = document.querySelector("#verTurnos");
 const listaTurnos = document.querySelector("#listaTurnos");
 const cerrarTurnos = document.querySelector("#cerrarTurnos");

  verTurnos.addEventListener("click", () => { 
    listaTurnos.showModal();
  })

  cerrarTurnos.addEventListener("click", ()=>{
    listaTurnos.close();
  })


  document.getElementById("formAsignarTurno").addEventListener("submit", (e) => {
    console.log("Formulario enviado ✅");
  });

