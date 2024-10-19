# 水源查成分

## 背景

在用 [`@Ink_mirror`](https://shuiyuan.sjtu.edu.cn/u/ink_mirror/summary) 老师的关键词脚本时，发现今年的成分表被签名档污染了，所以重新写了一个

排除列表：

- 签名档
- 多媒体内容：图片、视频、音频
- 链接：超链接、附件、`@` 提及
- 代码、公式
- 嵌入视频/链接块
- 水源内引用块

## 使用方法

1. 克隆本仓库
2. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```
3. 在 `cookies.txt` 中填入你的 `_t`，可在浏览器开发者模式中查看
4. 运行脚本
    ```bash
    python main.py
    ```
4. 按照提示输入用户名
5. 在 `data` 文件夹中查看结果