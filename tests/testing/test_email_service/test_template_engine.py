"""模板引擎测试。"""

import pytest

from taolib.testing.email_service.errors import TemplateRenderError
from taolib.testing.email_service.models.enums import EmailType
from taolib.testing.email_service.models.template import TemplateDocument
from taolib.testing.email_service.template.engine import TemplateEngine


class TestTemplateEngine:
    def setup_method(self):
        self.engine = TemplateEngine(unsubscribe_base_url="http://localhost:8002")

    def test_render_simple_variables(self, sample_template_document):
        result = self.engine.render(
            template_doc=sample_template_document,
            variables={"name": "Alice"},
        )
        assert result.subject == "Welcome, Alice!"
        assert "Alice" in result.html_body
        assert result.text_body == "Welcome, Alice!"

    def test_render_conditional(self):
        template = TemplateDocument(
            _id="t1",
            name="conditional",
            subject_template="Hello",
            html_template="{% if vip %}<b>VIP</b>{% else %}Regular{% endif %}",
        )
        result = self.engine.render(template, {"vip": True})
        assert "<b>VIP</b>" in result.html_body

        result = self.engine.render(template, {"vip": False})
        assert "Regular" in result.html_body

    def test_render_loop(self):
        template = TemplateDocument(
            _id="t2",
            name="loop",
            subject_template="Items",
            html_template="{% for item in items %}<li>{{ item }}</li>{% endfor %}",
        )
        result = self.engine.render(template, {"items": ["A", "B", "C"]})
        assert "<li>A</li>" in result.html_body
        assert "<li>C</li>" in result.html_body

    def test_render_missing_variable_raises(self):
        template = TemplateDocument(
            _id="t3",
            name="missing",
            subject_template="{{ missing_var }}",
            html_template="<p>body</p>",
        )
        with pytest.raises(TemplateRenderError):
            self.engine.render(template, {})

    def test_marketing_email_unsubscribe_link(self, sample_template_document):
        result = self.engine.render(
            template_doc=sample_template_document,
            variables={"name": "Bob"},
            email_type=EmailType.MARKETING,
            recipient_email="bob@example.com",
            unsubscribe_token="tok-123",
        )
        assert "unsubscribe" in result.html_body.lower()
        assert "tok-123" in result.html_body
        assert "bob@example.com" in result.html_body

    def test_transactional_no_unsubscribe_link(self, sample_template_document):
        result = self.engine.render(
            template_doc=sample_template_document,
            variables={"name": "Charlie"},
            email_type=EmailType.TRANSACTIONAL,
        )
        assert "unsubscribe" not in result.html_body.lower()

    def test_validate_template_valid(self):
        errors = self.engine.validate_template("<p>{{ name }}</p>", {"name": "test"})
        assert errors == []

    def test_validate_template_syntax_error(self):
        errors = self.engine.validate_template("{% if %}")
        assert len(errors) > 0
        assert "Syntax error" in errors[0] or "error" in errors[0].lower()

    def test_validate_template_missing_var(self):
        errors = self.engine.validate_template("{{ missing }}", {})
        assert len(errors) > 0



