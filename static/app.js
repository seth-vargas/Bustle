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

function isUserLoggedIn(data) {
  if (data["class"] === "danger") {
    $("#flashed-messages").replaceWith(`
        <div id="flashed-messages">
        <div class="alert alert-${data["class"]} alert-dismissible fade show" role="alert">
        <strong>${data["message"]}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
         </div>
        </div>

        `);
    $(".btn-close").on("click", closeFlashedMessage);
    return false;
  }
  return true;
}

// - - - - - - - - - - - - - - - - - - - - - - -  Working with backend requests - - - - - - - - - - - - - - - - - - - - - - -

async function postData(url = "", data = {}, instructions) {
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

async function addToCart(e) {
  e.preventDefault();
  const response = await postData(`/cart`, { id: this.dataset.id }, "POST");
  const data = response["data"];

  
  if (!isUserLoggedIn(data)) return;
  
  const cartBubble = document.querySelector("#cart-count")
  cartBubble.innerText = data["count_products_in_cart"]

  this.outerHTML = `
    <div class="d-flex justify-content-evenly align-items-center my-2">
        <button class="btn btn-outline-danger decrement" data-id="${this.dataset.id}" data-func="updateCart"
            data-role="decrement">
            <i class="fa-solid fa-minus"></i>
        </button>

        <small><span id="qty-${this.dataset.id}">${response["data"]["qty"]} </span>in cart</small>

        <button class="btn btn-outline-success increment" data-id="${this.dataset.id}" data-func="updateCart"
            data-role="increment">
            <i class="fa-solid fa-plus"></i></button>
    </div>
    `;
}

/* Gets ran when the user increments / decrements their cart */

async function updateCart() {
  const response = await editData("/cart", {
    id: this.dataset.id,
    func: this.dataset.func,
    role: this.dataset.role,
  });

  const data = response["data"]

  const cartBubble = document.querySelector("#cart-count")
  cartBubble.innerText = data["count_products_in_cart"]

  const isZero = data["qty"] <= 0 ? true : false;

  if (isZero) {
    this.parentElement.outerHTML = `
    <form action="/cart" class="d-grid mx-auto my-2 add-to-cart" data-id="${this.dataset.id}" method="post">
        <button class="btn btn-outline-dark">Add to cart</button>
    </form>
    `;

    return postData("/cart/delete", { id: this.dataset.id }, "DELETE");
  } else {
    const qty = document.querySelector(`#qty-${this.dataset.id}`);
    qty.innerText = `${data["qty"]} `;
  }
}

/* Gets ran when removing from /cart/delete */
async function removeFromCart() {
  // delete item from db
  const response = await postData("/cart/delete", { id: this.dataset.id }, "delete");
  const data = response["data"] 
  
  // update total
  const total = document.querySelector("#total");
  const newSum = (total.dataset.sum - data["price"]).toFixed(2)
  total.textContent = `$${ newSum }`;
  total.dataset.sum = newSum

  if (data["qty"] === 0) {
    this.closest(".row").remove()
    return
  }
  
  // update el on DOM
  const qty = document.querySelector(`#qty-${this.dataset.id}`)
  qty.innerText = `${data["qty"]} `;

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
