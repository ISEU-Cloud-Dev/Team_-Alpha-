FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiamos todo el contenido actual del proyecto
COPY . /code

# Cambiamos "app.main:app" por "app:app" si corremos desde dentro, o forzamos el path:
ENV PYTHONPATH=/code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]