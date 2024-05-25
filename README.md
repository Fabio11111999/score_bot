This repo contains a python project managed with [poetry](https://python-poetry.org/) 
that runs a telegram bot which keeps the score of a football(soccer) match.

# 🌍 Deploy docker image
- Build the docker image using ```docker build -t fmannino/telegram-score-bot  --platform linux/amd64 .```
- Tag docker image ```docker tag fmannino/telegram-score-bot fmannino/telegram-score-bot:1.0.0```
- Push the docker image ```docker push fmannino/telegram-score-bot:1.0.0```
- Run the docker image ```docker run score_bot_docker_image```