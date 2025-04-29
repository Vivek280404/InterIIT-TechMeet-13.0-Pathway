import os
import logging
import pathway as pw
from typing import List, Dict, Any
from pathway.udfs import DiskCache, ExponentialBackoffRetryStrategy
from pathway.xpacks.llm import embedders, llms, parsers, prompts
from pathway.xpacks.llm.question_answering import AdaptiveRAGQuestionAnswerer
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.servers import DocumentStoreServer
from pathway.stdlib.indexing import UsearchKnnFactory, TantivyBM25Factory, HybridIndexFactory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import threading
os.environ["PATHWAY_PERSISTENT_STORAGE"] = "./persistence_data"

load_dotenv('../.env')
# Configure text splitting parameters for document chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=800)


class DocumentProcessor:
    """
    A class to process documents and manage a document store server.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        # Configure environment and logging
        os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        self.host = host
        self.port = port
        self.app = None 
        self.vector_store = None
        
        self.parser = parsers.ParseUnstructured(mode="paged")
        self.embedder = embedders.LiteLLMEmbedder(
            capacity=30,
            model='voyage/voyage-3',
            retry_strategy=ExponentialBackoffRetryStrategy(max_retries=6),
            cache_strategy=DiskCache(),
        )

    def initialize_vector_store(self, path1):
        """       
        Initialize document store with provided file path
        """

        source1 = pw.io.fs.read(path=path1, with_metadata=True, format="binary", mode="streaming")  
        path2 = "../pipeline/temp_rag_space"
        source2 = pw.io.fs.read(path=path2, with_metadata=True, format="binary", mode="streaming")


        usearch = UsearchKnnFactory(embedder=self.embedder)
        bm25 = TantivyBM25Factory(ram_budget=524288000, in_memory_index=True)
        factories = [usearch, bm25]
        retriever_factory = HybridIndexFactory(factories, k=60)
        
        self.vector_store = DocumentStore.from_langchain_components(
            retriever_factory=retriever_factory,
            docs=[source1,source2],

            parser=self.parser,
            splitter=text_splitter,
        )


    def setup_document_server(self):
        """
        Configure document store server
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        self.app1 = DocumentStoreServer(
            host=self.host,
            port=4004,
            document_store=self.vector_store
        )


    def start_document_server(self):
        """
        Launch document server in background thread
        """
        server_thread = threading.Thread(
            target=self.app1.run,
            name="BaseDocument"
        )   
        server_thread.daemon = True
        server_thread.start()
        return server_thread
    
def main():
    # Initialize data directory for document storage
    data_dir = "../pipeline/Agents/LATS/temp_rag_space"
    os.makedirs(data_dir, exist_ok=True)
    
    # Set up and start servers
    processor = DocumentProcessor()
    processor.initialize_vector_store(data_dir)
    processor.setup_document_server()
    
    persistence_backend = pw.persistence.Backend.filesystem("./state/")
    persistence_config = pw.persistence.Config(persistence_backend)
    
    try:
        pw.run()
        processor.start_document_server()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")

if __name__ == "__main__":
    main()




