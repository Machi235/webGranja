const limite = document.querySelector("#ponerlimite");
const limiteAnimal = document.querySelector("#limiteAnimal");
const cerrarLimite = document.querySelector("#cerrarLimite");
const form = limiteAnimal.querySelector("form")

limite.addEventListener("click", () => {
  limiteAnimal.showModal();
  })
cerrarLimite.addEventListener("click", () => {
    limiteAnimal.close();
    })