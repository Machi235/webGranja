



//----------------------------------------------------------------------------------------------------------

  const crearHorario = document.querySelector("#crearHorario");
  const nuevoHorario = document.querySelector("#nuevoHorario");
  const form =  nuevoHorario.querySelector("form")

  crearHorario.addEventListener("click", () => { 
    nuevoHorario.showModal();
  })

  nuevoHorario.addEventListener("close", ()=>{
    form.reset();
  })

//----------------------------------------------------------------------------------------------------------

 const crearTurno = document.querySelector("#crearTurno");
 const nuevoTurno = document.querySelector("#nuevoTurno");

  crearTurno.addEventListener("click", () => { 
    nuevoTurno.showModal();
  })

  nuevoTurno.addEventListener("close", ()=>{
    form.reset();
  })

//----------------------------------------------------------------------------------------------------------

  const filtro = document.getElementById('filtroArea');
const tabla = document.getElementById('data');

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
