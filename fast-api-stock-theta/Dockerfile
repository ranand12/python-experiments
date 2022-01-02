FROM python:3.9-slim
COPY ./htmldirectory /app/htmldirectory
COPY ./main.py /app
COPY ./requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]