document.addEventListener("DOMContentLoaded", function () {
    const categoryLinks = document.querySelectorAll(".nav-item span[data-bs-target='#offcanvasSecondNavbar']");
    const secondOffcanvasBody = document.querySelector("#offcanvasSecondNavbar .offcanvas-body");
    const secondOffcanvasTitle = document.querySelector(".current-category");

    categoryLinks.forEach(link => {
        link.addEventListener("click", function () {
            const categoryName = this.previousElementSibling.textContent.trim(); // Récupérer le nom de la catégorie
            secondOffcanvasTitle.textContent = categoryName; // Mettre à jour le titre
            const subcategories = this.parentElement.querySelectorAll(".submenu-item"); // Trouver les sous-catégories
            
            let subcategoriesHTML = "<ul class='list-unstyled'>";
          
            subcategories.forEach(sub => {
                const subcategoryName = sub.textContent.trim();
                const activitiesNodeList = this.parentElement.querySelectorAll(`.${subcategoryName}_submenu-item`); 
                const activities = Array.from(activitiesNodeList); // Convertir NodeList en tableau
                const collapseId = `collapse-${subcategoryName.replace(/\s+/g, "-")}`; // Assurer un ID unique

                let subcategoryHTML = `
                    <li class="submenu-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>${subcategoryName}</span>
                            ${activities.length > 0 ? `
                                <button class="accordion-button collapsed p-0 border-0 bg-transparent toggle-btn d-flex justify-content-end" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                                    <span class="toggle-icon">+</span>
                                </button>
                            ` : ''}
                        </div>`;

                // Vérifier s'il y a des activités
                if (activities.length > 0) {
                    subcategoryHTML += `
                        <div id="${collapseId}" class="accordion-collapse collapse">
                            <div class="accordion-body">
                                <ul class="activity-list list-unstyled">
                                    ${activities.map(activity => `<li><a href="#">${activity.textContent.trim()}</a></li>`).join('')}
                                </ul>
                            </div>
                        </div>`;
                }

                subcategoryHTML += "</li>";
                subcategoriesHTML += subcategoryHTML;
            });

            subcategoriesHTML += "</ul>";

            secondOffcanvasBody.innerHTML = subcategoriesHTML; // Injecter le HTML des sous-catégories

            // Ajouter un événement pour basculer entre "+" et "-"
            document.querySelectorAll(".toggle-btn").forEach(button => {
                button.addEventListener("click", function () {
                    const icon = this.querySelector(".toggle-icon");
                    setTimeout(() => {
                        if (this.getAttribute("aria-expanded") === "true") {
                            icon.textContent = "-";
                        } else {
                            icon.textContent = "+";
                        }
                    }, 300); // Délai pour s'assurer que l'animation Bootstrap se termine
                });
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const desktopNavLinks = document.querySelectorAll('.desktop-nav-link');
    const testContainer = document.getElementById('test4');

    desktopNavLinks.forEach(link => {
        link.addEventListener('mouseenter', function () {
            const megaMenuRow = link.closest('.nav-item').querySelector('.mega-menu-row');

            if (megaMenuRow) {
                // Clone the mega-menu and append it to #test4
                const megaMenuRowClone = megaMenuRow.cloneNode(true);

                testContainer.innerHTML = ''; // Clear previous content
                testContainer.appendChild(megaMenuRowClone);

                // Show the test-container with the mega-menu content
                testContainer.style.display = 'block';
            }
        });

        link.addEventListener('mouseleave', function (event) {
            // Attendre un peu avant de cacher pour voir si la souris est encore sur testContainer
            setTimeout(() => {
                if (!testContainer.matches(':hover')) {
                    testContainer.style.display = 'none';
                    testContainer.innerHTML = ''; // Clear the content when hiding
                }
            }, 200);
        });
    });

    // Garder le mega-menu ouvert si la souris est dessus
    testContainer.addEventListener('mouseenter', function () {
        testContainer.style.display = 'block';
    });

    testContainer.addEventListener('mouseleave', function () {
        testContainer.style.display = 'none';
        testContainer.innerHTML = ''; // Clear content when hiding
    });
});


