import http.server
import socketserver
import webbrowser
import os

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

if __name__ == "__main__":
    # Ensure working directory is this file's folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"✧ Launching Kindred App at http://localhost:{PORT} ...")
    webbrowser.open(f"http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT} (Press Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
