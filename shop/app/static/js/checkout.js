$(document).ready(function() {
    // Generic AJAX submit function for all forms
    $('.accordion-body form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var formData = new FormData(form[0]);
        var clientType = $('input[name="client_type"]:checked').val();
        console.log('Selected client type:', clientType);
        // Append client type to the form data (optional, if you want it sent with the form)
        // formData.append('client_type', clientType);
        var collapseId = form.closest('.accordion-collapse').attr('id');
        var nextCollapseId = getNextCollapseId(collapseId);
        console.log(form.attr('action'));
        console.log(formData);

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log("sd");
                if (response.success) {
                    console.log("mmm");
                    // Close the current accordion
                    $(`#${collapseId}`).collapse('hide');
                    // Open the next accordion if it exists
                    if (nextCollapseId) {
                        $(`#${nextCollapseId}`).collapse('show');
                    }
                    alert('Étape complétée avec succès !');
                } else {
                    alert('Une erreur est survenue. Veuillez réessayer.');
                }
            },
            error: function(xhr, status, error) {
           
                alert('Une erreur est survenue. Veuillez réessayer.');
            }
        });
    });

    // Function to get the ID of the next accordion section
    function getNextCollapseId(currentId) {
        const order = ['collapseConnexion', 'collapseAdresses', 'collapseLivraison', 'collapsePaiement'];
        const currentIndex = order.indexOf(currentId);
        return currentIndex < order.length - 1 ? order[currentIndex + 1] : null;
    }
});

// Sélectionner tous les boutons radio ayant le même nom 'client_type'
const radios = document.querySelectorAll('input[name="client_type"]');
if(radios ){
// Ajouter un écouteur d'événement sur chaque radio
radios.forEach(radio => {
    radio.addEventListener('change', function() {
        // Lorsque l'utilisateur change le bouton radio, on récupère la valeur sélectionnée
        console.log('Valeur sélectionnée :', this.value);
        if(this.value == "existing"){
            document.getElementById("checkout_connexion").style.display="block";
            document.getElementById("checkout_inscription").style.display="none";
        } else{
            document.getElementById("checkout_connexion").style.display="none";
            document.getElementById("checkout_inscription").style.display="block";
        }
    });
});

}
