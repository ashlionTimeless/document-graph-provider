import os
import getpass
from neo4j import GraphDatabase, Result
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tiktoken
import numpy as np
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Neo4jVector
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.utils import node_to_metadata_dict
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from llama_index.core import VectorStoreIndex
from tqdm import tqdm

from typing import Dict, Any

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def db_query(cypher: str, params: Dict[str, Any] = {}) -> pd.DataFrame:
    """Executes a Cypher statement and returns a DataFrame"""
    return driver.execute_query(
        cypher, parameters_=params, result_transformer_=Result.to_df
    )

index_name = "entity"

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







lc_retrieval_query = """
WITH collect(node) as nodes
// Entity - Text Unit Mapping
WITH
collect {
    UNWIND nodes as n
    MATCH (n)<-[:HAS_ENTITY]->(c:__Chunk__)
    WITH c, count(distinct n) as freq
    RETURN c.text AS chunkText
    ORDER BY freq DESC
    LIMIT $topChunks
} AS text_mapping,
// Entity - Report Mapping
collect {
    UNWIND nodes as n
    MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
    WITH c, c.rank as rank, c.weight AS weight
    RETURN c.summary 
    ORDER BY rank, weight DESC
    LIMIT $topCommunities
} AS report_mapping,
// Outside Relationships 
collect {
    UNWIND nodes as n
    MATCH (n)-[r:RELATED]-(m) 
    WHERE NOT m IN nodes
    RETURN r.description AS descriptionText
    ORDER BY r.rank, r.weight DESC 
    LIMIT $topOutsideRels
} as outsideRels,
// Inside Relationships 
collect {
    UNWIND nodes as n
    MATCH (n)-[r:RELATED]-(m) 
    WHERE m IN nodes
    RETURN r.description AS descriptionText
    ORDER BY r.rank, r.weight DESC 
    LIMIT $topInsideRels
} as insideRels,
// Entities description
collect {
    UNWIND nodes as n
    RETURN n.description AS descriptionText
} as entities
// We don't have covariates or claims here
RETURN {Chunks: text_mapping, Reports: report_mapping, 
       Relationships: outsideRels + insideRels, 
       Entities: entities} AS text, 1.0 AS score, {} AS metadata
"""

topChunks = 3
topCommunities = 3
topOutsideRels = 10
topInsideRels = 10
topEntities = 10
lc_vector = Neo4jVector.from_existing_index(
    OpenAIEmbeddings(model="text-embedding-3-small"),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=index_name,
    retrieval_query=lc_retrieval_query,
)


content = node_to_metadata_dict(TextNode(), remove_text=True, flat_metadata=False)

db_query(
    """
  MATCH (e:__Entity__)
  SET e += $content""",
    {"content": content},
)


embed_dim = 1536

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
    LIMIT {topChunks}
}} AS text_mapping,
// Entity - Report Mapping
collect {{
    UNWIND nodes as n
    MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
    WITH c, c.rank as rank, c.weight AS weight
    RETURN c.summary 
    ORDER BY rank, weight DESC
    LIMIT {topCommunities}
}} AS report_mapping,
// Outside Relationships 
collect {{
    UNWIND nodes as n
    MATCH (n)-[r:RELATED]-(m) 
    WHERE NOT m IN nodes
    RETURN r.description AS descriptionText
    ORDER BY r.rank, r.weight DESC 
    LIMIT {topOutsideRels}
}} as outsideRels,
// Inside Relationships 
collect {{
    UNWIND nodes as n
    MATCH (n)-[r:RELATED]-(m) 
    WHERE m IN nodes
    RETURN r.description AS descriptionText
    ORDER BY r.rank, r.weight DESC 
    LIMIT {topInsideRels}
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




from llama_index.embeddings.openai import OpenAIEmbedding

neo4j_vector = Neo4jVectorStore(
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_URI,
    embed_dim,
    index_name=index_name,
    retrieval_query=retrieval_query,
)
loaded_index = VectorStoreIndex.from_vector_store(neo4j_vector).as_query_engine(
    similarity_top_k=topEntities, embed_model=OpenAIEmbedding(model="text-embedding-3-small")
)



response = loaded_index.query("What do you know about Leonardo's family?")
print(response.response)
# print(response.source_nodes[0].text)