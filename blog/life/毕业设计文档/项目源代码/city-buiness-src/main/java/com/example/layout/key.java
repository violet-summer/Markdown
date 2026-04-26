package com.example.layout;

import java.security.SecureRandom;
import java.util.Base64;

public class key {

     public static void main(String[] args){
        byte[] keyBytes = new byte[32]; // HS256 推荐32字节
        new SecureRandom().nextBytes(keyBytes);
        String secretKey = Base64.getEncoder().encodeToString(keyBytes);
        System.out.println(secretKey);
    }

}
