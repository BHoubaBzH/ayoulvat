// flash message disparait au bout d un certain temps
  $(document).ready(function() {
      // messages timeout for 10 sec 
      setTimeout(function() {
          $('.alert-dismissible').fadeOut('slow');
      }, 4000); // <-- time in milliseconds, 3000 =  3 sec

      // delete message
      $('.del-msg').live('click',function(){
          $('.del-msg').parent().attr('style', 'display:none;');
      })
  });