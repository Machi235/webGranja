const buscador = document.getElementById('buscador');
const filtroEspecie = document.getElementById('filtroEspecie');
const filtroSalud = document.getElementById('filtroSalud');
const lista = document.getElementById('data');

function filtrarAnimales() {
    const nombre = buscador.value.toLowerCase();
    const especie = filtroEspecie.value.toLowerCase();
    const salud = filtroSalud.value.toLowerCase();

    const cards = lista.getElementsByClassName('animal');

    for (let card of cards) {
        const nombreAnimal = card.querySelector('.card-title').textContent.toLowerCase();
        const especieAnimal = card.querySelector('.card-especie').textContent.toLowerCase();
        const saludAnimal = card.querySelector('.card-salud').textContent.toLowerCase();

        // Mostrar si cumple todas las condiciones
        if (
            (nombre === "" || nombreAnimal.includes(nombre)) &&
            (especie === "" || especieAnimal.includes(especie)) &&
            (salud === "" || saludAnimal.includes(salud))
        ) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}

// Eventos
buscador.addEventListener('input', filtrarAnimales);
filtroEspecie.addEventListener('change', filtrarAnimales);
filtroSalud.addEventListener('change', filtrarAnimales);
