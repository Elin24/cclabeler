FROM python:3.9.9
WORKDIR /workspace
ADD . /workspace
RUN pip install -r requirements.txt
RUN git clone https://github.com/fabricejourdan/cclabeler.git

RUN chown -R 42420:42420 /workspace
ENV HOME=/workspace

WORKDIR /workspace/cclabeler
CMD [ "python" , "manage.py", "runserver" ,"0.0.0.0:8000" ]
