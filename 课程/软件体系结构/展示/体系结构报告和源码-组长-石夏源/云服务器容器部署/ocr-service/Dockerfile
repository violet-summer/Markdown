#FROM ubuntu:24.04
# Copy the current directory contents into the container at /app
#COPY . /app
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9-slim

# Copy your application code
COPY . /app
WORKDIR /app




RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ setuptools
# Install dependencies
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
# Set the working directory
WORKDIR /app
# Update the apt sources list to use Aliyun mirror
RUN echo "deb https://mirrors.aliyun.com/debian/ bullseye main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian-security/ bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib" >> /etc/apt/sources.list

RUN apt update
# Update the package list
RUN apt-get update
RUN apt install libgl1-mesa-glx -y
RUN apt-get install libglib2.0-dev -y
RUN apt-get install libgomp1 libstdc++6 -y

# Make port 8090 available to the world outside this container
EXPOSE 8090
# Run an empty command when the container launches
#CMD ["/bin/sh", "-c", "while :; do sleep 10; done"]
# Run server.py when the container launches
CMD ["python", "server.py"]