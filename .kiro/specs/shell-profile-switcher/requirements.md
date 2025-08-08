# Requirements Document

## Introduction

这个功能为 kolja-aws 工具添加一个 shell 集成功能，允许用户通过 `kolja aws sp` 命令安装一个交互式的 AWS Profile 切换器到他们的 shell 配置文件中。安装后，用户可以通过简单的 `sp` 命令快速选择和切换 AWS profiles，提升日常 AWS 开发工作流的效率。

## Requirements

### Requirement 1

**User Story:** 作为一个 AWS 开发者，我希望在 `pip3 install kolja-aws` 时自动安装 shell 集成脚本到我的 shell 配置文件中，这样我就可以立即使用 `sp` 命令进行 profile 切换。

#### Acceptance Criteria

1. WHEN 用户执行 `pip3 install kolja-aws` THEN 系统 SHALL 在安装过程中自动检测当前使用的 shell 类型（bash, zsh, fish 等）
2. WHEN 系统检测到 shell 类型 THEN 系统 SHALL 确定对应的配置文件路径（~/.bashrc, ~/.zshrc, ~/.config/fish/config.fish 等）
3. WHEN 配置文件路径确定后 THEN 系统 SHALL 将 shell 函数代码添加到配置文件中
4. IF 配置文件中已存在相同的函数 THEN 系统 SHALL 更新现有函数而不是重复添加
5. WHEN 安装完成 THEN 系统 SHALL 提示用户重新加载 shell 或执行 source 命令

### Requirement 2

**User Story:** 作为一个 AWS 开发者，我希望通过简单的 `sp` 命令启动一个交互式的 profile 选择器，这样我就可以快速浏览和选择可用的 AWS profiles。

#### Acceptance Criteria

1. WHEN 用户在终端中执行 `sp` THEN 系统 SHALL 显示一个交互式的 profile 选择菜单
2. WHEN 显示选择菜单 THEN 系统 SHALL 列出所有可用的 AWS profiles
3. WHEN 显示 profiles THEN 系统 SHALL 使用箭头键导航和高亮当前选中的 profile
4. WHEN 显示 profiles THEN 系统 SHALL 在当前活动的 profile 旁边显示特殊标记（如 ❯ 符号）
5. IF 没有找到任何 profiles THEN 系统 SHALL 显示友好的错误消息
6. WHEN 用户按 Enter 键 THEN 系统 SHALL 选择当前高亮的 profile

### Requirement 3

**User Story:** 作为一个 AWS 开发者，我希望选择 profile 后能够自动设置 AWS_PROFILE 环境变量，这样我就不需要手动执行 export 命令。

#### Acceptance Criteria

1. WHEN 用户选择一个 profile THEN 系统 SHALL 自动执行 `export AWS_PROFILE=<selected_profile>`
2. WHEN 环境变量设置完成 THEN 系统 SHALL 显示确认消息，包含选中的 profile 名称
3. WHEN 设置环境变量 THEN 系统 SHALL 确保变量在当前 shell 会话中立即生效
4. IF profile 设置失败 THEN 系统 SHALL 显示错误消息并保持当前环境变量不变

### Requirement 4

**User Story:** 作为一个 AWS 开发者，我希望 shell 集成能够与现有的 kolja-aws 功能兼容，这样我就可以无缝地使用所有功能。

#### Acceptance Criteria

1. WHEN shell 脚本执行 THEN 系统 SHALL 使用与 kolja-aws 相同的方法来发现 AWS profiles
2. WHEN 读取 profiles THEN 系统 SHALL 支持标准的 AWS credentials 和 config 文件格式
3. WHEN 处理 profiles THEN 系统 SHALL 正确处理 SSO profiles 和传统的 access key profiles
4. IF kolja-aws 配置发生变化 THEN shell 脚本 SHALL 反映这些变化而无需重新安装

### Requirement 5

**User Story:** 作为一个系统管理员，我希望安装过程是安全和可逆的，这样我就可以放心地在团队中推广这个工具。

#### Acceptance Criteria

1. WHEN 安装 shell 脚本 THEN 系统 SHALL 在修改配置文件前创建备份
2. WHEN 创建备份 THEN 系统 SHALL 使用时间戳命名备份文件
3. WHEN 安装过程中出现错误 THEN 系统 SHALL 自动恢复原始配置文件
4. WHEN 用户请求卸载 THEN 系统 SHALL 提供移除 shell 集成的选项
5. IF 配置文件权限不足 THEN 系统 SHALL 显示清晰的错误消息和解决建议