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

    const method = "DELETE";
    const element = this.closest(".");

    updateHtmlOnFavoritestUpdate(method, element);
}
