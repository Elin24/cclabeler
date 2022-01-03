FROM python:3.9.9
LABEL maintainer="datalab-mi"

RUN mkdir /workspace && chown -R 42420:42420 /workspace
WORKDIR /workspace
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R 42420:42420 /workspace
CMD [ "python" , "manage.py", "runserver" ,"0.0.0.0:8000" ]
