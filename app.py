import logging
from dotenv import load_dotenv
import os  # To access environment variables
from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import OperationalError, extras

# Load environment variables from .env file
load_dotenv()

# Set up logging for detailed output
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        logging.debug(f"Connecting to DB at {os.getenv('DB_HOST')}")
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME'),
            port=os.getenv('DB_PORT')
        )
        logging.debug("Database connection successful.")
        return connection
    except OperationalError as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        raise

# Route to display the home page
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to my Flask app!'})

# Route to get all items
@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)  # Using RealDictCursor for dict-like results
        cursor.execute('SELECT * FROM items')  # Assuming 'items' is the correct table name
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(items)
    except OperationalError as e:
        logging.error(f"Error fetching items: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Route to add a new item
@app.route('/items', methods=['POST'])
def add_item():
    try:
        new_item = request.get_json()
        if not new_item or 'name' not in new_item or 'description' not in new_item:
            return jsonify({'message': 'Invalid input, name and description are required'}), 400

        name = new_item['name']
        description = new_item['description']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name, description) VALUES (%s, %s)', (name, description))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Item added successfully'}), 201
    except OperationalError as e:
        logging.error(f"Error adding item: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500


# Route to update an existing item
@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    try:
        # Get the new data from the request
        updated_item = request.get_json()
        if not updated_item or 'name' not in updated_item or 'description' not in updated_item:
            return jsonify({'message': 'Invalid input, name and description are required'}), 400

        name = updated_item['name']
        description = updated_item['description']

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the item exists
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        if not item:
            return jsonify({'message': 'Item not found'}), 404

        # Update the item in the database
        cursor.execute('UPDATE items SET name = %s, description = %s WHERE id = %s', 
                       (name, description, id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Item updated successfully'}), 200

    except OperationalError as e:
        logging.error(f"Error updating item: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500


# Route to delete an item
@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Item not found'}), 404

        cursor.execute('DELETE FROM items WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Item deleted successfully'})
    except OperationalError as e:
        logging.error(f"Error deleting item {id}: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Error handler for 404 - Resource not found
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({'message': 'Resource not found'}), 404

# Error handler for 400 - Bad request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request. Please check the input.'}), 400

# Error handler for 500 - Internal server error
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
