package com.example.user_service.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.core.io.ByteArrayResource;

import java.io.IOException;

@Service
public class OcrService {

    @Autowired
    private RestTemplate restTemplate;

    public String callOcrService(MultipartFile file) throws IOException {
        String ocrServiceUrl = "http://ocr-service/ocr";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        ByteArrayResource fileAsResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        };

        HttpEntity<ByteArrayResource> requestEntity = new HttpEntity<>(fileAsResource, headers);

        ResponseEntity<String> response = restTemplate.postForEntity(ocrServiceUrl, requestEntity, String.class);
        return response.getBody();
    }
}