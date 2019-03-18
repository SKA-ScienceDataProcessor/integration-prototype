#!/usr/bin/env bash
watch -n 1 docker service ls --filter name=PB --format \"{{.ID}} - {{.Name}}\"
