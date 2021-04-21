FROM python:3

WORKDIR /opt/scibowlgreeter

COPY requirements.txt ./
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install discord.py[voice]

CMD [ "python", "scibowlgreeter.py"]