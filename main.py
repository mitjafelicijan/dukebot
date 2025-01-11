import os
import sys
import logging
import sqlite3
import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
import filters
import healhcheck
import dashboard
import chat

from llama_index.llms.ollama import Ollama
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

# Set up logging format.
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# Indexes the current corpus or loads existing one.
local_index = None
if not os.path.exists(config.STORAGE_DIR):
    logging.critical("Index does not exist")
    sys.exit(1)
else:
    logging.info("Loading locally stored context")
    storage_context = StorageContext.from_defaults(persist_dir=config.STORAGE_DIR)
    local_index = load_index_from_storage(storage_context, embed_model="local")

# Final check if the corpus was indexed.
if local_index is None:
    logging.error("Loaded index is not valid")
    sys.exit(1)

# Creates a FastAPI app and continues.
app = FastAPI(
    title="AI Assistant",
    version="0.1",
    description="AI Assistant server",
)

# Creates database connection and creates a log table.
db_connection = sqlite3.connect("./logs.db")
db_connection.execute("CREATE TABLE IF NOT EXISTS questions(x_key TEXT, created_at TEXT, question TEXT, answer TEXT)")
db_connection.commit()
db_connection.row_factory = sqlite3.Row
app.db = {
    "connection": db_connection,
    "cursor": db_connection.cursor(),
}

# Adding other stuff to the app context.
app.templates = Jinja2Templates(directory="./templates")
app.templates.env.filters['format_datetime'] = filters.format_datetime
app.startup_time = datetime.datetime.now()
app.query_engine = local_index.as_query_engine(llm=Ollama(model=config.OLLAMA_MODEL, request_timeout=60.0))
app.message_queues = {}
app.max_queue_capacity = config.MAX_QUEUE_CAPACITY

# FIXME: Demo UI that should be removed when this is production ready.
app.mount("/demo", StaticFiles(directory="demo"), name="demo")

# Including routers.
app.include_router(healhcheck.router)
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(chat.router, prefix="/chat")
