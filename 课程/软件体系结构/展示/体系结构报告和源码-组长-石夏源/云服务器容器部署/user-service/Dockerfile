FROM openjdk:21-jdk-buster
COPY target/user-service-0.0.1-SNAPSHOT.jar user-service.jar
EXPOSE 8085
ENTRYPOINT ["java", "-jar", "/user-service.jar"]