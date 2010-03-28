$(document).ready(function(){
    fancybox_config = {
    'overlayShow' : false,
    'zoomSpeedIn' : 600,
    'zoomSpeedOut' : 500,
    'easingIn' : 'easeOutBack',
    'easingOut' : 'easeInBack'
    }
    fancybox_config_cert = {
    'overlayShow' : false,
    'zoomSpeedIn' : 0,
    'zoomSpeedOut' : 0,
    'frameHeight': 300
    //'easingIn' : 'easeOutSine',
    //'easingOut' : 'easeInCubic'
    }
    $("a.cert").fancybox(fancybox_config_cert);
    $("#main_photo_container").css("background", "url(/media/gfx/ajax-loader.gif) center center no-repeat");
    $("#main_photo_link").fancybox(fancybox_config);
    
    $("a.thumb_link").click(function(){
      $main_photo = $("#main_photo");
      $main_photo_link = $("#main_photo_link");
      var url = $(this).attr("href");
      var fullsize_url = $(this).attr("rel");
      var title = $(this).attr("title");
      var main_url = $main_photo.attr("src");
      if (url != main_url) {
        //console.log(url);
        $main_photo.fadeOut("fast", function(){
          $main_photo.attr("src", url).fadeIn("fast");
          $main_photo_link.attr("href", fullsize_url);
          $main_photo_link.attr("title", title);
          $("#main_photo_link").fancybox(fancybox_config);
        }); // eof fadeOut callback
        $("a.thumb_link.active").removeClass("active");
        $(this).addClass("active");
        
      }
      return false;
      });
    
    }); // eof doc ready
