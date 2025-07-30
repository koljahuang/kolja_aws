"""
SSO配置相关的自定义异常类

该模块定义了SSO配置管理过程中可能出现的各种异常类型，
每个异常都包含清晰的错误信息和修复建议。
"""

from typing import List, Optional, Dict, Any


class SSOConfigError(Exception):
    """SSO配置相关错误的基类
    
    所有SSO配置相关的异常都应该继承自这个基类。
    提供了基本的错误信息和上下文管理功能。
    """
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, 
                 suggestions: Optional[List[str]] = None):
        """初始化SSO配置错误
        
        Args:
            message: 错误描述信息
            context: 错误上下文信息，包含相关的配置数据
            suggestions: 修复建议列表
        """
        super().__init__(message)
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        """返回格式化的错误信息"""
        error_msg = super().__str__()
        
        if self.context:
            error_msg += f"\n上下文信息: {self.context}"
        
        if self.suggestions:
            error_msg += "\n修复建议:"
            for i, suggestion in enumerate(self.suggestions, 1):
                error_msg += f"\n  {i}. {suggestion}"
        
        return error_msg


class InvalidSSOConfigError(SSOConfigError):
    """无效的SSO配置错误
    
    当SSO配置格式不正确或包含无效值时抛出此异常。
    """
    
    def __init__(self, session_name: str, field_name: str, field_value: Any, 
                 expected_format: str, context: Optional[Dict[str, Any]] = None):
        """初始化无效配置错误
        
        Args:
            session_name: SSO会话名称
            field_name: 无效的字段名
            field_value: 无效的字段值
            expected_format: 期望的格式描述
            context: 额外的上下文信息
        """
        message = (f"SSO会话 '{session_name}' 中的字段 '{field_name}' "
                  f"值 '{field_value}' 无效")
        
        error_context = {
            "session_name": session_name,
            "field_name": field_name,
            "field_value": field_value,
            "expected_format": expected_format
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            f"确保 '{field_name}' 字段的格式符合: {expected_format}",
            f"检查 settings.toml 中 [sso_sessions.{session_name}] 部分的配置",
            "参考文档中的配置示例进行修正"
        ]
        
        super().__init__(message, error_context, suggestions)


class MissingSSOConfigError(SSOConfigError):
    """缺失的SSO配置错误
    
    当必需的SSO配置字段或会话不存在时抛出此异常。
    """
    
    def __init__(self, missing_item: str, item_type: str = "field", 
                 session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """初始化缺失配置错误
        
        Args:
            missing_item: 缺失的项目名称
            item_type: 缺失项目的类型 ("field", "session", "section")
            session_name: 相关的SSO会话名称（如果适用）
            context: 额外的上下文信息
        """
        if item_type == "field" and session_name:
            message = f"SSO会话 '{session_name}' 缺少必需的字段 '{missing_item}'"
        elif item_type == "session":
            message = f"未找到SSO会话配置 '{missing_item}'"
        elif item_type == "section":
            message = f"settings.toml 中缺少 '{missing_item}' 配置部分"
        else:
            message = f"缺少必需的SSO配置项 '{missing_item}'"
        
        error_context = {
            "missing_item": missing_item,
            "item_type": item_type,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = []
        if item_type == "field":
            suggestions.extend([
                f"在 settings.toml 的 [sso_sessions.{session_name}] 部分添加 '{missing_item}' 字段",
                "确保所有必需字段都已配置: sso_start_url, sso_region"
            ])
        elif item_type == "session":
            suggestions.extend([
                f"在 settings.toml 中添加 [sso_sessions.{missing_item}] 配置部分",
                "检查会话名称是否拼写正确"
            ])
        elif item_type == "section":
            suggestions.extend([
                "在 settings.toml 中添加 [sso_sessions] 配置部分",
                "确保配置文件格式正确"
            ])
        
        suggestions.append("参考文档中的完整配置示例")
        
        super().__init__(message, error_context, suggestions)


class InvalidURLError(SSOConfigError):
    """无效的URL格式错误
    
    当SSO起始URL格式不正确时抛出此异常。
    """
    
    def __init__(self, url: str, session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """初始化无效URL错误
        
        Args:
            url: 无效的URL
            session_name: 相关的SSO会话名称
            context: 额外的上下文信息
        """
        if session_name:
            message = f"SSO会话 '{session_name}' 的起始URL '{url}' 格式无效"
        else:
            message = f"URL '{url}' 格式无效"
        
        error_context = {
            "invalid_url": url,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "确保URL以 'https://' 开头",
            "检查URL是否包含有效的域名",
            "确保URL格式符合标准格式，例如: https://start.home.awsapps.cn/directory/xxx",
            "验证URL是否可以在浏览器中正常访问"
        ]
        
        super().__init__(message, error_context, suggestions)


class InvalidRegionError(SSOConfigError):
    """无效的AWS区域错误
    
    当AWS区域格式不正确时抛出此异常。
    """
    
    def __init__(self, region: str, session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """初始化无效区域错误
        
        Args:
            region: 无效的AWS区域
            session_name: 相关的SSO会话名称
            context: 额外的上下文信息
        """
        if session_name:
            message = f"SSO会话 '{session_name}' 的AWS区域 '{region}' 格式无效"
        else:
            message = f"AWS区域 '{region}' 格式无效"
        
        error_context = {
            "invalid_region": region,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "使用有效的AWS区域代码，例如: us-east-1, ap-southeast-2, cn-northwest-1",
            "检查区域代码的拼写是否正确",
            "确保区域代码符合AWS标准格式: <region>-<availability-zone>-<number>",
            "参考AWS官方文档获取完整的区域列表"
        ]
        
        super().__init__(message, error_context, suggestions)


class SSOConfigFileError(SSOConfigError):
    """SSO配置文件相关错误
    
    当配置文件读取、解析或写入出现问题时抛出此异常。
    """
    
    def __init__(self, file_path: str, operation: str, original_error: Optional[Exception] = None,
                 context: Optional[Dict[str, Any]] = None):
        """初始化配置文件错误
        
        Args:
            file_path: 相关的文件路径
            operation: 执行的操作 ("read", "write", "parse")
            original_error: 原始异常对象
            context: 额外的上下文信息
        """
        message = f"配置文件 '{file_path}' {operation}操作失败"
        if original_error:
            message += f": {str(original_error)}"
        
        error_context = {
            "file_path": file_path,
            "operation": operation,
            "original_error": str(original_error) if original_error else None
        }
        if context:
            error_context.update(context)
        
        suggestions = []
        if operation == "read":
            suggestions.extend([
                "检查文件是否存在",
                "确保有足够的文件读取权限",
                "验证文件路径是否正确"
            ])
        elif operation == "write":
            suggestions.extend([
                "检查目录是否存在",
                "确保有足够的文件写入权限",
                "检查磁盘空间是否充足"
            ])
        elif operation == "parse":
            suggestions.extend([
                "检查TOML文件格式是否正确",
                "确保配置文件语法符合TOML标准",
                "使用TOML验证工具检查文件格式"
            ])
        
        suggestions.append("查看详细错误信息以获取更多诊断信息")
        
        super().__init__(message, error_context, suggestions)


class SSOTemplateGenerationError(SSOConfigError):
    """SSO模板生成错误
    
    当模板生成过程中出现问题时抛出此异常。
    """
    
    def __init__(self, template_type: str, reason: str, 
                 context: Optional[Dict[str, Any]] = None):
        """初始化模板生成错误
        
        Args:
            template_type: 模板类型 ("session_block", "full_template")
            reason: 失败原因
            context: 额外的上下文信息
        """
        message = f"{template_type}模板生成失败: {reason}"
        
        error_context = {
            "template_type": template_type,
            "failure_reason": reason
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "检查SSO配置是否完整和有效",
            "确保所有必需的配置字段都已提供",
            "验证配置数据的格式是否正确",
            "查看详细错误信息以确定具体问题"
        ]
        
        super().__init__(message, error_context, suggestions)