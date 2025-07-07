from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.utils import node_to_metadata_dict
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import VectorStoreIndex
from .db_query import db_query

index_name = "entity"

class PrepareVectorLlamaIndex:

    def run(self):        
        db_query(
            """
        CREATE VECTOR INDEX """
            + index_name
            + """ IF NOT EXISTS FOR (e:__Entity__) ON e.description_embedding
        OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
        }}
        """
        )
        db_query(
            """
        MATCH (n:`__Community__`)<-[:IN_COMMUNITY]-()<-[:HAS_ENTITY]-(c)
        WITH n, count(distinct c) AS chunkCount
        SET n.weight = chunkCount"""
        )

        content = node_to_metadata_dict(TextNode(), remove_text=True, flat_metadata=False)
        db_query(
            """
        MATCH (e:__Entity__)
        SET e += $content""",
            {"content": content},
        )
        return True