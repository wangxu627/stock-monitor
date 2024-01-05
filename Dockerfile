FROM python:3.11.4
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ENTRYPOINT ["bash","/app/run_fg_direct.sh"]