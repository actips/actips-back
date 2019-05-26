#!/usr/bin/env bash

celery -A actips worker -l info #--concurrency=8