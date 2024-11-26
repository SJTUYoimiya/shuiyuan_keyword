# 水源社区一键查成分脚本

## 介绍

背景信息请见[水源帖子](https://shuiyuan.sjtu.edu.cn/t/topic/317129)，本项目基于 Python3 编写，若未安装 Python3，请参考 [miniconda](https://docs.anaconda.com/miniconda/)

Update: 感谢 [@Teruteru](https://shuiyuan.sjtu.edu.cn/t/topic/317129/94) 提供的方法，将本项目改为本地运行，不再需要爬水源，旧版程序放在 `old` 分支中

## 使用方法

1. 请求水源归档
    在 `偏好设置>账户>导出您的数据` 中请求归档，几分钟后 system 会通过水源私聊发送你的归档文件，下载并解压
2. 克隆本仓库到本地. 在你认为合适的路径下执行以下命令
    ```bash
    git clone https://github.com/SJTUYoimiya/shuiyuan_keyword.git
    ```
    将水源归档文件中 `user_archive.csv` 复制到项目根目录下
3. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```
4. 运行脚本. 在项目根目录下执行以下命令
    ```bash
    python shuiyuan_keywords.py
    ```
5. 按 `Enter` 键确认，开始执行脚本
6. 运行结束后，结果会储存在 `<username>` 文件夹中

## 使用方法（old）

1. 克隆本仓库到本地. 在你认为合适的路径下执行以下命令
    ```bash
    git clone https://github.com/SJTUYoimiya/shuiyuan_keyword.git
    ```
2. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```
3. 添加 Cookie 以登录水源. 在浏览器中，打开开发者模式（F12），在`应用>存储>Cookies>https://shuiyuan.sjtu.edu.cn` 中找到 `_t`，将其值复制到 `cookies.txt` 中
    ```bash
    echo "_t=your_token" > cookies.txt
    ```
    将 `your_token` 替换为你的 `_t` 的值

    > 也可手动复制，注意 Cookie 要以 `_t=your_token` 的形式保存。 
    
    > Safari 浏览器进入开发者模式与 Win/Linux 不同. 首先需要按 `⌘,` 进入设置页，在 `高级` 中勾选 `显示网页开发者功能` 打开开发者模式，然后按 `⌘⌥I` 打开开发者菜单，在 `储存空间>Cookie>https://shuiyuan.sjtu.edu.cn` 中找到 Cookie. 
4. 运行脚本. 在项目根目录下执行以下命令
    ```bash
    python crawler/main.py
    ```
5. 按照提示输入用户名
    ```bash
    Enter ur Shuiyuan username: <username>
    ```

    按 `Enter` 键确认，开始执行脚本
6. 运行结束后，结果会储存在 `<username>` 文件夹中
