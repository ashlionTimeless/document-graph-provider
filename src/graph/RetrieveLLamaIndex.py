import os
from neo4j import GraphDatabase, Result
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tiktoken
import numpy as np
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.utils import node_to_metadata_dict
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import VectorStoreIndex
from tqdm import tqdm
from llama_index.embeddings.openai import OpenAIEmbedding

from typing import Dict, Any

from Driver import driver

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE")

model_name = "text-embedding-3-small"

class RetrieverLlamaIndex:

    def __init__(self, index_name: str):
        self.index_name = index_name
        self.embed_model = OpenAIEmbedding(model=model_name)

    def getParameters(self):
        return {
            "topChunks": 3,
            "topCommunities": 3,
            "topOutsideRels": 10,
            "topInsideRels": 10,
            "topEntities": 10,
            "embed_dim": 1536
        }

    def getRetrievalQuery(self):
        parameters = self.getParameters()
        retrieval_query = f"""
        WITH collect(node) as nodes
        // Entity - Text Unit Mapping
        WITH
        nodes,
        collect {{
            UNWIND nodes as n
            MATCH (n)<-[:HAS_ENTITY]->(c:__Chunk__)
            WITH c, count(distinct n) as freq
            RETURN c.text AS chunkText
            ORDER BY freq DESC
            LIMIT {parameters["topChunks"]}
        }} AS text_mapping,
        // Entity - Report Mapping
        collect {{
            UNWIND nodes as n
            MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
            WITH c, c.rank as rank, c.weight AS weight
            RETURN c.summary 
            ORDER BY rank, weight DESC
            LIMIT {parameters["topCommunities"]}
        }} AS report_mapping,
        // Outside Relationships 
        collect {{
            UNWIND nodes as n
            MATCH (n)-[r:RELATED]-(m) 
            WHERE NOT m IN nodes
            RETURN r.description AS descriptionText
            ORDER BY r.rank, r.weight DESC 
            LIMIT {parameters["topOutsideRels"]}
        }} as outsideRels,
        // Inside Relationships 
        collect {{
            UNWIND nodes as n
            MATCH (n)-[r:RELATED]-(m) 
            WHERE m IN nodes
            RETURN r.description AS descriptionText
            ORDER BY r.rank, r.weight DESC 
            LIMIT {parameters["topInsideRels"]}
        }} as insideRels,
        // Entities description
        collect {{
            UNWIND nodes as n
            RETURN n.description AS descriptionText
        }} as entities
        // We don't have covariates or claims here
        RETURN "Chunks:" + apoc.text.join(text_mapping, '|') + "\nReports: " + apoc.text.join(report_mapping,'|') +  
            "\nRelationships: " + apoc.text.join(outsideRels + insideRels, '|') + 
            "\nEntities: " + apoc.text.join(entities, "|") AS text, 1.0 AS score, nodes[0].id AS id, 
            {{_node_type:nodes[0]._node_type, _node_content:nodes[0]._node_content}} AS metadata
        """
        return retrieval_query

    def setRetrievalQuery(self, retrieval_query: str):
        self.retrieval_query = retrieval_query


    def getEmbedModel(self):
        return self.embed_model

    def getIndexName(self):
        return self.index_name

    def getVectorStore(self):
        neo4j_vector = Neo4jVectorStore(
            NEO4J_USERNAME,
            NEO4J_PASSWORD,
            NEO4J_URI,
            self.getParameters()["embed_dim"],
            index_name=self.getIndexName(),
            retrieval_query=self.getRetrievalQuery(),
        )
        return neo4j_vector

    def getIndex(self):
        loaded_index = VectorStoreIndex.from_vector_store(self.getVectorStore()).as_query_engine(
            similarity_top_k=self.getParameters()["topEntities"], embed_model=self.getEmbedModel()
        )
        return loaded_index


    def retrieve(self, document_id: str, query: str):
        response = self.getIndex().query(query)
        return response.response