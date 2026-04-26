package com.example.layout.config;

import com.example.layout.utils.security;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collections;

public class JwtAuthenticationFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (StringUtils.hasText(header) && header.startsWith("Bearer ")) {
            System.out.println("token: " + header);
            String token = header.substring(7);
            try {
                String userIdStr = security.decodeAccessToken(token);
                System.out.println("Extracted user ID from token: " + userIdStr);
                if (userIdStr != null) {
                    Long userId = Long.valueOf(userIdStr);
                    UsernamePasswordAuthenticationToken authentication =
                            new UsernamePasswordAuthenticationToken(userId, null, Collections.emptyList());
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                }
            } catch (Exception e) {
                // token无效，忽略，后续可自定义异常处理
                System.out.println("token无效: " + e.getMessage());
            }
        }
        filterChain.doFilter(request, response);
    }
}
