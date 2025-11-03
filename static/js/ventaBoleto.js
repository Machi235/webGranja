const boleta = document.querySelector("#boleta");
const venderBoleta = document.querySelector("#venderBoleta");
const cerrarVenta = document.querySelector("#cerrarVenta");

boleta.addEventListener("click", () => {
    venderBoleta.showModal();
})
cerrarVenta.addEventListener("click", () => {
    venderBoleta.close();
})