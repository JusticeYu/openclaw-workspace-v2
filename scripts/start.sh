#!/bin/bash

nohup openclaw gateway run --port 5000 --bind lan > /app/work/logs/bypass/dev.log 2>&1 &