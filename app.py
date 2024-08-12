from flask import Flask, request, render_template, redirect, url_for, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import logging
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# Initialize the Neo4j driver
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        logger.info("Connected to Neo4j successfully.")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise

driver = get_neo4j_driver()

@app.route('/')
def index():
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS num_nodes")
            num_nodes = result.single()["num_nodes"]
        return render_template('index.html', num_nodes=num_nodes)
    except Exception as e:
        logger.error(f"Failed to fetch node count: {e}")
        return f"An error occurred: {str(e)}", 500

@app.route('/create', methods=['POST'])
def create_nodes():
    try:
        start_time = time.time()  # Start the timer
        
        with driver.session() as session:
            # List of queries to run sequentially
            queries = [
                """
                LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/athletes.csv' AS row
                MERGE (a:Athlete {code: row.code})
                SET a.name = row.name,
                    a.gender = row.gender,
                    a.height = toInteger(row.height),
                    a.weight = toInteger(row.weight),
                    a.birth_date = date(row.birth_date),
                    a.birth_place = row.birth_place,
                    a.nickname = row.nickname,
                    a.hobbies = split(row.hobbies, ','),
                    a.occupation = split(row.occupation, ','),
                    a.education = row.education,
                    a.reason = row.reason
                """,
                """
                LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/athletes.csv' AS row
                MERGE (c:Country {name: row.country})
                SET c.country_code = row.country_code
                """,
                """
                LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/events.csv' AS row
                MERGE (s:Sport {name: row.sport})
                SET s.sport_code = row.sport_code,
                    s.sport_tag = row.sport_tag,
                    s.sport_url = row.sport_url
                """,
                """
                LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/events.csv' AS row 
                MERGE (e:Event {name: row.event})
                """,
                """
                LOAD CSV WITH HEADERS
                FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/events.csv' AS row
                MATCH (e:Event) WHERE e.name=row.event
                MATCH (s:Sport) WHERE s.name= row.sport
                MERGE (e)-[r:BELONGS_TO]->(s)
                """,
                """
                LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/medallists.csv' AS row
                MATCH (a:Athlete {name: row.name}), (e:Event {name: row.event})
                CALL apoc.merge.relationship(a,
                    'HAS_WON_IN_PLACE_' + row.medal_code,
                    {medal_date: date(row.medal_date)},
                    {},
                    e,
                    {}
                ) YIELD rel
                RETURN a,rel,e
                """,
                """
                LOAD CSV WITH HEADERS
                FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/athletes.csv' AS row
                MATCH (a:Athlete) WHERE a.name=row.name
                MATCH (c:Country) WHERE c.name=row.country
                MERGE (a)-[r:HAS_COUNTRY]->(c)
                """
            ]
            
            # Execute each query sequentially
            for query in queries:
                result = session.run(query)
                result.consume()  # Ensure the query is fully processed before moving to the next one
            
            # Get the number of nodes and relationships
            node_count_result = session.run("MATCH (n) RETURN count(n) AS num_nodes")
            num_nodes = node_count_result.single()["num_nodes"]
            
            relationship_count_result = session.run("MATCH ()-[r]->() RETURN count(r) AS num_relationships")
            num_relationships = relationship_count_result.single()["num_relationships"]
        
        end_time = time.time()  # End the timer
        time_taken = end_time - start_time
        
        # Pass the information to the index template
        return render_template('index.html', num_nodes=num_nodes, num_relationships=num_relationships, time_taken=time_taken)
    
    except Exception as e:
        logger.error(f"An error occurred while creating nodes: {e}")
        return f"An error occurred while creating nodes: {str(e)}", 500

@app.route('/cleanup', methods=['POST'])
def cleanup_nodes():
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"An error occurred during cleanup: {e}")
        return str(e), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start the server: {e}")
