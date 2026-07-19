FROM openjdk:21-jdk-buster
COPY target/common-utils-0.0.1-SNAPSHOT.jar /app/common-utils.jar
COPY . /app/
WORKDIR /app/
EXPOSE 8086
ENTRYPOINT ["java", "-jar", "/app/common-utils.jar"]
