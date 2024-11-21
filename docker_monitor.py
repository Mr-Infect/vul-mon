from flask import Flask
import docker

app = Flask(__name__)
client = docker.from_env()

@app.route('/metrics')
def docker_metrics():
    metrics = []
    for container in client.containers.list():
        stats = container.stats(stream=False)
        cpu_usage = calculate_cpu_percentage(stats)
        mem_usage = calculate_memory_percentage(stats)
        metrics.append(f'container_cpu_usage{{name="{container.name}"}} {cpu_usage}')
        metrics.append(f'container_mem_usage{{name="{container.name}"}} {mem_usage}')
    return '\n'.join(metrics)

def calculate_cpu_percentage(stats):
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    cpu_percentage = (cpu_delta / system_cpu_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
    return cpu_percentage

def calculate_memory_percentage(stats):
    mem_usage = stats['memory_stats']['usage']
    mem_limit = stats['memory_stats']['limit']
    mem_percentage = (mem_usage / mem_limit) * 100
    return mem_percentage

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
