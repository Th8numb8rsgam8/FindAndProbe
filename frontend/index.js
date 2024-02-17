(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
		$(".close").on("click", function(e) {
			e.preventDefault();
			$(".detail, html, body").toggleClass("open");
		});

		HandleUpdates();
	}, false);


	const HandleUpdates = function()
	{
		// const title_names = new Array();
		const table_titles = [
			"url", "method", "status_code", 
			"reason", "apparent_encoding", "elapsed_time"]

		let row_number = 0;
		// const titles = document.querySelector("#title_row ul");
		const titles = document.getElementById("title_row");
		const data_table = document.getElementById("data");
		const socket = new WebSocket("ws://192.168.192.131:3000/");

		table_titles.forEach((name) =>
		{
			const new_column = document.createElement("th");
			new_column.innerHTML = name;
			new_column.id = name;
			titles.appendChild(new_column);
		});

		socket.addEventListener("open", function (event)
		{
			socket.send("BROWSER");
		});
		
		socket.addEventListener("close", function (event)
		{
			console.log("CONNECTION CLOSED");
		});

		socket.addEventListener("message", function (event)
		{
			const link_data = JSON.parse(event.data);
			row_number += 1;
			const data_row = document.createElement("tr");
			data_row.classList.add("row", `row_${row_number}`);
			switch (link_data.sender)
			{
				case "Finder":
					table_titles.forEach((name) =>
					{
						const data_column = document.createElement("td");
						data_column.innerHTML = link_data[name];
						data_column.classList.add(name, `row_${row_number}`);
						data_row.appendChild(data_column);
					});
					const data_column = document.createElement("td");
					const select_btn = document.createElement("a");
					data_column.classList.add("select", `row_${row_number}`);
					select_btn.classList.add("button", `row_${row_number}`);
					select_btn.innerHTML = "Select";
					data_column.appendChild(select_btn);
					data_row.appendChild(data_column);
					data_table.appendChild(data_row);
					$(`.button.row_${row_number}`).on("click", function(e) {
						e.preventDefault();
						$(".detail, html, body").toggleClass("open");
					});
					break;
				case "Probe":
					// console.log(Object.keys(link_data));
					break;
			}
		});
	}
})();
