# api_docs.py
"""
API 文档元数据定义（完整版，收录全部 69 个接口）。
结构说明：
- category: 分类名
- icon:     分类图标（emoji）
- endpoints: 该分类下所有 API
    - method:      HTTP 方法
    - path:        路由路径（含占位符）
    - description: 功能简述
    - params:      参数列表 [{name, type, required, desc}]
    - example:     cURL 请求示例
    - response:    响应 JSON 片段
"""

API_DOCS = [
    # ================================================================
    # 🎬 影片 Movie
    # ================================================================
    {
        "category": "影片 Movie",
        "icon": "🎬",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/movie/<movie_id>",
                "description": "获取影片完整详情（含演员、标签、预览图、相关影片、排行榜等）",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                ],
                "example": "curl http://localhost:9560/api/movie/RdEb4",
                "response": '{"success": 1, "data": {"movie": {...}}}',
            },
            {
                "method": "GET",
                "path": "/api/movie/<movie_id>/magnets",
                "description": "获取影片磁力链接列表（含 hash、大小、HD、字幕、时间）",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                ],
                "example": "curl http://localhost:9560/api/movie/1Axvvw/magnets",
                "response": '{"success": 1, "data": {"magnets": [{"hash": "...", "name": "...", "size": 1024, "hd": true, "cnsub": true, "created_at": "..."}]}}',
            },
            {
                "method": "GET",
                "path": "/api/movie/<movie_id>/reviews",
                "description": "获取影片用户评论列表",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "hotly（最热）/ recently（最新），默认 hotly"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/movie/1Axvvw/reviews?sort_by=hotly&page=1&limit=24'",
                "response": '{"success": 1, "data": {"reviews": [{"id": "...", "username": "...", "score": 5, "content": "...", "likes_count": 3}]}}',
            },
            {
                "method": "POST",
                "path": "/api/movie/<movie_id>/reviews",
                "description": "添加评论 / 标记想看 / 标记看过",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "status", "type": "body(form)", "required": True, "desc": "want_watch（想看）/ watched（看过）"},
                    {"name": "score", "type": "body(form)", "required": False, "desc": "评分 1-5，0 表示未评分"},
                    {"name": "content", "type": "body(form)", "required": False, "desc": "评论内容"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/movie/<movie_id>/reviews \\\n"
                    "  -F 'status=watched' -F 'score=5' -F 'content=很棒！'"
                ),
                "response": '{"success": 1, "data": {"review": {"id": "xxx", "status": "watched", "score": 5}}}',
            },
            {
                "method": "DELETE",
                "path": "/api/movie/<movie_id>/reviews/<review_id>",
                "description": "删除评论 / 取消想看、看过",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "review_id", "type": "path", "required": True, "desc": "评论 ID"},
                ],
                "example": "curl -X DELETE http://localhost:9560/api/movie/<movie_id>/reviews/<review_id>",
                "response": '{"success": 1}',
            },
            {
                "method": "POST",
                "path": "/api/movie/<movie_id>/reviews/<review_id>/like",
                "description": "点赞 / 取消点赞评论（toggle，无需 body）",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "review_id", "type": "path", "required": True, "desc": "评论 ID"},
                ],
                "example": "curl -X POST http://localhost:9560/api/movie/<movie_id>/reviews/<review_id>/like",
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/movie/<movie_id>/related-lists",
                "description": "获取与当前影片相关的清单列表",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 12"},
                ],
                "example": "curl 'http://localhost:9560/api/movie/1Axvvw/related-lists?page=1&limit=12'",
                "response": '{"success": 1, "data": {"lists": [{"id": "...", "name": "...", "movies_count": 10}]}}',
            },
            {
                "method": "GET",
                "path": "/api/movie/<movie_id>/lists",
                "description": "获取「加入清单」弹窗数据（我的清单 + 是否已加入该影片）",
                "params": [
                    {"name": "movie_id", "type": "path", "required": True, "desc": "影片 ID"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/movie/1Axvvw/lists?page=1&limit=24'",
                "response": '{"success": 1, "data": {"lists": [{"id": "...", "name": "...", "has_movie": true}]}}',
            },
            {
                "method": "GET",
                "path": "/api/latest",
                "description": "最新上架影片列表",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "all/0有码/1无码/2欧美/3FC2/4动漫，默认 all"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "all/can_play/magnets/subtitle，默认 all"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "update（更新时间）/ release（发布时间），默认 update"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/latest?type=all&filter_by=all&sort_by=update&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/hot",
                "description": "播放热播榜（日/周/月）",
                "params": [
                    {"name": "period", "type": "query", "required": False, "desc": "daily / weekly / monthly，默认 daily"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "all / high_score，默认 all"},
                ],
                "example": "curl 'http://localhost:9560/api/hot?period=daily&filter_by=high_score'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/top250",
                "description": "Top 250 榜单",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 50"},
                    {"name": "type", "type": "query", "required": False, "desc": "all/0/1/2/3/4，默认 all"},
                    {"name": "type_value", "type": "query", "required": False, "desc": "细分类型值，类别/年份 id"},
                ],
                "example": "curl 'http://localhost:9560/api/top250?page=1&limit=50&type=all&type_value='",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/rankings",
                "description": "综合排行榜（日/周/月 / 演员月榜）",
                "params": [
                    {"name": "period", "type": "query", "required": False, "desc": "daily / weekly / monthly / actor_monthly，默认 daily"},
                    {"name": "type", "type": "query", "required": False, "desc": "0有码/1无码/2欧美/3FC2，默认 0"},
                ],
                "example": "curl 'http://localhost:9560/api/rankings?period=weekly&type=0'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/recommend_periods",
                "description": "往期佳片期数列表",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/recommend_periods?page=1&limit=24'",
                "response": '{"success": 1, "data": {"periods": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/recommend_period",
                "description": "获取特定期数的往期佳片影片列表",
                "params": [
                    {"name": "period", "type": "query", "required": True, "desc": "期数（整数），如 1、2、3"},
                ],
                "example": "curl 'http://localhost:9560/api/recommend_period?period=1'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
        ],
    },

    # ================================================================
    # 🎭 演员 Actor
    # ================================================================
    {
        "category": "演员 Actor",
        "icon": "🎭",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/actor/<actor_id>",
                "description": "获取演员详细信息（含标签、基础筛选、是否已收藏）",
                "params": [
                    {"name": "actor_id", "type": "path", "required": True, "desc": "演员 ID，如 RdEb4"},
                ],
                "example": "curl http://localhost:9560/api/actor/RdEb4",
                "response": '{"success": 1, "data": {"actor": {...}, "has_collected": false}}',
            },
            {
                "method": "GET",
                "path": "/api/movies",
                "description": "按演员 / 标签 / 年份 查询影片列表（演员主页使用）",
                "params": [
                    {"name": "actor_id", "type": "query", "required": True, "desc": "演员 ID"},
                    {"name": "filter_tags", "type": "query", "required": False, "desc": "基础标签 ID，逗号分隔"},
                    {"name": "tags", "type": "query", "required": False, "desc": "类别标签 ID，逗号分隔（最多 5 个）"},
                    {"name": "year", "type": "query", "required": False, "desc": "发行年份，如 2024"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "release / score / hit / want_watch_count / watched_count / update"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/movies?actor_id=RdEb4&sort_by=release&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...], "current_page": 1}}',
            },
            {
                "method": "GET",
                "path": "/api/actors/recommend",
                "description": "推荐演员（新人 / 本月热度 / 编辑推荐）",
                "params": [],
                "example": "curl http://localhost:9560/api/actors/recommend",
                "response": '{"success": 1, "data": {"new_actors": [], "monthly_actors": [], "recommend_actors": []}}',
            },
            {
                "method": "GET",
                "path": "/api/actresses",
                "description": "有码女演员列表（支持年龄 / 身高 / 罩杯 / 三围区间筛选）",
                "params": [
                    {"name": "age", "type": "query", "required": False, "desc": "年龄区间，如 19,39"},
                    {"name": "height", "type": "query", "required": False, "desc": "身高区间，如 150,170"},
                    {"name": "cup", "type": "query", "required": False, "desc": "罩杯区间，如 A,P"},
                    {"name": "bust", "type": "query", "required": False, "desc": "胸围区间，如 70,120"},
                    {"name": "waist", "type": "query", "required": False, "desc": "腰围区间，如 50,90"},
                    {"name": "hips", "type": "query", "required": False, "desc": "臀围区间，如 70,120"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/actresses?age=19,39&cup=C,F&page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/actors/male",
                "description": "有码男演员列表（固定 type=0, gender=1，无筛选）",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/actors/male?page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/actors/uncensored",
                "description": "无码演员列表（固定 type=1，gender=all，无筛选）",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/actors/uncensored?page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/actors/eu/female",
                "description": "欧美女演员列表（固定 type=2, gender=0）",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/actors/eu/female?page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/actors/eu/male",
                "description": "欧美男演员列表（固定 type=2, gender=1）",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/actors/eu/male?page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/actor/<actor_id>/collect",
                "description": "收藏或取消收藏演员",
                "params": [
                    {"name": "actor_id", "type": "path", "required": True, "desc": "演员 ID"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/actor/RdEb4/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1, "message": "收藏成功"}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_actors",
                "description": "获取我收藏的演员列表",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "all / 0有码 / 1无码 / 2欧美，默认 all"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_actors?type=all&page=1&limit=30'",
                "response": '{"success": 1, "data": {"actors": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/my/collected_actors/batch_uncollect",
                "description": "批量取消收藏演员",
                "params": [
                    {"name": "ids", "type": "body(json)", "required": True, "desc": "演员 ID 数组，如 [\"RdEb4\", \"PQErN\"]"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/my/collected_actors/batch_uncollect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"ids\": [\"RdEb4\", \"PQErN\"]}'"
                ),
                "response": '{"success": 1}',
            },
        ],
    },

    # ================================================================
    # 🏷️ 番号 Code
    # ================================================================
    {
        "category": "番号 Code",
        "icon": "🏷️",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/code/<code_id>",
                "description": "获取番号基础信息",
                "params": [
                    {"name": "code_id", "type": "path", "required": True, "desc": "番号前缀，如 IPX"},
                ],
                "example": "curl http://localhost:9560/api/code/IPX",
                "response": '{"success": 1, "data": {"code": {...}}}',
            },
            {
                "method": "GET",
                "path": "/api/code-movies",
                "description": "获取该番号下的影片列表（支持筛选 + 排序）",
                "params": [
                    {"name": "code_id", "type": "query", "required": True, "desc": "番号前缀（自动转大写）"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "p（可播放）/ m（含磁链）/ c（含字幕）/ 空（全部）"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "digit（番号）或其他，默认 digit"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/code-movies?code_id=IPX&filter_by=&sort_by=digit&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/code/<code_id>/collect",
                "description": "收藏 / 取消收藏番号",
                "params": [
                    {"name": "code_id", "type": "path", "required": True, "desc": "番号前缀"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/code/IPX/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_codes",
                "description": "获取我收藏的番号列表",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_codes?page=1&limit=30'",
                "response": '{"success": 1, "data": {"codes": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/series/letters",
                "description": "获取番号列表",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/series/letters?page=1&limit=24'",
                "response": '{"success": 1, "data": {"letters": [...]}}',
            },
        ],
    },

    # ================================================================
    # 📂 系列 Series
    # ================================================================
    {
        "category": "系列 Series",
        "icon": "📂",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/series/<series_id>",
                "description": "获取系列基本信息（名称、作品数等）",
                "params": [
                    {"name": "series_id", "type": "path", "required": True, "desc": "系列 ID"},
                ],
                "example": "curl http://localhost:9560/api/series/xxxx",
                "response": '{"success": 1, "data": {"series": {...}, "has_collected": false}}',
            },
            {
                "method": "GET",
                "path": "/api/series-movies",
                "description": "获取系列下的影片列表（筛选 + 排序）",
                "params": [
                    {"name": "series_id", "type": "query", "required": True, "desc": "系列 ID"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "p / m / c / 空"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "release / score 等，默认 release"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/series-movies?series_id=xxxx&filter_by=&sort_by=release&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/series",
                "description": "获取系列列表（按类型）",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "0有码/1无码/2欧美/4动漫，默认 0"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/series?type=0&page=1&limit=24'",
                "response": '{"success": 1, "data": {"series": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/series/<series_id>/collect",
                "description": "收藏 / 取消收藏系列",
                "params": [
                    {"name": "series_id", "type": "path", "required": True, "desc": "系列 ID"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/series/<series_id>/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_series",
                "description": "获取我收藏的系列列表",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_series?page=1&limit=30'",
                "response": '{"success": 1, "data": {"series": [...]}}',
            },
        ],
    },

    # ================================================================
    # 🏢 片商 Maker
    # ================================================================
    {
        "category": "片商 Maker",
        "icon": "🏢",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/maker/<maker_id>",
                "description": "获取片商基础信息（名称、作品数、类型、是否已收藏）",
                "params": [
                    {"name": "maker_id", "type": "path", "required": True, "desc": "片商 ID"},
                ],
                "example": "curl http://localhost:9560/api/maker/nq4a",
                "response": '{"success": 1, "data": {"maker": {...}, "has_collected": false}}',
            },
            {
                "method": "GET",
                "path": "/api/maker-movies",
                "description": "获取片商下的影片列表（筛选 + 排序）",
                "params": [
                    {"name": "maker_id", "type": "query", "required": True, "desc": "片商 ID"},
                    {"name": "type", "type": "query", "required": False, "desc": "视频类型 0/1/2/3/4，默认 0"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "p / m / c / 空"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "release / score / hit / want_watch_count / watched_count"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/maker-movies?maker_id=nq4a&type=0&filter_by=&sort_by=release&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/makers",
                "description": "片商列表（按类型）",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "0有码/1无码/2欧美/3FC2/4动漫，默认 0"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/makers?type=0&page=1&limit=24'",
                "response": '{"success": 1, "data": {"makers": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/maker/<maker_id>/collect",
                "description": "收藏 / 取消收藏片商",
                "params": [
                    {"name": "maker_id", "type": "path", "required": True, "desc": "片商 ID"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/maker/<maker_id>/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_makers",
                "description": "获取我收藏的片商列表",
                "params": [
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_makers?page=1&limit=24'",
                "response": '{"success": 1, "data": {"makers": [...]}}',
            },
        ],
    },

    # ================================================================
    # 🎬 导演 Director
    # ================================================================
    {
        "category": "导演 Director",
        "icon": "🎬",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/director/<director_id>",
                "description": "获取导演基础信息",
                "params": [
                    {"name": "director_id", "type": "path", "required": True, "desc": "导演 ID"},
                ],
                "example": "curl http://localhost:9560/api/director/6d8M",
                "response": '{"success": 1, "data": {"director": {...}, "has_collected": false}}',
            },
            {
                "method": "GET",
                "path": "/api/director-movies",
                "description": "获取导演下的影片列表（筛选 + 排序）",
                "params": [
                    {"name": "director_id", "type": "query", "required": True, "desc": "导演 ID"},
                    {"name": "type", "type": "query", "required": False, "desc": "视频类型 0/1/2/3/4，默认 0"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "p / m / c / 空"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "release / score / hit / want_watch_count / watched_count，默认 release"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/director-movies?director_id=6d8M&type=0&filter_by=&sort_by=release&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/directors",
                "description": "导演列表（按类型）",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "0有码 / 2欧美，默认 0"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/directors?type=0&page=1&limit=24'",
                "response": '{"success": 1, "data": {"directors": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/director/<director_id>/collect",
                "description": "收藏 / 取消收藏导演",
                "params": [
                    {"name": "director_id", "type": "path", "required": True, "desc": "导演 ID"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/director/xxxx/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_directors",
                "description": "获取我收藏的导演列表",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "all / 0 / 1 / 2，默认 all"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 30"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_directors?type=all&page=1&limit=30'",
                "response": '{"success": 1, "data": {"directors": [...]}}',
            },
        ],
    },

    # ================================================================
    # 📋 清单 List
    # ================================================================
    {
        "category": "清单 List",
        "icon": "📋",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/list/<list_id>",
                "description": "获取清单基础信息",
                "params": [
                    {"name": "list_id", "type": "path", "required": True, "desc": "清单 ID"},
                ],
                "example": "curl http://localhost:9560/api/list/X4Xze",
                "response": '{"success": 1, "data": {"list": {...}, "has_collected": false}}',
            },
            {
                "method": "GET",
                "path": "/api/list-movies",
                "description": "获取清单下的影片列表（筛选 + 排序）",
                "params": [
                    {"name": "list_id", "type": "query", "required": True, "desc": "清单 ID"},
                    {"name": "filter_by", "type": "query", "required": False, "desc": "p / m / c / 空"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "update / release / score，默认 update"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/list-movies?list_id=X4Xze&filter_by=&sort_by=update&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/list/<list_id>/collect",
                "description": "收藏 / 取消收藏清单",
                "params": [
                    {"name": "list_id", "type": "path", "required": True, "desc": "清单 ID"},
                    {"name": "action", "type": "body(json)", "required": True, "desc": "collect / uncollect"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/list/<list_id>/collect \\\n"
                    "  -H 'Content-Type: application/json' \\\n"
                    "  -d '{\"action\": \"collect\"}'"
                ),
                "response": '{"success": 1}',
            },
            {
                "method": "GET",
                "path": "/api/my/collected_lists",
                "description": "获取我收藏的清单列表",
                "params": [
                    {"name": "sort_by", "type": "query", "required": False, "desc": "create / update，默认 create"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/my/collected_lists?sort_by=create&page=1&limit=24'",
                "response": '{"success": 1, "data": {"lists": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/my_lists",
                "description": "获取我创建的清单列表",
                "params": [
                    {"name": "sort_by", "type": "query", "required": False, "desc": "create 等，默认 create"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/my_lists?sort_by=create&page=1&limit=24'",
                "response": '{"success": 1, "data": {"lists": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/lists",
                "description": "创建新清单（可同时把某影片加入）",
                "params": [
                    {"name": "movie_id", "type": "body(form)", "required": True, "desc": "当前要加入的影片 ID"},
                    {"name": "name", "type": "body(form)", "required": True, "desc": "清单名称（最长 20 字）"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/lists \\\n"
                    "  -F 'movie_id=<movie_id>' -F 'name=我的最爱'"
                ),
                "response": '{"success": 1, "data": {"list": {"id": "...", "name": "我的最爱"}}}',
            },
            {
                "method": "PATCH",
                "path": "/api/lists/<list_id>",
                "description": "重命名清单（支持 query 或 form 传 name）",
                "params": [
                    {"name": "list_id", "type": "path", "required": True, "desc": "清单 ID"},
                    {"name": "name", "type": "query|body(form)", "required": True, "desc": "新名称"},
                ],
                "example": "curl -X PATCH 'http://localhost:9560/api/lists/<list_id>?name=新名字'",
                "response": '{"success": 1}',
            },
            {
                "method": "DELETE",
                "path": "/api/lists/<list_id>",
                "description": "删除清单",
                "params": [
                    {"name": "list_id", "type": "path", "required": True, "desc": "清单 ID"},
                ],
                "example": "curl -X DELETE http://localhost:9560/api/lists/<list_id>",
                "response": '{"success": 1}',
            },
            {
                "method": "POST",
                "path": "/api/lists/<list_id>/movie_action",
                "description": "加入 / 移除影片到指定清单",
                "params": [
                    {"name": "list_id", "type": "path", "required": True, "desc": "清单 ID"},
                    {"name": "movie_id", "type": "body(form)", "required": True, "desc": "影片 ID"},
                    {"name": "action", "type": "body(form)", "required": True, "desc": "add / remove"},
                ],
                "example": (
                    "curl -X POST http://localhost:9560/api/lists/<list_id>/movie_action \\\n"
                    "  -F 'movie_id=<movie_id>' -F 'action=add'"
                ),
                "response": '{"success": 1}',
            },
        ],
    },

    # ================================================================
    # 🏷️ 标签 Tag
    # ================================================================
    {
        "category": "标签 Tag",
        "icon": "🏷️",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/tags",
                "description": "获取标签列表（按类型）",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "0有码/1无码/2欧美/3FC2/4动漫，默认 0"},
                ],
                "example": "curl 'http://localhost:9560/api/tags?type=0'",
                "response": '{"success": 1, "data": {"tags": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/tag-movies",
                "description": "按标签组合 + 年份 + 时长 + 月份 查询影片列表",
                "params": [
                    {"name": "type", "type": "query", "required": False, "desc": "类型 0/1/2/3/4，默认 0"},
                    {"name": "base_tags", "type": "query", "required": False, "desc": "基础标签 ID，逗号分隔"},
                    {"name": "other_tags", "type": "query", "required": False, "desc": "其他标签 ID，逗号分隔"},
                    {"name": "duration_tags", "type": "query", "required": False, "desc": "时长标签"},
                    {"name": "year", "type": "query", "required": False, "desc": "发行年份"},
                    {"name": "month", "type": "query", "required": False, "desc": "发行月份"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "release / score 等，默认 release"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/tag-movies?type=0&base_tags=&other_tags=&year=2024&sort_by=release&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
        ],
    },

    # ================================================================
    # 🔍 搜索 Search
    # ================================================================
    {
        "category": "搜索 Search",
        "icon": "🔍",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/search",
                "description": "综合搜索（影片 / 演员 / 番号 / 清单 / 系列 / 片商 / 导演）",
                "params": [
                    {"name": "q", "type": "query", "required": True, "desc": "关键词（为空时返回空结果）"},
                    {"name": "type", "type": "query", "required": False, "desc": "movie / actor / code / list / series / maker / director，默认 movie"},
                    {"name": "movie_type", "type": "query", "required": False, "desc": "影片类型 all / 0 / 1 / 2 / 3 / 4"},
                    {"name": "movie_sort_by", "type": "query", "required": False, "desc": "relevance / release / score，默认 relevance"},
                    {"name": "movie_filter_by", "type": "query", "required": False, "desc": "all / can_play / magnets / subtitle，默认 all"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/search?q=IPX-997&type=movie&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...], "actors": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/search_magnet",
                "description": "磁力搜索（按关键词、排序方式）",
                "params": [
                    {"name": "q", "type": "query", "required": True, "desc": "关键词（为空时返回空结果）"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "relevance / created / files / size，默认 relevance"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/search_magnet?q=IPX-997&sort_by=relevance&page=1&limit=24'",
                "response": '{"success": 1, "data": {"magnets": [...]}}',
            },
            {
                "method": "POST",
                "path": "/api/search_image",
                "description": "以图识图（上传图片，识别影片或演员）",
                "params": [
                    {"name": "target", "type": "query", "required": True, "desc": "movie / actor"},
                    {"name": "image", "type": "body(form)", "required": True, "desc": "图片文件（≤20MB）"},
                ],
                "example": (
                    "curl -X POST 'http://localhost:9560/api/search_image?target=movie' \\\n"
                    "  -F 'image=@/path/to/image.jpg'"
                ),
                "response": '{"success": 1, "data": {"matches": [...]}}',
            },
        ],
    },

    # ================================================================
    # 💬 短评 Reviews
    # ================================================================
    {
        "category": "短评 Reviews",
        "icon": "💬",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/reviews",
                "description": "热门短评列表（按周期）",
                "params": [
                    {"name": "period", "type": "query", "required": False, "desc": "latest / weekly / monthly / quarterly / yearly / all，默认 latest"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/reviews?period=latest&page=1&limit=24'",
                "response": '{"success": 1, "data": {"reviews": [...]}}',
            },
        ],
    },

    # ================================================================
    # 📰 资讯 Article
    # ================================================================
    {
        "category": "资讯 Article",
        "icon": "📰",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/articles",
                "description": "AV 资讯列表（可按作者 / 分类筛选）",
                "params": [
                    {"name": "author_id", "type": "query", "required": False, "desc": "作者 ID，可为空"},
                    {"name": "category_id", "type": "query", "required": False, "desc": "分类 ID，可为空"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 12"},
                ],
                "example": "curl 'http://localhost:9560/api/articles?author_id=&category_id=&page=1&limit=12'",
                "response": '{"success": 1, "data": {"articles": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/article/<article_id>",
                "description": "获取单篇 AV 资讯详情",
                "params": [
                    {"name": "article_id", "type": "path", "required": True, "desc": "文章 ID"},
                ],
                "example": "curl http://localhost:9560/api/article/rY0k",
                "response": '{"success": 1, "data": {"article": {...}}}',
            },
        ],
    },

    # ================================================================
    # 👤 用户 User（含"我的想看/看过"）
    # ================================================================
    {
        "category": "用户 User",
        "icon": "👤",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/v1/users",
                "description": "获取当前登录用户信息数据",
                "params": [],
                "example": "curl http://localhost:9560/api/v1/users",
                "response": '{"success": 1, "data": {"user": {...}}}',
            },
            {
                "method": "GET",
                "path": "/api/v1/users/additional",
                "description": "获取当前用户额外信息（统计、等级等）",
                "params": [],
                "example": "curl http://localhost:9560/api/v1/users/additional",
                "response": '{"success": 1, "data": {...}}',
            },
            {
                "method": "GET",
                "path": "/api/my_watchlist",
                "description": "获取「我的想看」影片列表",
                "params": [
                    {"name": "status", "type": "query", "required": False, "desc": "want_watch（默认）"},
                    {"name": "type", "type": "query", "required": False, "desc": "all / 0 / 1 / 2 / 3 / 4，默认 all"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "create / release / score，默认 create"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/my_watchlist?status=want_watch&sort_by=create&order_by=desc&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
            {
                "method": "GET",
                "path": "/api/my_watched",
                "description": "获取「我的看过」影片列表（支持按评分筛选）",
                "params": [
                    {"name": "status", "type": "query", "required": False, "desc": "watched（默认）"},
                    {"name": "type", "type": "query", "required": False, "desc": "all / 0 / 1 / 2 / 3 / 4，默认 all"},
                    {"name": "sort_by", "type": "query", "required": False, "desc": "create / release / score，默认 create"},
                    {"name": "order_by", "type": "query", "required": False, "desc": "asc / desc，默认 desc"},
                    {"name": "star", "type": "query", "required": False, "desc": "评分筛选，如 5（可选）"},
                    {"name": "page", "type": "query", "required": False, "desc": "页码，默认 1"},
                    {"name": "limit", "type": "query", "required": False, "desc": "每页数量，默认 24"},
                ],
                "example": "curl 'http://localhost:9560/api/my_watched?status=watched&star=5&page=1&limit=24'",
                "response": '{"success": 1, "data": {"movies": [...]}}',
            },
        ],
    },

    # ================================================================
    # ⚙️ 通用 General
    # ================================================================
    {
        "category": "通用 General",
        "icon": "⚙️",
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/image",
                "description": "图片代理（自动解密 XOR 加密图、识别格式、校验完整性、缓存 30 天）",
                "params": [
                    {"name": "url", "type": "query", "required": True, "desc": "原始图片 URL（需 URL 编码）"},
                ],
                "example": "curl 'http://localhost:9560/api/image?url=https%3A%2F%2Ftp.spfcas.com%2Frhe951l4q%2Favatars%2Fee%2FeE2d.jpg'",
                "response": "二进制图片（带正确 Content-Type 和 Cache-Control）",
            },
        ],
    },
]