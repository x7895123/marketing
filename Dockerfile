#docker exec -it $(docker ps -f name=arena_calc-bonus --format "{{.ID}}") /bin/sh
# docker rmi $(docker images | grep marketing)

#FROM python:3.8.7
FROM python:3.11.0-alpine3.16

LABEL company="VS"

RUN apk add --no-cache \
        tzdata\
    && echo "Asia/Almaty" > /etc/timezone

ENV LANG=C.UTF-8 \
    TZ=Asia/Almaty


# Set the working directory to /app
WORKDIR /app


# Copy the current directory contents into the container at /app
ADD ./app/ /app


ADD ./requirements.txt /app

# Install GCC
#RUN apk update && apk add --no-cache python3-dev \
#                        gcc \
#                        libc-dev
# RUN apk add --no-cache python3-dev \
#                       gcc \
#                       libc-dev
# RUN apk add --no-cache gcc libc-dev
#RUN apk add  --no-cache libffi-dev build-base


# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir --upgrade pip
#RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN python main.py