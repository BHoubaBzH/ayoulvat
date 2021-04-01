/*
    dans le groupe id="liste_creneaux" , met le fond de la case selectionnée en couleur


$(document).ready(function(){
    console.log('ready');
    $('#liste_creneaux button').click(function(e) {
        e.preventDefault();
        $that = $(this);
        // supprime les class active des boutons sous "ul > il" référents de that
        $that.closest("ul").find('il').find('button').removeClass('active');
        // set class active sur le bouton en cours : that
        $that.addClass('active');
    });
});
*/
