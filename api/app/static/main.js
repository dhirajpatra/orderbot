
$( document ).ready(function() {
    console.log( "ready!" );

    $("#btnregister").click(function(){
        if ($("input#password").val() != $("input#password_confirm").val()) {
            alert('Password and password confirm must be same!');
            return false;
        }
    });

    $(".btn-primary").click(function() {
        if (confirm('Are you sure?')) {
          var url = $(this).attr('href');
          $('#content').load(url);
        }
      });

      $('.hideshow').on('click', function(event) {  
        $('.add_more').toggle('show');
    });

    function getBotResponse() {
      var rawText = $("#textInput").val();
      var userHtml = '<p class="userText"><span>' + rawText + '</span></p>';
      $("#textInput").val("");
      $("#chatbox").append(userHtml);
      document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
      $.get("/get", { msg: rawText }).done(function(data) {
        var botHtml = '<p class="botText"><span>' + data + '</span></p>';
        $("#chatbox").append(botHtml);
        document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
      });
    }
    $("#textInput").keypress(function(e) {
        if ((e.which == 13) && document.getElementById("textInput").value != "" ){
            getBotResponse();
        }
    });
    $("#buttonInput").click(function() {
        if (document.getElementById("textInput").value != "") {
            getBotResponse();
        }
    })
});