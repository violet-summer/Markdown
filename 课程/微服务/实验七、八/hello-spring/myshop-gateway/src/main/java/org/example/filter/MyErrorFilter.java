//package org.example.filter;
//
//import com.fasterxml.jackson.databind.ObjectMapper;
//import com.netflix.zuul.ZuulFilter;
//import com.netflix.zuul.context.RequestContext;
//import com.netflix.zuul.exception.ZuulException;
//import org.example.pojo.Result;
//import org.springframework.cloud.netflix.zuul.filters.support.FilterConstants;
//import org.springframework.stereotype.Component;
//
//import javax.servlet.http.HttpServletResponse;
//
//
///*** 自定义错误类型的Zuul过滤器 */
//
//@Component
//public class MyErrorFilter extends ZuulFilter {
//    @Override
//    public String filterType() {
//        return FilterConstants.ERROR_TYPE;
//    }
//    @Override
//    public int filterOrder() {
//        return 0;
//    }
//    @Override
//    public boolean shouldFilter() {
//        return true;
//    }
//    @Override
//    public Object run() throws ZuulException {
//        System.out.println("进入自定义异常过滤器");
//        //1.捕获异常信息
//        RequestContext currentContext = RequestContext.getCurrentContext();
//        HttpServletResponse response = currentContext.getResponse();
//        //ZuulException: 封装其他zuul过滤器执行过程中发现的异常信息
//        ZuulException exception = (ZuulException)currentContext.get("throwable");
//        //2.把异常信息以json格式输出给前端
//        //2.1 构建错误信息
//        Result result = new Result(false,"执行失败："+exception.getMessage());
//        //2.2 转换Result为json字符串
//        ObjectMapper objectMapper = new ObjectMapper();
//        try {
//            String jsonString = objectMapper.writeValueAsString(result);
//            //2.3 把json字符串写回给用户
//            response.setContentType("text/json;charset=utf-8");
//            response.getWriter().write(jsonString);
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
//        return null;
//    }
//}