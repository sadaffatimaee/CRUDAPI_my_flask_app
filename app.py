import logging
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

# Set up logging for detailed output
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# MySQL database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # MySQL host (for local setup, use localhost)
            user='root',       # MySQL username (default: root)
            password='7406312344',  # Replace with your MySQL password
            database='my_flask_db'     # Replace with your actual database name
        )
        return connection
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
        raise

# Route to get all items
@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_db_connection()  # Get the connection
        cursor = conn.cursor(dictionary=True)  # Get a cursor to interact with the DB
        cursor.execute('SELECT * FROM items')  # Execute SQL query
        items = cursor.fetchall()  # Fetch all rows from the query result
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        return jsonify(items)  # Return items as JSON response
    except Error as e:
        logging.error(f"Error fetching items: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Route to add a new item
@app.route('/items', methods=['POST'])
def add_item():
    try:
        new_item = request.get_json()  # Get the JSON data sent in the request body
        if not new_item or 'name' not in new_item or 'description' not in new_item:
            return jsonify({'message': 'Invalid input, name and description are required'}), 400
        
        name = new_item['name']  # Get the name of the item
        description = new_item['description']  # Get the description of the item

        conn = get_db_connection()  # Get the connection
        cursor = conn.cursor()  # Get a cursor to interact with the DB
        cursor.execute('INSERT INTO items (name, description) VALUES (%s, %s)', (name, description))  # Insert item
        conn.commit()  # Commit the changes to the database
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        
        return jsonify({'message': 'Item added successfully'}), 201  # Return a success message
    except Error as e:
        logging.error(f"Error adding item: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Route to update an item
@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    try:
        updated_item = request.get_json()  # Get the JSON data for the updated item
        if not updated_item or 'name' not in updated_item or 'description' not in updated_item:
            return jsonify({'message': 'Invalid input, name and description are required'}), 400
        
        name = updated_item['name']  # Get the updated name
        description = updated_item['description']  # Get the updated description

        conn = get_db_connection()  # Get the connection
        cursor = conn.cursor()  # Get a cursor to interact with the DB
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Item not found'}), 404
        
        cursor.execute('UPDATE items SET name = %s, description = %s WHERE id = %s', 
                       (name, description, id))  # Update the item
        conn.commit()  # Commit the changes
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        
        return jsonify({'message': 'Item updated successfully'})  # Return a success message
    except Error as e:
        logging.error(f"Error updating item {id}: {e}")
        return jsonify({'message': 'Internal server error. Please try again later.'}), 500

# Route to delete an item
@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    try:
        conn = get_db_connection()  # Get the connection
        cursor = conn.cursor()  # Get a cursor to interact with the DB
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Item not found'}), 404
        
        cursor.execute('DELETE FROM items WHERE id = %s', (id,))  # Delete the item with the given id
        conn.commit()  # Commit the changes
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        
        return jsonify({'message': 'Item deleted successfully'})  # Return a success message
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
    app.run(debug=True, host='0.0.0.0', port=5000)  # Bind to all interfaces to allow external access
