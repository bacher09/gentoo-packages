$('.nav-tabs a').click(function(e){ 
    e.preventDefault();
    var objs = $(this);
    var obj = objs[0],
    real_url = obj.href;
    obj.href = "#" + obj.attributes["tab-id"].value;
    obj.real_url = real_url;
    objs.tab("show");
    obj.href = real_url;
});

$('.nav-tabs a').on("show", function(e){ 
    history.pushState(null, null, e.target.real_url);
});
