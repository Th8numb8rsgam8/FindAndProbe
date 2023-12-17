(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
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
					console.log("FINDER");
					break;
				case "Probe":
					console.log("PROBE");
					break;
			}
		});
	}, false);
})();
