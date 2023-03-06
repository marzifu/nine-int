FROM python:3.12.0

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-chace-dir -r requirements.ext

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
