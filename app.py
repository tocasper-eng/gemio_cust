from flask import Flask, request, jsonify, render_template
from db import get_connection

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('cust.html')


@app.route('/api/dict/kindno')
def get_kindno():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT dictnm FROM dict WHERE dictno = 'kindno'")
        return jsonify([row[0] for row in cur.fetchall()])
    finally:
        conn.close()


@app.route('/api/cust')
def list_cust():
    q = request.args.get('q', '').strip()
    sql = "SELECT num, custno, custnm, kindno, address0 FROM cust"
    params = []
    if q:
        sql += " WHERE custno LIKE ? OR custnm LIKE ? OR address0 LIKE ?"
        params = [f'%{q}%', f'%{q}%', f'%{q}%']
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return jsonify([dict(zip(cols, r)) for r in cur.fetchall()])
    finally:
        conn.close()


@app.route('/api/cust', methods=['POST'])
def create_cust():
    d = request.json
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM cust WHERE custno = ?", d['custno'])
        if cur.fetchone():
            return jsonify({'error': 'duplicate_custno'}), 409
        cur.execute(
            "INSERT INTO cust (custno, custnm, kindno, address0) VALUES (?,?,?,?)",
            d['custno'], d.get('custnm'), d.get('kindno'), d.get('address0')
        )
        conn.commit()
        return jsonify({'ok': True}), 201
    finally:
        conn.close()


@app.route('/api/cust/<int:num>', methods=['PUT'])
def update_cust(num):
    d = request.json
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM cust WHERE custno = ? AND num <> ?", d['custno'], num)
        if cur.fetchone():
            return jsonify({'error': 'duplicate_custno'}), 409
        cur.execute(
            "UPDATE cust SET custno=?, custnm=?, kindno=?, address0=? WHERE num=?",
            d['custno'], d.get('custnm'), d.get('kindno'), d.get('address0'), num
        )
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()


@app.route('/api/cust/<int:num>', methods=['DELETE'])
def delete_cust(num):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cust WHERE num = ?", num)
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
