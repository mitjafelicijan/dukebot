console.log("Chatbot init...");

window.addEventListener("load", () => {
  window.chatbot = {
    eventSource: null,
    key: null,
  }
  
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

      const question = document.createElement("h4");
      question.innerText = decodedEvent.question.trim();
      responseItem.appendChild(question);

      const answer = document.createElement("div");
      answer.innerText = decodedEvent.answer.trim();
      responseItem.appendChild(answer);

      responsesElement.insertBefore(responseItem, responsesElement.firstChild);
    } catch (err){
      console.error(err);
    }
  });

  // Handles form for sending questions to SSE/Chatbot server.
  const questionElement = document.querySelector("textarea.question"); 
  const sendMessageElement = document.querySelector("button.send"); 

  if (questionElement && sendMessageElement) {
    sendMessageElement.addEventListener("click", async () => {
      const data = new FormData();
      data.append("question", questionElement.value);
      
      const response = await fetch("/chat/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Key": window.chatbot.key },
        body: JSON.stringify({ question: questionElement.value }),
      });

      if (response.status != 201) {
        alert("Something went wrong!");
      }
    });
  }
});
