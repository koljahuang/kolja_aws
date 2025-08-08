# Implementation Plan

- [x] 1. 创建核心数据模型和异常类
  - 实现 ShellConfig 和 ProfileInfo 数据类
  - 创建 ShellIntegrationError 异常层次结构
  - 编写数据模型的验证逻辑和单元测试
  - _Requirements: 1.1, 4.1_

- [x] 2. 实现 Shell 环境检测功能
  - 创建 ShellDetector 类，检测当前使用的 shell 类型
  - 实现配置文件路径解析逻辑，支持 bash, zsh, fish
  - 添加 shell 支持性检查和错误处理
  - 编写 ShellDetector 的单元测试
  - _Requirements: 1.1, 1.2_

- [x] 3. 实现 AWS Profile 加载器
  - 创建 ProfileLoader 类，重用现有的 AWS config 解析逻辑
  - 实现 load_profiles() 方法，从 ~/.aws/config 读取所有 profiles
  - 实现 get_current_profile() 方法，检测当前活动的 AWS_PROFILE
  - 添加 profile 验证和错误处理
  - 编写 ProfileLoader 的单元测试
  - _Requirements: 2.2, 4.1, 4.2_

- [x] 4. 实现配置文件备份管理器
  - 创建 BackupManager 类，处理配置文件的备份和恢复
  - 实现 create_backup() 方法，使用时间戳命名备份文件
  - 实现 restore_backup() 和 cleanup_old_backups() 方法
  - 添加文件权限检查和错误处理
  - 编写 BackupManager 的单元测试
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 5. 实现 Shell 脚本生成器
  - 创建 ScriptGenerator 类，生成特定 shell 的集成脚本
  - 实现 generate_bash_script() 方法，生成 Bash/Zsh 兼容脚本
  - 实现 generate_fish_script() 方法，生成 Fish shell 脚本
  - 添加脚本模板和特殊字符转义处理
  - 编写 ScriptGenerator 的单元测试，验证生成脚本的语法正确性
  - _Requirements: 1.3, 2.1_

- [x] 6. 实现交互式 Profile 切换器
  - 创建 ProfileSwitcher 类，处理交互式 profile 选择
  - 实现 show_interactive_menu() 方法，显示可选择的 profiles 列表
  - 添加箭头键导航和当前 profile 高亮显示功能
  - 实现 switch_profile() 方法，验证并返回选中的 profile
  - 添加键盘中断处理和错误恢复
  - 编写 ProfileSwitcher 的单元测试
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 7. 实现 Shell 集成安装器
  - 创建 ShellInstaller 类，协调整个安装过程
  - 实现 install() 方法，检测 shell、生成脚本、修改配置文件
  - 实现 uninstall() 和 is_installed() 方法
  - 添加安装过程的事务性处理，确保失败时能够回滚
  - 集成所有组件并处理安装过程中的错误
  - 编写 ShellInstaller 的单元测试
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.3, 5.4_

- [x] 8. 实现 post-install hook 集成
  - 创建 post_install.py 脚本，在包安装后自动运行
  - 在 pyproject.toml 中配置 post-install hook
  - 实现安装过程的用户友好输出和进度指示
  - 添加安装失败时的优雅降级处理
  - 提供手动安装选项作为备选方案
  - _Requirements: 1.1, 1.5_

- [x] 9. 创建 shell_integration 模块
  - 创建 kolja_aws/shell_integration.py 文件
  - 导出 ProfileSwitcher 类供 shell 脚本调用
  - 实现模块级别的错误处理和日志记录
  - 确保模块可以独立运行，不依赖 CLI 框架
  - 添加模块的集成测试
  - _Requirements: 2.1, 3.1, 3.2, 3.3_

- [x] 10. 实现环境变量设置功能
  - 在 ProfileSwitcher 中添加环境变量设置逻辑
  - 确保 AWS_PROFILE 在当前 shell 会话中立即生效
  - 添加设置成功的确认消息显示
  - 实现设置失败时的错误处理和回滚
  - 编写环境变量设置的单元测试
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 11. 添加错误处理和用户体验优化
  - 实现友好的错误消息显示，包含解决建议
  - 添加 profile 不存在时的错误处理
  - 实现权限不足时的清晰错误提示
  - 添加加载指示器和用户反馈
  - 优化交互式菜单的响应速度
  - _Requirements: 2.5, 5.5_

- [x] 12. 编写集成测试套件
  - 创建端到端安装测试，覆盖不同 shell 环境
  - 实现交互式功能的自动化测试
  - 添加备份和恢复机制的测试
  - 创建卸载功能的验证测试
  - 实现错误场景的集成测试
  - _Requirements: 所有需求的集成验证_

- [x] 13. 更新项目文档和配置
  - 更新 README.md，添加 shell 集成功能的使用说明
  - 在 pyproject.toml 中添加新的依赖项（如果需要）
  - 创建故障排除文档和常见问题解答
  - 添加功能演示和使用示例
  - 更新版本号和变更日志
  - _Requirements: 所有需求的文档支持_