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

