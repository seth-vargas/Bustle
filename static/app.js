$( ".add-to-cart" ).on( "submit" , addToCart )
$( ".remove-from-cart" ).on( "click", removeFromCart )
$( ".add-to-favorites" ).on( "submit" , addToFavorites )
$( ".remove-from-favorites" ).on( "submit", removeFromFavorites )
$( ".btn-close" ).on( "click", closeFlashedMessage )

function closeFlashedMessage() {
    console.log(this.parentElement.remove())
}

function isUserLoggedIn(data) {
    if (data["class"] === "danger") {
        $("#flashed-messages").replaceWith(`
        <div id="flashed-messages">
        <div class="alert alert-${data["class"]} mx-auto my-1 rounded-pill text-center">
        <small class="my-auto"><b>${data["message"]}</b></small>
        <button type="button" class="btn-close m-auto" aria-label="Close"></button>
        </div>
        </div>
        `)
        $( ".btn-close" ).on( "click", closeFlashedMessage )
        return false
    }
    return true
}

function updateHtmlOnCartUpdate(method, element) {
    if (method === "POST") {
        element.innerHTML = `<button class="btn btn-success disabled">Added to cart!</button>`
    } else {
        element.remove()
    }
}

function updateHtmlOnFavoritestUpdate(method, element) {
    if (method === "POST") {
        element.innerHTML = `<button class="btn btn-outline-success disabled">Added to favorites!</button>`
    } else {
        element.remove()
    }
}

async function postData(url = "", data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
         body: JSON.stringify(data)
    })
    return response.json()
}

async function deleteData(url="", data={}) {
    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    return response.json()
}

async function addToCart(e) {
    e.preventDefault()
    const productId = this.dataset.id
    const response = await postData(`/cart`, {id: productId})
    const data = response["response"]

    if (isUserLoggedIn(data)) {
        const method = response["data"]["method"]
        const element = this
        updateHtmlOnCartUpdate(method, element)
    }
}

async function removeFromCart() {
    const productId = this.dataset.id
    const response = await deleteData("/cart/delete", {id: productId})
    const method = response["data"]["method"]
    const element = this.closest(".row")

    updateHtmlOnCartUpdate(method, element)
}

async function addToFavorites(e) {
    e.preventDefault()
    const productId = this.dataset.id
    const response = await postData("/favorites", {id: productId})
    const data = response["response"]

    if (isUserLoggedIn(data)) {
        const method = response["data"]["method"]
        const element = this
        updateHtmlOnFavoritestUpdate(method, element)
    }
}

async function removeFromFavorites(e) {
    e.preventDefault()
    const productId = this.dataset.id
    const response = await deleteData("/favorites/delete", {id: productId})
    const method = response["data"]["method"]
    const element = this.closest(".col-sm-3")

    updateHtmlOnFavoritestUpdate(method, element)
}


