$(document).ready(function() {

  $("#top_menu ul.top_menu > li:last > a").addClass("right_corner");

  $("#top_menu ul.top_menu > li > a").each(function(){
    var content = $(this).html();
    content = content.replace("»","");
    $(this).html(content);
    });

  $("#top_menu ul.top_menu > li > ul").each(function(){
    $(this).find("> li:last").addClass("last");
    $(this).append('<li class="rounded_corners">&nbsp;</li>');
  });

  $("#top_menu ul.top_menu > li > ul > li > ul").each(function(){
    $(this).find("> li:last").addClass("last");
    $(this).prepend('<li class="rounded_corners_top">&nbsp;</li>');
    $(this).append('<li class="rounded_corners">&nbsp;</li>');
  });



    if($.browser.msie) {

		$("#top_menu ul.top_menu > li").hover(
			function() {
				$(this).find("> ul").css("left", "0px");
				$(this).css("z-index", "1003");
			},
			
			function() {
				$(this).find("> ul").css("left", "-9999em");
				$(this).css("z-index", "1000");
			});

      $("#top_menu ul.top_menu > li > ul > li > ul").parent("li").hover(
      function() {
      $(this).find("> ul").css("top", "0px");
      $(this).find("> ul").css("left", "208px");
      },
      function() {
      $(this).find("> ul").css("left", "-9999em");
      });
    } // end of if :>

    $("select#manufacturer_widget").change(function(){
        var url = $(this).find("option:selected").val();  
        if(url != 0){
        window.location = url;
        }
        }); // eof manufacturer widget

    $("form.formular input[type='text'],form.formular input[type='password']").addClass('text');
    $("form.formular input[type='button'],form.formular input[type='submit']").addClass('submit');

    var pages = $("ul.pages:first li").length;
    var pagin_width = (28*pages)+72;
    $("div.pages").css("width", pagin_width+"px");

	}); // eof doc. ready

jQuery.fn.shake = function(times, amount){
  this.each(function(){
      for (var x = 1; x <= times; x++){
        $(this)
        .animate({ marginLeft: -amount },10)
        .animate({ marginLeft: 0 },50)
        .animate({ marginLeft: amount },10)
        .animate({ marginLeft: 0 },50);
      }
  });
  return this;
}

