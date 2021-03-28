/*
    dans le groupe id="liste_creneaux" , met le fond de la case selectionnée en couleur
*/

$(document).ready(function(){
    console.log('ready');
    $('#liste_creneaux button').click(function(e) {
        e.preventDefault();
        $that = $(this);
        $that.closest("ul").find('il').find('button').removeClass('active');
        $that.addClass('active');
    });
});
