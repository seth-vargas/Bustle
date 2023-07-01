$(document).on("click", ".add-to-favorites", addToFavorites);
$(document).on("click", ".remove-from-favorites", removeFromFavorites);
$(document).on("click", ".remove-from-table", removeFromTable);

// - - - - - - - - - - - - - - - - - - - - - - -  Making HTML updates - - - - - - - - - - - - - - - - - - - - - - -

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
    this.closest(".cart-table-row").remove()
    postData("/cart/delete", { id: this.dataset.id }, "DELETE");
}



function updateHtmlOnFavoritestUpdate(method, element) {
    if (method === "POST") {
        element.innerHTML = `<button class="btn btn-outline-success disabled">Added to favorites!</button>`;

    } else {
        element.remove();
    }
}

// - - - - - - - - - - - - - - - - - - - - - - -  Working with favorites - - - - - - - - - - - - - - - - - - - - - - -

async function addToFavorites(e) {
    console.log("IN addToavorites");
    e.preventDefault();
    const productId = this.dataset.id;
    const instructions = this.method;
    const response = await postData(
        "/favorites",
        { id: productId },
        instructions
    );

    const favForm = this
    favForm.innerHTML = `
    <form action="/favorites/delete" class="d-grid mx-auto my-2 remove-from-favorites" data-id="${this.dataset.id}" method="DELETE">
        <button class="btn btn-outline-danger">Remove from favorites</button>
    </form>
    `
    favForm.addEventListener("click", removeFromFavorites)
}

async function removeFromFavorites(e) {
    console.log("IN removeFromFavorites");
    e.preventDefault();

    const response = await postData(
        "/favorites/delete",
        { id: this.dataset.id },
        "DELETE"
    );

    const url = document.location.href
    if (url.endsWith("/favorites")) {
        const prodCard = this.closest(".col")
        prodCard.remove()
    } else {
        const favForm = this
        favForm.outerHTML = `
        <form action="/favorites" class="d-grid mx-auto my-2 add-to-favorites" data-id="${this.dataset.id}" method="post" data-instructions="post">
            <button class="btn btn-outline-dark">Add to favorites</button>
        </form>
        `
        favForm.addEventListener("click", addToFavorites)
    }
}
