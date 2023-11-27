(function() {

	"use strict";

	window.addEventListener("DOMContentLoaded", () =>
	{
		const socket = new WebSocket("ws://192.168.192.131:3000/");

		socket.addEventListener("open", function (event)
		{
			socket.send("BROWSER");
		});
		
		// setInterval(() =>
		// {
		// 	socket.send("CONNECTION ESTABLISHED");	

		// }, 1000);
		
		socket.addEventListener("close", function (event)
		{
			console.log("CONNECTION CLOSED");
		});

		socket.addEventListener("message", function (event)
		{
			console.log(JSON.parse(event.data));
		});
	}, false);
})();
