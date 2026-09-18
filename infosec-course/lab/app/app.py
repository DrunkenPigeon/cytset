import sqlite3
import requests
import jwt
import subprocess
import threading
import time
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Инициализация тестовой базы SQLite в памяти
def get_db():
    conn = sqlite3.connect("lab.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        balance INTEGER DEFAULT 100
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        price INTEGER,
        is_hidden BOOLEAN DEFAULT 0
    )
    """)
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM products")
    cursor.execute("INSERT INTO users (username, password_hash, role, balance) VALUES ('admin', 'pbkdf2:sha256:admin_salt_hash_9921', 'superadmin', 1000)")
    cursor.execute("INSERT INTO users (username, password_hash, role, balance) VALUES ('alice', 'pbkdf2:sha256:user_salt_hash_1182', 'student', 150)")
    cursor.execute("INSERT INTO products (title, description, price, is_hidden) VALUES ('Security Token', 'Hardware security key', 50, 0)")
    cursor.execute("INSERT INTO products (title, description, price, is_hidden) VALUES ('Master Key', 'CONFIDENTIAL EXPLOIT ARCHIVE', 99999, 1)")
    conn.commit()
    conn.close()

init_db()

# ==============================================================================
# ENDPOINT 1: SQL Injection (Union & Blind Time-Based)
# Уязвимость: конкатенация строк в SQL-запросе
# ==============================================================================
@app.route('/api/v1/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    conn = get_db()
    cursor = conn.cursor()
    
    # VULNERABLE: прямое форматирование строки
    sql = f"SELECT id, title, description, price FROM products WHERE is_hidden = 0 AND title LIKE '%{query}%'"
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify([dict(ix) for ix in rows])
    except Exception as e:
        return jsonify({"error": str(e), "executed_sql": sql}), 500

# ==============================================================================
# ENDPOINT 2: SSRF (Server-Side Request Forgery)
# Уязвимость: отправка HTTP-запроса по переданному URL без проверки схемы и IP
# ==============================================================================
@app.route('/api/v1/fetch', methods=['POST'])
def fetch_remote_resource():
    target_url = request.json.get('url', '')
    if not target_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
        
    try:
        # VULNERABLE: прямой запрос к произвольному хосту, включая internal_net и localhost
        response = requests.get(target_url, timeout=3)
        return jsonify({
            "target": target_url,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text[:2000] # Ограничение размера для вывода
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# ENDPOINT 3: Race Condition (Limit Overrun)
# Уязвимость: отсутствие транзакционной блокировки при проверке и изменении баланса
# ==============================================================================
coupon_redeemed = {}
coupon_lock = threading.Lock()

@app.route('/api/v1/coupon/redeem', methods=['POST'])
def redeem_coupon():
    username = request.json.get('username', 'alice')
    coupon_code = request.json.get('coupon', '')
    
    if coupon_code != "HACK-UNIVERSITY-2026":
        return jsonify({"error": "Invalid coupon code"}), 400
        
    # VULNERABLE: Check-then-Act без атомарности и блокировок
    if coupon_redeemed.get(username, False):
        return jsonify({"error": "Coupon already used"}), 400
        
    # Искусственная задержка имитирует тяжелую бизнес-логику или сетевой вызов
    time.sleep(0.1)
    
    coupon_redeemed[username] = True
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + 100 WHERE username = ?", (username,))
    conn.commit()
    
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    new_bal = cursor.fetchone()['balance']
    conn.close()
    
    return jsonify({"success": True, "new_balance": new_bal})

# ==============================================================================
# ENDPOINT 4: Broken Auth & JWT Key Confusion
# Уязвимость: проверка подписи с использованием публичного RSA-ключа как секрета HMAC
# ==============================================================================
SERVER_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy0kQ6V7q9Z3eO5w7dM3x
... (simulated rsa key) ...
-----END PUBLIC KEY-----"""

@app.route('/api/v1/auth/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Bearer token required"}), 401
        
    token = auth_header.split(' ')[1]
    try:
        # VULNERABLE: не указан жесткий список разрешенных алгоритмов
        # При передаче токена с alg=HS256 библиотека может использовать
        # строковый SERVER_PUBLIC_KEY в качестве секретного симметричного пароля
        decoded = jwt.decode(token, SERVER_PUBLIC_KEY, algorithms=["HS256", "RS256"])
        return jsonify({"status": "authenticated", "payload": decoded})
    except Exception as e:
        return jsonify({"error": f"Token verification failed: {str(e)}"}), 403

# ==============================================================================
# ENDPOINT 5: Command Injection
# Уязвимость: конкатенация ввода в системный shell
# ==============================================================================
@app.route('/api/v1/diagnostic/ping', methods=['GET'])
def ping_diagnostic():
    host = request.args.get('host', '127.0.0.1')
    # VULNERABLE: shell=True с несанитизированной строкой
    cmd = f"ping -c 2 {host}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({"output": output.decode('utf-8', errors='ignore')})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output.decode('utf-8', errors='ignore')}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
