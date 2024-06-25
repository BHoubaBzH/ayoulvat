$(document).ready(function() {
  
    var scrollHandler = null;
    
    function autoScroll () {
      clearInterval(scrollHandler);
      scrollHandler = setInterval(function() {
        /*var nextScroll = $('.autoscroll').scrollTop() + 20;*/
        /*$('.autoscroll').scrollTop(nextScroll);*/
        var nextScroll2 = $('.autoscroll').scrollLeft() + 10;
        $('.autoscroll').scrollLeft(nextScroll2);
      },2000);
    }
    
     $('.autoscroll').scroll(function() {
      // Stop interval after user scrolls
      clearInterval(scrollHandler);
      // Wait 2 seconds and then start auto scroll again
      // Or comment out this line if you don't want to autoscroll after the user has scrolled once
      //setTimeout(autoScroll, 200);
     });
     
     autoScroll();
  });