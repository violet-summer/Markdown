package org.example.pojo;

/*** 封装响应数据 */
public class Result {
    private Boolean flag;
    private String message;
    public Result() {
    }
    public Result(Boolean flag, String message) {
        this.flag = flag;
        this.message = message;
    }
    public Boolean getFlag() {
        return flag;
    }
    public void setFlag(Boolean flag) {
        this.flag = flag;
    }
    public String getMessage() {
        return message;
    }
    public void setMessage(String message) {
        this.message = message;
    }
}