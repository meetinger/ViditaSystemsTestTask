FROM python:3.10-bullseye
RUN mkdir "/docker_app"
WORKDIR "/docker_app"
COPY ".env_docker" ".env"
COPY . .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD ["python", "-u", "main.py"]