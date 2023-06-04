$( ".add-to-cart" ).on( "submit" , addToCart )
$( ".remove-from-cart" ).on( "click", removeFromCart )

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
    console.log(`Clicked ${this.dataset.id}!`)
    const productId = this.dataset.id

    const response = await postData(`/cart`, {id: productId})

    console.log(response)
}

async function removeFromCart(e) {
    console.log(`Clicked ${this.dataset.id}`)
    const productId = this.dataset.id
    
    const response = await deleteData("/cart/delete", {id: productId})

    console.log(response)
}

// TODO : Handle adding to favorites
// TODO : Handle removing from favorites
