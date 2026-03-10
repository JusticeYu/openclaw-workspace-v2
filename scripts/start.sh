#!/bin/bash

nohup openclaw gateway run --port 5000 --host 0.0.0.0 > /app/work/logs/bypass/dev.log 2>&1 &