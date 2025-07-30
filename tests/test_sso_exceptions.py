"""
SSO异常类的单元测试

测试所有自定义异常类的功能，包括错误信息格式化、
上下文信息管理和修复建议提供。
"""

import pytest
from kolja_aws.sso_exceptions import (
    SSOConfigError,
    InvalidSSOConfigError,
    MissingSSOConfigError,
    InvalidURLError,
    InvalidRegionError,
    SSOConfigFileError,
    SSOTemplateGenerationError
)


class TestSSOConfigError:
    """测试基础异常类SSOConfigError"""
    
    def test_basic_error_creation(self):
        """测试基本错误创建"""
        error = SSOConfigError("测试错误消息")
        assert str(error) == "测试错误消息"
        assert error.context == {}
        assert error.suggestions == []
    
    def test_error_with_context(self):
        """测试带上下文信息的错误"""
        context = {"key": "value", "number": 42}
        error = SSOConfigError("测试错误", context=context)
        
        error_str = str(error)
        assert "测试错误" in error_str
        assert "上下文信息" in error_str
        assert "key" in error_str
        assert "value" in error_str
    
    def test_error_with_suggestions(self):
        """测试带修复建议的错误"""
        suggestions = ["建议1", "建议2", "建议3"]
        error = SSOConfigError("测试错误", suggestions=suggestions)
        
        error_str = str(error)
        assert "测试错误" in error_str
        assert "修复建议" in error_str
        assert "1. 建议1" in error_str
        assert "2. 建议2" in error_str
        assert "3. 建议3" in error_str
    
    def test_error_with_context_and_suggestions(self):
        """测试同时包含上下文和建议的错误"""
        context = {"session": "test-session"}
        suggestions = ["检查配置", "重新尝试"]
        error = SSOConfigError("完整错误", context=context, suggestions=suggestions)
        
        error_str = str(error)
        assert "完整错误" in error_str
        assert "上下文信息" in error_str
        assert "修复建议" in error_str
        assert "session" in error_str
        assert "检查配置" in error_str


class TestInvalidSSOConfigError:
    """测试无效SSO配置错误"""
    
    def test_invalid_config_error_creation(self):
        """测试无效配置错误创建"""
        error = InvalidSSOConfigError(
            session_name="test-session",
            field_name="sso_start_url",
            field_value="invalid-url",
            expected_format="https://..."
        )
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "sso_start_url" in error_str
        assert "invalid-url" in error_str
        assert "无效" in error_str
        
        # 检查上下文信息
        assert error.context["session_name"] == "test-session"
        assert error.context["field_name"] == "sso_start_url"
        assert error.context["field_value"] == "invalid-url"
        assert error.context["expected_format"] == "https://..."
        
        # 检查修复建议
        assert len(error.suggestions) > 0
        assert any("格式符合" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_config_error_with_additional_context(self):
        """测试带额外上下文的无效配置错误"""
        additional_context = {"config_file": "settings.toml"}
        error = InvalidSSOConfigError(
            session_name="prod",
            field_name="sso_region",
            field_value="invalid-region",
            expected_format="AWS region format",
            context=additional_context
        )
        
        assert error.context["config_file"] == "settings.toml"
        assert error.context["session_name"] == "prod"


class TestMissingSSOConfigError:
    """测试缺失SSO配置错误"""
    
    def test_missing_field_error(self):
        """测试缺失字段错误"""
        error = MissingSSOConfigError(
            missing_item="sso_start_url",
            item_type="field",
            session_name="test-session"
        )
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "sso_start_url" in error_str
        assert "缺少必需的字段" in error_str
        
        # 检查修复建议包含字段添加指导
        assert any("添加" in suggestion and "sso_start_url" in suggestion 
                  for suggestion in error.suggestions)
    
    def test_missing_session_error(self):
        """测试缺失会话错误"""
        error = MissingSSOConfigError(
            missing_item="prod-session",
            item_type="session"
        )
        
        error_str = str(error)
        assert "prod-session" in error_str
        assert "未找到SSO会话配置" in error_str
        
        # 检查修复建议包含会话添加指导
        assert any("添加" in suggestion and "sso_sessions.prod-session" in suggestion 
                  for suggestion in error.suggestions)
    
    def test_missing_section_error(self):
        """测试缺失配置部分错误"""
        error = MissingSSOConfigError(
            missing_item="sso_sessions",
            item_type="section"
        )
        
        error_str = str(error)
        assert "sso_sessions" in error_str
        assert "缺少" in error_str and "配置部分" in error_str
        
        # 检查修复建议包含部分添加指导
        assert any("[sso_sessions]" in suggestion for suggestion in error.suggestions)
    
    def test_missing_config_with_context(self):
        """测试带上下文的缺失配置错误"""
        context = {"config_path": "/path/to/settings.toml"}
        error = MissingSSOConfigError(
            missing_item="sso_region",
            item_type="field",
            session_name="dev",
            context=context
        )
        
        assert error.context["config_path"] == "/path/to/settings.toml"
        assert error.context["missing_item"] == "sso_region"


class TestInvalidURLError:
    """测试无效URL错误"""
    
    def test_invalid_url_error_basic(self):
        """测试基本无效URL错误"""
        error = InvalidURLError("not-a-url")
        
        error_str = str(error)
        assert "not-a-url" in error_str
        assert "格式无效" in error_str
        
        # 检查修复建议包含URL格式指导
        assert any("https://" in suggestion for suggestion in error.suggestions)
        assert any("域名" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_url_error_with_session(self):
        """测试带会话名的无效URL错误"""
        error = InvalidURLError("invalid-url", session_name="test-session")
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "invalid-url" in error_str
        assert "起始URL" in error_str
        
        assert error.context["invalid_url"] == "invalid-url"
        assert error.context["session_name"] == "test-session"
    
    def test_invalid_url_error_with_context(self):
        """测试带额外上下文的无效URL错误"""
        context = {"validation_step": "initial_check"}
        error = InvalidURLError("bad-url", context=context)
        
        assert error.context["validation_step"] == "initial_check"
        assert error.context["invalid_url"] == "bad-url"


class TestInvalidRegionError:
    """测试无效AWS区域错误"""
    
    def test_invalid_region_error_basic(self):
        """测试基本无效区域错误"""
        error = InvalidRegionError("invalid-region")
        
        error_str = str(error)
        assert "invalid-region" in error_str
        assert "格式无效" in error_str
        
        # 检查修复建议包含区域格式指导
        assert any("us-east-1" in suggestion for suggestion in error.suggestions)
        assert any("AWS区域代码" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_region_error_with_session(self):
        """测试带会话名的无效区域错误"""
        error = InvalidRegionError("bad-region", session_name="prod")
        
        error_str = str(error)
        assert "prod" in error_str
        assert "bad-region" in error_str
        assert "AWS区域" in error_str
        
        assert error.context["invalid_region"] == "bad-region"
        assert error.context["session_name"] == "prod"
    
    def test_invalid_region_error_suggestions(self):
        """测试无效区域错误的修复建议"""
        error = InvalidRegionError("wrong")
        
        suggestions_text = " ".join(error.suggestions)
        assert "ap-southeast-2" in suggestions_text
        assert "cn-northwest-1" in suggestions_text
        assert "拼写" in suggestions_text
        assert "AWS标准格式" in suggestions_text


class TestSSOConfigFileError:
    """测试SSO配置文件错误"""
    
    def test_file_read_error(self):
        """测试文件读取错误"""
        original_error = FileNotFoundError("文件不存在")
        error = SSOConfigFileError(
            file_path="/path/to/settings.toml",
            operation="read",
            original_error=original_error
        )
        
        error_str = str(error)
        assert "/path/to/settings.toml" in error_str
        assert "read操作失败" in error_str
        assert "文件不存在" in error_str
        
        # 检查读取操作的修复建议
        assert any("文件是否存在" in suggestion for suggestion in error.suggestions)
        assert any("读取权限" in suggestion for suggestion in error.suggestions)
    
    def test_file_write_error(self):
        """测试文件写入错误"""
        error = SSOConfigFileError(
            file_path="/readonly/settings.toml",
            operation="write"
        )
        
        error_str = str(error)
        assert "write操作失败" in error_str
        
        # 检查写入操作的修复建议
        assert any("写入权限" in suggestion for suggestion in error.suggestions)
        assert any("磁盘空间" in suggestion for suggestion in error.suggestions)
    
    def test_file_parse_error(self):
        """测试文件解析错误"""
        parse_error = ValueError("TOML格式错误")
        error = SSOConfigFileError(
            file_path="settings.toml",
            operation="parse",
            original_error=parse_error
        )
        
        error_str = str(error)
        assert "parse操作失败" in error_str
        assert "TOML格式错误" in error_str
        
        # 检查解析操作的修复建议
        assert any("TOML文件格式" in suggestion for suggestion in error.suggestions)
        assert any("TOML标准" in suggestion for suggestion in error.suggestions)
    
    def test_file_error_with_context(self):
        """测试带上下文的文件错误"""
        context = {"line_number": 15, "column": 8}
        error = SSOConfigFileError(
            file_path="config.toml",
            operation="parse",
            context=context
        )
        
        assert error.context["line_number"] == 15
        assert error.context["column"] == 8
        assert error.context["file_path"] == "config.toml"


class TestSSOTemplateGenerationError:
    """测试SSO模板生成错误"""
    
    def test_session_block_generation_error(self):
        """测试会话块生成错误"""
        error = SSOTemplateGenerationError(
            template_type="session_block",
            reason="缺少必需的配置字段"
        )
        
        error_str = str(error)
        assert "session_block模板生成失败" in error_str
        assert "缺少必需的配置字段" in error_str
        
        # 检查模板生成的修复建议
        assert any("SSO配置是否完整" in suggestion for suggestion in error.suggestions)
        assert any("必需的配置字段" in suggestion for suggestion in error.suggestions)
    
    def test_full_template_generation_error(self):
        """测试完整模板生成错误"""
        error = SSOTemplateGenerationError(
            template_type="full_template",
            reason="配置数据格式不正确"
        )
        
        error_str = str(error)
        assert "full_template模板生成失败" in error_str
        assert "配置数据格式不正确" in error_str
        
        assert error.context["template_type"] == "full_template"
        assert error.context["failure_reason"] == "配置数据格式不正确"
    
    def test_template_generation_error_with_context(self):
        """测试带上下文的模板生成错误"""
        context = {
            "session_name": "prod",
            "missing_fields": ["sso_start_url", "sso_region"]
        }
        error = SSOTemplateGenerationError(
            template_type="session_block",
            reason="字段验证失败",
            context=context
        )
        
        assert error.context["session_name"] == "prod"
        assert error.context["missing_fields"] == ["sso_start_url", "sso_region"]
        assert error.context["template_type"] == "session_block"


class TestExceptionInheritance:
    """测试异常继承关系"""
    
    def test_all_exceptions_inherit_from_base(self):
        """测试所有异常都继承自基类"""
        exceptions = [
            InvalidSSOConfigError("test", "field", "value", "format"),
            MissingSSOConfigError("item", "field"),
            InvalidURLError("url"),
            InvalidRegionError("region"),
            SSOConfigFileError("path", "read"),
            SSOTemplateGenerationError("type", "reason")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, SSOConfigError)
            assert isinstance(exception, Exception)
    
    def test_exception_context_and_suggestions_available(self):
        """测试所有异常都有上下文和建议属性"""
        exceptions = [
            InvalidSSOConfigError("test", "field", "value", "format"),
            MissingSSOConfigError("item", "field"),
            InvalidURLError("url"),
            InvalidRegionError("region"),
            SSOConfigFileError("path", "read"),
            SSOTemplateGenerationError("type", "reason")
        ]
        
        for exception in exceptions:
            assert hasattr(exception, 'context')
            assert hasattr(exception, 'suggestions')
            assert isinstance(exception.context, dict)
            assert isinstance(exception.suggestions, list)
            assert len(exception.suggestions) > 0  # 所有异常都应该有建议


if __name__ == "__main__":
    pytest.main([__file__])