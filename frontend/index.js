(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
		HandleUpdates();
	}, false);


	const HandleUpdates = function()
	{
		const title_names = new Array();
		let row_number = 0;
		// const titles = document.querySelector("#title_row ul");
		const titles = document.getElementById("title_row");
		const data_table = document.getElementById("data");
		const socket = new WebSocket("ws://192.168.192.131:3000/");

		socket.addEventListener("open", function (event)
		{
			socket.send("BROWSER");
		});
		
		socket.addEventListener("close", function (event)
		{
			console.log("CONNECTION CLOSED");
		});

		const check_inclusion = function(included)
		{
			if (!included) {
				// const new_column = document.createElement("li");
				const new_column = document.createElement("th");
				new_column.innerHTML = name;
				new_column.id = name;
				titles.appendChild(new_column);
				const col_width = document.getElementById(name).getBoundingClientRect().width
				title_names.push({"name": name, "col_width": `${col_width}px`});
			}
		}

		socket.addEventListener("message", function (event)
		{
			const link_data = JSON.parse(event.data);
			row_number += 1;
			const data_row = document.createElement("tr");
			data_row.classList.add("row", `row_${row_number}`);
			const data_columns = new Array();
			switch (link_data.sender)
			{
				case "Finder":
					console.log(link_data);
					for (let [name, value] of Object.entries(link_data))
					{
						if (name === "request_headers")
						{
							for (let [sub_name, value] of Object.entries(link_data.name))
							{
								const included = title_names
									.find(item => item.name === `${name} - ${sub_name}`);
								check_inclusion(included);
							}
						}
						else
						{
							const included = title_names.find(item => item.name === name);
							check_inclusion(included);
						}
					}

					title_names.forEach((item) => {
						const data_column = document.createElement("td");
						let col_name = null;
						if (item.name.includes("request_headers"))
						{
							const names = item.name.split(" - ");
							data_column.innerHTML = link_data[names[0]][names[1]];
						}
						else
						{
							data_column.innerHTML = link_data[item.name];
						}
						data_column.classList.add(item.name);
						data_column.style.width = item.col_width;
						// data_column.title = document.getElementById(name).title;
						// data_column.title = title_names.findIndex((el) => el === name);
						// data_columns.push(data_column);
						data_row.appendChild(data_column);
					});
					data_table.appendChild(data_row);
					break;
				case "Probe":
					// console.log(Object.keys(link_data));
					break;
			}
		});
	}
})();
