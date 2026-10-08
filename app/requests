FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

COPY entrypoint.sh /app/entrypoint.sh

COPY db/entrypoint-db.sh /db/entrypoint-db.sh

RUN chmod +x /app/entrypoint.sh

RUN chmod +x /db/entrypoint-db.sh

RUN pip install --upgrade pip && pip3 install -r requirements.txt

#COPY . /app

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]
