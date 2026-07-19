package com.example.user_service.controller;

import com.example.user_service.service.OcrService;
import io.jsonwebtoken.JwtBuilder;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

@RestController
@RefreshScope
@RequestMapping("/user")
public class UserController {
    private final com.example.user_service.service.UserService userService;

    private final RestTemplate restTemplate;


    private final com.example.user_service.service.OcrService ocrService;


    public UserController(com.example.user_service.service.UserService userService, RestTemplate restTemplate, OcrService ocrService) {
        this.userService = userService;
        this.restTemplate = restTemplate;
        this.ocrService = ocrService;
    }

    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody com.example.user_service.DTO.LoginDTO loginDTO) {

        if (!userService.Login(loginDTO)) {
            return new ResponseEntity<>("用户名或密码错误", HttpStatus.NOT_FOUND);
        } else {

            // 指定签名的时候使用的签名算法，也就是header那部分
            SignatureAlgorithm signatureAlgorithm = SignatureAlgorithm.HS256;

            // 生成JWT的时间
            long expMillis = System.currentTimeMillis() + 7200000;
            Date exp = new Date(expMillis);

            Map<String, Object> claims = new HashMap<>();
            claims.put("username", loginDTO.getUsername());
            // 设置jwt的body
            JwtBuilder builder = Jwts.builder()
                    .setClaims(claims)
                    // 设置签名使用的签名算法和签名使用的秘钥
                    .signWith(signatureAlgorithm, "OCR_BACKEND_SECRET".getBytes(StandardCharsets.UTF_8))
                    // 设置过期时间
                    .setExpiration(exp);

            String token = builder.compact();

            return new ResponseEntity<>(token, HttpStatus.OK);
        }

    }

    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody com.example.user_service.DTO.RegisterDTO registerDTO) {
        if (!userService.Register(registerDTO)) {
            return new ResponseEntity<>("用户名已存在", HttpStatus.BAD_REQUEST);
        } else {


            return new ResponseEntity<>("用户注册成功", HttpStatus.OK);
        }
    }

    @PostMapping("/ocr_run")
    @ResponseBody
    public ResponseEntity<Object> ocrRun(@RequestParam("file") MultipartFile file) throws IOException {
        String flaskServiceUrl = "http://ocr-service/ocr";
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        });

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<String> response = restTemplate.exchange(flaskServiceUrl, HttpMethod.POST, requestEntity, String.class);

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(new String(Objects.requireNonNull(response.getBody()).getBytes(StandardCharsets.ISO_8859_1), StandardCharsets.UTF_8));
    }

    @PostMapping("/process")
    public String processOcr(@RequestParam("file") MultipartFile file) {
        try {
            return ocrService.callOcrService(file);
        } catch (IOException e) {
            e.printStackTrace();
            return "Error processing OCR";
        }
    }
}
