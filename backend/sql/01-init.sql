-- ============================================================================
-- Agent Application - Database Schema (MySQL)
-- ============================================================================
-- Description: 数据库表结构定义
-- Version: 1.0.0
-- Date: 2026-01-28
-- ============================================================================

-- ============================================================================
-- 创建数据库 (如果不存在)
-- ============================================================================
CREATE DATABASE IF NOT EXISTS `agent_app`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `agent_app`;

-- ============================================================================
-- 1. 用户表 (users)
-- ============================================================================
-- 说明: 存储用户基本信息
-- ============================================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名，唯一',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希值 (bcrypt)',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱地址',
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_email` (`email`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================================
-- 2. MCP服务器配置表 (mcp_servers)
-- ============================================================================
-- 说明: 存储用户的 MCP (Model Context Protocol) 服务器配置
-- ============================================================================
CREATE TABLE IF NOT EXISTS `mcp_servers` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'MCP服务器ID，主键',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
    `name` VARCHAR(100) NOT NULL COMMENT 'MCP服务器名称',
    `description` TEXT DEFAULT NULL COMMENT 'MCP服务器描述',
    `server_type` ENUM('stdio', 'sse') NOT NULL COMMENT '服务器连接类型',
    `connection_params` JSON NOT NULL COMMENT '连接参数 (JSON格式)',
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active' COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`),
    CONSTRAINT `fk_mcp_servers_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MCP服务器配置表';

-- connection_params JSON 示例:
-- stdio 类型:
-- {
--     "command": ["python", "path/to/server.py"],
--     "env": {
--         "API_KEY": "xxx"
--     }
-- }
--
-- sse 类型:
-- {
--     "url": "http://localhost:8080/sse",
--     "headers": {
--         "Authorization": "Bearer xxx"
--     }
-- }

-- ============================================================================
-- 3. LLM配置表 (llm_configs)
-- ============================================================================
-- 说明: 存储用户的 LLM (大语言模型) 配置
-- ============================================================================
CREATE TABLE IF NOT EXISTS `llm_configs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'LLM配置ID，主键',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
    `provider` ENUM('openai', 'anthropic', 'custom') NOT NULL COMMENT 'LLM提供商',
    `model_name` VARCHAR(100) NOT NULL COMMENT '模型名称',
    `api_key` VARCHAR(255) DEFAULT NULL COMMENT 'API密钥 (加密存储)',
    `base_url` VARCHAR(500) DEFAULT NULL COMMENT '自定义API端点 (本地部署或自定义)',
    `max_tokens` INT NOT NULL DEFAULT 4096 COMMENT '最大生成长度',
    `temperature` DECIMAL(3,2) NOT NULL DEFAULT 0.70 COMMENT '温度参数 (0.00 - 2.00)',
    `top_p` DECIMAL(3,2) DEFAULT 1.00 COMMENT 'Top P 采样',
    `is_default` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为默认配置',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_provider` (`provider`),
    KEY `idx_is_default` (`is_default`),
    CONSTRAINT `fk_llm_configs_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='LLM配置表';

-- LLM配置示例:
--
-- OpenAI:
-- {
--     "provider": "openai",
--     "model_name": "gpt-4-turbo",
--     "base_url": "https://api.openai.com/v1",
--     "api_key": "sk-xxx",
--     "max_tokens": 4096,
--     "temperature": 0.7
-- }
--
-- 本地部署 QwQ-32B (vLLM):
-- {
--     "provider": "custom",
--     "model_name": "Qwen/QwQ-32B-Preview",
--     "base_url": "http://localhost:8000/v1",
--     "api_key": "dummy",
--     "max_tokens": 8192,
--     "temperature": 0.7
-- }
--
-- 本地部署 QwQ-32B (Ollama):
-- {
--     "provider": "custom",
--     "model_name": "qwq:32b",
--     "base_url": "http://localhost:11434/v1",
--     "api_key": "ollama",
--     "max_tokens": 8192
-- }

-- ============================================================================
-- 4. 对话表 (conversations)
-- ============================================================================
-- 说明: 存储用户的对话会话
-- ============================================================================
CREATE TABLE IF NOT EXISTS `conversations` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '对话ID，主键',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
    `llm_config_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '使用的LLM配置ID',
    `title` VARCHAR(200) DEFAULT NULL COMMENT '对话标题',
    `status` ENUM('active', 'archived', 'deleted') NOT NULL DEFAULT 'active' COMMENT '对话状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_llm_config_id` (`llm_config_id`),
    KEY `idx_status` (`status`),
    KEY `idx_updated_at` (`updated_at`),
    CONSTRAINT `fk_conversations_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_conversations_llm_config_id`
        FOREIGN KEY (`llm_config_id`)
        REFERENCES `llm_configs` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话表';

-- ============================================================================
-- 5. 消息表 (messages)
-- ============================================================================
-- 说明: 存储对话中的每条消息
-- ============================================================================
CREATE TABLE IF NOT EXISTS `messages` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息ID，主键',
    `conversation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属对话ID',
    `role` ENUM('user', 'assistant', 'system', 'tool') NOT NULL COMMENT '消息角色',
    `content` LONGTEXT NOT NULL COMMENT '消息内容',
    `tool_calls` JSON DEFAULT NULL COMMENT '工具调用记录 (JSON格式)',
    `tool_call_id` VARCHAR(100) DEFAULT NULL COMMENT '工具调用ID (tool消息用)',
    `tokens_used` INT DEFAULT NULL COMMENT '使用的token数量',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_conversation_id` (`conversation_id`),
    KEY `idx_role` (`role`),
    KEY `idx_created_at` (`created_at`),
    CONSTRAINT `fk_messages_conversation_id`
        FOREIGN KEY (`conversation_id`)
        REFERENCES `conversations` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- tool_calls JSON 示例:
-- [
--     {
--         "id": "call_abc123",
--         "type": "function",
--         "function": {
--             "name": "web_search",
--             "arguments": "{\"query\": \"人工智能 最新新闻\"}"
--         }
--     }
-- ]

-- ============================================================================
-- 6. 内置工具配置表 (builtin_tools)
-- ============================================================================
-- 说明: 存储用户启用的内置工具配置
-- ============================================================================
CREATE TABLE IF NOT EXISTS `builtin_tools` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '工具配置ID，主键',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
    `tool_name` VARCHAR(50) NOT NULL COMMENT '工具名称',
    `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    `config_params` JSON DEFAULT NULL COMMENT '工具配置参数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_tool` (`user_id`, `tool_name`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_is_enabled` (`is_enabled`),
    CONSTRAINT `fk_builtin_tools_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='内置工具配置表';

-- 内置工具列表:
-- - file_save: 文件保存
-- - file_read: 文件读取
-- - file_search: 文件搜索
-- - web_search: 网络搜索

-- ============================================================================
-- 7. 工具执行历史表 (tool_executions)
-- ============================================================================
-- 说明: 记录每次工具执行的详细历史 (用于审计和调试)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `tool_executions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '执行记录ID，主键',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
    `message_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '关联的消息ID',
    `tool_name` VARCHAR(100) NOT NULL COMMENT '工具名称',
    `tool_type` ENUM('builtin', 'mcp', 'custom') NOT NULL COMMENT '工具类型',
    `mcp_server_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'MCP服务器ID (mcp类型)',
    `tool_params` JSON NOT NULL COMMENT '工具参数',
    `execution_time_ms` INT DEFAULT NULL COMMENT '执行时间(毫秒)',
    `status` ENUM('success', 'failed', 'error') NOT NULL COMMENT '执行状态',
    `result` LONGTEXT DEFAULT NULL COMMENT '执行结果',
    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_message_id` (`message_id`),
    KEY `idx_tool_name` (`tool_name`),
    KEY `idx_tool_type` (`tool_type`),
    KEY `idx_mcp_server_id` (`mcp_server_id`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`),
    CONSTRAINT `fk_tool_executions_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_tool_executions_message_id`
        FOREIGN KEY (`message_id`)
        REFERENCES `messages` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT `fk_tool_executions_mcp_server_id`
        FOREIGN KEY (`mcp_server_id`)
        REFERENCES `mcp_servers` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具执行历史表';

-- ============================================================================
-- 8. 系统设置表 (system_settings)
-- ============================================================================
-- 说明: 存储系统级别设置 (每个用户或全局)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `system_settings` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '设置ID，主键',
    `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID (NULL表示全局设置)',
    `setting_key` VARCHAR(100) NOT NULL COMMENT '设置键',
    `setting_value` TEXT NOT NULL COMMENT '设置值',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '设置描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_key` (`user_id`, `setting_key`),
    KEY `idx_setting_key` (`setting_key`),
    CONSTRAINT `fk_system_settings_user_id`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统设置表';

-- ============================================================================
-- 插入默认内置工具配置 (所有用户默认启用)
-- ============================================================================
-- 注意: 实际使用时需要为每个用户创建，这里只是示例

-- INSERT INTO `builtin_tools` (`user_id`, `tool_name`, `is_enabled`)
-- VALUES (1, 'file_save', TRUE),
--        (1, 'file_read', TRUE),
--        (1, 'file_search', TRUE),
--        (1, 'web_search', TRUE);

-- ============================================================================
-- 创建视图 (可选，便于查询)
-- ============================================================================

-- 视图: 用户会话统计
CREATE OR REPLACE VIEW `v_user_conversation_stats` AS
SELECT
    u.id AS user_id,
    u.username,
    COUNT(DISTINCT c.id) AS total_conversations,
    COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) AS active_conversations,
    COUNT(m.id) AS total_messages,
    MIN(c.created_at) AS first_conversation,
    MAX(c.created_at) AS last_conversation
FROM `users` u
LEFT JOIN `conversations` c ON u.id = c.user_id
LEFT JOIN `messages` m ON c.id = m.conversation_id
GROUP BY u.id, u.username;

-- 视图: 工具执行统计
CREATE OR REPLACE VIEW `v_tool_execution_stats` AS
SELECT
    u.id AS user_id,
    u.username,
    te.tool_name,
    te.tool_type,
    COUNT(te.id) AS total_executions,
    COUNT(CASE WHEN te.status = 'success' THEN 1 END) AS success_count,
    COUNT(CASE WHEN te.status = 'failed' THEN 1 END) AS failed_count,
    COUNT(CASE WHEN te.status = 'error' THEN 1 END) AS error_count,
    AVG(te.execution_time_ms) AS avg_execution_time_ms,
    MIN(te.execution_time_ms) AS min_execution_time_ms,
    MAX(te.execution_time_ms) AS max_execution_time_ms
FROM `users` u
JOIN `tool_executions` te ON u.id = te.user_id
GROUP BY u.id, u.username, te.tool_name, te.tool_type;

-- ============================================================================
-- 索引优化建议 (根据实际数据量和查询模式添加)
-- ============================================================================

-- 如果消息表数据量很大，可以添加复合索引:
-- ALTER TABLE `messages` ADD INDEX `idx_conversation_created` (`conversation_id`, `created_at`);
-- ALTER TABLE `messages` ADD INDEX `idx_user_role` (`conversation_id`, `role`);

-- 如果工具执行历史表数据量很大，可以添加复合索引:
-- ALTER TABLE `tool_executions` ADD INDEX `idx_user_tool_created` (`user_id`, `tool_name`, `created_at`);
-- ALTER TABLE `tool_executions` ADD INDEX `idx_user_status_created` (`user_id`, `status`, `created_at`);

-- ============================================================================
-- 完成提示
-- ============================================================================
-- 数据库结构初始化完成！
--
-- 使用说明:
-- 1. 执行此脚本创建数据库和表结构
-- 2. 根据需要修改数据库名称 'agent_app'
-- 3. 根据实际需求调整表结构和索引
-- 4. 确保应用程序连接参数与数据库配置一致
--
-- 注意事项:
-- - 所有表使用 utf8mb4 字符集，支持 emoji 等特殊字符
-- - 时间字段使用 DATETIME 类型
-- - JSON 字段用于存储灵活配置
-- - 添加了外键约束保证数据一致性
-- - 添加了索引优化查询性能
-- ============================================================================