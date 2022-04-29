// afficher un loader pendant que le client attend un retour du serveur
// utile dans la sidebar dans l evenement
function loader() {
    var x = document.getElementById("loader");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }