import json
import os
import time
import hashlib
import requests
from typing import Optional
import config as cfg
from utils import show_log


class JavJHSClient:
    API = f"https://{cfg.API_HOST}/api"

    SECRET = (
        "71cf27bb3c0bcdf207b64abecddc970098c7421ee7203b9cdae54478478a199e7"
        "d5a6e1a57691123c1a931c057842fb73ba3b3c83bcd69c17ccf174081e3d8aa"
    )

    def __init__(self):
        self.username = cfg.USERNAME
        self.password = cfg.PASSWORD
        self.token: Optional[str] = None

        self.session = requests.Session()
        self.session.headers.update({
            "user-agent": "Dart/3.5 (dart:io)",
            "accept-language": "zh-TW",
            "host": cfg.API_HOST,
        })

        self._load_token()

    # ===== token 持久化 =====
    def _load_token(self):
        if os.path.exists(cfg.TOKEN_FILE):
            with open(cfg.TOKEN_FILE, "r", encoding="utf-8") as f:
                self.token = json.load(f).get("token")

            if self.token:
                self.session.headers["authorization"] = f"Bearer {self.token}"

    def _save_token(self):
        with open(cfg.TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": self.token}, f)

    # ===== jdsignature =====
    def build_jdsignature(self):
        curr = int(time.time())
        raw = f"{curr}{self.SECRET}"
        md5_val = hashlib.md5(raw.encode()).hexdigest()
        return f"{curr}.lpw6vgqzsp.{md5_val}"

    # ===== 登录 =====
    def login(self):
        """
        return: (token, jdsignature)
        """
        url = (
            f"{self.API}/v1/sessions"
            f"?username={self.username}"
            f"&password={self.password}"
            f"&device_uuid=08d5cd7f-af0f-4864-9efd-d3f87691112a"
            f"&device_name=XiaoMi"
            f"&device_model=realme/RMX6688"
            f"&platform=android"
            f"&system_version=14"
            f"&app_version=official"
            f"&app_version_number=1.9.35"
            f"&app_channel=official"
        )

        jdsignature = self.build_jdsignature()
        headers = {"jdsignature": jdsignature}

        r = self.session.post(url, headers=headers, timeout=15)
        r.raise_for_status()

        data = r.json()
        self.token = data.get("data", {}).get("token", "")
        if not self.token:
            raise RuntimeError("登录失败：无法获取 token，请检查账号密码或网络")

        self.session.headers["authorization"] = f"Bearer {self.token}"
        self._save_token()
        return self.token, jdsignature

    # ===== 核心请求封装 =====
    def _request(self, method: str, path: str, **kwargs):
        """
        统一的请求核心逻辑，处理签名、Token验证、重登录以及网络重试
        """
        max_retries = 3  # 总尝试次数（含令牌失效后的重试）
        url = f"{self.API}{path}"
        kwargs.setdefault("timeout", 15)

        for attempt in range(max_retries):
            try:
                # 1. 若无 token，先登录（若登录失败会抛出异常）
                if not self.token:
                    self.login()

                # 2. 准备请求头和签名
                headers = kwargs.pop("headers", {})
                headers["jdsignature"] = self.build_jdsignature()
                kwargs["headers"] = headers

                show_log(f"[{method}] request url: {url}")
                if "params" in kwargs and kwargs["params"]:
                    show_log(f"request params: {kwargs['params']}")

                # 3. 发送请求
                r = self.session.request(method, url, **kwargs)

                # 4. 尝试解析 JSON
                try:
                    data = r.json()
                except ValueError:
                    r.raise_for_status()
                    return r.text

                # 5. 检查令牌是否失效
                is_token_expired = False
                if r.status_code == 401:
                    is_token_expired = True
                elif isinstance(data, dict):
                    if data.get("action") == "JWTVerificationError" or data.get("success") == 0:
                        msg = str(data.get("message", ""))
                        if "登" in msg or "JWT" in msg or "token" in msg:
                            is_token_expired = True

                # 6. 令牌失效 → 重新登录，然后继续下一次循环（消耗一次尝试次数）
                if is_token_expired:
                    show_log("⚠️ 检测到 Token 失效，尝试重新登录...")
                    self.login()  # 登录失败会抛异常，跳出循环
                    # 登录成功后，使用新 token 重新发起请求
                    continue  # 跳至下一次 for 循环

                # 7. 正常响应
                r.raise_for_status()
                return data

            except requests.exceptions.Timeout as e:
                # 超时重试（指数退避）
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    show_log(f"请求超时（{e}），{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

            except requests.exceptions.ConnectionError as e:
                # 连接错误重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    show_log(f"连接错误（{e}），{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

            except requests.HTTPError as e:
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    show_log(f"服务端错误 {e.response.status_code}，{wait_time}秒后重试")
                    time.sleep(wait_time)
                    continue
                raise

            except Exception as e:
                # 其他异常（包括登录失败、HTTPError等）不重试，直接抛出
                show_log(f"请求发生错误: {e}")
                raise

        # 理论上循环结束而未返回的情况（如所有尝试都遇到令牌失效且未抛出），抛出错误
        raise RuntimeError("重试次数已用尽，未成功获取数据")

    # ===== 请求封装 =====
    def _get(self, path, params=None):
        return self._request("GET", path, params=params)

    def _post(self, path, data=None, json=None, files=None, params=None):
        return self._request("POST", path, data=data, json=json, files=files, params=params)

    def _delete(self, path, data=None, json=None, files=None, params=None):
        return self._request("DELETE", path, data=data, json=json, files=files, params=params)

    def _patch(self, path, data=None, json=None, params=None):
        return self._request("PATCH", path, data=data, json=json, params=params)

    # 👇 追加以下新方法 👇
    def collect_actor(self, actor_id: str, action: str = "collect"):
        """
        收藏或取消收藏演员
        :param action: 'collect' 表示收藏，'uncollect' 表示取消收藏
        """
        return self._post(
            f"/v1/actors/{actor_id}/collect_actions",
            files={"name": (None, action)}
        )

    def get_collected_actors(self, req_type: str = "all", page: int = 1, limit: int = 30):
        """
        获取收藏的演员列表
        :param req_type: 'all'(全部), '0'(有码), '1'(无码), '2'(欧美)
        """
        return self._get(
            "/v1/users/collected_actors",
            {
                "type": req_type,
                "page": page,
                "limit": limit
            }
        )

    def batch_uncollect_actors(self, actor_ids: list):
        """
        批量取消收藏演员
        :param actor_ids: 演员 ID 列表，例如 ['K4W06', 'PQErN']
        """
        ids_str = ",".join(actor_ids)
        return self._delete(
            "/v1/actors/batch_uncollection",
            files={"ids": (None, ids_str)}
        )

    def top250(self, page=1, limit=50, req_type="all", type_value=""):
        """获取 Top 250 榜单"""
        return self._get(
            "/v1/movies/top",
            {
                "start_rank": 1,
                "type": req_type,
                "type_value": type_value,
                "ignore_watched": "false",
                "page": page,
                "limit": limit
            }
        )

    # 👇 追加下面这个新方法：
    def playback_rankings(self, period="daily", filter_by="all"):
        return self._get(
            "/v1/rankings/playback",
            {
                "period": period,
                "filter_by": filter_by
            }
        )

    def get_hot_reviews(self, period: str = "latest", page: int = 1, limit: int = 24):
        """获取各周期热门短评"""
        return self._get(
            "/v1/reviews/hotly",
            {
                "period": period,
                "page": page,
                "limit": limit
            }
        )

    def collect_code(self, code_id: str, action: str = "collect"):
        """
        收藏或取消收藏番号
        :param action: 'collect' 表示收藏，'uncollect' 表示取消收藏
        """
        return self._post(
            f"/v1/codes/{code_id}/collect_actions",
            files={"name": (None, action)}
        )

    def get_collected_codes(self, page: int = 1, limit: int = 30):
        """
        获取收藏的番号列表 (对应抓包的 URL 可能为 /v1/users/collected_codes)
        """
        return self._get(
            "/v1/users/collected_codes",
            {
                "page": page,
                "limit": limit
            }
        )

    def batch_uncollect_codes(self, code_ids: list):
        """
        批量取消收藏番号
        """
        ids_str = ",".join(code_ids)
        return self._delete(
            "/v1/codes/batch_uncollection",
            files={"ids": (None, ids_str)}
        )

    # ================= 新增：系列收藏相关 =================
    def collect_series(self, series_id: str, action: str = "collect"):
        """
        收藏或取消收藏系列
        :param action: 'collect' 表示收藏，'uncollect' 表示取消收藏
        """
        return self._post(
            f"/v1/series/{series_id}/collect_actions",
            files={"name": (None, action)}
        )

    def get_collected_series(self, page: int = 1, limit: int = 30):
        """
        获取收藏的系列列表
        """
        return self._get(
            "/v1/users/collected_series",
            {
                "page": page,
                "limit": limit
            }
        )

    # ================= 新增：导演收藏相关 =================
    def collect_director(self, director_id: str, action: str = "collect"):
        """
        收藏或取消收藏导演
        :param action: 'collect' 表示收藏，'uncollect' 表示取消收藏
        """
        return self._post(
            f"/v1/directors/{director_id}/collect_actions",
            files={"name": (None, action)}
        )

    def get_collected_directors(self, req_type: str = "all", page: int = 1, limit: int = 30):
        """
        获取收藏的导演列表
        """
        return self._get(
            "/v1/users/collected_directors",
            {
                "type": req_type,
                "page": page,
                "limit": limit
            }
        )

    def batch_uncollect_directors(self, director_ids: list):
        """
        批量取消收藏导演
        """
        ids_str = ",".join(director_ids)
        return self._delete(
            "/v1/directors/batch_uncollection",
            files={"ids": (None, ids_str)}
        )

    # ================= 新增：片商收藏相关 =================
    def collect_maker(self, maker_id: str, action: str = "collect"):
        """
        收藏或取消收藏片商
        :param action: 'collect' 表示收藏，'uncollect' 表示取消收藏
        """
        return self._post(
            f"/v1/makers/{maker_id}/collect_actions",
            files={"name": (None, action)}
        )

    def get_collected_makers(self, page: int = 1, limit: int = 24):
        """
        获取收藏的片商列表
        """
        return self._get(
            "/v1/users/collected_makers",
            {
                "page": page,
                "limit": limit
            }
        )