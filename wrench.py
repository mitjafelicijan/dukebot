import os
import sys
import logging
import argparse

import config

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def action_index():
    from llama_index.llms.ollama import Ollama
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        load_index_from_storage,
    )

    local_index = None
    
    # Indexes the current corpus or loads existing one.
    if not os.path.exists(config.STORAGE_DIR):
        logging.info(f"Indexing new context in `{config.CORPUS_DIR}` and storing it locally in `{config.STORAGE_DIR}`.")
        try:
            documents = SimpleDirectoryReader(config.CORPUS_DIR).load_data()
            local_index = VectorStoreIndex.from_documents(documents, embed_model="local")
            local_index.storage_context.persist(persist_dir=config.STORAGE_DIR)
        except Exception as e:
            logging.error(f"Indexing of corpus `{config.CORPUS_DIR}` failed with error: {e}")
    else:
        logging.info(f"Index for `{config.CORPUS_DIR}` already exists in `{config.STORAGE_DIR}`.")

    # Final check if the corpus was indexed.
    if local_index is None:
        logging.info(f"Index in `{config.STORAGE_DIR}` not indexed.")
        sys.exit()
    else:
        logging.info(f"Index `{config.STORAGE_DIR}` created.")
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
        print(f"This action will index folder `{config.CORPUS_DIR}` and introduce vector index in `{config.STORAGE_DIR}`.")
        confirmation = input("Do you want to perform the action? (yes/no): ").strip().lower()
        if confirmation == "yes":
            action_index()
