import os
import sys
import logging
import sqlite3
import datetime

from dotenv import load_dotenv
load_dotenv()
OPENAI_APIKEY = os.environ["OPENAI_APIKEY"]
OPENAI_MODEL = os.environ["OPENAI_MODEL"]
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
MAX_QUEUE_CAPACITY = int(os.environ["MAX_QUEUE_CAPACITY"])
CORPUS_DIR = os.environ["CORPUS_DIR"]
STORAGE_DIR = os.environ["STORAGE_DIR"]
LOGS_DATABASE = os.environ["LOGS_DATABASE"]

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

import filters
import default
import healhcheck
import statistics
import chat

# Set up logging format.
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL, api_key=OPENAI_APIKEY)

# Indexes the current corpus or loads existing one.
local_index = None
if not os.path.exists(STORAGE_DIR):
    logging.critical("Index does not exist")
    sys.exit(1)
else:
    logging.info("Loading locally stored context")
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
    local_index = load_index_from_storage(storage_context, embed_model=embed_model)

# Final check if the corpus was indexed.
if local_index is None:
    logging.error("Loaded index is not valid")
    sys.exit(1)

# Creates a FastAPI app and continues.
app = FastAPI(
    title="Duke Bot",
    version="0.1",
    description="Texas Knighs WoW Chatbot",
)

# Creates database connection and creates a log table.
db_connection = sqlite3.connect(LOGS_DATABASE)
db_connection.execute("CREATE TABLE IF NOT EXISTS questions(x_key TEXT, created_at TEXT, user_prompt TEXT, system_prompt TEXT, answer TEXT)")
db_connection.commit()
db_connection.row_factory = sqlite3.Row
app.db = {
    "connection": db_connection,
    "cursor": db_connection.cursor(),
}

# Relay configuration into FastApi application.
app.OPENAI_APIKEY = OPENAI_APIKEY
app.EMBEDDING_MODEL = EMBEDDING_MODEL
app.MAX_QUEUE_CAPACITY = MAX_QUEUE_CAPACITY
app.CORPUS_DIR = CORPUS_DIR
app.STORAGE_DIR = STORAGE_DIR
app.LOGS_DATABASE = LOGS_DATABASE
app.OPENAI_MODEL = OPENAI_MODEL

# Adding other stuff to the app context.
app.templates = Jinja2Templates(directory="./templates")
app.templates.env.filters['format_datetime'] = filters.format_datetime
app.startup_time = datetime.datetime.now()
app.query_engine = local_index.as_query_engine(llm=OpenAI(model=OPENAI_MODEL, api_key=OPENAI_APIKEY, request_timeout=60.0))
app.message_queues = {}
app.max_queue_capacity = MAX_QUEUE_CAPACITY

# Static assets like js, css, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Including routers.
app.include_router(default.router)
app.include_router(healhcheck.router, prefix="/healhcheck")
app.include_router(statistics.router, prefix="/statistics")
app.include_router(chat.router, prefix="/chat")
