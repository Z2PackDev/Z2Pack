var ToC =
  "<nav role='navigation' class='table-of-contents'>" +
    "<h1>Contents</h1>" +
    "<ul>";

var newLine, el, title, link;

var ul_open = false;

$("h1,h2").each(function() {

    el = $(this);
    title = el.text();
    if(el.attr("id") != 'dismiss') {
        if(el.is('h1')) {
            link = "#" + el.attr("id");
            
            newLine = "";
            if(ul_open) {
                newLine += "</ul> </li>";
            }
            newLine +=
            "<li>" +
            "<a href='" + link + "'>" +
            title +
            "</a>" +
            "<ul>";
            ul_open = true;
            ToC += newLine;
        }
        else {
            link = "#" + el.attr("id");

            newLine =
            "<li>" +
            "<a href='" + link + "'>" +
            title +
            "</a>" +
            "</li>";

            ToC += newLine;
            
        }
        
        
    }
});

ToC +=
   "</li> </ul> </ul>" +
  "</nav>";
$(".to_ToC").prepend(ToC);
