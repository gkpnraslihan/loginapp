from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/users':
            # Veritabanına bağlan
            conn = sqlite3.connect('path/to/your/newdb.db')  # Veritabanı dosyanızın yolunu burada belirtin
            c = conn.cursor()
            # Kullanıcıları çek
            c.execute("SELECT * FROM auth_user")
            users = c.fetchall()
            conn.close()

            # Kullanıcıları JSON formatına dönüştür
            user_list = [{'id': user[0], 'username': user[1], 'email': user[2]} for user in users]

            # JSON yanıtı döndür
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(user_list).encode())

    def do_POST(self):
        if self.path == '/users' or self.path == '/users/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_data = json.loads(post_data)

            # Kullanıcıyı veritabanına ekle
            conn = sqlite3.connect('path/to/your/newdb.db')  # Veritabanı dosyanızın yolunu burada belirtin
            c = conn.cursor()
            c.execute("INSERT INTO auth_user (username, email) VALUES (?, ?)",
                      (user_data['username'], user_data['email']))
            conn.commit()
            conn.close()

            # Başarılı yanıtı döndür
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'User added successfully'}).encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
