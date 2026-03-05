#!/usr/bin/env python3
"""
Lightweight Docker Container Dashboard
Minimal Flask app for edge IoT devices
"""
import docker
from flask import Flask, jsonify, render_template
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_docker_client():
    """Get Docker client with error handling"""
    try:
        # Set DOCKER_HOST to use unix socket explicitly
        os.environ['DOCKER_HOST'] = 'unix:///var/run/docker.sock'
        
        # Use from_env() which will pick up DOCKER_HOST
        return docker.from_env()
    except Exception as e:
        logging.error(f"Failed to connect to Docker: {e}")
        return None

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/containers')
def get_containers():
    """Get all running containers with their details"""
    client = get_docker_client()
    if not client:
        return jsonify({'error': 'Cannot connect to Docker daemon'}), 500
    
    try:
        containers = client.containers.list(all=True)
        container_list = []
        
        for container in containers:
            stats = None
            if container.status == 'running':
                try:
                    # Get stats without streaming for minimal overhead
                    stats_data = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = stats_data['cpu_stats']['cpu_usage']['total_usage'] - \
                                stats_data['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats_data['cpu_stats']['system_cpu_usage'] - \
                                   stats_data['precpu_stats']['system_cpu_usage']
                    cpu_percent = 0.0
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * len(stats_data['cpu_stats']['cpu_usage'].get('percpu_usage', [1])) * 100.0
                    
                    # Calculate memory usage
                    mem_usage = stats_data['memory_stats'].get('usage', 0)
                    mem_limit = stats_data['memory_stats'].get('limit', 1)
                    mem_percent = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0
                    
                    stats = {
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_usage': mem_usage,
                        'memory_limit': mem_limit,
                        'memory_percent': round(mem_percent, 2)
                    }
                except Exception as e:
                    logging.warning(f"Failed to get stats for {container.name}: {e}")
            
            container_info = {
                'id': container.short_id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.short_id,
                'status': container.status,
                'created': container.attrs['Created'],
                'ports': container.ports,
                'stats': stats
            }
            container_list.append(container_info)
        
        return jsonify({'containers': container_list})
    
    except Exception as e:
        logging.error(f"Error fetching containers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system')
def get_system_info():
    """Get Docker system information"""
    client = get_docker_client()
    if not client:
        return jsonify({'error': 'Cannot connect to Docker daemon'}), 500
    
    try:
        info = client.info()
        return jsonify({
            'containers': info.get('Containers', 0),
            'containers_running': info.get('ContainersRunning', 0),
            'containers_paused': info.get('ContainersPaused', 0),
            'containers_stopped': info.get('ContainersStopped', 0),
            'images': info.get('Images', 0),
            'server_version': info.get('ServerVersion', 'Unknown'),
            'operating_system': info.get('OperatingSystem', 'Unknown'),
            'architecture': info.get('Architecture', 'Unknown'),
            'memory_total': info.get('MemTotal', 0),
            'cpus': info.get('NCPU', 0)
        })
    except Exception as e:
        logging.error(f"Error fetching system info: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

# Made with Bob
