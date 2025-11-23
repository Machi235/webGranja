document.addEventListener("DOMContentLoaded", () => {
    const buscador = document.getElementById("buscador");
    const filtroRol = document.getElementById("filtroRol");
    const fichas = document.querySelectorAll(".ficha");

    function filtrar() {
        const textoBusqueda = buscador.value.toLowerCase();
        const rolSeleccionado = filtroRol.value;

        fichas.forEach(ficha => {
            const nombre = ficha.querySelector(".nombre").textContent.toLowerCase();
            const rol = ficha.querySelector(".rol").textContent;

            const coincideNombre = nombre.includes(textoBusqueda);
            const coincideRol = rolSeleccionado === "" || rol === rolSeleccionado;

            if (coincideNombre && coincideRol) {
                ficha.style.display = "flex";
            } else {
                ficha.style.display = "none";
            }
        });
    }

    buscador.addEventListener("input", filtrar);
    filtroRol.addEventListener("change", filtrar);
});
