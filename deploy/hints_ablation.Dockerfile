# Hints ablation: the image the held-out test numbers come from (crmroute:local
# 0374d9c6e7b7, commit 7beda40) with only agent/app/config.py and agent/app/prompts.py
# replaced. Both files are unchanged since 7beda40 apart from the CRMROUTE_TASK_HINTS
# flag, so the flag is the only change to the measured agent.
#   docker tag 0374d9c6e7b7 crmroute:test-7beda40   # BuildKit needs a tag, not an image id
#   docker build -f deploy/hints_ablation.Dockerfile --build-arg BASE=crmroute:test-7beda40 -t crmroute:nohints .
ARG BASE
FROM ${BASE}
COPY agent/app/config.py agent/app/prompts.py /srv/agent/app/
RUN rm -f /srv/agent/app/__pycache__/config.*.pyc /srv/agent/app/__pycache__/prompts.*.pyc
