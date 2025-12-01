document.addEventListener("DOMContentLoaded", function() {
    // Tabs
    let productsTab = document.getElementById("products-tab");
    let collectionsTab = document.getElementById("collections-tab");

    function switchTab(tab) {
        let showProducts = tab.id === "products-tab";
        document.getElementById("products-section").style.display = showProducts ? "block" : "none";
        document.getElementById("collections-section").style.display = showProducts ? "none" : "block";
        productsTab.classList.toggle("active", showProducts);
        collectionsTab.classList.toggle("active", !showProducts);
    }
    productsTab.addEventListener("click", () => switchTab(productsTab));
    collectionsTab.addEventListener("click", () => switchTab(collectionsTab));

    // Filters show more / search
    window.toggleShowMore = function(type) {
        let container = document.getElementById(type + "-filters");
        let extras = container.querySelectorAll(".extra-item");
        let link = event.target;
        extras.forEach(item => item.classList.toggle("d-none"));
        link.textContent = link.textContent.includes("Show More") ? "Show Less ▲" : "Show More ▼";
    }

    window.filterItems = function(input, type) {
        let filter = input.value.toLowerCase();
        let container = document.getElementById(type + "-filters");
        container.querySelectorAll(".form-check").forEach(item => {
            let text = item.textContent.toLowerCase();
            item.style.display = text.includes(filter) ? "" : "none";
        });
    }
});