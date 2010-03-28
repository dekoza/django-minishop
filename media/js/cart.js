$(document).ready(function() {

    $("input[type='radio'][name='payment'], input[type='radio'][name='shipment']").bind("click.submission", function(){
      if($("input[type='radio'][name='payment']:checked").length > 0 && $("input[type='radio'][name='shipment']:checked").length > 0) {
        $("form#shipment_payment_form").submit();
      }
      });

    $("input#submit_order").dblclick(function() { return false; });

    }); // eof doc ready
