import os
from haystack.document_stores import ElasticsearchDocumentStore

# Documents must be .txt files
doc_dir = '../data/documents/'

# Get the host where Elasticsearch is running, default to localhost
host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

document_store = ElasticsearchDocumentStore(
    host=host,
    port=9202,
    username="",
    password=""
)

document_store.delete_all_documents()

from haystack import Pipeline
from haystack.nodes import TextConverter, PreProcessor

indexing_pipeline = Pipeline()
text_converter = TextConverter()
preprocessor = PreProcessor(
    clean_whitespace=True,
    clean_header_footer=True,
    clean_empty_lines=True,
    split_by="word",
    split_length=400,
    split_overlap=20,
    split_respect_sentence_boundary=True,
)

import os

indexing_pipeline.add_node(component=text_converter, name="TextConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["TextConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

files_to_index = [f'{doc_dir}{f}' for f in os.listdir(doc_dir) if '.txt' in f]
indexing_pipeline.run_batch(file_paths=files_to_index)