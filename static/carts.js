// - - - - - - - - - - - - - - - - - - - - - - -  Working with carts - - - - - - - - - - - - - - - - - - - - - - -

$(document).on("click", ".add-to-cart", addToCart);
$(document).on("click", ".remove-from-cart", removeFromCart);
$(document).on("click", ".decrement", updateCart);
$(document).on("click", ".increment", updateCart);

/* Runs when user initally adds an item to their cart */
async function addToCart(e) {

    console.log("IN addToCart")

    e.preventDefault();
    const response = await postData(`/cart`, { id: this.dataset.id }, "POST");

    if (isUserLoggedIn(response)) {

        const cartBubble = document.querySelector("#cart-count")
        cartBubble.innerText = response.num_items_in_cart

        this.outerHTML = `
      <div class="d-flex justify-content-evenly align-items-center my-2">
          <button class="btn btn-outline-danger decrement" data-id="${this.dataset.id}" data-func="updateCart"
              data-role="decrement">
              <i class="fa-solid fa-minus"></i>
          </button>
  
          <small><span id="qty-${this.dataset.id}-card">1</span> in cart</small>
  
          <button class="btn btn-outline-success increment" data-id="${this.dataset.id}" data-func="updateCart"
              data-role="increment">
              <i class="fa-solid fa-plus"></i></button>
      </div>
      `;
        const cartDiv = document.querySelector("#cart")
        const newLi = document.createElement("li")
        newLi.classList.add("list-group-item")
        newLi.id = `${response.prod_id}`
        newLi.innerHTML = `
      <div class="row">
        <small>${response.prod_title}</small>
      </div>
      <div class="row">
        <small>
          <span id="qty-${response.prod_id}-cart" data-id="${response.prod_id}" data-price="${response.prod_price}">1</span> x $${response.prod_price.toFixed(2)}
        </small>
      </div>
      <div class="row">
        <b>${response.prod_price.toFixed(2)}</b>
      </div>
    `
        cartDiv.append(newLi)
    }
}

/* Gets ran when the user increments / decrements their cart */

async function updateCart() {

    console.log("IN updateCart")

    const response = await editData("/cart", {
        id: this.dataset.id,
        func: this.dataset.func,
        role: this.dataset.role,
    });


    const cartBubble = document.querySelector("#cart-count")
    const qtyElements = document.querySelectorAll(`#qty-${this.dataset.id}`)

    cartBubble.innerText = response.num_items_in_cart
    qtyElements.forEach((element) => {
        element.innerText = `${response.qty} `
    })

    if (response.qty <= 0) {

        const url = document.location.href
        if (url.endsWith("/cart")) {
            const row = this.closest(".cart-table-row")
            row.remove()
        } else {
            const cartLi = document.querySelector(`#${this.dataset.id}`)
            const postForm = this.parentElement

            cartLi.remove()
            postForm.outerHTML = `
        <form action="/cart" class="d-grid mx-auto my-2 add-to-cart" data-id="${this.dataset.id}" method="post">
        <button class="btn btn-outline-dark">Add to cart</button>
        </form>
        `;
        }
        const response = await postData("/cart/delete", { id: this.dataset.id }, "DELETE");
        console.log(response)
        console.log(this.dataset.id)
    }
}

/* Gets ran when removing from /cart/delete */
async function removeFromCart() {

    console.log("IN removeFromCart")

    // delete item from db
    const response = await postData("/cart/delete", { id: this.dataset.id }, "delete");

    // update total
    const total = document.querySelector("#total");
    const newSum = response["sub_total"].toFixed(2)
    total.textContent = `$${newSum}`;
    total.dataset.sum = newSum

    const cartBubble = document.querySelector("#cart-count")
    cartBubble.innerText = response["count_products_in_cart"]

    if (!response.qty || response.qty === 0) {
        // Remove row from DOM
        this.closest(".row").remove()
    } else {
        // update el on DOM
        const qty = document.querySelector(`#qty-${this.dataset.id}-card`)
        qty.innerText = `${response.qty} `;
    }
}

