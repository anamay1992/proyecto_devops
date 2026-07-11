from flask import Flask, jsonify, request
import pymysql
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'cisco-devasc-super-secret-key-2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=60)
jwt = JWTManager(app)

DB_HOST = '172.18.144.1' 
DB_USER = 'root'
DB_PASSWORD = 'cabanillas'
DB_NAME = 'library'

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Faltan datos (username, password)"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
            cursor.execute(sql, (data['username'], hashed_password))
            conn.commit()
        return jsonify({"message": f"Usuario {data['username']} registrado exitosamente"}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409
    finally:
        conn.close()

@app.route('/api/v1/loginViaBasic', methods=['POST'])
def login_basic():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"error": "Se requieren credenciales Basic Auth"}), 401
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (auth.username,))
        user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], auth.password):
        # Generamos un token real firmado criptográficamente
        access_token = create_access_token(identity=user['username'])
        return jsonify({"token": access_token}), 200
    
    return jsonify({"error": "Credenciales inválidas"}), 401


@app.route('/api/v1/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
    conn.close()
    return jsonify(books), 200

@app.route('/api/v1/books', methods=['POST'])
@jwt_required()
def add_book():
    new_book = request.get_json()
    if not new_book or 'title' not in new_book or 'author' not in new_book:
        return jsonify({"error": "Faltan datos obligatorios (title, author)"}), 400
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "INSERT INTO books (title, author) VALUES (%s, %s)"
        cursor.execute(sql, (new_book['title'], new_book['author']))
        conn.commit()
        new_book['id'] = cursor.lastrowid
    conn.close()
    return jsonify(new_book), 201

@app.route('/api/v1/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    data = request.get_json()
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Libro no encontrado"}), 404
            
        sql = "UPDATE books SET title = COALESCE(%s, title), author = COALESCE(%s, author) WHERE id = %s"
        cursor.execute(sql, (data.get('title'), data.get('author'), book_id))
        conn.commit()
        
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        updated_book = cursor.fetchone()
    conn.close()
    return jsonify(updated_book), 200

@app.route('/api/v1/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        rows_affected = cursor.rowcount
        conn.commit()
    conn.close()
    
    if rows_affected > 0:
        return jsonify({"message": f"Libro con ID {book_id} eliminado exitosamente"}), 200
    return jsonify({"error": "Libro no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)