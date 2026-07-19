FROM openjdk:21-jdk-buster
COPY target/ocr-gateway-0.0.1-SNAPSHOT.jar /app/ocr-gateway.jar
WORKDIR /app/
EXPOSE 8087
ENTRYPOINT ["java", "-jar", "/app/ocr-gateway.jar"]