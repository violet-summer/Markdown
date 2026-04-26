## 处理excel数据收获2024/4/29



1. **Matplotlib**：使用了Matplotlib库来创建和保存图形。了解了如何使用`plt.xticks()`来设置x轴的刻度和标签。

2. **Python列表**：你了解了如何创建和修改Python列表，包括如何使用`range()`函数和列表切片。

3. **Python正则表达式**：你使用了Python的`re`模块来处理字符串。你了解了如何使用`re.sub()`和`re.search()`函数，以及如何编写正则表达式来匹配特定的字符序列。

4. **Python文件操作**：你了解了如何使用`os.path.join()`来构造文件路径，以及如何处理文件名中的特殊字符。

5. **Python异常和警告**：你遇到了一个关于字体的警告，你了解了这个警告的原因以及如何解决这个问题。

6. **Python数据处理**：你处理了一些CSV文件，这些文件包含了日期和数值。你可能使用了Python的`csv`模块或者`pandas`库来读取和处理这些数据。

# [numpy 和 pandas ](https://benpaodewoniu.github.io/2018/12/17/python39/)

### [pandas](https://zhuanlan.zhihu.com/p/59307125)

loc、iloc

# [Matplotlib](https://www.matplotlib.org.cn/)2D图形库



## SQLite

## json文件

```
# 获取所有的数值
values = [item[1] for sublist in data for item in sublist['data']]
```

从左往右；data是json文件load；sublist为data数据项；item为sublist的key为data的数据项，item[1]取data的第二项
