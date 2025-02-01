import os
import sys
import logging
import argparse

from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from dotenv import load_dotenv
load_dotenv()
OPENAI_APIKEY = os.environ["OPENAI_APIKEY"]
OPENAI_MODEL = os.environ["OPENAI_MODEL"]
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
MAX_QUEUE_CAPACITY = int(os.environ["MAX_QUEUE_CAPACITY"])
CORPUS_DIR = os.environ["CORPUS_DIR"]
STORAGE_DIR = os.environ["STORAGE_DIR"]
LOGS_DATABASE = os.environ["LOGS_DATABASE"]

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def action_index():
    # from llama_index.llms.ollama import Ollama
    from llama_index.llms.openai import OpenAI
    local_index = None

    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL, api_key=OPENAI_APIKEY)

    # Indexes the current corpus or loads existing one.
    if not os.path.exists(STORAGE_DIR):
        logging.info(f"Indexing new context in `{CORPUS_DIR}` and storing it locally in `{STORAGE_DIR}`.")
        try:
            documents = SimpleDirectoryReader(input_dir=CORPUS_DIR, recursive=True).load_data()
            local_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
            local_index.storage_context.persist(persist_dir=STORAGE_DIR)
        except Exception as e:
            logging.error(f"Indexing of corpus `{CORPUS_DIR}` failed with error: {e}")
    else:
        logging.info(f"Index for `{CORPUS_DIR}` already exists in `{STORAGE_DIR}`.")

    # Final check if the corpus was indexed.
    if local_index is None:
        logging.info(f"Index in `{STORAGE_DIR}` not indexed.")
        sys.exit()
    else:
        logging.info(f"Index `{STORAGE_DIR}` created.")
        sys.exit()
        

if __name__ == "__main__":
    program_description = [
        "CLI utility that helps setting up of LLM indexes, storages etc.",
    ]

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description=" ".join(program_description))
    parser.add_argument("--index", help="indexes local storage and saves vector index to local folder", action="store_true")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()

    if args.index:
        print(f"This action will index folder `{CORPUS_DIR}` and introduce vector index in `{STORAGE_DIR}`.")
        confirmation = input("Do you want to perform the action? (yes/no): ").strip().lower()
        if confirmation == "yes":
            action_index()
