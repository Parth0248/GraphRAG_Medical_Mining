from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def clean_database():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    with driver.session() as session:
        # 1. Count trash nodes before
        print("Checking for trash nodes...")
        result = session.run("""
            MATCH (n:Entity)
            WHERE n.name STARTS WITH '#' 
               OR n.name STARTS WITH '-' 
               OR n.name STARTS WITH '*'
               OR size(n.name) < 2
               OR n.name CONTAINS '##'
            RETURN count(n) as count, collect(n.name) as names
        """)
        record = result.single()
        count = record['count']
        names = record['names'][:20] # Show first 20
        
        print(f"Found {count} potential trash nodes.")
        if count > 0:
            print(f"Examples: {names}")
            
            # 2. Delete them
            print("Deleting trash nodes...")
            session.run("""
                MATCH (n:Entity)
                WHERE n.name STARTS WITH '#' 
                   OR n.name STARTS WITH '-' 
                   OR n.name STARTS WITH '*'
                   OR size(n.name) < 2
                   OR n.name CONTAINS '##'
                DETACH DELETE n
            """)
            print("Trash nodes deleted.")
        else:
            print("No trash nodes found matching criteria.")
            
        # 3. Verify total count
        result = session.run("MATCH (n) RETURN count(n) as total")
        print(f"Total nodes remaining: {result.single()['total']}")

    driver.close()

if __name__ == "__main__":
    clean_database()
