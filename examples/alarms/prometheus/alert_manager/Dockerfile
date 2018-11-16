FROM prom/alertmanager
ADD alerts.yml /etc/
CMD ["--config.file=/etc/alerts.yml", "--storage.path=/alertmanager"]
