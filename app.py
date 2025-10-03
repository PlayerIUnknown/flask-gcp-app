from flask import Flask, jsonify, render_template_string
import psutil
import platform
import os
import subprocess
import json
from datetime import datetime
import socket

app = Flask(__name__)

# Dashboard HTML template with modern styling
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask GCP App - Infrastructure Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.8;
            color: #b0b0b0;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(42, 42, 74, 0.8);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        
        .card h3 {
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 1.4rem;
            border-bottom: 2px solid #9c88ff;
            padding-bottom: 8px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #b0b0b0;
        }
        
        .metric-value {
            font-weight: 600;
            color: #9c88ff;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-running {
            background-color: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        
        .status-warning {
            background-color: #FF9800;
            box-shadow: 0 0 10px rgba(255, 152, 0, 0.5);
        }
        
        .status-error {
            background-color: #F44336;
            box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #9c88ff, #7c4dff);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .deployment-info {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            grid-column: 1 / -1;
            border: 1px solid rgba(156, 136, 255, 0.3);
        }
        
        .deployment-info h3 {
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }
        
        .deployment-step {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #9c88ff;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #9c88ff, #7c4dff);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: block;
            margin: 20px auto;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .timestamp {
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Flask GCP Infrastructure Dashboard</h1>
            <p>Real-time monitoring of your deployment pipeline and system performance</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Performance -->
            <div class="card">
                <h3>🖥️ System Performance</h3>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value">{{ cpu_percent }}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ cpu_percent }}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Memory Usage</span>
                    <span class="metric-value">{{ memory_percent }}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ memory_percent }}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Disk Usage</span>
                    <span class="metric-value">{{ disk_percent }}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ disk_percent }}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Load Average</span>
                    <span class="metric-value">{{ load_avg }}</span>
                </div>
            </div>
            
            <!-- System Information -->
            <div class="card">
                <h3>ℹ️ System Information</h3>
                <div class="metric">
                    <span class="metric-label">Hostname</span>
                    <span class="metric-value">{{ hostname }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Platform</span>
                    <span class="metric-value">{{ platform }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Python Version</span>
                    <span class="metric-value">{{ python_version }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Flask Version</span>
                    <span class="metric-value">{{ flask_version }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">{{ uptime }}</span>
                </div>
            </div>
            
            <!-- Network Information -->
            <div class="card">
                <h3>🌐 Network Information</h3>
                <div class="metric">
                    <span class="metric-label">Internal IP</span>
                    <span class="metric-value">{{ internal_ip }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Zone</span>
                    <span class="metric-value">{{ gcp_zone }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">VM Name</span>
                    <span class="metric-value">{{ vm_name }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Network I/O</span>
                    <span class="metric-value">{{ network_io }}</span>
                </div>
            </div>
            
            <!-- Service Status -->
            <div class="card">
                <h3>⚙️ Service Status</h3>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-running"></span>Flask App
                    </span>
                    <span class="metric-value">Running</span>
                </div>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-running"></span>Gunicorn
                    </span>
                    <span class="metric-value">Active</span>
                </div>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-running"></span>Nginx
                    </span>
                    <span class="metric-value">Active</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Connections</span>
                    <span class="metric-value">{{ active_connections }}</span>
                </div>
            </div>
            
            <!-- Deployment Pipeline -->
            <div class="card deployment-info">
                <h3>🚀 CI/CD Pipeline</h3>
                <div class="deployment-step">
                    <strong>1. Code Repository</strong><br>
                    <small>Git repository connected to Cloud Build</small>
                </div>
                <div class="deployment-step">
                    <strong>2. Cloud Build Trigger</strong><br>
                    <small>Automated build on push to main branch</small>
                </div>
                <div class="deployment-step">
                    <strong>3. VM Deployment</strong><br>
                    <small>SSH to web-server-01 in asia-south2-a</small>
                </div>
                <div class="deployment-step">
                    <strong>4. Service Restart</strong><br>
                    <small>Systemd service 'myapp' restarted</small>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Deploy</span>
                    <span class="metric-value">{{ last_deploy }}</span>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
        
        <div class="timestamp">
            Last updated: {{ current_time }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def hello_world():
    return '<h1>Hello, Google Cloud! Your application (+ CI/CD) is live!!!!</h1>'

@app.route('/dashboard')
def dashboard():
    """Comprehensive infrastructure and performance dashboard"""
    
    # System performance metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 'N/A'
    
    # System information
    hostname = socket.gethostname()
    platform_info = f"{platform.system()} {platform.release()}"
    python_version = platform.python_version()
    
    # Network information
    internal_ip = socket.gethostbyname(hostname)
    
    # Get network I/O
    net_io = psutil.net_io_counters()
    network_io = f"↑{net_io.bytes_sent // (1024*1024)}MB ↓{net_io.bytes_recv // (1024*1024)}MB"
    
    # GCP specific information (from cloudbuild.yaml)
    gcp_zone = "asia-south2-a"
    vm_name = "web-server-01"
    
    # Service status simulation (in real deployment, you'd check actual service status)
    active_connections = len(psutil.net_connections())
    
    # Get Flask version
    try:
        import flask
        flask_version = flask.__version__
    except:
        flask_version = "Unknown"
    
    # Get uptime
    boot_time = psutil.boot_time()
    uptime_seconds = psutil.time.time() - boot_time
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime = f"{uptime_hours}h {uptime_minutes}m"
    
    # Current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Last deploy time (simulated - in real scenario, you'd get this from git or deployment logs)
    last_deploy = "Just now"  # This could be enhanced to read from git logs or deployment metadata
    
    return render_template_string(DASHBOARD_TEMPLATE,
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_percent=disk.percent,
        load_avg=round(load_avg, 2) if load_avg != 'N/A' else 'N/A',
        hostname=hostname,
        platform=platform_info,
        python_version=python_version,
        flask_version=flask_version,
        uptime=uptime,
        internal_ip=internal_ip,
        gcp_zone=gcp_zone,
        vm_name=vm_name,
        network_io=network_io,
        active_connections=active_connections,
        last_deploy=last_deploy,
        current_time=current_time
    )

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for real-time metrics (for potential future enhancements)"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Run the app on all available network interfaces (0.0.0.0) on port 80
    app.run(host='0.0.0.0', port=8080)
