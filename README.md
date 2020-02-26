# Metrics and Structured Logs Demo

This Demo uses:

- prometheus
- grafana
- loki

to demo Structured logs and metrics. This Repo is for teaching feel free to take
and learn.

The demo webserver is a inventory of beer.

- The code all runs in memory to be easily reset
- has no permissions model
- is just a http wrapper and metrics collector around an array

## requirements

```
docker plugin install  grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
```

## Run Demo

```
docker-compose up -d --build
```
