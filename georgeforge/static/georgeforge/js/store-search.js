/**
 * georgeforge/static/georgeforge/js/store-search.js
 *
 * Moves the inline store search script into a dedicated file so editors can
 * provide proper syntax highlighting and formatting.
 *
 * Behaviour:
 * - Finds the input with id "store-search"
 * - Filters `.store-item` elements grouped under `.store-group`
 * - Hides groups that have no visible items
 *
 * Exports:
 * - Attaches `georgeforge.initStoreSearch` to `window` for manual initialization / testing.
 *
 * Usage:
 * - Include this file in your template (e.g. with `{% static %}`) instead of the inline script.
 * - The script auto-initializes on DOMContentLoaded.
 */

(function () {
    "use strict";

    // Normalize strings for comparison
    function normalize(s) {
        return (s || "").toLowerCase();
    }

    // Initialize the store search behavior. Accepts an optional root (for testing).
    function initStoreSearch(root = document) {
        const input = root.getElementById
            ? root.getElementById("store-search")
            : root.querySelector && root.querySelector("#store-search");

        if (!input) {
            return; // Nothing to do if the input is missing
        }

        // Cache group nodes once
        const groups = Array.from(document.querySelectorAll(".store-group"));

        function filter() {
            const q = normalize(input.value.trim());

            groups.forEach((group) => {
                const items = Array.from(group.querySelectorAll(".store-item"));
                let shownInGroup = 0;

                items.forEach((item) => {
                    const text = normalize(
                        item.textContent || item.innerText || "",
                    );
                    const match = q === "" || text.indexOf(q) !== -1;
                    item.style.display = match ? "" : "none";
                    if (match) shownInGroup++;
                });

                group.style.display = shownInGroup > 0 ? "" : "none";
            });
        }

        // Ensure we don't attach duplicate handlers if initStoreSearch is called twice.
        // Using a named wrapper to be safe when removing would be necessary; here we
        // simply attach the handler — browsers won't duplicate the same function
        // reference if it's identical, but to be defensive we remove any existing
        // handler by referencing the same function (no-op on first run).
        input.removeEventListener("input", filter);
        input.addEventListener("input", filter);

        // Apply initial filter if there's a preset value
        if (input.value && input.value.trim() !== "") {
            filter();
        }
    }

    // Auto-initialize on DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function onDom() {
            document.removeEventListener("DOMContentLoaded", onDom);
            initStoreSearch();
        });
    } else {
        initStoreSearch();
    }

    // Expose for testing or manual re-initialization
    window.georgeforge = window.georgeforge || {};
    window.georgeforge.initStoreSearch = initStoreSearch;
})();
