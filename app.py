from flask import Flask, request, render_template, redirect, url_for
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get environment variables
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# Initialize the Neo4j driver
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    exit(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_nodes():
    try:
        with driver.session() as session:
            
            session.run("""LOAD CSV WITH HEADERS
                        FROM 'https://raw.githubusercontent.com/looeejee/olympic-graph/main/data/athletes.csv' AS row
                        MERGE (a:Athlete {code: row.code})
                        SET
                            a.name = row.name,
                            a.gender = row.gender,
                            a.height = toInteger(row.height),
                            a.weight = toInteger(row.weight),
                            a.birth_date = date(row.birth_date),
                            a.birth_place = row.birth_place,
                            a.birth_place = row.birth_place,
                            a.nickname = row.nickname,
                            a.hobbies= split(row.hobbies, ','),
                            a.occupation = split(row.occupation,','),
                            a.education = a.education,
                            a.reason = a.reason, id=i)""")
            num_nodes = session.run(" MATCH (n) RETURN count(n)")
        return redirect(url_for('index'), num_nodes=num_nodes)
    except Exception as e:
        return "An error occurred while creating nodes.", str(e)
    
@app.route('/cleanup', methods=['POST'])
def cleanup_nodes():
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

