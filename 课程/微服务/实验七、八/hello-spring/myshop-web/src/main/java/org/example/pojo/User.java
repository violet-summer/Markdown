package org.example.pojo;

import javax.persistence.*;
import java.io.Serializable;

/**
 * 用户实体
 */
@Entity
@Table(name = "arc_user")
public class User implements Serializable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;//编号
    private String username;//用户名
    private String password;//密码
    private String sex;//性别
    private Double money;//余额
    public User() {
    }
    public User(Integer id, String username, String password, String sex, Double money) {
        this.id = id;
        this.username = username;
        this.password = password;
        this.sex = sex;
        this.money = money;
    }
    public Integer getId() {        return id;    }
    public void setId(Integer id) {        this.id = id;    }
    public String getUsername() {        return username;    }
    public void setUsername(String username) {        this.username = username;    }
    public String getPassword() {        return password;    }
    public void setPassword(String password) {        this.password = password;    }
    public String getSex() {        return sex;    }
    public void setSex(String sex) {        this.sex = sex;    }
    public Double getMoney() {        return money;    }
    public void setMoney(Double money) {        this.money = money;    }

    public String toString() {return username;}
}
