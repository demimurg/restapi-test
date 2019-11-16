FROM python:3.7
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV FLASK_APP joke_api
ENV FLASK_ENV development

CMD ["flask", "run", "-h", "0.0.0.0"]