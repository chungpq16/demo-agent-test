"""
Mockup API system for AI agent demo
Simulates infrastructure monitoring endpoints
"""
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/infrastructure', methods=['GET'])
def check_infrastructure():
    """Check system infrastructure status"""
    return jsonify({
        "status": "success",
        "http_code": 200,
        "message": "System infrastructure is operational",
        "details": {
            "cpu_usage": "45%",
            "memory_usage": "67%",
            "disk_usage": "32%",
            "uptime": "15 days, 4 hours"
        }
    }), 200

@app.route('/network', methods=['GET'])
def check_network():
    """Check network connectivity status"""
    return jsonify({
        "status": "success", 
        "http_code": 200,
        "message": "Network connections are healthy",
        "details": {
            "external_connectivity": "OK",
            "dns_resolution": "OK",
            "latency": "12ms",
            "bandwidth": "98% available"
        }
    }), 200

@app.route('/certificate', methods=['GET'])
def check_certificate():
    """Check SSL certificate status"""
    return jsonify({
        "status": "warning",
        "http_code": 200, 
        "message": "SSL certificate will expire in 7 days",
        "details": {
            "certificate_name": "*.company.com",
            "expiry_date": "2025-08-20",
            "days_remaining": 7,
            "issuer": "Let's Encrypt Authority X3"
        }
    }), 200

@app.route('/deployment', methods=['GET'])
def check_deployment():
    """Check deployment status"""
    return jsonify({
        "status": "error",
        "http_code": 500,
        "message": "Last deployment failed",
        "details": {
            "deployment_id": "deploy-2025-08-12-001",
            "failure_reason": "Database migration timeout",
            "failed_at": "2025-08-12T14:30:22Z",
            "rollback_status": "completed"
        }
    }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Overall health check endpoint"""
    return jsonify({
        "status": "mixed",
        "message": "Some systems have issues",
        "endpoints": {
            "infrastructure": "OK",
            "network": "OK", 
            "certificate": "WARNING",
            "deployment": "ERROR"
        }
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Mockup Infrastructure API...")
    print("📍 Available endpoints:")
    print("   GET /infrastructure - Check system infrastructure")
    print("   GET /network - Check network connectivity") 
    print("   GET /certificate - Check SSL certificates")
    print("   GET /deployment - Check deployment status")
    print("   GET /health - Overall health check")
    print("\n🌐 Server running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
