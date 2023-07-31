FROM python:3.8
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
# CMD ["python", "app.py"]
ENTRYPOINT ["bash","/app/run_fg_direct.sh"]