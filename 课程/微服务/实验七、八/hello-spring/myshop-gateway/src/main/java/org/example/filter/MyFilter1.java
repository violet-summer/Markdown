//package org.example.filter;
//
//import com.netflix.zuul.ZuulFilter;
//import com.netflix.zuul.exception.ZuulException;
//import org.springframework.cloud.netflix.zuul.filters.support.FilterConstants;
//import org.springframework.stereotype.Component;
//
///**
// * 第一个Zuul过滤器MyFilter1
// */
//
//@Component
//public class MyFilter1 extends ZuulFilter {
//    //过滤器类型
//    @Override
//    public String filterType() {
//        return FilterConstants.PRE_TYPE;
//    }
//    //过滤器执行顺序，数值越大优先级越低
//    @Override
//    public int filterOrder() {
//        return 1;
//    }
//    //是否让该过滤器生效
//    @Override
//    public boolean shouldFilter() {
//        return true;
//    }
//    //过滤逻辑代码
//    @Override
//    public Object run() throws ZuulException {
//        System.out.println("执行MyFilter1过滤器");
//        return null;
//    }
//}
