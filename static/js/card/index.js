	function loadCards(searchTerm = "") {
		$.post(".", { searchTerm: searchTerm}).done(function(data) {
			$('#resultsHolder').empty();
			var parsed = JSON.parse(data);
			//console.log(parsed);
			for (var i = 0; i < parsed.length; i++) {
				var markup = "<tr role='row'><td class='col-md-3'><a href='"+parsed[i][2]+"'><h3>"+parsed[i][0]+"</h3></a></td><td class='col-md-6'>"+parsed[i][1]+"</td><td class='col-md-3'>"+parsed[i][3]+"</td></tr>";
				$('#resultsHolder').append(markup);
			}
			$('table').tablesorter();
			$('table').trigger("update");
		});
	}
	$(document).ready(function() {
		loadCards("");
		$('#nameSearchInput').keyup(function(event) {
			if (event.keyCode == 13) {
				loadCards($('#nameSearchInput').val());
			}
		});
	});
