$(document).ready(function(){
    $("ul#txt_menu li a").each(function(i){
      $(this).click(function(){
        $("div.jstab_active").removeClass("jstab_active").addClass("jstab");
        $("div.jstab:eq("+i+")").removeClass("jstab").addClass("jstab_active");
        if(i == 3) {
        $("ul#txt_menu li a.right").removeClass("right")
        $("ul#txt_menu li a").addClass("left");
        $(this).removeClass("right_corner");
        }
        if(i == 0) {
        $("ul#txt_menu li a.left").removeClass("left")
        $("ul#txt_menu li a").addClass("right");
        $(this).removeClass("left_corner");
        }
        $("ul#txt_menu li a:eq("+(i+1)+")").removeClass("left").addClass("right");
        $("ul#txt_menu li a:eq("+(i-1)+")").removeClass("right").addClass("left");
        $("ul#txt_menu li a.active").removeClass("active");
        $(this).removeClass("left").removeClass("right").addClass("active");
          if(!$("ul#txt_menu li a:eq(0)").hasClass("left_corner") && i >0) { 
            $("ul#txt_menu li a:eq(0)").addClass("left_corner");
          }
          if(!$("ul#txt_menu li a:eq(3)").hasClass("right_corner") && i <3) { 
            $("ul#txt_menu li a:eq(3)").addClass("right_corner");
          }
        return false;
        }); 
      }); // eof .each
    
    }); // eof doc. ready ========================
