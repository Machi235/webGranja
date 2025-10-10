const buscador = document.getElementById('buscador');
const filtroTipo = document.getElementById('filtroTipo');
const filtroEstado = document.getElementById('filtroEstado');
const lista = document.getElementById('data');

function filtrarHabitats() {
    const nombre = buscador.value.toLowerCase();
    const tipo = filtroTipo.value.toLowerCase();
    const estado = filtroEstado.value.toLowerCase();

    const cards = lista.getElementsByClassName('card');

    for (let card of cards) {
        const nombreHabitat = card.querySelector('.nombre').textContent.toLowerCase();
        const tipoHabitat= card.querySelector('.tipo').textContent.toLowerCase();
        const estadoHabitat = card.querySelector('.estado').textContent.toLowerCase();

        // Mostrar si cumple todas las condiciones
        if (
            (nombre === "" || nombreHabitat.includes(nombre)) &&
            (tipo === "" || tipoHabitat.includes(tipo)) &&
            (estado === "" || estadoHabitat.includes(estado))
        ) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}

// Eventos
buscador.addEventListener('input', filtrarHabitats);
filtroTipo.addEventListener('change', filtrarHabitats);
filtroEstado.addEventListener('change', filtrarHabitats);