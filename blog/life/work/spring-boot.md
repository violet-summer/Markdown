记得保留初始化数据库得代码，便于迁移，不然换机器得时候数据库重新建表很麻烦

# mybatis-plus

这个玩意有了自动建表得main-java代码方式，不需要死扣那个麻烦的配置文件


# JWT（JSON Web Token）

1. 是一种用于安全传递信息的令牌格式，常用于用户认证和授权。
2. 生成：后端根据用户信息生成一个加密的 token，通常包含用户 ID、过期时间等。
3. 解析：后端或前端读取 token，提取其中的信息（如用户身份）。
4. 验证：检查 token 是否有效（如签名正确、未过期），防止伪造和非法访问。
5. JWT 让前后端可以安全地传递用户身份和权限信息，**无需每次都查数据库**。

# 关于yaml字段能够被解析

源于我一直认为yaml文件的解析是自带的，只要安装各种驱动就能自动解析其配置，实际上这个玩意解析需要一个单独依赖。各种数据库驱动并不会提供这个功能。

你说得完全正确！`spring-boot-starter-data-jpa` **确实包含了** `spring-boot-starter-jdbc` 的所有功能，并且在此基础上增加了 JPA 的支持。让我详细解释一下这个依赖关系链：

## 一、依赖关系层次

```
spring-boot-starter-data-jpa
├── spring-boot-starter-jdbc (传递依赖)
│   ├── HikariCP (连接池)
│   ├── spring-jdbc
│   └── ... 
├── spring-boot-starter (传递依赖)
│   └── snakeyaml (YAML解析)
├── hibernate-core (ORM框架)
├── spring-data-jpa
└── ...
```

所以当你添加 `spring-boot-starter-data-jpa` 时，它已经通过传递依赖包含了：
1. **`snakeyaml`** - 解析 YAML 文件
2. **`spring-boot-starter-jdbc`** - 提供数据源自动配置
3. **`DataSourceAutoConfiguration`** - 读取并应用 `spring.datasource` 配置

## 二、为什么 `spring-boot-starter-data-jpa` 就能解析 YAML？

### 1. 自动配置的触发条件
Spring Boot 的自动配置是基于 classpath 下的类来判断的：

```java
// 在 DataSourceAutoConfiguration 中
@AutoConfiguration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    // ...
}
```

当你的 classpath 中有：
- `DataSource.class` (来自 `spring-jdbc` 或 `HikariCP`)
- JPA 相关类 (来自 `hibernate-core` 或 `spring-data-jpa`)

自动配置就会被触发，开始读取 YAML 中的 `spring.datasource` 配置。

### 2. 完整的依赖树验证
你可以通过以下命令查看真实的依赖关系：
```bash
mvn dependency:tree -Dincludes=org.springframework.boot
```

输出会显示：
```
[INFO] +- org.springframework.boot:spring-boot-starter-data-jpa:jar:3.x.x
[INFO]    +- org.springframework.boot:spring-boot-starter-jdbc:jar:3.x.x
[INFO]    |  +- com.zaxxer:HikariCP:jar:5.x.x
[INFO]    |  +- org.springframework:spring-jdbc:jar:6.x.x
[INFO]    +- org.springframework.boot:spring-boot-starter:jar:3.x.x
[INFO]       +- org.yaml:snakeyaml:jar:2.x
```

## 三、实际使用的依赖配置

### 最小配置（使用 JPA）
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.33</version>
    <scope>runtime</scope>
</dependency>
```

### YAML 配置示例
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
  
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true
```

## 四、关键点总结

1. **`spring-boot-starter-data-jpa` 是“全家桶”**：
   - 它包含了 JDBC 的所有功能
   - 额外增加了 JPA、Hibernate 的支持
   - 自动包含了 YAML 解析能力（通过传递依赖）

2. **YAML 解析的底层原理不变**：
   - 仍然是 `snakeyaml` 负责解析文件
   - 仍然是 `@ConfigurationProperties` 负责绑定到配置类
   - 仍然是自动配置类负责创建 Bean

3. **选择建议**：
   - 如果**需要 JPA**（实体映射、Repository 等）→ 用 `spring-boot-starter-data-jpa`
   - 如果**只需要 JDBC**（直接使用 JdbcTemplate）→ 用 `spring-boot-starter-jdbc`（更轻量）

4. **为什么你的 YAML 配置能生效？**
   因为 `spring-boot-starter-data-jpa` 带来了：
   - `snakeyaml` → 读取 YAML
   - `DataSourceAutoConfiguration` → 创建数据源
   - `DataSourceProperties` → 绑定配置属性

所以你的理解完全正确：**`spring-boot-starter-data-jpa` 这个依赖已经提供了完整的 YAML 解析和数据源配置功能**，不需要额外添加 `spring-boot-starter-jdbc`。


# 关于spring可以持续运行

```xml
<dependency>  
    <groupId>org.springframework.boot</groupId>  
    <artifactId>spring-boot-starter-web</artifactId>  
</dependency>
```

如果没有这依赖，spring项目会启动成功后又自动退出而不是持续监听。


# open-api

## 使用

1. 其根据yaml生成的内容会生成在Java项目的target类之中，不会污染源码，可以直接在src目录下引用。
2. 关于控制器接口，生成器会生成对应的api接口类在target之中，直接在src中实现即可/当然也可以直接用对象自定义接口即可，生成器会有接口类的默认实现。

## 字段命名

只需要在yaml文件中配置好蛇形命名法就好，生成器会自动做到转为驼峰java类的属性的。

## bug

### number 类型

报错场景，我在yaml中定义了number类型，但是在java中不能直接转为double类型。直接原因就是生成器默认行为是把number对应到`BigDecimal`对象，而对象不可以直接拆箱为double。
#### 错误原因总结

- **错误本质**：代码中使用反射调用 `getX()` 返回的是 `BigDecimal` 对象，但随后试图通过 `(double)` 强制转换将其变为基本类型 `double`。Java 不支持这种直接转换，因为 `BigDecimal` 是对象类型，不是 `Double` 包装类，无法自动拆箱。
- **根本来源**：OpenAPI Generator 默认将 OpenAPI 规范中的 `number` 类型映射为 `BigDecimal`，以保持精度。但你的反射代码未正确处理 `BigDecimal`，未调用 `.doubleValue()` 方法获取 `double` 值。

#### BigDecimal 类型优势

1. **精度可控**：`BigDecimal` 可以精确表示任意精度的十进制数，不会出现二进制浮点数（如 `float`、`double`）的精度丢失问题。例如 `0.1 + 0.2` 在 `double` 中结果为 `0.30000000000000004`，而 `BigDecimal` 能精确得到 `0.3`。
2. **适合金融、科学计算**：在需要精确结果的场景（如货币计算、坐标转换、物理量计算）中，`BigDecimal` 是标准选择。
3. **丰富的方法**：提供加减乘除、比较、取整、小数位数控制等精确运算方法，且可指定舍入模式。
4. **与数据库类型匹配**：数据库中的 `DECIMAL`、`NUMERIC` 类型通常映射为 `BigDecimal`，避免精度损失。

尽管 `BigDecimal` 运算速度稍慢于基本类型，但在精度优先的场景下，其优势远大于性能损耗。你的 SVG 坐标计算涉及浮点运算，使用 `BigDecimal` 可以确保坐标精确，但需要在代码中通过 `.doubleValue()` 或 `.intValue()` 等正确提取数值。



# proto

## 安装

需要本地的protoc编译器，直接解压压缩包，在项目配置中使用路径指定exe执行文件使用即可。

## 序列化

在解析message的时候，结果是proto的类型对象，应该使用proto库的序列化方式才可以正确存入数据库的`json`字段属性。

通信两端都要利用proto解析，避免一端使用自带的json解析库。