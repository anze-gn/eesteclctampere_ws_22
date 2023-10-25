FROM python:alpine

# install dependencies from requirements.txt
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# copy all files
COPY . /

# run bot
CMD python GNHTTbot.py
