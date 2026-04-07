"""taolib.site 模块测试 — 模型、服务层、路由集成测试."""
import pytest

# taolib.site 模块当前未集成到 taolib 包中，跳过测试
pytest.importorskip("taolib.site")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taolib.site.auth import SessionManager, hash_password, verify_password
from taolib.site.config import SiteConfig
from taolib.site.database import Base
from taolib.site.md import count_words, estimate_reading_time, render_markdown
from taolib.site.models import (
    AdminUser,
    Category,
)
from taolib.site.services import (
    create_article,
    create_category,
    create_comment,
    create_contact_message,
    delete_article,
    delete_category,
    delete_comment,
    delete_contact_message,
    get_all_articles,
    get_all_categories,
    get_all_comments,
    get_article_by_id,
    get_article_by_slug,
    get_category_article_counts,
    get_contact_messages,
    get_featured_articles,
    get_or_create_tag,
    get_pending_comments_count,
    get_published_articles,
    get_site_stats,
    mark_message_read,
    slugify,
    update_article,
    update_category,
    update_comment_status,
)

# ─── Fixtures ────────────────────────────────────────────


@pytest.fixture
def db_session():
    """创建内存数据库会话用于单元测试."""
    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def seeded_db(db_session):
    """带种子数据的会话（1 个分类 + 1 个管理员）."""
    cat = Category(name="测试", slug="test", color="#333", icon="T", sort_order=1)
    db_session.add(cat)
    admin = AdminUser(
        username="admin",
        password_hash=hash_password("changeme"),
        display_name="Admin",
    )
    db_session.add(admin)
    db_session.commit()
    return db_session


@pytest.fixture
def app():
    """创建测试用 FastAPI 应用.

    使用 StaticPool 确保 SQLite :memory: 在 TestClient 的
    工作线程中也能访问同一个数据库连接。
    """
    import taolib.site.database as db_mod

    old_engine = db_mod._engine
    old_session = db_mod._SessionLocal

    # 创建共享连接的引擎（StaticPool 让跨线程共用同一连接）
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    session_local = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    # 直接注入引擎和会话工厂，绕过 init_db 的防重入保护
    db_mod._engine = engine
    db_mod._SessionLocal = session_local
    Base.metadata.create_all(bind=engine)

    # 种子数据
    config = SiteConfig(
        site_title="测试站点",
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key-123",
        admin_username="admin",
        admin_password="testpass",
    )
    from taolib.site.seed import seed_database

    db = session_local()
    try:
        seed_database(db, config)
    finally:
        db.close()

    # 构建应用（跳过 init_db / create_tables，已手动完成）
    from pathlib import Path

    from fastapi import FastAPI, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates

    from taolib.site.app import _datefmt, _now, _shortdate

    application = FastAPI(title=config.site_title, docs_url=None, redoc_url=None)
    application.state.config = config

    pkg_dir = Path(__file__).resolve().parent.parent / "src" / "taolib" / "site"
    templates = Jinja2Templates(directory=str(pkg_dir / "templates"))
    templates.env.filters["datefmt"] = _datefmt
    templates.env.filters["shortdate"] = _shortdate
    templates.env.globals["now"] = _now
    application.state.templates = templates

    application.mount(
        "/static", StaticFiles(directory=str(pkg_dir / "static")), name="static"
    )

    from taolib.site.routes.admin import router as admin_router
    from taolib.site.routes.api import router as api_router
    from taolib.site.routes.public import router as public_router

    application.include_router(api_router)
    application.include_router(admin_router)
    application.include_router(public_router)

    @application.exception_handler(404)
    async def not_found(request: Request, _exc: Exception):
        from taolib.site.services import get_all_categories as _get_cats

        _db = db_mod.get_session()
        try:
            categories = _get_cats(_db)
        finally:
            _db.close()
        return templates.TemplateResponse(
            request,
            "404.html",
            {"request": request, "config": config, "categories": categories},
            status_code=404,
        )

    yield application

    # 恢复全局状态
    engine.dispose()
    db_mod._engine = old_engine
    db_mod._SessionLocal = old_session


@pytest.fixture
def client(app):
    """FastAPI 测试客户端."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def admin_client(client):
    """已登录管理员的测试客户端."""
    client.post("/admin/login", data={"username": "admin", "password": "testpass"})
    return client


# ═══════════════════════════════════════════════════════════
# 认证模块测试
# ═══════════════════════════════════════════════════════════


class TestAuth:
    def test_hash_password_not_deterministic(self):
        assert hash_password("abc") != hash_password("abc")

    def test_hash_password_different_inputs(self):
        assert hash_password("abc") != hash_password("xyz")

    def test_hash_password_is_bcrypt_format(self):
        h = hash_password("secret")
        assert h.startswith("$2")  # bcrypt hash prefix

    def test_verify_password_correct(self):
        h = hash_password("secret")
        assert verify_password("secret", h) is True

    def test_verify_password_wrong(self):
        h = hash_password("secret")
        assert verify_password("wrong", h) is False

    def test_session_manager_roundtrip(self):
        sm = SessionManager("my-secret", max_age=3600)
        token = sm.create_token(1, "admin")
        data = sm.verify_token(token)
        assert data is not None
        assert data["user_id"] == 1
        assert data["username"] == "admin"

    def test_session_manager_invalid_token(self):
        sm = SessionManager("my-secret", max_age=3600)
        assert sm.verify_token("garbage-token") is None

    def test_session_manager_wrong_secret(self):
        sm1 = SessionManager("secret-1", max_age=3600)
        sm2 = SessionManager("secret-2", max_age=3600)
        token = sm1.create_token(1, "admin")
        assert sm2.verify_token(token) is None


# ═══════════════════════════════════════════════════════════
# Markdown 模块测试
# ═══════════════════════════════════════════════════════════


class TestMarkdown:
    def test_render_markdown_basic(self):
        result = render_markdown("# Hello\n\nworld")
        assert "<h1" in result["html"]
        assert "Hello" in result["html"]

    def test_render_markdown_code_block(self):
        result = render_markdown("```python\nprint('hi')\n```")
        assert "print" in result["html"]

    def test_render_markdown_toc(self):
        result = render_markdown("## Heading Two\n\n### Heading Three")
        assert result["toc"]  # toc 应非空

    def test_count_words_chinese(self):
        assert count_words("你好世界") == 4

    def test_count_words_english(self):
        assert count_words("hello world") == 2

    def test_count_words_mixed(self):
        count = count_words("你好 hello world")
        assert count == 4  # 2 中文 + 2 英文

    def test_estimate_reading_time_minimum(self):
        assert estimate_reading_time("hi") >= 1

    def test_estimate_reading_time_long(self):
        # 900 字 / 300 wpm = 3 分钟
        text = "字" * 900
        assert estimate_reading_time(text) == 3


# ═══════════════════════════════════════════════════════════
# 工具函数测试
# ═══════════════════════════════════════════════════════════


class TestSlugify:
    def test_english(self):
        assert slugify("Hello World") == "hello-world"

    def test_chinese(self):
        slug = slugify("你好世界")
        assert "你好世界" in slug

    def test_special_chars(self):
        slug = slugify("hello@world#test!")
        assert "@" not in slug
        assert "#" not in slug

    def test_multiple_spaces(self):
        assert slugify("hello   world") == "hello-world"

    def test_empty_returns_untitled(self):
        assert slugify("") == "untitled"
        assert slugify("   ") == "untitled"


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 分类
# ═══════════════════════════════════════════════════════════


class TestCategoryServices:
    def test_create_category(self, db_session):
        cat = create_category(db_session, name="Python", slug="python", color="#3572A5")
        assert cat.id is not None
        assert cat.slug == "python"

    def test_create_category_auto_slug(self, db_session):
        cat = create_category(db_session, name="My Category")
        assert cat.slug == "my-category"

    def test_get_all_categories(self, db_session):
        create_category(db_session, name="A", slug="a", sort_order=2)
        create_category(db_session, name="B", slug="b", sort_order=1)
        cats = get_all_categories(db_session)
        assert len(cats) == 2
        assert cats[0].name == "B"  # 按 sort_order 排序

    def test_update_category(self, db_session):
        cat = create_category(db_session, name="Old", slug="old")
        updated = update_category(db_session, cat.id, name="New")
        assert updated.name == "New"

    def test_update_category_not_found(self, db_session):
        assert update_category(db_session, 9999, name="X") is None

    def test_delete_category(self, db_session):
        cat = create_category(db_session, name="Del", slug="del")
        assert delete_category(db_session, cat.id) is True
        assert get_all_categories(db_session) == []

    def test_delete_category_not_found(self, db_session):
        assert delete_category(db_session, 9999) is False


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 标签
# ═══════════════════════════════════════════════════════════


class TestTagServices:
    def test_get_or_create_tag_new(self, db_session):
        tag = get_or_create_tag(db_session, "Python")
        db_session.commit()
        assert tag.name == "Python"
        assert tag.slug == "python"

    def test_get_or_create_tag_existing(self, db_session):
        t1 = get_or_create_tag(db_session, "Python")
        db_session.commit()
        t2 = get_or_create_tag(db_session, "Python")
        assert t1.id == t2.id


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 文章
# ═══════════════════════════════════════════════════════════


class TestArticleServices:
    def test_create_article_draft(self, seeded_db):
        article = create_article(seeded_db, title="Draft", content="content")
        assert article.status == "draft"
        assert article.published_at is None

    def test_create_article_published(self, seeded_db):
        article = create_article(
            seeded_db, title="Published", content="content", status="published"
        )
        assert article.status == "published"
        assert article.published_at is not None

    def test_create_article_with_tags(self, seeded_db):
        article = create_article(
            seeded_db,
            title="Tagged",
            content="content",
            tag_names=["Python", "Web"],
        )
        assert len(article.tags) == 2
        assert {t.name for t in article.tags} == {"Python", "Web"}

    def test_create_article_with_category(self, seeded_db):
        cats = get_all_categories(seeded_db)
        article = create_article(
            seeded_db,
            title="Categorized",
            content="content",
            category_id=cats[0].id,
        )
        assert article.category_id == cats[0].id

    def test_create_article_slug_unique(self, seeded_db):
        a1 = create_article(seeded_db, title="Same Title", content="1")
        a2 = create_article(seeded_db, title="Same Title", content="2")
        assert a1.slug != a2.slug

    def test_create_article_word_count(self, seeded_db):
        article = create_article(
            seeded_db, title="Count", content="这是一段包含十个中文字符的内容"
        )
        assert article.word_count > 0

    def test_get_published_articles(self, seeded_db):
        create_article(seeded_db, title="Pub", content="c", status="published")
        create_article(seeded_db, title="Draft", content="c", status="draft")
        articles, total = get_published_articles(seeded_db)
        assert total == 1
        assert articles[0].title == "Pub"

    def test_get_all_articles(self, seeded_db):
        create_article(seeded_db, title="A1", content="c", status="published")
        create_article(seeded_db, title="A2", content="c", status="draft")
        articles, total = get_all_articles(seeded_db)
        assert total == 2

    def test_get_all_articles_filter_status(self, seeded_db):
        create_article(seeded_db, title="A1", content="c", status="published")
        create_article(seeded_db, title="A2", content="c", status="draft")
        articles, total = get_all_articles(seeded_db, status="draft")
        assert total == 1
        assert articles[0].title == "A2"

    def test_get_featured_articles(self, seeded_db):
        create_article(
            seeded_db, title="F", content="c", status="published", featured=True
        )
        create_article(seeded_db, title="NF", content="c", status="published")
        featured = get_featured_articles(seeded_db)
        assert len(featured) == 1
        assert featured[0].title == "F"

    def test_get_article_by_slug(self, seeded_db):
        create_article(seeded_db, title="Slug Test", content="c")
        article = get_article_by_slug(seeded_db, "slug-test")
        assert article is not None
        assert article.title == "Slug Test"

    def test_get_article_by_id(self, seeded_db):
        created = create_article(seeded_db, title="ID Test", content="c")
        article = get_article_by_id(seeded_db, created.id)
        assert article is not None
        assert article.title == "ID Test"

    def test_update_article(self, seeded_db):
        article = create_article(seeded_db, title="Old", content="old content")
        updated = update_article(
            seeded_db, article.id, title="New", content="new content"
        )
        assert updated.title == "New"
        assert updated.word_count > 0

    def test_update_article_tags(self, seeded_db):
        article = create_article(
            seeded_db, title="T", content="c", tag_names=["A", "B"]
        )
        updated = update_article(seeded_db, article.id, tag_names=["C"])
        assert len(updated.tags) == 1
        assert updated.tags[0].name == "C"

    def test_update_article_not_found(self, seeded_db):
        assert update_article(seeded_db, 9999, title="X") is None

    def test_delete_article(self, seeded_db):
        article = create_article(seeded_db, title="Del", content="c")
        assert delete_article(seeded_db, article.id) is True
        assert get_article_by_id(seeded_db, article.id) is None

    def test_delete_article_not_found(self, seeded_db):
        assert delete_article(seeded_db, 9999) is False

    def test_get_published_articles_search(self, seeded_db):
        create_article(
            seeded_db, title="Python Guide", content="learn python", status="published"
        )
        create_article(
            seeded_db, title="Java Guide", content="learn java", status="published"
        )
        articles, total = get_published_articles(seeded_db, search="python")
        assert total == 1

    def test_get_published_articles_pagination(self, seeded_db):
        for i in range(5):
            create_article(
                seeded_db,
                title=f"Page {i}",
                content="c",
                status="published",
            )
        articles, total = get_published_articles(seeded_db, page=1, per_page=2)
        assert total == 5
        assert len(articles) == 2


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 评论
# ═══════════════════════════════════════════════════════════


class TestCommentServices:
    def test_create_comment(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        comment = create_comment(
            seeded_db,
            article_id=article.id,
            author_name="User",
            author_email="u@test.com",
            content="Nice!",
        )
        assert comment.status == "pending"

    def test_create_comment_auto_approve(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        comment = create_comment(
            seeded_db,
            article_id=article.id,
            author_name="User",
            author_email="u@test.com",
            content="Auto!",
            auto_approve=True,
        )
        assert comment.status == "approved"

    def test_update_comment_status(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        comment = create_comment(
            seeded_db,
            article_id=article.id,
            author_name="U",
            author_email="u@t.com",
            content="Hi",
        )
        updated = update_comment_status(seeded_db, comment.id, "approved")
        assert updated.status == "approved"

    def test_update_comment_status_not_found(self, seeded_db):
        assert update_comment_status(seeded_db, 9999, "approved") is None

    def test_delete_comment(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        comment = create_comment(
            seeded_db,
            article_id=article.id,
            author_name="U",
            author_email="u@t.com",
            content="Del",
        )
        assert delete_comment(seeded_db, comment.id) is True

    def test_delete_comment_not_found(self, seeded_db):
        assert delete_comment(seeded_db, 9999) is False

    def test_get_all_comments_filter(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        create_comment(
            seeded_db,
            article_id=article.id,
            author_name="U1",
            author_email="u@t.com",
            content="c1",
        )
        create_comment(
            seeded_db,
            article_id=article.id,
            author_name="U2",
            author_email="u@t.com",
            content="c2",
            auto_approve=True,
        )
        comments, total = get_all_comments(seeded_db, status="pending")
        assert total == 1

    def test_get_pending_comments_count(self, seeded_db):
        article = create_article(seeded_db, title="A", content="c", status="published")
        create_comment(
            seeded_db,
            article_id=article.id,
            author_name="U",
            author_email="u@t.com",
            content="p",
        )
        assert get_pending_comments_count(seeded_db) == 1


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 联系消息
# ═══════════════════════════════════════════════════════════


class TestContactMessageServices:
    def test_create_message(self, db_session):
        msg = create_contact_message(
            db_session, name="Test", email="t@t.com", message="hello"
        )
        assert msg.id is not None
        assert msg.is_read is False

    def test_get_messages(self, db_session):
        create_contact_message(db_session, name="A", email="a@t.com", message="m1")
        create_contact_message(db_session, name="B", email="b@t.com", message="m2")
        messages, total = get_contact_messages(db_session)
        assert total == 2

    def test_mark_read(self, db_session):
        msg = create_contact_message(
            db_session, name="T", email="t@t.com", message="hi"
        )
        updated = mark_message_read(db_session, msg.id)
        assert updated.is_read is True

    def test_mark_read_not_found(self, db_session):
        assert mark_message_read(db_session, 9999) is None

    def test_delete_message(self, db_session):
        msg = create_contact_message(
            db_session, name="T", email="t@t.com", message="hi"
        )
        assert delete_contact_message(db_session, msg.id) is True
        messages, total = get_contact_messages(db_session)
        assert total == 0

    def test_delete_message_not_found(self, db_session):
        assert delete_contact_message(db_session, 9999) is False


# ═══════════════════════════════════════════════════════════
# 服务层测试 — 统计
# ═══════════════════════════════════════════════════════════


class TestStatsServices:
    def test_get_site_stats(self, seeded_db):
        create_article(seeded_db, title="A", content="c", status="published")
        stats = get_site_stats(seeded_db)
        assert stats["total_articles"] == 1
        assert stats["published_articles"] == 1
        assert stats["draft_articles"] == 0
        assert stats["total_categories"] == 1

    def test_get_category_article_counts(self, seeded_db):
        cats = get_all_categories(seeded_db)
        create_article(
            seeded_db,
            title="A",
            content="c",
            status="published",
            category_id=cats[0].id,
        )
        counts = get_category_article_counts(seeded_db)
        assert counts.get("test") == 1


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 公共页面
# ═══════════════════════════════════════════════════════════


class TestPublicRoutes:
    def test_home(self, client):
        r = client.get("/", follow_redirects=True)
        assert r.status_code == 200
        assert "测试站点" in r.text

    def test_about(self, client):
        r = client.get("/about", follow_redirects=True)
        assert r.status_code == 200

    def test_contact(self, client):
        r = client.get("/contact", follow_redirects=True)
        assert r.status_code == 200

    def test_archive(self, client):
        r = client.get("/archive", follow_redirects=True)
        assert r.status_code == 200

    def test_search_empty(self, client):
        r = client.get("/search", follow_redirects=True)
        assert r.status_code == 200

    def test_search_with_query(self, client):
        r = client.get("/search?q=test", follow_redirects=True)
        assert r.status_code == 200

    def test_rss_feed(self, client):
        r = client.get("/feed.xml", follow_redirects=True)
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "")

    def test_atom_feed(self, client):
        r = client.get("/atom.xml", follow_redirects=True)
        assert r.status_code == 200

    def test_article_page(self, client):
        """种子数据包含 welcome 文章."""
        r = client.get("/article/welcome", follow_redirects=True)
        assert r.status_code == 200
        assert "欢迎" in r.text

    def test_article_not_found(self, client):
        r = client.get("/article/nonexistent", follow_redirects=True)
        assert r.status_code == 404

    def test_category_page(self, client):
        r = client.get("/category/dao", follow_redirects=True)
        assert r.status_code == 200

    def test_category_not_found(self, client):
        r = client.get("/category/nonexistent", follow_redirects=True)
        assert r.status_code == 404

    def test_404_page(self, client):
        r = client.get("/nonexistent-path", follow_redirects=True)
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 管理后台认证
# ═══════════════════════════════════════════════════════════


class TestAdminAuth:
    def test_login_page(self, client):
        r = client.get("/admin/login", follow_redirects=True)
        assert r.status_code == 200

    def test_login_success(self, client):
        r = client.post(
            "/admin/login", data={"username": "admin", "password": "testpass"}
        )
        assert r.status_code == 302
        assert r.headers["location"] == "/admin"
        assert "session" in r.cookies

    def test_login_failure(self, client):
        r = client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert "用户名或密码错误" in r.text

    def test_logout(self, admin_client):
        r = admin_client.get("/admin/logout")
        assert r.status_code == 302
        assert r.headers["location"] == "/admin/login"

    def test_admin_redirect_when_not_logged_in(self, client):
        r = client.get("/admin")
        assert r.status_code == 302
        assert "/admin/login" in r.headers["location"]

    def test_already_logged_in_redirect(self, admin_client):
        r = admin_client.get("/admin/login")
        assert r.status_code == 302
        assert r.headers["location"] == "/admin"


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 管理后台页面
# ═══════════════════════════════════════════════════════════


class TestAdminPages:
    def test_dashboard(self, admin_client):
        r = admin_client.get("/admin", follow_redirects=True)
        assert r.status_code == 200

    def test_articles_list(self, admin_client):
        r = admin_client.get("/admin/articles", follow_redirects=True)
        assert r.status_code == 200

    def test_comments_list(self, admin_client):
        r = admin_client.get("/admin/comments", follow_redirects=True)
        assert r.status_code == 200

    def test_categories_page(self, admin_client):
        r = admin_client.get("/admin/categories", follow_redirects=True)
        assert r.status_code == 200

    def test_messages_page(self, admin_client):
        r = admin_client.get("/admin/messages", follow_redirects=True)
        assert r.status_code == 200

    def test_new_article_page(self, admin_client):
        r = admin_client.get("/admin/articles/new", follow_redirects=True)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 文章 CRUD
# ═══════════════════════════════════════════════════════════


class TestAdminArticleCRUD:
    def test_create_article(self, admin_client):
        r = admin_client.post(
            "/admin/articles/new",
            data={
                "title": "New Article",
                "content": "# Test\n\nContent here.",
                "category_id": "",
                "tags": "python,test",
                "status": "draft",
                "excerpt": "",
                "featured": "",
                "cover_image": "",
            },
        )
        assert r.status_code == 302
        assert "/edit" in r.headers["location"]

    def test_edit_article_page(self, admin_client):
        # 种子数据中有 ID=1 的 welcome 文章
        r = admin_client.get("/admin/articles/1/edit", follow_redirects=True)
        assert r.status_code == 200
        assert "欢迎" in r.text

    def test_edit_article_not_found(self, admin_client):
        r = admin_client.get("/admin/articles/9999/edit")
        assert r.status_code == 302

    def test_update_article(self, admin_client):
        r = admin_client.post(
            "/admin/articles/1/edit",
            data={
                "title": "Updated Title",
                "content": "Updated content",
                "category_id": "",
                "tags": "",
                "status": "published",
                "excerpt": "",
                "featured": "",
                "cover_image": "",
            },
        )
        assert r.status_code == 302
        assert "saved=1" in r.headers["location"]

    def test_delete_article(self, admin_client):
        # 先创建一篇文章
        admin_client.post(
            "/admin/articles/new",
            data={
                "title": "To Delete",
                "content": "c",
                "category_id": "",
                "tags": "",
                "status": "draft",
                "excerpt": "",
                "featured": "",
                "cover_image": "",
            },
        )
        r = admin_client.post("/admin/articles/2/delete")
        assert r.status_code == 302
        assert r.headers["location"] == "/admin/articles"


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 分类 CRUD
# ═══════════════════════════════════════════════════════════


class TestAdminCategoryCRUD:
    def test_create_category(self, admin_client):
        r = admin_client.post(
            "/admin/categories/new",
            data={
                "name": "New Cat",
                "slug": "new-cat",
                "description": "desc",
                "color": "#ff0000",
                "icon": "N",
                "sort_order": "10",
            },
        )
        assert r.status_code == 302
        assert r.headers["location"] == "/admin/categories"

    def test_update_category(self, admin_client):
        r = admin_client.post(
            "/admin/categories/1/edit",
            data={
                "name": "Updated",
                "slug": "dao",
                "description": "updated",
                "color": "#000",
                "icon": "U",
                "sort_order": "1",
            },
        )
        assert r.status_code == 302

    def test_delete_category(self, admin_client):
        # 创建一个新分类用于删除
        admin_client.post(
            "/admin/categories/new",
            data={
                "name": "Temp",
                "slug": "temp",
                "description": "",
                "color": "#999",
                "icon": "",
                "sort_order": "99",
            },
        )
        r = admin_client.post("/admin/categories/6/delete")
        assert r.status_code == 302


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 评论管理
# ═══════════════════════════════════════════════════════════


class TestAdminCommentManagement:
    def _create_comment(self, client):
        """通过 API 提交评论."""
        client.post(
            "/api/comments",
            data={
                "article_id": "1",
                "author_name": "Visitor",
                "author_email": "v@test.com",
                "content": "Test comment",
                "parent_id": "0",
            },
        )

    def test_approve_comment(self, admin_client):
        self._create_comment(admin_client)
        r = admin_client.post("/admin/comments/1/approve")
        assert r.status_code == 302

    def test_reject_comment(self, admin_client):
        self._create_comment(admin_client)
        r = admin_client.post("/admin/comments/1/reject")
        assert r.status_code == 302

    def test_delete_comment(self, admin_client):
        self._create_comment(admin_client)
        r = admin_client.post("/admin/comments/1/delete")
        assert r.status_code == 302


# ═══════════════════════════════════════════════════════════
# 路由集成测试 — 消息管理
# ═══════════════════════════════════════════════════════════


class TestAdminMessageManagement:
    def _create_message(self, client):
        client.post(
            "/api/contact",
            data={
                "name": "Visitor",
                "email": "v@test.com",
                "subject": "Hello",
                "message": "Test message",
            },
        )

    def test_mark_read(self, admin_client):
        self._create_message(admin_client)
        r = admin_client.post("/admin/messages/1/read")
        assert r.status_code == 302

    def test_delete_message(self, admin_client):
        self._create_message(admin_client)
        r = admin_client.post("/admin/messages/1/delete")
        assert r.status_code == 302


# ═══════════════════════════════════════════════════════════
# API 路由测试
# ═══════════════════════════════════════════════════════════


class TestAPIRoutes:
    def test_submit_comment(self, client):
        r = client.post(
            "/api/comments",
            data={
                "article_id": "1",
                "author_name": "User",
                "author_email": "u@test.com",
                "content": "Hello",
                "parent_id": "0",
            },
        )
        assert r.status_code == 302
        assert "comment_status" in r.headers["location"]

    def test_submit_comment_empty_content(self, client):
        r = client.post(
            "/api/comments",
            data={
                "article_id": "1",
                "author_name": "User",
                "author_email": "u@test.com",
                "content": "   ",
                "parent_id": "0",
            },
            follow_redirects=True,
        )
        assert r.status_code == 400

    def test_submit_comment_article_not_found(self, client):
        r = client.post(
            "/api/comments",
            data={
                "article_id": "9999",
                "author_name": "User",
                "author_email": "u@test.com",
                "content": "Hello",
                "parent_id": "0",
            },
            follow_redirects=True,
        )
        assert r.status_code == 404

    def test_submit_contact(self, client):
        r = client.post(
            "/api/contact",
            data={
                "name": "Test",
                "email": "t@test.com",
                "subject": "Hi",
                "message": "Hello",
            },
        )
        assert r.status_code == 302
        assert "success" in r.headers["location"]

    def test_submit_contact_empty(self, client):
        # name/email/message 非空但全空白 -> 触发业务层校验重定向
        r = client.post(
            "/api/contact",
            data={"name": "X", "email": "x@t.com", "subject": "", "message": "   "},
        )
        assert r.status_code == 302
        assert "error" in r.headers["location"]

    def test_preview_markdown(self, admin_client):
        r = admin_client.post(
            "/api/preview-markdown",
            data={"content": "# Hello"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        data = r.json()
        assert "<h1" in data["html"]


# ═══════════════════════════════════════════════════════════
# 配置测试
# ═══════════════════════════════════════════════════════════


class TestConfig:
    def test_default_config(self):
        config = SiteConfig()
        assert config.site_title == "道源"
        assert config.articles_per_page == 10
        assert "sqlite" in config.database_url

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("TAOLIB_SITE_TITLE", "My Blog")
        monkeypatch.setenv("TAOLIB_SITE_ARTICLES_PER_PAGE", "20")
        config = SiteConfig.from_env()
        assert config.site_title == "My Blog"
        assert config.articles_per_page == 20
