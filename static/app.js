// - - - - - - - - - - - - - - - - - - - - - - -  DOM manipulation - - - - - - - - - - - - - - - - - - - - - - -

addEventListener("load", (event) => {
  const content = document.getElementById("content")
  const loader = document.getElementById("loader")
  content.removeAttribute("class")
  loader.setAttribute("class", "visually-hidden")
});

$(document).on("click", ".add-to-cart", addToCart);
$(document).on("click", ".add-to-favorites", addToFavorites);
$(document).on("click", ".remove-from-favorites", removeFromFavorites);
$(document).on("click", ".decrement", updateCart);
$(document).on("click", ".increment", updateCart);
$(document).on("click", ".remove-from-cart", removeFromCart);
$(document).on("click", ".remove-from-table", removeFromTable);
$(document).on("click", ".btn-close", closeFlashedMessage);

// - - - - - - - - - - - - - - - - - - - - - - -  Helper functions  - - - - - - - - - - - - - - - - - - - - - - -

function closeFlashedMessage() {
  this.parentElement.remove();
}

// - - - - - - - - - - - - - - - - - - - - - - -  Making HTML updates - - - - - - - - - - - - - - - - - - - - - - -

function updateHtmlOnFavoritestUpdate(method, element) {
  if (method === "POST") {
    element.innerHTML = `<button class="btn btn-outline-success disabled">Added to favorites!</button>`;
  } else {
    element.remove();
  }
}

function isUserLoggedIn(response) {
  if (response.class === "danger") {
    $("#flashed-messages").replaceWith(`
        <div id="flashed-messages">
        <div class="alert alert-${response.class} alert-dismissible fade show" role="alert">
        <strong>${response.message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
         </div>
        </div>

        `);
    $(".btn-close").on("click", closeFlashedMessage);
    return false;
  }
  return true;
}

function removeFromTable() {
  this.closest(".table-row").remove()
}

// - - - - - - - - - - - - - - - - - - - - - - -  Working with backend requests - - - - - - - - - - - - - - - - - - - - - - -

async function postData(url = "", data = {}, instructions) {

  console.log("IN postData")

  const response = await fetch(url, {
    method: instructions,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

async function editData(url, data) {

  console.log("IN editData")

  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

// - - - - - - - - - - - - - - - - - - - - - - -  Working with carts - - - - - - - - - - - - - - - - - - - - - - -

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
        <span id="qty-${response.prod_id}-cart" data-id="${response.prod_id}" data-price="${response.prod_price}">1</span> x $${(response.prod_price).toFixed(2)}
      </small>
    </div>
    <div class="row">
      <b>${(response.prod_price).toFixed(2)}</b>
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
  const cartQuantity = document.querySelector(`#qty-${this.dataset.id}-cart`);
  const cardQuantity = document.querySelector(`#qty-${this.dataset.id}-card`);

  cartQuantity.innerText = `${response.qty} `
  cartBubble.innerText = response.num_items_in_cart
  cardQuantity.innerText = `${response.qty} `

  if (response.qty <= 0) {
    const cartLi = document.querySelector(`#${this.dataset.id}`)
    const postForm = this.parentElement

    cartLi.remove()
    postForm.outerHTML = `
    <form action="/cart" class="d-grid mx-auto my-2 add-to-cart" data-id="${this.dataset.id}" method="post">
    <button class="btn btn-outline-dark">Add to cart</button>
    </form>
    `;
    postData("/cart/delete", { id: this.dataset.id }, "DELETE");
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

// - - - - - - - - - - - - - - - - - - - - - - -  Working with favorites - - - - - - - - - - - - - - - - - - - - - - -

async function addToFavorites(e) {
  e.preventDefault();
  const productId = this.dataset.id;
  const instructions = this.method;
  const response = await postData(
    "/favorites",
    { id: productId },
    instructions
  );
  const data = response["data"];

  if (isUserLoggedIn(data)) {
    const method = response["data"]["method"];
    const element = this;
    updateHtmlOnFavoritestUpdate(method, element);
  }
}

async function removeFromFavorites(e) {
  e.preventDefault();

  const response = await postData(
    "/favorites/delete",
    { id: this.dataset.id },
    "DELETE"
  );

  const method = response["data"]["method"];
  const element = this.closest(".col-sm-3");

  updateHtmlOnFavoritestUpdate(method, element);
}
