import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from api import JavJHSClient
import config as cfg
import io
from PIL import Image
import time

app = Flask(__name__)


# 初始化 Client (请替换为实际的账号密码)
jav_client = JavJHSClient()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/actor/<actor_id>')
def actor_page(actor_id):
    return render_template('actor_home.html', actor_id=actor_id)


@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    return render_template('movie_detail.html')


@app.route('/api/actor/<actor_id>', methods=['GET'])
def get_actor_info(actor_id):
    try:
        # 使用 client 的 _get 方法，路径参数用 params 字典传递
        data = jav_client._get(
            f"/v1/actors/{actor_id}",
            params={"from_rankings": "false"}
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/movies', methods=['GET'])
def get_movies():
    actor_id = request.args.get('actor_id')
    tags = request.args.get('tags', '')
    filter_tags = request.args.get('filter_tags', '')
    year = request.args.get('year', '')
    sort_by = request.args.get('sort_by', 'release')
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 24)

    # 构造 filter_by: 0:a:演员ID:筛选标签:年份
    # 筛选标签字段即使为空也要保留占位
    filter_by = f"0:a:{actor_id}:{filter_tags}"
    if year:
        filter_by += f":{year}"

    params = {
        "filter_by": filter_by,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }

    if tags:
        params["filter_by_tags"] = tags

    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/movie/<movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    try:
        data = jav_client._get(
            f"/v4/movies/{movie_id}",
            params={"from_rankings": "false"}
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/movie/<movie_id>/magnets', methods=['GET'])
def get_movie_magnets(movie_id):
    try:
        data = jav_client._get(f"/v1/movies/{movie_id}/magnets")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/movie/<movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    sort_by = request.args.get('sort_by', 'hotly')
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 24)

    params = {
        "sort_by": sort_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get(f"/v1/movies/{movie_id}/reviews", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/tags')
def tag_search():
    return render_template('tag_search.html')

@app.route('/api/tags', methods=['GET'])
def get_tags():
    # 接收前端传来的 type 参数，默认为 0（有码）
    req_type = request.args.get('type', '0')
    try:
        # 将 type 传给官方 API
        data = jav_client._get("/v2/tags", params={"type": req_type})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/tag-movies', methods=['GET'])
def get_tag_movies():
    # 接收类别参数
    req_type = request.args.get('type', '0')
    base_tags = request.args.get('base_tags', '')
    other_tags = request.args.get('other_tags', '')
    duration_tags = request.args.get('duration_tags', '')
    year = request.args.get('year', '')
    month = request.args.get('month', '')
    sort_by = request.args.get('sort_by', 'release')
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 动态使用 req_type 拼接 7 段式 filter_by: 类别:t:基本标签:其他标签:年份:时长标签:月份
    filter_by = f"{req_type}:t:{base_tags}:{other_tags}:{year}:{duration_tags}:{month}"

    params = {
        "filter_by": filter_by,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/actors/recommend', methods=['GET'])
def get_actors_recommend():
    try:
        # client.pyの_getメソッドを利用して認証ヘッダー(jdsignature等)を自動付与してリクエストします
        data = jav_client._get("/v1/actors/recommend")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/search')
def search_page():
    # 允许直接通过 /search?q=石川澪 访问
    keyword = request.args.get('q', '')
    return render_template('search.html', initial_keyword=keyword)


@app.route('/api/search', methods=['GET'])
def api_search_movies():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"success": 1, "data": {"movies": [], "actors": [], "current_page": 1}})

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 接收目标类型：movie 或 actor
    search_type = request.args.get('type', 'movie')

    movie_type = request.args.get('movie_type', 'all')
    movie_sort_by = request.args.get('movie_sort_by', 'relevance')
    movie_filter_by = request.args.get('movie_filter_by', 'all')

    params = {
        "q": q,
        "from_recent": "false",
        "type": search_type,  # 动态传入搜索类型
        "movie_type": movie_type,
        "movie_sort_by": movie_sort_by,
        "movie_filter_by": movie_filter_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v2/search", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/hot')
def hot_page():
    return render_template('hot.html')

@app.route('/api/hot', methods=['GET'])
def api_get_hot_rankings():
    period = request.args.get('period', 'daily')
    filter_by = request.args.get('filter_by', 'all')
    try:
        data = jav_client.playback_rankings(period=period, filter_by=filter_by)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/top250')
def top250_page():
    """Top 250 页面"""
    return render_template('top250.html')

@app.route('/api/top250', methods=['GET'])
def api_get_top250():
    """Top 250 数据接口"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    req_type = request.args.get('type', 'all')
    type_value = request.args.get('type_value', '')

    try:
        data = jav_client.top250(page=page, limit=limit, req_type=req_type, type_value=type_value)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/latest')
def latest_page():
    """最新上架页面"""
    return render_template('latest.html')

@app.route('/api/latest', methods=['GET'])
def api_get_latest():
    """最新上架数据接口"""
    req_type = request.args.get('type', 'all')
    filter_by = request.args.get('filter_by', 'all')
    sort_by = request.args.get('sort_by', 'update')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "type": req_type,
        "filter_by": filter_by,
        "sort_by": sort_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/movies/latest", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/rankings')
def rankings_page():
    """综合排行榜页面"""
    return render_template('rankings.html')

@app.route('/api/rankings', methods=['GET'])
def api_get_rankings():
    """多类别排行榜数据接口"""
    # 接收前端传来的参数
    period = request.args.get('period', 'daily')  # daily, weekly, monthly, actor_monthly
    req_type = request.args.get('type', '0')      # 0:有码, 1:无码, 2:欧美, 3:FC2

    try:
        if period == 'actor_monthly':
            # 演员月榜接口
            data = jav_client._get("/v1/rankings/actors", params={"type": req_type})
        else:
            # 作品榜单接口
            data = jav_client._get("/v1/rankings", params={"type": req_type, "period": period})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：番号系列相关路由 =================

@app.route('/code/<code_id>')
def code_page(code_id):
    """渲染番号详情主页"""
    return render_template('code_home.html', code_id=code_id)


@app.route('/api/code/<code_id>', methods=['GET'])
def api_get_code_info(code_id):
    """获取番号基础信息"""
    try:
        data = jav_client._get(f"/v1/codes/{code_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/code-movies', methods=['GET'])
def api_get_code_movies():
    """获取番号下的影片列表 (支持筛选和排序)"""
    code_id = request.args.get('code_id')
    if code_id:
        code_id = str(code_id).upper()
    filter_val = request.args.get('filter_by', '')  # p(可播放), m(磁链), c(字幕), 空(全部)
    sort_by = request.args.get('sort_by', 'digit')  # 默认按番号排序
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 构造 filter_by 字段: 0:c:番号ID:过滤条件 (例如 0:c:MO:m)
    filter_str = f"0:c:{code_id}:{filter_val}"

    params = {
        "filter_by": filter_str,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：清单相关路由 =================

@app.route('/list/<list_id>')
def list_page(list_id):
    """清单详情页"""
    return render_template('list_home.html', list_id=list_id)


@app.route('/api/list/<list_id>', methods=['GET'])
def api_get_list_info(list_id):
    """获取清单基本信息"""
    try:
        data = jav_client._get(f"/v1/lists/{list_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/list-movies', methods=['GET'])
def api_get_list_movies():
    """获取清单下的影片列表（支持筛选和排序）"""
    list_id = request.args.get('list_id')
    if not list_id:
        return jsonify({"success": 0, "error": "缺少 list_id"}), 400

    filter_val = request.args.get('filter_by', '')   # p, m, c 或空
    sort_by = request.args.get('sort_by', 'update')  # update, release, score
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 构造 filter_by: 0:l:list_id:filter
    filter_str = f"0:l:{list_id}:{filter_val}"
    params = {
        "type": 0,
        "filter_by": filter_str,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：系列相关路由 =================

@app.route('/series/<series_id>')
def series_page(series_id):
    """系列详情页"""
    return render_template('series_home.html', series_id=series_id)


@app.route('/api/series/<series_id>', methods=['GET'])
def api_get_series_info(series_id):
    """获取系列基本信息"""
    try:
        data = jav_client._get(f"/v1/series/{series_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/series-movies', methods=['GET'])
def api_get_series_movies():
    """获取系列下的影片列表 (支持筛选和排序)"""
    series_id = request.args.get('series_id')
    if not series_id:
        return jsonify({"success": 0, "error": "缺少 series_id"}), 400

    filter_val = request.args.get('filter_by', '')   # p(可播放), m(磁链), c(字幕), 空(全部)
    sort_by = request.args.get('sort_by', 'release') # 默认按发布日期
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 构造 filter_by: 0:s:系列ID:过滤条件
    filter_str = f"0:s:{series_id}:{filter_val}"

    params = {
        "filter_by": filter_str,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：片商相关路由 =================

@app.route('/maker/<maker_id>')
def maker_page(maker_id):
    """片商详情页"""
    return render_template('maker_home.html', maker_id=maker_id)


@app.route('/api/maker/<maker_id>', methods=['GET'])
def api_get_maker_info(maker_id):
    """获取片商基本信息"""
    try:
        data = jav_client._get(f"/v1/makers/{maker_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/maker-movies', methods=['GET'])
def api_get_maker_movies():
    """获取片商下的影片列表 (支持筛选和排序)"""
    maker_id = request.args.get('maker_id')
    if not maker_id:
        return jsonify({"success": 0, "error": "缺少 maker_id"}), 400

    # 注意：片商类型可能为 0~4，但 filter_by 的第一段是视频类型，这里需要根据片商的 type 来设置？
    # 但抓包显示 filter_by=3:m:nq4a:m，其中 3 是视频类型（FC2），m 表示 maker，nq4a 是 ID，最后 m 是筛选条件。
    # 为了简化，我们从请求中获取视频类型参数，默认为 0（有码），但更好的做法是让前端传递 type。
    req_type = request.args.get('type', '0')  # 默认 0，但片商可能有自己的类型
    filter_val = request.args.get('filter_by', '')  # p, m, c 或空
    sort_by = request.args.get('sort_by', 'release')
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 构造 filter_by: 视频类型:m:片商ID:过滤条件
    filter_str = f"{req_type}:m:{maker_id}:{filter_val}"

    params = {
        "filter_by": filter_str,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：导演相关路由 =================

@app.route('/director/<director_id>')
def director_page(director_id):
    """导演详情页"""
    return render_template('director_home.html', director_id=director_id)


@app.route('/api/director/<director_id>', methods=['GET'])
def api_get_director_info(director_id):
    """获取导演基本信息"""
    try:
        data = jav_client._get(f"/v1/directors/{director_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/director-movies', methods=['GET'])
def api_get_director_movies():
    """获取导演下的影片列表（支持筛选和排序）"""
    director_id = request.args.get('director_id')
    if not director_id:
        return jsonify({"success": 0, "error": "缺少 director_id"}), 400

    # 视频类型（从请求中获取，默认为0）
    req_type = request.args.get('type', '0')
    filter_val = request.args.get('filter_by', '')   # p, m, c 或空
    sort_by = request.args.get('sort_by', 'release')
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    # 构造 filter_by: 视频类型:d:导演ID:过滤条件
    filter_str = f"{req_type}:d:{director_id}:{filter_val}"

    params = {
        "filter_by": filter_str,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/movies/tags", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：女演员有码列表 =================

@app.route('/actors')
def actors_page():
    tab = request.args.get('tab', 'recommend')  # 默认推荐
    return render_template('actors.html', active_tab=tab)

@app.route('/actresses')
def actresses_mosaic_page():
    return redirect(url_for('actors_page', tab='actress'))

@app.route('/api/actresses', methods=['GET'])
def api_get_actresses():
    """获取有码女演员列表（支持筛选）"""
    # 固定参数：有码(type=0)、女性(gender=0)
    req_type = 0
    gender = 0

    # 分页参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)

    # 筛选参数（范围，格式如 "19,39"）
    age = request.args.get('age', '')
    height = request.args.get('height', '')
    cup = request.args.get('cup', '')
    bust = request.args.get('bust', '')
    waist = request.args.get('waist', '')
    hips = request.args.get('hips', '')

    # 构建请求参数
    params = {
        "type": req_type,
        "gender": gender,
        "page": page,
        "limit": limit
    }

    # 添加可选筛选参数（如果非空）
    if age:
        params["age"] = age
    if height:
        params["height"] = height
    if cup:
        params["cup"] = cup
    if bust:
        params["bust"] = bust
    if waist:
        params["waist"] = waist
    if hips:
        params["hips"] = hips

    try:
        data = jav_client._get("/v1/actors", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/actors/male')
def actors_male_page():
    return redirect(url_for('actors_page', tab='male'))

@app.route('/api/actors/male', methods=['GET'])
def api_get_actors_male():
    """获取有码男演员列表（无筛选）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    params = {"type": 0, "gender": 1, "page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/actors", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/actors/uncensored')
def actors_uncensored_page():
    return redirect(url_for('actors_page', tab='uncensored'))

@app.route('/api/actors/uncensored', methods=['GET'])
def api_get_actors_uncensored():
    """获取无码演员列表（无筛选）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    params = {"type": 1, "gender": "all", "page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/actors", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：欧美演员 API =================

@app.route('/api/actors/eu/female', methods=['GET'])
def api_get_actors_eu_female():
    """获取欧美女演员列表（无筛选）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    params = {"type": 2, "gender": 0, "page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/actors", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/actors/eu/male', methods=['GET'])
def api_get_actors_eu_male():
    """获取欧美男演员列表（无筛选）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    params = {"type": 2, "gender": 1, "page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/actors", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


# ================= 新增：系列列表页面相关路由 =================

@app.route('/series')
def series_page_list():
    """渲染系列列表主页（包含番号和有码选项卡）"""
    tab = request.args.get('tab', 'letters')
    return render_template('series.html', active_tab=tab)


@app.route('/api/series/letters', methods=['GET'])
def api_get_series_letters():
    """获取系列番号列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {"page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/series/letters", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/series', methods=['GET'])
def api_get_series_list():
    """获取系列（如：有码）列表"""
    req_type = request.args.get('type', '0')  # 默认0为有码
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {"type": req_type, "page": page, "limit": limit}
    try:
        data = jav_client._get("/v1/series", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= AV资讯相关路由 =================

@app.route('/articles')
def articles_page():
    """AV资讯列表页"""
    return render_template('articles.html')

@app.route('/article/<article_id>')
def article_detail_page(article_id):
    """AV资讯详情页"""
    return render_template('article_detail.html', article_id=article_id)

@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    """获取AV资讯列表"""
    author_id = request.args.get('author_id', '')
    category_id = request.args.get('category_id', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 12, type=int)

    params = {
        "author_id": author_id,
        "category_id": category_id,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v1/articles", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/article/<article_id>', methods=['GET'])
def api_get_article_detail(article_id):
    """获取单篇AV资讯详情"""
    try:
        data = jav_client._get(f"/v1/articles/{article_id}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 找磁链相关路由 =================

@app.route('/search_magnet')
def search_magnet_page():
    """找磁链搜索页面"""
    return render_template('search_magnet.html')


@app.route('/api/search_magnet', methods=['GET'])
def api_search_magnet():
    """磁链搜索 API（对接 /v1/search_magnet）"""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"success": 1, "data": {"magnets": [], "current_page": 1}})

    sort_by = request.args.get('sort_by', 'relevance')   # relevance / created / files / size
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "q": q,
        "sort_by": sort_by,
        "from_recent": "true",    # 抓包固定参数
        "page": page,
        "limit": limit
    }

    try:
        data = jav_client._get("/v1/search_magnet", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 片商列表相关路由 =================

@app.route('/makers')
def makers_page():
    """片商列表页面"""
    tab = request.args.get('tab', 'censored')  # 默认有码
    return render_template('makers.html', active_tab=tab)


@app.route('/api/makers', methods=['GET'])
def api_get_makers():
    """获取片商列表（支持类型和分页）"""
    req_type = request.args.get('type', '0')   # 0有码 1无码 2欧美 3FC2 4动漫
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    try:
        data = jav_client._get("/v1/makers", params={"type": req_type, "page": page, "limit": limit})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 导演列表相关路由 =================

@app.route('/directors')
def directors_page():
    """导演列表页面"""
    tab = request.args.get('tab', 'censored')  # 默认有码
    return render_template('directors.html', active_tab=tab)


@app.route('/api/directors', methods=['GET'])
def api_get_directors():
    """获取导演列表（支持类型和分页）"""
    req_type = request.args.get('type', '0')   # 0有码 1无码 2欧美 3FC2 4动漫
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    try:
        data = jav_client._get("/v1/directors", params={"type": req_type, "page": page, "limit": limit})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 往期佳片相关路由 =================

@app.route('/recommend_periods')
def recommend_periods_page():
    """往期佳片页面"""
    return render_template('recommend_periods.html')


@app.route('/api/recommend_periods', methods=['GET'])
def api_get_recommend_periods():
    """获取往期佳片期数列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)
    try:
        data = jav_client._get("/v1/movies/recommend_periods", params={"page": page, "limit": limit})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/recommend_period', methods=['GET'])
def api_get_recommend_period():
    """获取特定期数的影片列表"""
    period = request.args.get('period', type=int)
    if not period:
        return jsonify({"success": 0, "error": "缺少 period 参数"}), 400
    try:
        data = jav_client._get("/v1/movies/recommend", params={"period": period})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：相关清单 =================

@app.route('/api/movie/<movie_id>/related-lists', methods=['GET'])
def api_get_related_lists(movie_id):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 12, type=int)
    try:
        data = jav_client._get("/v1/lists/related", params={"movie_id": movie_id, "page": page, "limit": limit})
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 我的想看页面 =================
@app.route('/my_watchlist')
def my_watchlist_page():
    return render_template('my_watchlist.html')

@app.route('/api/my_watchlist', methods=['GET'])
def api_get_my_watchlist():
    """获取我的想看列表（代理后端接口）"""
    status = request.args.get('status', 'want_watch')
    req_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort_by', 'create')
    order_by = request.args.get('order_by', 'desc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "status": status,
        "type": req_type,
        "sort_by": sort_by,
        "order_by": order_by,
        "page": page,
        "limit": limit,
        "star": ""   # 抓包中固定为空
    }
    try:
        data = jav_client._get("/v2/users/review_movies", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 影片详情页“想看”操作 =================
@app.route('/api/movie/<movie_id>/reviews', methods=['POST'])
def api_add_review(movie_id):
    """加入想看（POST 表单）"""
    status = request.form.get('status')
    score = request.form.get('score', 0)
    content = request.form.get('content', '')
    data = {
        'status': status,
        'score': score,
        'content': content
    }
    try:
        result = jav_client._post(f"/v1/movies/{movie_id}/reviews", data=data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/movie/<movie_id>/reviews/<review_id>', methods=['DELETE'])
def api_delete_review(movie_id, review_id):
    """删除想看（取消）"""
    try:
        result = jav_client._delete(f"/v1/movies/{movie_id}/reviews/{review_id}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 我的看过页面 =================
@app.route('/my_watched')
def my_watched_page():
    return render_template('my_watched.html')

@app.route('/api/my_watched', methods=['GET'])
def api_get_my_watched():
    """获取我的看过列表（代理后端接口）"""
    status = request.args.get('status', 'watched')
    req_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort_by', 'create')
    order_by = request.args.get('order_by', 'desc')
    star = request.args.get('star', '')          # 评分筛选，可为空
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "status": status,
        "type": req_type,
        "sort_by": sort_by,
        "order_by": order_by,
        "star": star,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v2/users/review_movies", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 清单相关路由 =================

@app.route('/api/movie/<movie_id>/lists', methods=['GET'])
def api_get_movie_lists(movie_id):
    """获取当前影片相关的清单列表（含是否已加入标记）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)
    try:
        data = jav_client._get("/v1/lists/simple", params={
            "movie_id": movie_id,
            "page": page,
            "limit": limit
        })
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/lists/<list_id>/movie_action', methods=['POST'])
def api_list_movie_action(list_id):
    """加入或移除影片到指定清单"""
    movie_id = request.form.get('movie_id')
    action = request.form.get('action')   # 'add' 或 'remove'
    if not movie_id or action not in ('add', 'remove'):
        return jsonify({"success": 0, "error": "缺少必要参数"}), 400
    try:
        # 直接转发到后端接口
        data = {"movie_id": movie_id, "name": action}
        result = jav_client._post(f"/v1/lists/{list_id}/movie_actions", data=data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/lists', methods=['POST'])
def api_create_list():
    """创建新清单（并自动将当前影片加入）"""
    movie_id = request.form.get('movie_id')
    name = request.form.get('name')
    if not movie_id or not name:
        return jsonify({"success": 0, "error": "缺少必要参数"}), 400
    try:
        data = {"movie_id": movie_id, "name": name}
        result = jav_client._post("/v1/lists", data=data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


# ================= 我的清单列表页面 =================
@app.route('/my_lists')
def my_lists_page():
    """我的清单列表页"""
    return render_template('my_lists.html')


@app.route('/api/my_lists', methods=['GET'])
def api_get_my_lists():
    """获取我的清单列表数据"""
    sort_by = request.args.get('sort_by', 'create')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "sort_by": sort_by,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v1/lists", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 清单重命名 & 删除 =================

@app.route('/api/lists/<list_id>', methods=['PATCH'])
def api_update_list(list_id):
    """重命名清单"""
    # 官方 API 使用 query 参数传递新名称
    name = request.args.get('name') or request.form.get('name')
    if not name:
        return jsonify({"success": 0, "error": "缺少 name 参数"}), 400
    try:
        result = jav_client._patch(f"/v1/lists/{list_id}", params={"name": name})
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/lists/<list_id>', methods=['DELETE'])
def api_delete_list(list_id):
    """删除清单"""
    try:
        result = jav_client._delete(f"/v1/lists/{list_id}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# 我的收藏 - 演员
@app.route('/my/collected_actors')
def my_collected_actors_page():
    """渲染我的收藏演员页面"""
    return render_template('my_collected_actors.html')

@app.route('/api/actor/<actor_id>/collect', methods=['POST'])
def api_actor_collect(actor_id):
    """单个演员收藏/取消收藏接口"""
    data = request.json or {}
    action = data.get('action', 'collect')  # 'collect' 或 'uncollect'
    try:
        res = jav_client.collect_actor(actor_id, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/my/collected_actors', methods=['GET'])
def api_get_my_collected_actors():
    """获取我收藏的演员列表"""
    req_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    try:
        res = jav_client.get_collected_actors(req_type=req_type, page=page, limit=limit)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/my/collected_actors/batch_uncollect', methods=['POST'])
def api_batch_uncollect_collected_actors():
    """批量取消收藏演员接口"""
    data = request.json or {}
    actor_ids = data.get('ids', [])
    if not actor_ids:
        return jsonify({"success": 0, "message": "未选择任何演员"})
    try:
        res = jav_client.batch_uncollect_actors(actor_ids)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# ================= 清单收藏相关路由 =================

@app.route('/api/list/<list_id>/collect', methods=['POST'])
def api_list_collect(list_id):
    """收藏或取消收藏清单"""
    data = request.json or {}
    action = data.get('action', 'collect')   # 'collect' 或 'uncollect'
    if action not in ('collect', 'uncollect'):
        return jsonify({"success": 0, "error": "action 参数必须是 collect 或 uncollect"}), 400

    try:
        # 调用后端接口，使用 files 参数模拟 multipart/form-data
        result = jav_client._post(
            f"/v1/lists/{list_id}/collect_actions",
            files={"name": (None, action)}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/api/my/collected_lists', methods=['GET'])
def api_get_my_collected_lists():
    """获取我收藏的清单列表"""
    sort_by = request.args.get('sort_by', 'create')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    params = {
        "sort_by": sort_by,
        "page": page,
        "limit": limit
    }
    try:
        data = jav_client._get("/v1/users/collected_lists", params=params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500


@app.route('/my/collected_lists')
def my_collected_lists_page():
    """渲染我收藏的清单页面"""
    return render_template('my_collected_lists.html')

# 个人信息
@app.route('/profile')
def profile_page():
    """用户个人主页（前端异步加载数据）"""
    return render_template('profile.html')

@app.route('/api/v1/users', methods=['GET'])
def api_get_user_info():
    try:
        data = jav_client._get("/v1/users")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

@app.route('/api/v1/users/additional', methods=['GET'])
def api_get_user_additional():
    try:
        data = jav_client._get("/v1/users/additional")
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

# ================= 看短评相关路由 =================

@app.route('/reviews')
def reviews_page():
    """渲染看短评主页"""
    return render_template('reviews.html')


@app.route('/api/reviews', methods=['GET'])
def api_get_reviews():
    """获取热门短评列表代理接口"""
    period = request.args.get('period', 'latest')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)

    try:
        data = jav_client.get_hot_reviews(period=period, page=page, limit=limit)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# 评论点赞
@app.route('/api/movie/<movie_id>/reviews/<review_id>/like', methods=['POST'])
def api_review_like(movie_id, review_id):
    """点赞或取消点赞评论（toggle）"""
    try:
        # 官方接口无需 body，直接 POST 即可
        result = jav_client._post(f"/v1/movies/{movie_id}/reviews/{review_id}/like")
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：我的收藏 - 番号 =================

@app.route('/my/collected_codes')
def my_collected_codes_page():
    """渲染我的收藏番号页面"""
    return render_template('my_collected_codes.html')

@app.route('/api/my/collected_codes', methods=['GET'])
def api_get_my_collected_codes():
    """获取我收藏的番号列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    try:
        res = jav_client.get_collected_codes(page=page, limit=limit)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/code/<code_id>/collect', methods=['POST'])
def api_code_collect(code_id):
    """单个番号收藏/取消收藏接口"""
    data = request.json or {}
    action = data.get('action', 'collect')  # 'collect' 或 'uncollect'
    try:
        res = jav_client.collect_code(code_id, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/my/collected_codes/batch_uncollect', methods=['POST'])
def api_batch_uncollect_collected_codes():
    """批量取消收藏番号接口"""
    data = request.json or {}
    code_ids = data.get('ids', [])
    if not code_ids:
        return jsonify({"success": 0, "message": "未选择任何番号"})
    try:
        res = jav_client.batch_uncollect_codes(code_ids)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})


# ================= 新增：我的系列收藏路由 =================

@app.route('/my/collected_series')
def my_collected_series_page():
    """渲染我的收藏系列页面"""
    return render_template('my_collected_series.html')

@app.route('/api/my/collected_series', methods=['GET'])
def api_get_collected_series():
    """获取我收藏的系列列表数据"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    try:
        data = jav_client.get_collected_series(page=page, limit=limit)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

@app.route('/api/series/<series_id>/collect', methods=['POST'])
def api_collect_series(series_id):
    """处理收藏/取消收藏系列的操作"""
    data = request.get_json() or {}
    action = data.get('action', 'collect')
    try:
        res = jav_client.collect_series(series_id, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

# ================= 新增：我的收藏 - 导演 =================
@app.route('/my/collected_directors')
def my_collected_directors_page():
    """渲染我的收藏导演页面"""
    return render_template('my_collected_directors.html')

@app.route('/api/my/collected_directors', methods=['GET'])
def api_get_my_collected_directors():
    """获取我收藏的导演列表"""
    req_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    try:
        res = jav_client.get_collected_directors(req_type=req_type, page=page, limit=limit)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/director/<director_id>/collect', methods=['POST'])
def api_director_collect(director_id):
    """单个导演收藏/取消收藏接口"""
    data = request.json or {}
    action = data.get('action', 'collect')  # 'collect' 或 'uncollect'
    try:
        res = jav_client.collect_director(director_id, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/my/collected_directors/batch_uncollect', methods=['POST'])
def api_batch_uncollect_collected_directors():
    """批量取消收藏导演接口"""
    data = request.json or {}
    director_ids = data.get('ids', [])
    if not director_ids:
        return jsonify({"success": 0, "message": "未选择任何导演"})
    try:
        res = jav_client.batch_uncollect_directors(director_ids)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# ================= 新增：片商收藏相关路由 =================

@app.route('/my/collected_makers')
def my_collected_makers_page():
    """渲染我收藏的片商页面"""
    return render_template('my_collected_makers.html')

@app.route('/api/maker/<maker_id>/collect', methods=['POST'])
def api_maker_collect(maker_id):
    """单个片商收藏/取消收藏接口"""
    data = request.json or {}
    action = data.get('action', 'collect')  # 'collect' 或 'uncollect'
    try:
        res = jav_client.collect_maker(maker_id, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

@app.route('/api/my/collected_makers', methods=['GET'])
def api_get_my_collected_makers():
    """获取我收藏的片商列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)
    try:
        res = jav_client.get_collected_makers(page=page, limit=limit)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# 识图
@app.route('/search_image')
def search_image():
    """以图识图独立页面"""
    return render_template('search_image.html')

def is_valid_image(data: bytes) -> bool:
    """检查数据是否为有效的图片（JPEG/PNG/WEBP）"""
    if len(data) < 12:
        return False
    # JPEG: FF D8 FF
    if data[:3] == b'\xff\xd8\xff':
        return True
    # PNG: 89 50 4E 47
    if data[:4] == b'\x89PNG':
        return True
    # WEBP: RIFF????WEBP (前4字节 RIFF, 第8-11字节 WEBP)
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return True
    # 可选：用 PIL 再次验证（更严格）
    try:
        Image.open(io.BytesIO(data)).verify()
        return True
    except Exception:
        return False

def decrypt_image(enc: bytes) -> bytes:
    """解密异或加密的图片数据，首字节为密钥"""
    if not enc:
        return b""
    key = enc[0]
    return bytes(b ^ key for b in enc[1:])

@app.route('/api/image_proxy')
def image_proxy():
    max_retries = 3
    retry_delay = 1  # 初始延迟秒数
    url = request.args.get('url')
    if not url:
        return jsonify({"success": 0, "error": "缺少 url 参数"}), 400

    if 'c0.jdbstatic.com' in url:
        return redirect(url)

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            # 下载加密数据
            resp = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "Dart/3.5 (dart:io)"}
            )
            resp.raise_for_status()

            encrypted_data = resp.content
            decrypted = decrypt_image(encrypted_data)  # 自定义函数

            # 验证解密结果
            if not is_valid_image(decrypted):
                raise ValueError("解密后数据不是有效的图片")

            # 成功，根据后缀返回对应 MIME
            mimetype = 'image/jpeg'
            if url.lower().endswith('.png'):
                mimetype = 'image/png'
            elif url.lower().endswith('.webp'):
                mimetype = 'image/webp'

            # 构建响应，设置缓存头（强缓存 30 天）
            response = Response(decrypted, mimetype=mimetype)
            response.headers['Cache-Control'] = 'public, max-age=2592000'  # 30天

            return response

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                # 指数退避：1s, 2s, 4s...
                sleep_time = retry_delay * (2 ** (attempt - 1))
                time.sleep(sleep_time)
            # 否则继续下一次尝试

    # 所有重试均失败
    return jsonify({
        "success": 0,
        "error": f"下载或解密失败: {str(last_exception)}",
        "retries": max_retries
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host=cfg.HOST, port=cfg.PORT)
