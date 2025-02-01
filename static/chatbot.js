console.log("Chatbot init...");

window.addEventListener("load", () => {
	window.chatbot = {
		eventSource: null,
		key: null,
	}

	// Handles form for sending questions to SSE/Chatbot server.
	const userPromptElement = document.querySelector("textarea.user-prompt"); 
	const systemPromptElement = document.querySelector("textarea.system-prompt"); 
	const sendMessageElement = document.querySelector("button.send"); 
	const sendMessageOriginalText = sendMessageElement.textContent;

	// Connect to SSE server.
	window.chatbot.eventSource = new EventSource("/chat/stream");
	console.table(window.chatbot.eventSource);

	// Listen for "key" event from SSE server.
	// This gets returned as soon as connection is extablished
	// and contains a verification key.
	window.chatbot.eventSource.addEventListener("key", (event) => {
		window.chatbot.key = event.data;
		console.log(`Verification key: ${event.data}`);
	});

	// Listen for "message" event from SSE server.
	// This will contain responses to questions asked.
	const responsesElement = document.querySelector("section.responses"); 
	window.chatbot.eventSource.addEventListener("message", (event) => {
		try {
			const decodedEvent = JSON.parse(event.data);
			console.log(decodedEvent);

			const responseItem = document.createElement("div");
			responseItem.classList.add("border", "p-2");

			const question = document.createElement("h4");
			question.classList.add("font-bold");
			question.innerText = decodedEvent.user_prompt.trim();
			responseItem.appendChild(question);

			const answer = document.createElement("div");
			answer.innerText = decodedEvent.answer.trim();
			responseItem.appendChild(answer);

			responsesElement.insertBefore(responseItem, responsesElement.firstChild);

			// Reset send button.
			sendMessageElement.textContent = sendMessageOriginalText;
			sendMessageElement.disabled = false;
		} catch (err){
			console.error(err);
		}
	});

	if (userPromptElement && systemPromptElement && sendMessageElement) {
		if (localStorage.getItem("user-prompt")) {
			userPromptElement.value = localStorage.getItem("user-prompt");
		}

		if (localStorage.getItem("system-prompt")) {
			systemPromptElement.value = localStorage.getItem("system-prompt");
		}

		sendMessageElement.addEventListener("click", async () => {
			sendMessageElement.textContent = "Waiting for response...";
			sendMessageElement.disabled = true;

			localStorage.setItem("user-prompt", userPromptElement.value.trim());
			localStorage.setItem("system-prompt", systemPromptElement.value.trim());
			
			setTimeout(async () => {
				const response = await fetch("/chat/ask", {
					method: "POST",
					headers: { "Content-Type": "application/json", "X-Key": window.chatbot.key },
					body: JSON.stringify({
						user_prompt: userPromptElement.value,
						system_prompt: systemPromptElement.value,
					}),
				});

				if (response.status != 201) {
					alert("Something went wrong!");
				}
			}, 100);
		});
	}
});
