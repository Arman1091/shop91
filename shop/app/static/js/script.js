document.addEventListener("DOMContentLoaded", function () {
  const mobileMenuButton = document.getElementById("mobileMenuButton");
  const mobileSidebar = document.getElementById("mobileSidebar");
  const closeSidebar = document.getElementById("closeSidebar");

  // Ouvrir le menu mobile
  // mobileMenuButton.addEventListener("click", function () {
  //   mobileSidebar.classList.add("open");
  // });

  // Fermer le menu mobile
  // closeSidebar.addEventListener("click", function () {
  //   mobileSidebar.classList.remove("open");
  // });

  // Gestion des dropdowns dans le menu mobile
  document.querySelectorAll(".dropdown-mobile > a").forEach((dropdownLink) => {
    dropdownLink.addEventListener("click", function (e) {
      e.preventDefault(); // Empêche la navigation
      const parent = dropdownLink.parentElement;

      // Basculer la classe "open" pour afficher/masquer le sous-menu
      if (parent.classList.contains("open")) {
        parent.classList.remove("open");
      } else {
        // Fermer les autres dropdowns
        document
          .querySelectorAll(".dropdown-mobile.open")
          .forEach((openDropdown) => {
            openDropdown.classList.remove("open");
          });
        parent.classList.add("open");
      }
    });
  });

  // Gestion des sous-dropdowns (subcategories)
  document
    .querySelectorAll(".dropdown-submenu-mobile > a")
    .forEach((submenuLink) => {
      submenuLink.addEventListener("click", function (e) {
        e.preventDefault(); // Empêche la navigation
        const parent = submenuLink.parentElement;

        // Basculer la classe "open" pour afficher/masquer le sous-sous-menu
        if (parent.classList.contains("open")) {
          parent.classList.remove("open");
        } else {
          // Fermer les autres sous-dropdowns dans le même niveau
          parent.parentElement
            .querySelectorAll(".dropdown-submenu-mobile.open")
            .forEach((openSubmenu) => {
              openSubmenu.classList.remove("open");
            });
          parent.classList.add("open");
        }
      });
    });
});
