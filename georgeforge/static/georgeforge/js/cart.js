(function () {
    "use strict";

    const CART_KEY = "georgeforge_cart";
    const CHECKOUT_URL = "/georgeforge/api/cart/checkout";

    function getCart() {
        const cart = localStorage.getItem(CART_KEY);
        return cart ? JSON.parse(cart) : [];
    }

    function saveCart(cart) {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        updateCounter();
    }

    function updateCounter() {
        const cart = getCart();
        const counter = document.getElementById("cart-counter");
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

        if (totalItems > 0) {
            counter.textContent = totalItems;
            counter.style.display = "block";
        } else {
            counter.style.display = "none";
        }
    }

    function showToast(message) {
        const toast = document.createElement("div");
        toast.className = "position-fixed bottom-0 end-0 p-3";
        toast.style.zIndex = "1100";
        toast.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-body">${message}</div>
            </div>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function formatNumber(num) {
        return parseFloat(num).toLocaleString("en-US", {
            maximumFractionDigits: 2,
            minimumFractionDigits: 2,
        });
    }

    function formatISK(amount) {
        return `${formatNumber(amount)} ISK`;
    }

    function openCart() {
        const drawer = document.getElementById("cart-drawer");
        const overlay = document.getElementById("cart-overlay");
        drawer.classList.add("open");
        overlay.classList.add("open");
        renderCart();
    }

    function closeCart() {
        const drawer = document.getElementById("cart-drawer");
        const overlay = document.getElementById("cart-overlay");
        drawer.classList.remove("open");
        overlay.classList.remove("open");
    }

    function renderCart() {
        const cart = getCart();
        const cartItems = document.getElementById("cart-items");
        const cartEmpty = document.getElementById("cart-empty");
        const cartSummary = document.getElementById("cart-summary");
        const cartCheckout = document.getElementById("cart-checkout");

        if (cart.length === 0) {
            cartItems.innerHTML = "";
            cartEmpty.style.display = "block";
            cartSummary.style.display = "none";
            cartCheckout.style.display = "none";
            return;
        }

        cartEmpty.style.display = "none";
        cartSummary.style.display = "block";
        cartCheckout.style.display = "block";

        let html = "";
        let totalItems = 0;
        let totalCost = 0;
        let totalDeposit = 0;

        cart.forEach((item, index) => {
            const itemTotalCost = item.price * item.quantity;
            const itemTotalDeposit = item.deposit * item.quantity;

            totalItems += item.quantity;
            totalCost += itemTotalCost;
            totalDeposit += itemTotalDeposit;

            html += `
                <div class="cart-item" data-index="${index}">
                    <div class="d-flex align-items-start gap-2">
                        <img src="${item.icon}"
                             width="48"
                             height="48"
                             alt="${item.name}" />
                        <div class="flex-grow-1">
                            <h6 class="mb-0">${item.name}</h6>
                            <div class="small text-muted">
                                ${formatISK(item.price)} / unit
                                ${item.deposit > 0 ? `| ${formatISK(item.deposit)} deposit` : ""}
                            </div>
                        </div>
                        <button type="button"
                                class="btn btn-sm btn-outline-danger remove-from-cart"
                                data-index="${index}">&times;</button>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <div class="d-flex align-items-center gap-2">
                            <button type="button"
                                    class="btn btn-sm btn-outline-secondary decrease-quantity"
                                    data-index="${index}">-</button>
                            <span class="fw-bold">${item.quantity}</span>
                            <button type="button"
                                    class="btn btn-sm btn-outline-secondary increase-quantity"
                                    data-index="${index}">+</button>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold">${formatISK(itemTotalCost)}</div>
                            ${item.deposit > 0 ? `<div class="small text-muted">+ ${formatISK(itemTotalDeposit)} deposit</div>` : ""}
                        </div>
                    </div>
                </div>
            `;
        });

        cartItems.innerHTML = html;
        document.getElementById("cart-total-items").textContent = totalItems;
        document.getElementById("cart-total-cost").textContent =
            formatISK(totalCost);
        document.getElementById("cart-total-deposit").textContent =
            formatISK(totalDeposit);

        attachCartEventListeners();
    }

    function attachCartEventListeners() {
        document.querySelectorAll(".remove-from-cart").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const index = parseInt(e.target.dataset.index, 10);
                removeFromCart(index);
            });
        });

        document.querySelectorAll(".decrease-quantity").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const index = parseInt(e.target.dataset.index, 10);
                updateQuantity(index, -1);
            });
        });

        document.querySelectorAll(".increase-quantity").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const index = parseInt(e.target.dataset.index, 10);
                updateQuantity(index, 1);
            });
        });
    }

    function addToCart(forSaleId, quantity) {
        const cart = getCart();
        const storeItem = document.querySelector(
            `[data-for-sale-id="${forSaleId}"]`,
        );

        if (!storeItem) {
            showToast("Item not found");
            return;
        }

        const forSaleIdNum = parseInt(forSaleId, 10);
        const existingItem = cart.find(
            (item) => item.for_sale_id === forSaleIdNum,
        );

        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            cart.push({
                for_sale_id: parseInt(forSaleId, 10),
                eve_type_id: parseInt(storeItem.dataset.eveTypeId, 10),
                name: storeItem.dataset.eveTypeName,
                icon: storeItem.dataset.eveTypeIcon,
                price: parseFloat(storeItem.dataset.price),
                deposit: parseFloat(storeItem.dataset.deposit),
                description: storeItem.dataset.description,
                quantity: quantity,
            });
        }

        saveCart(cart);
        showToast(
            `Added ${quantity}x ${storeItem.dataset.eveTypeName} to cart`,
        );
    }

    function removeFromCart(index) {
        const cart = getCart();
        const removed = cart.splice(index, 1)[0];
        saveCart(cart);
        renderCart();
        showToast(`Removed ${removed.name} from cart`);
    }

    function updateQuantity(index, delta) {
        const cart = getCart();
        const item = cart[index];

        item.quantity += delta;

        if (item.quantity < 1) {
            cart.splice(index, 1);
        }

        saveCart(cart);
        renderCart();
    }

    function clearCart() {
        localStorage.removeItem(CART_KEY);
        updateCounter();
        renderCart();
    }

    async function checkoutCart(formData) {
        const cart = getCart();

        if (cart.length === 0) {
            showToast("Your cart is empty");
            return;
        }

        const items = cart.map((item) => ({
            for_sale_id: item.for_sale_id,
            quantity: item.quantity,
        }));

        const payload = {
            items: items,
            deliverysystem_id: formData.deliverysystem_id,
            notes: formData.notes || "",
        };

        try {
            const response = await fetch(CHECKOUT_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": formData.csrf_token,
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (data.success) {
                clearCart();
                closeCart();
                showToast("Order placed successfully!");
                window.location.href = "/georgeforge/orders";
            } else {
                showToast(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Checkout error:", error);
            showToast("Error placing order");
        }
    }

    function init() {
        updateCounter();

        const cartToggle = document.getElementById("cart-toggle");
        const cartClose = document.getElementById("cart-close");
        const cartOverlay = document.getElementById("cart-overlay");
        const checkoutForm = document.getElementById("checkout-form");

        if (cartToggle) {
            cartToggle.addEventListener("click", openCart);
        }

        if (cartClose) {
            cartClose.addEventListener("click", closeCart);
        }

        if (cartOverlay) {
            cartOverlay.addEventListener("click", closeCart);
        }

        document.querySelectorAll(".add-to-cart").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const forSaleId = e.target.dataset.forSaleId;
                const quantityInput = document.getElementById(
                    `quantity-${forSaleId}`,
                );
                const quantity = parseInt(quantityInput.value, 10);

                if (quantity >= 1) {
                    addToCart(forSaleId, quantity);
                } else {
                    showToast("Quantity must be at least 1");
                }
            });
        });

        if (checkoutForm) {
            checkoutForm.addEventListener("submit", (e) => {
                e.preventDefault();

                const deliverysystemId =
                    document.getElementById("delivery-system").value;
                const notes = document.getElementById("notes").value;
                const csrfToken = document.querySelector(
                    'input[name="csrfmiddlewaretoken"]',
                ).value;

                if (!deliverysystemId) {
                    showToast("Please select a delivery location");
                    return;
                }

                checkoutCart({
                    deliverysystem_id: parseInt(deliverysystemId, 10),
                    notes: notes,
                    csrf_token: csrfToken,
                });
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
