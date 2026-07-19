//package org.example.filter;
//
//import com.netflix.zuul.ZuulFilter;
//import com.netflix.zuul.exception.ZuulException;
//import org.springframework.cloud.netflix.zuul.filters.support.FilterConstants;
//import org.springframework.stereotype.Component;
//
///**
// * 第二个Zuul过滤器MyFilter2
// */
//
//@Component
//public class MyFilter2 extends ZuulFilter {
//    //过滤器类型
//    @Override
//    public String filterType() {
//        return FilterConstants.PRE_TYPE;
//    }
//    //过滤器执行顺序，数值越大优先级越低
//    @Override
//    public int filterOrder() {
//        return 2;
//    }
//    @Override
//    public boolean shouldFilter() {
//        return true;
//    }
//    @Override
//    public Object run() throws ZuulException {
//        System.out.println("执行MyFilter2过滤器");
//        return null;
//    }
//}
