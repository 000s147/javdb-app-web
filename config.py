import os


# Javdb Token保存文件
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "javdb_token.json")


# Javdb 用户名
USERNAME = ""
# Javdb 密码
PASSWORD = ""


# Javdb 域名
# 国际线路域名长期稳定，国内线路域名可能会改变
# jdforrepam.com    # 国际线路
# apidd.spthgb.com  # 国内线路1
# apidd.czssdgz.com # 国内线路2
API_HOST = "jdforrepam.com"


# 本地WEB服务器IP与端口
HOST = "0.0.0.0"
PORT = 9560


# 版本号
VERSION = "1.1.1"
# 构建日期
BUILD_DATE = "2026-11-14"
# 项目主页
GITHUB_URL = "https://github.com/000s147/javdb-app-web"

