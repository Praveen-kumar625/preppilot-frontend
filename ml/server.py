"""
PrePilot Lightweight Local ML Server
Uses Python's standard library http.server to expose the verified Random Forest
inference pipeline over HTTP with CORS support. Zero external backend dependencies needed.
"""
import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure ml module path is accessible
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from predict import ReadinessPredictor

class PrePilotAPIHandler(BaseHTTPRequestHandler):
    predictor = None

    @classmethod
    def get_predictor(cls):
        if cls.predictor is None:
            cls.predictor = ReadinessPredictor.get_instance()
        return cls.predictor

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/" or self.path == "/api/health":
            p = self.get_predictor()
            response = {
                "status": "online",
                "service": "PrePilot ML Inference Server",
                "model": "Random Forest Classifier",
                "version": "1.0.0",
                "accuracy": "92.89%",
                "supported_roles": p.supported_roles
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
        elif self.path == "/api/roles":
            p = self.get_predictor()
            self._set_headers(200)
            self.wfile.write(json.dumps({"roles": p.supported_roles}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/api/predict":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode("utf-8"))

                p = self.get_predictor()
                result = p.predict(payload)

                # Include live model confirmation badge in response
                result["mode"] = "live_ml"
                result["model_info"] = {
                    "algorithm": "Random Forest",
                    "accuracy": "92.89%",
                    "records_evaluated": 60000
                }

                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                err_response = {
                    "status": "error",
                    "error_message": str(e),
                    "mode": "error"
                }
                self.wfile.write(json.dumps(err_response).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Concise console logging
        sys.stdout.write(f"[PrePilot ML API] {self.address_string()} - {format%args}\n")
        sys.stdout.flush()

def run_server(port=5000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, PrePilotAPIHandler)
    print("=" * 70)
    print(f"PrePilot ML Inference Server active at: http://127.0.0.1:{port}")
    print("Serving real Random Forest model predictions (92.89% Accuracy)")
    print("Endpoints:")
    print(f"  - GET  http://127.0.0.1:{port}/api/health")
    print(f"  - POST http://127.0.0.1:{port}/api/predict")
    print("=" * 70)
    httpd.serve_forever()

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
