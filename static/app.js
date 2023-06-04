$( ".add-to-cart" ).on( "submit" , addToCart )
$( ".remove-from-cart" ).on( "click", removeFromCart )

function updateHtml(method, element) {
    if (method === "POST") {
        element.innerHTML = `<button class="btn btn-success disabled">Added to cart!</button>`
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

    const method = response["response"]["method"]
    const element = this

    updateHtml(method, element)
}

async function removeFromCart(e) {
    const productId = this.dataset.id
    
    const response = await deleteData("/cart/delete", {id: productId})

    const method = response["response"]["method"]
    const element = this.closest(".row")

    updateHtml(method, element)
}

// TODO : Handle adding to favorites
// TODO : Handle removing from favorites
