$( ".add-to-cart" ).on( "submit" , addToCart )
$( ".remove-from-cart" ).on( "click", removeFromCart )
$( ".add-to-favorites" ).on( "submit" , addToFavorites )
$( ".remove-from-favorites" ).on( "submit", removeFromFavorites )

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

    const method = response["data"]["method"]
    const element = this

    updateHtmlOnCartUpdate(method, element)
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
    console.log(this)
    const productId = this.dataset.id

    const response = await postData("/favorites", {id: productId})

    const method = response["data"]["method"]
    const element = this

    updateHtmlOnFavoritestUpdate(method, element)
}

async function removeFromFavorites(e) {
    e.preventDefault()
    const productId = this.dataset.id
    
    const response = await deleteData("/favorites/delete", {id: productId})

    const method = response["data"]["method"]
    const element = this.closest(".col-sm-3")

    updateHtmlOnFavoritestUpdate(method, element)
}


