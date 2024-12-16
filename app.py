import logging
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

# Set up logging for detailed output
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# MySQL database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Change this to 'localhost' if you're not using Docker
            user='root',
            password='7406312344',
            database='my_flask_db'
        )
        return connection
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
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
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM items')
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(items)
    except Error as e:
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
    except Error as e:
        logging.error(f"Error adding item: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Route to update an item
@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    try:
        updated_item = request.get_json()
        if not updated_item or 'name' not in updated_item or 'description' not in updated_item:
            return jsonify({'message': 'Invalid input, name and description are required'}), 400

        name = updated_item['name']
        description = updated_item['description']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Item not found'}), 404

        cursor.execute('UPDATE items SET name = %s, description = %s WHERE id = %s',
                       (name, description, id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Item updated successfully'})
    except Error as e:
        logging.error(f"Error updating item {id}: {e}")
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
    except Error as e:
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
