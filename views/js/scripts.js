function reload() {
    $("#progressModal").modal("show");

    // Open a WebSocket connection to the Python Bottle app
    var loc = window.location.href;
    var hostname = $.url(loc).attr("host");
    var port = $.url(loc).attr("port");
    var ws_url = "ws://" + hostname + ":" + port + "/ws"
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

            $("#progressModal").modal("hide");
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
    if (!this.asc) {
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

function addToCrap(url) {
  $.ajax({
    type: "GET",
    url: "/addcrap/" + url,
    success: function(response) {
      $('#help-filter-text').text(response.url);
      $('#filter-text').val(response.filter);
      $('#filterModal').modal('show');
    },
    error: function() {
      alert("Error sending backend request");
    }
  });
}

function editCrap(url) {
  $.ajax({
    type: "GET",
    url: "/editcrap",
    success: function(response) {
      $('#filter-text').val(response.filter);
      $('#filterModal').modal('show');
    },
    error: function() {
      alert("Error sending backend request");
    }
  });
}

function saveCrap() {
  var crapFilter = { filter: $("#filter-text").val() };
  $.ajax({
    type: "POST",
    url: "/savecrap",
    data: crapFilter,
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(response) {
      $('#filterModal').modal('hide');
      const toast = new bootstrap.Toast($('#saveToast'));
      toast.show();
    },
    error: function(xhr, status, error) {
      console.error("Error: " + error.message + " status: " + status); // Log error message
    }
  });
}

function generateUUID() {
  $.ajax({
    type: "GET",
    url: "/getuuid",
    success: function(response) {
      $('#filter-text').val(response.filter);
      $('#uuid').val(response.uuid);
      $('#uuidModal').modal('show');
    },
    error: function() {
      alert("Error sending backend request");
    }
  });
}

function saveUUIDandFilter() {
  var this_uuid = $('#uuid').val();
  var crapFilter = {uuid: this_uuid, filter: $("#filter-text").val()};
  $.ajax({
    type: "POST",
    url: "/newuuid",
    data: crapFilter,
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(response) {
      console.log(response);
      $('#uuidModal').modal('hide');
      window.location.href = "./?uuid=" + this_uuid;
    },
    error: function(xhr, status, error) {
      console.error("Error: " + error.message + " status: " + status); // Log error message
    }
  });
}

function showWhy(crapIndex) {
  $.ajax({
      url: '/showwhy',
      type: 'POST',
      data: {'id': crapIndex},
      success: function(response) {
          // Replace the span element with the response
          $(this).replaceWith(response.why);
      }.bind(this),
      error: function(xhr, status, error) {
          console.log("Error:", error);
      }
  });
}
