package com.example.filter;

import com.example.context.BaseContext;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

// 全局请求过滤器
@Component
public class GlobalRequestFilter implements GlobalFilter, Ordered {


    private static final String SECRET_KEY = "OCR_BACKEND_SECRET";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {

        // 打印请求路径
        String path = exchange.getRequest().getURI().getPath();
        System.out.println("Request Path: " + path);

        // 定义不需要处理的路径
        List<String> excludedPaths = Arrays.asList("/user/login", "/user/register");

        // 如果请求路径在不处理的路径列表中，直接跳过后续的过滤逻辑
        if (excludedPaths.contains(path)) {
            return chain.filter(exchange);
        }

        // jwt过滤
        String token = exchange.getRequest().getHeaders().getFirst("token");
        System.out.println("Token: " + token);
        if (token == null || token.equals("")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            System.out.println("Token is null or empty");
            return exchange.getResponse().setComplete();
        }

        try {
            Claims claims = Jwts.parser()
                    .setSigningKey(SECRET_KEY.getBytes(StandardCharsets.UTF_8))
                    .parseClaimsJws(token)
                    .getBody();
            String username = claims.get("username").toString();
            // 存入上下文中
            BaseContext.setCurrentId(username);
            // 将解析出的信息存入请求头，供后续路由使用
            exchange.getRequest().mutate()
                    .header("username", claims.getSubject())
                    .build();
        } catch (Exception e) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return -1; // 优先级
    }
}
