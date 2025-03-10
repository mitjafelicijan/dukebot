# Duke Chatbot Server & Utilities

Specialized World of Warcraft bot using GPT LLM via RAG. This prioritizes
locally indexed data instead of LLM general knowledge.

> [!NOTE]
> Current system prompt used is in [system_prompt.txt](./system_prompt.txt)
> which should be updated as we move along with testing. Use this prompt in the
> chat UI for testing and tweaking responses.

## Requirements

- Python 3.10+
- Pip 24.0+
- Lua 5.4+ (only for development)
- GNU Make 4.4+ (only for development)

## Local development

> [!IMPORTANT]
> This requires OpenAI API access and account. So make sure you have an account
> and some money deposited for testing. You will also need to create API
> credentials in OpenAI Dashboard.

```sh
# Create virtual environment.
python3 -m venv .venv

# Activate environment.
source .venv/bin/activate

# Install dependencies manually (preferred).
pip install python-dotenv fastapi "uvicorn[standard]" jinja2 asyncio \
    llama-index llama-index-llms-openai llama-index-embeddings-huggingface \
    pandas markdownify

# Install dependencies with requirements.txt (not preferred since this implies
# host machine has Nvidia GPU).
pip install -r requirements.txt

# Prepare environmental file.
cp .env.sample .env

# Edit `.env` file and fill missing information.
vim .env

# Reindex and create new vector database (not needed if nothing changed in
# corpus data).
make index

# Run development server (on port 6969).
make dev

# Run normal server
make server
# or
uvicorn main:app --port 6969 --workers 6
```

Open browser http://localhost:6969/chat.

## Data importing

All the final data that is used in indexing by RAF is located in `corpus`
directory. However this data needs to be first exported from other sources like
pfQuest and other sources like Wowhead comments.

All scripts that generate corpus data are located in `importer` directory.

- `warcrafttavern.py` - fetches data from Warcraft Tavern and generates
  markdown files from list of links defined `warcrafttavern.csv`.
- `quests.lua` - takes pfQuest data and generates markdown files of quests.
- `quests-comments.py` - takes `comments.csv` and appends all valid comments to
  quest data. Comment data is provided by web scraper written by
  [kakexd](https://github.com/kakexd/webscrape).

> [!NOTE]
> Do not execute this scripts unnecessarily. These should only be ran after new
> content is being added. Also do not change corpus data.

### Support utility

With repo comes a helper CLI utility `wrench.py` that has couple of
options to index etc. New things will be added to this.

> [!NOTE]
> You will still need to go through Local development part of this readme file
> and install all dependencies.

```sh
# Let's assume you have activated virtual environment with
# `source .venv/bin/activate`.
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

## Corpus data sources

- pfQuest and pfQuest-turtle addon for quests
- wowhead.com for quest comments
- warcrafttavern.com for professions, dungeons, general
- turtle-wow.fandom.com and forum.turtle-wow.org for custom Turtle data

