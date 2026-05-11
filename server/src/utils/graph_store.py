from neo4j import GraphDatabase
from src.utils.config import settings

class MemgraphStore:
    def __init__(self):
        auth = None
        print("----------------------------------------------------")
        print(settings.MEMGRAPH_USER, settings.MEMGRAPH_PASSWORD)
        print("----------------------------------------------------")
        if settings.MEMGRAPH_USER and settings.MEMGRAPH_PASSWORD:
            auth = (settings.MEMGRAPH_USER, settings.MEMGRAPH_PASSWORD)
            
        self.driver = GraphDatabase.driver(
            settings.MEMGRAPH_URI,
            auth=auth
        )

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
            
    def insert_clause_and_relationships(self, chunk_id, text, metadata, references, conflicts_with, supersedes):
        """
        Merge a Clause node and create relationships based on LLM extraction.
        """
        query = """
        MERGE (c:Clause {id: $chunk_id})
        SET c.text = $text, c.metadata = $metadata
        """
        
        with self.driver.session() as session:
            session.run(query, {"chunk_id": chunk_id, "text": text, "metadata": str(metadata)})
            
            for ref in (references or []):
                session.run(
                    """
                    MATCH (c:Clause {id: $chunk_id})
                    MERGE (t:Clause {name: $ref})
                    MERGE (c)-[:REFERENCES]->(t)
                    """,
                    {"chunk_id": chunk_id, "ref": ref}
                )
                
            for conflict in (conflicts_with or []):
                session.run(
                    """
                    MATCH (c:Clause {id: $chunk_id})
                    MERGE (t:Clause {name: $conflict})
                    MERGE (c)-[:CONFLICTS_WITH]->(t)
                    """,
                    {"chunk_id": chunk_id, "conflict": conflict}
                )
                
            for supersede in (supersedes or []):
                session.run(
                    """
                    MATCH (c:Clause {id: $chunk_id})
                    MERGE (t:Clause {name: $supersede})
                    MERGE (c)-[:SUPERSEDES]->(t)
                    """,
                    {"chunk_id": chunk_id, "supersede": supersede}
                )
