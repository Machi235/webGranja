const buscador = document.getElementById('buscador');
const filtroRol = document.getElementById('filtroRol');
const lista = document.getElementById('data');

function filtrarUsuarios() {
    const nombre = buscador.value.toLowerCase();
    const rol = filtroRol.value.toLowerCase();

    const cards = lista.getElementsByClassName('usuario');

    for (let card of cards) {
        const nombreUsuario = card.querySelector('.card-title').textContent.toLowerCase();
        const rolUsuario = card.querySelector('.card-rol').textContent.toLowerCase();

        if (
            (nombre === "" || nombreUsuario.includes(nombre)) &&
            (rol === "" || rolUsuario.includes(rol))
        ) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}

buscador.addEventListener('input', filtrarUsuarios);
filtroRol.addEventListener('change', filtrarUsuarios);
