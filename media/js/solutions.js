$(document).ready(function() {
    $("ul#menu_right > li > a").addClass("brown");

    $("ul#menu_right > li > ul").hide();
    $("ul#menu_right > li > a").click(function(){
      $(this).siblings("ul").slideToggle("fast"); 
      if($(this).siblings("ul").length > 0) {
      return false;
      } else {
      return true;
      }
      });// eof click

    }); // eof doc. ready
