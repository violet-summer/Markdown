package com.example.layout.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/api/city")
public class CityController {


//
    @GetMapping("/info")
    public String getCityInfo() {
        return "城市信息";
        }

}
