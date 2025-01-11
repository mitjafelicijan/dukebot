# Chatbot server

This server handles chatbot interactions, managing conversations and
collecting statistics for performance analysis.

## Local development

### Install Ollama and run Mistral model

```sh
curl -fsSL https://ollama.com/install.sh | sh
```

You can check which models are running by `ollama list`.

To install new model you do `ollama pull mistral`. Check for all the
available models on https://ollama.com/library.

Make sure you also change `OLLAMA_MODEL` variable in `config.py` to also
use that model in the chatbot.

### Provision and run server

```sh
python3 -m venv .venv
source .venv/bin/activate

pip install fastapi "uvicorn[standard]" jinja2 asyncio llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
```

Then run `make dev`. Make sure Ollama is running and Mistral model is
running as well.

### Support utility

With repo comes a helper CLI utility `wrench.py` that has couple of
options to index etc. New things will be added to this.

> You will still need to go through Provision part of this tutorial and
> install all dependencies.

```sh
# Let's assume you have activated virtual environment with `source .venv/bin/activate`.
python3 wrench.py -h
```

You should see this output.

```text
usage: wrench.py [-h] [--index]

CLI utility that helps setting up of LLM indexes, storages etc.

options:
  -h, --help  show this help message and exit
  --index     indexes local storage and saves vector index to local folder
```

## Example of chatbot frontend

Example of the chatbot frontend is located in [demo](./demo) folder. The
chatbot uses server push with Server0sent events to make things a
little easier.

Check `demo/chatbot.js` for implementation details.
