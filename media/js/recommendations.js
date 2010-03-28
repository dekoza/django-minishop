$(document).ready(function(){

        var SAVE_URL = "/panel/recommendations/category/save/";

        $("div#recommendations").sortable({
          stop: function(e,ui) {
          ui.item.css({'top':'0','left':'0'});
          }
        });

        var products_url = "/panel/ajax/products/category/";
        var recom_url = "/panel/ajax/recommendations/category/";
        $("select[name='category']").change(function(){
                var cat_id = $(this).val();
                clear_msgs();
                $("div#recommendations, div#products_div").append("<div class=\"loading\"></div>");

                $.getJSON(recom_url, {category_id : cat_id}, function(data) {
                        $("div#recommendations div.recommendation, div#no_recom").remove();
                        var amount = 0;
                        $.each(data, function(i, item){
                                create_recommendation(item);
                                amount = i;
                        });
                        if(amount == 0) {
                        $("div#recommendations").append("<div id=\"no_recom\">Brak rekomendacji</div>");
                        }
                        $("div#recommendations div.loading").remove();
                });

                $.getJSON(products_url, {category_id : cat_id}, function(data) {
                        $("table#products tbody").html("");
                        $.each(data, function(i, item){
                                if(find_recommendation(item.pk)) {
                                        $("table#products").append("<tr class=\"off\" title=\""+item.pk+"\"><td>"+item.name+"</td><td>"+item.price+"</td></tr>");
                                } else {
                                        $("table#products").append("<tr title=\""+item.pk+"\"><td>"+item.name+"</td><td>"+item.price+"</td></tr>");
                                }
                        }); // eof data each
                        $("table#products tr").each(function(i) {
                                add_product_events(this);
                        }); // eof table products tr each
                        $("div#products_div div.loading").remove();
                });
                
        }); // eof select

        $("#save_recommendations").dblclick(function(){
                return false;
        }); // eof save_recom dblclick

        $("#save_recommendations").click(function(){
                product_ids = get_recommendations_ids();
                selected_types = get_recommendations_types();
                if (product_ids == "") {
                        product_ids = 'removeall';
                }
                cat_id = $("select[name='category']").val();
                $.getJSON(SAVE_URL, {products:product_ids, category_id:cat_id, types:selected_types}, function(data) {
                        $("span#request_info").html(data);
                });
        });//eof save_recom.. click
        if($("select[name='category']").val() != "") {
                $("select[name='category']").change();
        }

}); // eof doc ready

function get_recommendations_ids() {
        var ids = "";
        $("div.recommendation").each(function(i){
                var pk = $(this).find("input[name='product_id']").val();
                if (!i == 0) { 
                        ids += ","+pk;
                } else {
                        ids += pk;
                }
        }); // eof each
        return ids;
}
function get_recommendations_types() {
        var ids = "";
        $("div.recommendation").each(function(i){
                var pk = $(this).find("select[name='type']").val();
                if (!i == 0) { 
                        ids += ","+pk;
                } else {
                        ids += pk;
                }
        }); // eof each
        return ids;
}

function add_product_events(elem) {
        $(elem).click(function(){
                var data = {
                        'name': $(elem).find("td:first").text(),
                        'product_id': $(elem).attr("title")
                }
                create_recommendation(data);
                $(elem).addClass('off');
                //$(elem).unbind('click');
        });
}

function find_recommendation(id) {
        var is_present = false;
        $("div#recommendations div.recommendation").each(function(i){
                if ( Number($(this).find("input[name='product_id']").val()) == id ) {
                        is_present = true;
                }
        });
        return is_present;
}

function build_type_select(n) {
        var select = "";
        if (n == null) { n = 0; }
        for (o in recommendation_types){
                if(n == o) {
                        select += "<option value=\""+o+"\" selected=\"selected\">"+recommendation_types[o]+"</option>";
                } else {
                        select += "<option value=\""+o+"\">"+recommendation_types[o]+"</option>";
                }
        }
        return select;
}

function create_recommendation(data) {
        clear_msgs();
        $("div#no_recom").remove();
        if (find_recommendation(data.product_id)) {
                return '';
        }
        var r = "";
        r += "<div class=\"recommendation\">";
        r += "<h2>"+data.name+"</h2>";
        r += "<div>";
        r += "<select name=\"type\">";
        r += build_type_select(data.type);
        r += "</select>";
        r += "<input type=\"button\" name=\"remove\" value=\"X\" />";
        r += "<input type=\"hidden\" name=\"product_id\" value=\""+data.product_id+"\" />";
        r += "</div>";
        r += "</div>";
        $("div#recommendations").append(r);
        $("div#recommendations div.recommendation:last input[name='remove']").click(function(){
                remove_recommendation($(this).parent().parent());
        });
}

function remove_recommendation(elem) {
        var product_id = $(elem).find("input[name='product_id']").val();
        $("table#products tr[title='"+product_id+"']").removeClass("off");
        $(elem).remove();
        if($("div.recommendation").length == 0) {
                $("div#recommendations").append("<div id=\"no_recom\">Brak rekomendacji</div>");
        }
}

function clear_msgs() {
        $("span#request_info").html("");
}
