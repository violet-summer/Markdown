package org.example.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/*** 用户Controller */
@RequestMapping("/user")
@RestController   // @RestController=@RequestMapping + @ResponseBody
public class HelloController {
    @RequestMapping("/hello")
    public String say(){
        return ("Hello, User!");
    }
}