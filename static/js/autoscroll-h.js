var targetElement = $('.autoscroll-h')
var scrollWidth = $(targetElement).get(0).scrollWidth;
var clientWidth = $(targetElement).get(0).clientWidth;
var hiddenPartWidth = scrollWidth - clientWidth;
var seuil = 200; // si partie cachée est plus petite que seuil (px), alors ne fait rien

//if (200 < hiddenPartWidth < 1000) {var speed = hiddenPartWidth * 10}
//else if (hiddenPartWidth < 5000) {var speed = hiddenPartWidth * 5}
//else {var speed = hiddenPartWidth * 10};
var speed = 10000;

if (hiddenPartWidth > seuil) {
  function animatethis(target, speed, scrollWidth, clientWidth) {
    $(targetElement).animate({ scrollLeft: scrollWidth - clientWidth },
    {
        duration: speed,
        complete: function () {
            target.animate({ scrollLeft: 0 },
            //{
            //    duration: speed,
            //    complete: function () {
            //        animatethis(target, speed, scrollWidth, clientWidth);
            //    }
            //}
          );
        }
    });
  };

  animatethis($(targetElement), speed, scrollWidth, clientWidth);

  $(targetElement).hover(function(){
    //Stop the animation when mouse in
    $(this).stop();
  },
  function(){
    //Start the animation when mouse out
    //animatethis($(targetElement), speed, scrollWidth, clientWidth);; 
  });
};
