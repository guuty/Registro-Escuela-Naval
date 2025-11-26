# gunicorn.conf.py
timeout = 120  # Aumentar de 30 a 120 segundos
workers = 2
bind = "0.0.0.0:10000"