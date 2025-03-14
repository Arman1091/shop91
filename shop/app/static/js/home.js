document.querySelectorAll('.support-plaque-thumbnails img').forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
        document.querySelectorAll('.support-plaque-thumbnails img').forEach(img => img.classList.remove('active'));
        this.classList.add('active');
    });
});
document.addEventListener("DOMContentLoaded", function () {
    let carousel = document.getElementById("supportPlaqueCarousel");
    let thumbnails = document.querySelectorAll(".thumbnails img");
    console.log(thumbnails);

    carousel.addEventListener("slid.bs.carousel", function (event) {
        let activeIndex = event.to; // Récupère l'index de l'image active dans le carousel

        // Supprime la classe 'active' de toutes les miniatures
        thumbnails.forEach(img => img.classList.remove("active"));

        // Ajoute la classe 'active' à la miniature correspondante
        thumbnails[activeIndex].classList.add("active");
    });
});

document.querySelectorAll('.par-materiel-plaque').forEach(plaque => {
    plaque.addEventListener('click', () => {
        alert(`Vous avez sélectionné : ${plaque.querySelector('p').textContent}`);
    });
});