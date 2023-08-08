FROM python:3.11.4-slim
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["bash","/app/run_fg_direct.sh"]