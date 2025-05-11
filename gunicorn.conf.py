
import multiprocessing

bind = "0.0.0.0:5002"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
