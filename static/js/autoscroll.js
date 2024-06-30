function animatethis(targetElement, speed) {
  var scrollWidth = $(targetElement).get(0).scrollWidth;
  var clientWidth = $(targetElement).get(0).clientWidth;
  $(targetElement).animate({ scrollLeft: scrollWidth - clientWidth },
  {
      duration: speed,
      complete: function () {
          targetElement.animate({ scrollLeft: 0 },
          {
              duration: speed,
              complete: function () {
                  animatethis(targetElement, speed);
              }
          });
      }
  });
};
animatethis($('.autoscroll'), 10000);

$('.autoscroll').hover(function(){
  $(this).stop(); //Stop the animation when mouse in
},
function(){
  animatethis($('.autoscroll'), 10000);; //Start the animation when mouse out
});