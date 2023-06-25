// - - - - - - - - - - - - - - - - - - - - - - -  DOM manipulation - - - - - - - - - - - - - - - - - - - - - - -

addEventListener("load", (event) => {
  const content = document.getElementById("content")
  const loader = document.getElementById("loader")
  content.removeAttribute("class")
  loader.setAttribute("class", "visually-hidden")
  autoCloseFlashedMessage()
});

$(document).on("click", ".btn-close", closeFlashedMessage);
// - - - - - - - - - - - - - - - - - - - - - - -  Helper functions  - - - - - - - - - - - - - - - - - - - - - - -

function closeFlashedMessage() {
  this.parentElement.remove();
}
 
function autoCloseFlashedMessage() {
  const $message = $(".btn-close")
  setTimeout( ()=> {
    $message.closest(".alert").remove()
  }, 5000)
}

