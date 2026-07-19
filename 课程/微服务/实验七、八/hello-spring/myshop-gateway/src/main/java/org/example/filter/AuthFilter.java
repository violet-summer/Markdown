//package org.example.filter;
//
//import com.netflix.zuul.ZuulFilter;
//import com.netflix.zuul.context.RequestContext;
//import com.netflix.zuul.exception.ZuulException;
//import org.springframework.cloud.netflix.zuul.filters.support.FilterConstants;
//import org.springframework.stereotype.Component;
//
//import javax.servlet.http.HttpServletRequest;
//import javax.servlet.http.HttpServletResponse;
//
///*** 权限控制过滤器 */
//
//@Component
//public class AuthFilter extends ZuulFilter {
//    @Override
//    public String filterType() {
//        return FilterConstants.PRE_TYPE;
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
//        //模拟执行异常
//        //int i = 10/0;
//        //1.获取当前请求的参数：token=user
//        RequestContext currentContext = RequestContext.getCurrentContext();
//        HttpServletRequest request = currentContext.getRequest();
//        HttpServletResponse response = currentContext.getResponse();
//        String token = request.getParameter("token");
//        if(!"user".equals(token)){
//            //不转发微服务，给用户响应
//            currentContext.setSendZuulResponse(false);
//            //设置401状态码
//            response.setStatus(401);
//            return null;
//        }
//        //继续转发
//        return null;
//    }
//}
