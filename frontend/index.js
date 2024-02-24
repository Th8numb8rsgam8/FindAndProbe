(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
		$(".close").on("click", function(e) {
			e.preventDefault();
			$("#detail, html, body").toggleClass("open");
		});

		HandleUpdates();
	}, false);


	const HandleUpdates = function()
	{
		const table_titles = [
			"url", "method", "status_code", 
			"reason", "apparent_encoding", "elapsed_time"]

		let row_number = 0;
		const titles = document.getElementById("title_row");
		const data_table = document.getElementById("data");
		const detail_container = document.getElementById("detail-container");
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
			console.log("OPENED");
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
			data_row.classList.add("row", `row_${row_number}`, link_data["url"]);
			switch (link_data.sender)
			{
				case "Finder":
					console.log("LINK");

					// Add target endpoint values to main table
					table_titles.forEach((name) =>
					{
						const data_column = document.createElement("td");
						data_column.classList.add(name, `row_${row_number}`);
						if (name === "url")
						{
							const a = document.createElement("a");
							a.innerHTML = link_data[name];
							a.setAttribute("href", link_data[name]);
							a.setAttribute("target", "_blank");
							data_column.appendChild(a);
						}
						else
						{
							data_column.innerHTML = link_data[name];
						}
						data_row.appendChild(data_column);
					});

					const detail_content = document.createElement("dl");
					detail_content.classList.add(`row_${row_number}`, link_data["url"]);

					["request_headers", "response_headers"].forEach((hdr) =>
					{
						for (const [key, val] of Object.entries(link_data[hdr]))
						{
							const detail_name = document.createElement("dt");
							const detail_value = document.createElement("dd");
							detail_name.innerHTML = key;
							detail_value.innerHTML = val;
							detail_content.appendChild(detail_name);
							detail_content.appendChild(detail_value);
						}
					});

					link_data["cookies"].forEach((component) => {
						for ([key, val] of Object.entries(component))
						{
							const detail_name = document.createElement("dt");
							const detail_value = document.createElement("dd");
							detail_name.innerHTML = key;
							detail_value.innerHTML = val;
							detail_content.appendChild(detail_name);
							detail_content.appendChild(detail_value);
						}
					});
					detail_container.appendChild(detail_content);

					// Add "Select" button
					const data_column = document.createElement("td");
					const select_btn = document.createElement("a");
					data_column.classList.add("select", `row_${row_number}`);
					select_btn.classList.add("button", `row_${row_number}`);
					select_btn.innerHTML = "Select";
					data_column.appendChild(select_btn);
					data_row.appendChild(data_column);
					data_table.appendChild(data_row);

					selectListener(row_number);
					break;
				case "Probe":
					// console.log(Object.keys(link_data));
					break;
			}
		});
	}

	const selectListener = function(row_number)
	{
		$(`.button.row_${row_number}`).on("click", function(e) {
			e.preventDefault();
			const detail_pages = document.querySelectorAll("#detail-container dl.open");
			detail_pages.forEach((page) =>
			{
				page.classList.remove("open");
			});
			document
				.querySelector(`#detail-container dl.row_${row_number}`)
				.classList.add("open");
			$(`#detail, html, body`).toggleClass("open");
		});
	}
})();
