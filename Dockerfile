FROM python

WORKDIR /test/backend

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]