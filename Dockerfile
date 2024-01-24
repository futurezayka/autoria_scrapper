FROM python:3.10
WORKDIR /scrapper
COPY requirements.txt /scrapper/
RUN pip install --no-cache-dir -r requirements.txt
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /scrapper/wait-for-it.sh
RUN apt-get update && apt-get install -y postgresql-client
COPY . /scrapper/
RUN chmod -R 755 /scrapper
CMD ["./wait-for-it.sh", "db:5432", "--", "python3", "./scraper.py"]