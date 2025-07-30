# 设计文档

## 概述

本设计旨在重构当前硬编码在`sso_session.template`文件中的SSO配置管理方式，将配置信息迁移到`settings.toml`文件中，并实现动态模板生成功能。这将提高系统的可配置性和可维护性，使用户能够通过修改配置文件来管理不同的SSO环境。

## 架构

### 当前架构问题
- SSO配置硬编码在模板文件中
- 需要手动维护多个环境的配置
- 配置变更需要修改代码文件

### 新架构设计
```
settings.toml (配置源) 
    ↓
SSO配置管理器 (读取和验证)
    ↓  
模板生成器 (动态生成)
    ↓
AWS配置文件 (最终输出)
```

## 组件和接口

### 1. 配置结构设计

在`settings.toml`中新增SSO配置块：

```toml
[sso_sessions.kolja-cn]
sso_start_url = "https://start.home.awsapps.cn/directory/xxx"
sso_region = "cn-northwest-1"
sso_registration_scopes = "sso:account:access"

[sso_sessions.kolja]
sso_start_url = "https://xxx/start"
sso_region = "ap-southeast-2"
sso_registration_scopes = "sso:account:access"
```

### 2. SSO配置管理器 (`sso_config_manager.py`)

**核心类：`SSOConfigManager`**

```python
class SSOConfigManager:
    def __init__(self, settings_instance)
    def get_sso_sessions() -> Dict[str, Dict[str, str]]
    def validate_sso_config(session_name: str, config: Dict) -> bool
    def get_session_config(session_name: str) -> Dict[str, str]
```

**职责：**
- 从settings.toml读取SSO配置
- 验证配置的完整性和正确性
- 提供配置访问接口

### 3. 模板生成器 (`sso_template_generator.py`)

**核心类：`SSOTemplateGenerator`**

```python
class SSOTemplateGenerator:
    def __init__(self, config_manager: SSOConfigManager)
    def generate_session_block(session_name: str, config: Dict) -> str
    def generate_full_template() -> str
    def write_template_to_file(file_path: str) -> None
```

**职责：**
- 基于配置生成SSO会话模板内容
- 维护模板格式的一致性
- 支持写入到文件或返回字符串

### 4. 配置验证器 (`sso_validator.py`)

**核心函数：**
```python
def validate_url(url: str) -> bool
def validate_aws_region(region: str) -> bool
def validate_sso_session_config(config: Dict) -> Tuple[bool, List[str]]
```

**职责：**
- URL格式验证
- AWS区域格式验证
- 配置完整性检查

## 数据模型

### SSOSessionConfig
```python
@dataclass
class SSOSessionConfig:
    session_name: str
    sso_start_url: str
    sso_region: str
    sso_registration_scopes: str = "sso:account:access"
    
    def validate(self) -> Tuple[bool, List[str]]
    def to_template_block(self) -> str
```

### SSOConfigCollection
```python
@dataclass
class SSOConfigCollection:
    sessions: Dict[str, SSOSessionConfig]
    
    def add_session(self, session: SSOSessionConfig) -> None
    def get_session(self, name: str) -> SSOSessionConfig
    def generate_template(self) -> str
```

## 错误处理

### 异常类型定义
```python
class SSOConfigError(Exception):
    """SSO配置相关错误的基类"""
    pass

class InvalidSSOConfigError(SSOConfigError):
    """无效的SSO配置错误"""
    pass

class MissingSSOConfigError(SSOConfigError):
    """缺失的SSO配置错误"""
    pass

class InvalidURLError(SSOConfigError):
    """无效的URL格式错误"""
    pass

class InvalidRegionError(SSOConfigError):
    """无效的AWS区域错误"""
    pass
```

### 错误处理策略
1. **配置读取错误**：提供清晰的错误信息和修复建议
2. **验证错误**：详细说明哪个字段有问题以及期望的格式
3. **文件操作错误**：处理文件权限和路径问题
4. **向后兼容**：如果配置不存在，回退到原有的模板文件方式

## 集成方案

### 1. 修改现有代码
- 更新`kolja_login.py`中的`set`命令，使用新的配置管理器
- 修改`utils.py`中的`get_section_metadata_from_template`函数，支持动态生成的模板
- 保持现有CLI接口不变，确保向后兼容

### 2. 配置迁移策略
- 提供迁移工具，将现有模板文件中的配置转换为settings.toml格式
- 支持混合模式：优先使用settings.toml，如果不存在则回退到模板文件
- 添加配置验证命令，帮助用户检查配置正确性

### 3. 渐进式部署
1. 第一阶段：实现配置读取和验证功能
2. 第二阶段：实现模板生成功能
3. 第三阶段：集成到现有CLI命令中
4. 第四阶段：添加迁移工具和向后兼容支持

## 测试策略

### 单元测试
- **配置管理器测试**：测试配置读取、验证和访问功能
- **模板生成器测试**：测试模板生成的正确性和格式
- **验证器测试**：测试各种验证规则和边界情况
- **数据模型测试**：测试数据类的行为和验证逻辑

### 集成测试
- **端到端配置流程测试**：从settings.toml读取到生成最终模板
- **CLI集成测试**：测试修改后的CLI命令功能
- **文件操作测试**：测试模板文件的读写操作
- **错误场景测试**：测试各种错误情况的处理

### 兼容性测试
- **向后兼容性测试**：确保现有功能不受影响
- **配置格式测试**：测试不同配置格式的处理
- **环境兼容性测试**：测试在不同操作系统和Python版本下的行为

## 性能考虑

### 配置缓存
- 实现配置缓存机制，避免重复读取settings.toml
- 监控配置文件变化，自动刷新缓存

### 模板生成优化
- 延迟生成：只在需要时生成模板内容
- 模板缓存：缓存生成的模板内容，直到配置变化

### 内存使用
- 使用生成器模式处理大量配置
- 及时释放不需要的配置对象