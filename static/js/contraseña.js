document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("formRegistro");
    const passwordInput = document.getElementById("password");
    const passwordHelp = document.getElementById("passwordHelp");

    form.addEventListener("submit", function(event) {
        const password = passwordInput.value;

        // Revisamos cada regla por separado
        if (password.length < 8) {
            event.preventDefault();
            passwordHelp.textContent = "La contraseña debe tener al menos 8 caracteres";
            return;
        }
        if (!/[A-Z]/.test(password)) {
            event.preventDefault();
            passwordHelp.textContent = "La contraseña debe contener al menos una letra mayúscula";
            return;
        }
        if (!/[a-z]/.test(password)) {
            event.preventDefault();
            passwordHelp.textContent = "La contraseña debe contener al menos una letra minúscula";
            return;
        }
        if (!/\d/.test(password)) {
            event.preventDefault();
            passwordHelp.textContent = "La contraseña debe contener al menos un número";
            return;
        }
        if (!/[!@#$%^&*]/.test(password)) {
            event.preventDefault();
            passwordHelp.textContent = "La contraseña debe contener al menos un carácter especial (!@#$%^&*)";
            return;
        }

        // Si pasa todas las validaciones, limpiamos mensaje
        passwordHelp.textContent = "";
    });

    // También validación en tiempo real mientras escribes
    passwordInput.addEventListener("input", function() {
        const password = passwordInput.value;

        if (password.length < 8) {
            passwordHelp.textContent = "La contraseña debe tener al menos 8 caracteres";
        } else if (!/[A-Z]/.test(password)) {
            passwordHelp.textContent = "La contraseña debe contener al menos una letra mayúscula";
        } else if (!/[a-z]/.test(password)) {
            passwordHelp.textContent = "La contraseña debe contener al menos una letra minúscula";
        } else if (!/\d/.test(password)) {
            passwordHelp.textContent = "La contraseña debe contener al menos un número";
        } else if (!/[!@#$%^&*]/.test(password)) {
            passwordHelp.textContent = "La contraseña debe contener al menos un carácter especial (!@#$%^&*)";
        } else {
            passwordHelp.textContent = "";
        }
    });
});

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