"""Test Neo4j connection"""
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {NEO4J_URI}")
print(f"Username: {NEO4J_USERNAME}")

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # Test query
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' as message")
        record = result.single()
        print(f"✅ {record['message']}")
        
        # Check database contents
        result = session.run("MATCH (n) RETURN count(n) as node_count")
        record = result.single()
        print(f"📊 Total nodes in database: {record['node_count']}")
        
        # Check node labels
        result = session.run("CALL db.labels()")
        labels = [record['label'] for record in result]
        print(f"🏷️  Node labels: {labels}")
    
    driver.close()
    print("\n✅ Neo4j connection test PASSED")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nPlease check:")
    print("1. Neo4j Aura database is running (not paused)")
    print("2. URI, username, and password are correct")
    print("3. Network connection is available")
