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
        num_nodes = int(request.form.get('num_nodes', '0'))
        with driver.session() as session:
            for i in range(num_nodes):
                session.run("CREATE (n:Node {id: $id}) RETURN n", id=i)
            session.close()
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)
    
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

