var ToC =
  "<nav role='navigation' class='table-of-contents'>" +
    "<h1>Contents</h1>" +
    "<ul>";

var newLine, el, title, link;

$("h2").each(function() {

    el = $(this);
    title = el.text();
    link = "#" + el.attr("id");

    newLine =
    "<li>" +
    "<a href='" + link + "'>" +
    title +
    "</a>" +
    "</li>";

    ToC += newLine;
    console.log(ToC);
    
});

ToC +=
   "</ul>" +
  "</nav>";
$(".to_ToC").prepend(ToC);
