 function togglePassword() {
            const passwordInput = document.getElementById("password");
            const icono = document.getElementById("icono-password");

            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                icono.classList.remove("bi-eye");
                icono.classList.add("bi-eye-slash");
            } else {
                passwordInput.type = "password";
                icono.classList.remove("bi-eye-slash");
                icono.classList.add("bi-eye");
            }
        }