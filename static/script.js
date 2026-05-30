document.addEventListener("DOMContentLoaded", function() {
    console.log("JS chargé");

    const form = document.querySelector("form");

    if (!form) return;

    const champPseudo = document.querySelector("input[name='user']");
    const champMdp = document.querySelector("input[name='mdp']");
    const champVerifmdp = document.querySelector("input[name='confirm_mdp']");

    function validerChamp(champ, condition, message) {

        let erreur = champ.parentElement.querySelector(".message-erreur");

        if (!condition) {
            if (!erreur) {
                erreur = document.createElement("p");
                erreur.classList.add("message-erreur");
                champ.parentElement.appendChild(erreur);
            }

            erreur.textContent = message;

            champ.classList.add("champ-invalide");

            return false;
        } else {
            if (erreur) erreur.remove();

            champ.classList.remove("champ-invalide");

            return true;
        }
    }

    champPseudo.addEventListener("input", function() {
        validerChamp(champPseudo, champPseudo.value.trim().length >= 4, "Le pseudo doit contenir au moins 5 caractères !");
    });

    champMdp.addEventListener("input", function() {
        validerChamp(champMdp, champMdp.value.trim().length >= 8, "Le mot de passe doit contenir au moins 8 caractères !");
    });

    champVerifmdp.addEventListener("input", function() {
        validerChamp(champVerifmdp, champVerifmdp.value == champMdp.value, "Les mot de passe ne correspondent pas !");
    });

    form.addEventListener("submit", function(event) {

        const pseudo_Ok = validerChamp(champPseudo, champPseudo.value.trim().length >= 4, "Le pseudo doit contenir au moins 5 caractères !");

        const mdp_Ok = validerChamp(champMdp, champMdp.value.trim().length >= 8, "Le mot de passe doit contenir au moins 8 caractères !");

        const verif_Ok = validerChamp(champVerifmdp, champVerifmdp.value == champMdp.value, "Les mot de passe ne correspondent pas !");

        if (!pseudo_Ok || !mdp_Ok || !verif_Ok) {
            event.preventDefault();
            return;
        } 
    });
});
