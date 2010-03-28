$(document).ready(function() {
    initial = $("a.vote:activevote").length;

    $("a.vote").each(function(i){
      $(this).bind('mouseover.votehiglight',
        function() {
        $("a.vote:activevote").deactivate();
        console.log($("a.vote:activevote"));
        $("a.vote:lt("+(i+1)+")").activate();
        });
      $(this).bind('mouseout.votehiglight',
        function() {
        $("a.vote:activevote").deactivate();
        $("a.vote:lt("+initial+")").activate();
        }
        );
      }); // eof each

    $("a.vote").bind('click.voteclick', function(){
      $("a.vote").unbind('mouseover.votehiglight');
      $("a.vote").unbind('mouseout.votehiglight');
      $("a.vote_pending").show();
      $("a.vote").unbind('click.voteclick');
      $("a.vote").bind('click.alreadyvoted', function(){return false;});
      var url = $(this).attr('href');
      $.ajax({
        type: "POST",
        url: url,
        data: 1,
        success: function(data) {
          data = $.secureEvalJSON(data);
          if(data["success"]){
            var score = data['score'];
            $("a.vote:active").deactivate();
            $("a.vote:lt("+score+")").activate();
            $("a.vote_pending").remove();
          }
        }
        });
      return false;
      });//eof vote click

    }); // eof doc ready

// selector extensions
  $.extend($.expr[':'],{
      activevote: function(a) {
      if($(a).find('img').length > 0){
        var active_img_regexp = /icon_star_active/;
        var img_src = $(a).find('img').attr('src');
        return src_contains(active_img_regexp, img_src);
      } else {
      return false;
      }
      },
      inactivevote: function(a) {
      if($(a).find('img').length > 0){
        var inactive_img_regexp = /icon_star_inactive/;
        var img_src = $(a).find('img').attr('src');
        return src_contains(inactive_img_regexp, img_src);
      } else {
      return false;
      }
      }
    }); // eof jquery extension

// method extensions
$.fn.extend({
    activate: function() {
      var inactive_img_regexp = /icon_star_inactive/;
      var img_src = this.find('img').attr('src');
      if(this.find('img').length > 0 && src_contains(inactive_img_regexp, img_src)){
        inactive_src = img_src.replace('inactive', 'active');
        this.find('img').attr('src', inactive_src);
      }
    },
    deactivate: function() {
      var active_img_regexp = /icon_star_active/;
      var img_src = this.find('img').attr('src');
      if(this.find('img').length > 0 && src_contains(active_img_regexp, img_src)){
        inactive_src = img_src.replace('active', 'inactive');
        this.find('img').attr('src', inactive_src);
      }
    }
    }); // eof fn.extend

// functions

function src_contains(img_regexp, img_src) {
  if(img_src.search(img_regexp) > -1) {
    return true;
  } else { 
    return false; 
  }
}
