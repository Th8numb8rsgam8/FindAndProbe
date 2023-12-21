(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
		HandleUpdates();
	}, false);


	const HandleUpdates = function()
	{
		const title_names = new Array();
		const titles = document.querySelector("#title_row ul");
		const socket = new WebSocket("ws://192.168.192.131:3000/");
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
			switch (link_data.sender)
			{
				case "Finder":
					for (let [name, value] of Object.entries(link_data))
					{
						if (!title_names.includes(name))
						{
							title_names.push(name);
							const new_column = document.createElement("li");
							new_column.innerHTML = name;
							titles.appendChild(new_column);
						}
					}
					break;
				case "Probe":
					console.log(Object.keys(link_data));
					break;
			}
		});
	}
})();
