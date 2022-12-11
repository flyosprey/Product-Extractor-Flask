# start by pulling the python image
FROM python:3.7.5-alpine

WORKDIR /app
# copy the requirements file into the image
COPY requirements.txt requirements.txt

# switch working directory

# install the dependencies and packages in the requirements file
RUN pip install --upgrade pip
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app/flask_app/"
# configure the container to run in an executed manner
CMD [ "python3.7", "flask_app/app.py",  "-m" , "flask", "run"]