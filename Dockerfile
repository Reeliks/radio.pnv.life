FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg cron && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY push_news.py .

RUN touch /var/log/news.log

ENV NEWS_CRON=/etc/cron.d/news-cron

RUN echo '*/2 * * * * /usr/bin/flock -n /tmp/news-scraper.lock /usr/local/bin/python3 -u /app/push_news.py >> /var/log/news.log 2>&1' \
    > ${NEWS_CRON} && \
    chmod 0644 ${NEWS_CRON} && \
    crontab ${NEWS_CRON}

CMD cron -f && tail -f /var/log/news.log