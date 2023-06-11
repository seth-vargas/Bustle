$(".add-to-cart").on("submit", addToCart);
$(".increment").on("submit", updateQuantity);
$(".decrement").on("submit", updateQuantity);
$(".remove-from-cart").on("click", removeFromCart);
$(".add-to-favorites").on("submit", addToFavorites);
$(".remove-from-favorites").on("submit", removeFromFavorites);
$(".btn-close").on("click", closeFlashedMessage);

function closeFlashedMessage() {
  this.parentElement.remove();
}

function updateData(url = "", data = {}, instructions = "") {}

async function updateQuantity(e) {
  e.preventDefault();
  console.log(this);
  const productId = this.dataset.id;
  const cls = this.class;
  const response = await updateData("cart", { id: productId }, cls);
  const data = response["response"];

  if (isUserLoggedIn(data)) {
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

function updateHtmlOnCartUpdate(method, element, qty) {
  if (method === "POST") {
    element.innerHTML = `
    <div class="d-flex justify-content-evenly align-items-center">
    <button class="btn btn-danger"><i class="fa-solid fa-minus"></i></button>
    <small>${qty} in cart</small>
    <button class="btn btn-light"><i class="fa-solid fa-plus"></i></button>
    </div>
    `;
    element.method = "patch";
    debugger;
  } else {
    element.remove();
  }
}

function updateHtmlOnFavoritestUpdate(method, element) {
  if (method === "POST") {
    element.innerHTML = `<button class="btn btn-outline-success disabled">Added to favorites!</button>`;
  } else {
    element.remove();
  }
}

async function postData(url = "", data = {}, instructions = "GET") {
    if (instructions == "DELETE") {
        const response = await fetch(url, )
    }
  const response = await fetch(url, {
    method: instructions,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

async function addToCart(e) {
  e.preventDefault();
  const productId = this.dataset.id;
  const instructions = this.method;
  const response = await postData(`/cart`, { id: productId }, instructions);
  const data = response["response"];

  if (isUserLoggedIn(data)) {
    const method = response["response"]["method"];
    const element = this;
    const qty = response["response"]["qty"];
    updateHtmlOnCartUpdate(method, element, qty);
  }
}

async function removeFromCart() {
  const productId = this.dataset.id;
  const instructions = this.method;
  const response = await postData("/cart/delete", { id: productId });
  const method = response["response"]["method"];
  const element = this.closest(".row");

  updateHtmlOnCartUpdate(method, element);
}

async function addToFavorites(e) {
  e.preventDefault();
  const productId = this.dataset.id;
  const instructions = this.method;
  const response = await postData(
    "/favorites",
    { id: productId },
    instructions
  );
  const data = response["response"];

  if (isUserLoggedIn(data)) {
    const method = response["response"]["method"];
    const element = this;
    updateHtmlOnFavoritestUpdate(method, element);
  }
}

async function removeFromFavorites(e) {
  e.preventDefault();
  const productId = this.dataset.id;
  const instructions = this.method;
  const response = await postData(
    "/favorites/delete",
    { id: productId },
    instructions
  );
  const method = response["response"]["method"];
  const element = this.closest(".col-sm-3");

  updateHtmlOnFavoritestUpdate(method, element);
}
