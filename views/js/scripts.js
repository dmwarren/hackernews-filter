function reload() {
    // Open a WebSocket connection to the Python Bottle app
    var loc = window.location.href;
    var hostname = $.url(loc).attr("host");
    var port = $.url(loc).attr("port");

    $.ajax({
      url: "/check_login_status",
      type: "GET",
      success: function(response) {
        if (response.logged_in) {
          $("#login-btn").text(response.email);
          $("#login-btn").removeAttr("onclick");
          $("#login-btn").attr("onclick", "doLogout()");
        } else {
        }
      },
      error: function(xhr, status, error) {
          console.log("Error:", error);
      }
    });

    var numPages = $("#num-pages").val();
    var ws_url = "ws://" + hostname + ":" + port + "/ws/" + numPages;

    var socket = new WebSocket(ws_url);
    console.log("WebSocket connection opened: " + ws_url);

    // Compile the Handlebars templates
    var progressTemplate = _.template($("#progress-template").html());
    var goodDataTemplate = _.template($("#good-data-template").html());
    var infoTemplate = _.template($("#info-template").html());
    var crapDataTemplate = _.template($("#crap-data-template").html());

    // Handle incoming messages from the WebSocket
    socket.onmessage = function(event) {
        var message = JSON.parse(event.data);
        console.log("Received message: ", message);
        if (message.type == "progress") {
            // If the message is a progress update, render the progress template
            console.log("Updating progress bar.");
            var progress = message.data;
            var progressHtml = _.template($('#progress-template').html())({progress: progress});
            $('.progress-bar').remove();
            $('.progress').append(progressHtml);
            $(".progress").removeClass("invisible");
        } else if (message.type == "data") {
            // If the message is data, render the data template
            console.log("Updating data.");
            var goodLenHtml = infoTemplate({ info: message.data.gl });
            $("#good-len").html(goodLenHtml);
            var crapLenHtml = infoTemplate({ info: message.data.cl });
            $("#crap-len").html(crapLenHtml);
            var dataHtml = goodDataTemplate({ stories: message.data.good});
            $("#good-table tbody").html(dataHtml);

            var dataHtml = crapDataTemplate({ stories: message.data.crap});
            $("#crap-table tbody").html(dataHtml);

            $(".progress").addClass("invisible");
        }
    };
            // Handle WebSocket connection errors
    socket.onerror = function(error) {
        console.log("WebSocket connection error: ", error);
    };

    // Handle WebSocket connection close
    socket.onclose = function(event) {
        console.log("WebSocket connection closed with code " + event.code + " and reason " + event.reason);
    };
    $("#reload-btn").click(function() {
        reload();
    });
}

function setupTableSort(id) {
    $("#" + id).on("click", "th", function() {
    var table = $(this).parents("table").eq(0);
    var rows = table.find("tr:gt(0)").toArray().sort(compare($(this).index()));
    this.asc = !this.asc;
    if (this.asc) {
      rows = rows.reverse();
    }
    for (var i = 0; i < rows.length; i++) {
      table.append(rows[i]);
    }
    });
}

function compare(index) {
  return function(a, b) {
    var valA = getCellValue(a, index);
    var valB = getCellValue(b, index);
    return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB);
  };
}

function getCellValue(row, index) {
  return $(row).children("td").eq(index).text();
}

function editCrap(url) {
  $.ajax({
    type: "GET",
    url: "/editcrap",
    success: function(response) {
      if (typeof url === 'undefined') {
      } else {
        $("#urlhelp").text(url);
        $("#urlhelp").show();
      }
      $('#filter-text').val(response.filter);
      $('#filterModal').modal('show');
    },
    error: function() {
      alert("Error sending backend request");
    }
  });
}

function saveCrap() {
  var crapFilter = { filter_lines: $("#filter-text").val() };
  $.ajax({
    type: "POST",
    url: "/savecrap",
    data: crapFilter,
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(response) {
      $('#filterModal').modal('hide');
      const toast = new bootstrap.Toast($('#saveToast'));
      $("#toast-text").text("New filter was saved");
      toast.show();
      reload();
    },
    error: function(xhr, status, error) {
      console.error("Error: " + error.message + " status: " + status); // Log error message
    }
  });
}

function showWhy(s_descr, s_url, icon) {
  var payload = { story: decodeString(s_descr), url: s_url};
  $.ajax({
    url: '/showwhy',
    type: 'POST',
    data: payload,
    dataType: "json",
    success: function(response) {
        // Replace the span element with the response
        var why = document.createElement("span");
        why.textContent = response.why;
        why.classList.add("badge", "text-bg-warning");
        $(icon).replaceWith(why);
    },
    error: function(xhr, status, error) {
        console.log("Error:", error);
    }
  });
}

function editFilter() {
  $.ajax({
    url: "/check_login_status",
    type: "GET",
    success: function(response) {
      console.log(response.logged_in);
      if (response.logged_in) {
        editCrap();
      } else {
        $("#loginModal").modal("show");
      }
    },
    error: function(xhr, status, error) {
        console.log("Error:", error);
    }
  })
}

function registerForm() {
  $("#repeat-password").show();
  $("#register-btn").hide();
  $("#form-login-btn").text("Register");
  $("#loginModalLabel").text("Register");
  $("#form-login-btn").attr("onclick", "register()");
  $("#inputPassword").off("keyup").on("keyup", matchPasswords);
  $("#repeatPassword").off("keyup").on("keyup", matchPasswords);
}

function register() {
  var email = $("#inputEmail").val();
  var password = $("#inputPassword").val();
  $.ajax({
    type: "POST",
    url: "/register",
    data: {email: email, pass: password},
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(response) {
      console.log(response);
      $('#loginModal').modal("hide");
      editCrap();
    },
    error: function(xhr, status, error) {
      console.error("Error: " + error.message + " status: " + status); // Log error message
    }
  });
}

function login() {
  var email = $("#inputEmail").val();
  var password = $("#inputPassword").val();
  $.ajax({
    type: "POST",
    url: "/login",
    data: {email: email, pass: password},
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(response) {
      if (response.success) {
        $('#loginModal').modal("hide");
        // load edit filter here
        $("#login-btn").text(email);
        $("#login-btn").removeAttr("onclick");
        $("#login-btn").attr("onclick", "doLogout()");
        const toast = new bootstrap.Toast($('#saveToast'));
        $("#toast-text").text(email + " logged in");
        toast.show();
        editCrap();
      } else {
        // show warning
        $("#loginAlert").show();
        console.log("User not found or wrong password")
      }
    },
    error: function(xhr, status, error) {
      console.error("Error: " + error.message + " status: " + status); // Log error message
    }
  });
}

function matchPasswords() {
  var password = $("#inputPassword").val();
  var repeat = $("#repeatPassword").val();
  if (password == repeat) {
    $("#inputPasswordm #repeatPassword").removeClass("is-invalid");
    $("#login-btn").prop("disabled", false);
  } else {
    $("#inputPasswordm #repeatPassword").addClass("is-invalid");
    $("#login-btn").prop("disabled", true);
  }
}

function encodeString(foo) {
  const encoder = new TextEncoder();
  const encodedData = encoder.encode(foo);
  return btoa(String.fromCharCode.apply(null, encodedData));
}

function decodeString(foo) {
  const decodedData = atob(foo);
  const decoder = new TextDecoder();
  return decoder.decode(new Uint8Array(decodedData.split('').map(c => c.charCodeAt(0))));
}

function doLogout() {
    $.ajax({
      url: "/logout",
      type: "GET",
      success: function(response) {
        if (!response.logged_in) {
          $("#login-btn").text("Login");
          $("#login-btn").removeAttr("onclick");
          $("#login-btn").attr("onclick", "doLogin()");
          const toast = new bootstrap.Toast($('#saveToast'));
          $("#toast-text").text("Logged out");
          toast.show();
        }
      },
      error: function(xhr, status, error) {
          console.log("Error:", error);
      }
    });

}

function doLogin() {
  $("#loginModal").modal("show");
}
