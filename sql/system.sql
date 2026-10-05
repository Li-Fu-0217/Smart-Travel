-- =====================================================================
-- 智慧旅游智能助手系统 · 全量数据库脚本（唯一权威 schema）
-- 幂等：可反复执行（先 DROP 再 CREATE，再插种子）
-- 字符集 utf8mb4 / utf8mb4_unicode_ci，库名 travel_assistant
-- 说明：唯一约束与索引只在此脚本中声明，SQLModel 模型不重复声明；
--       严禁用 SQLModel.metadata.create_all() 建表（会丢唯一约束与索引）。
-- =====================================================================

CREATE DATABASE IF NOT EXISTS travel_assistant DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE travel_assistant;

-- =====================================================================
-- 系统权限域（系统表 5 张）
-- =====================================================================

DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL COMMENT '用户名',
  password VARCHAR(100) NOT NULL COMMENT 'bcrypt 哈希',
  role VARCHAR(20) NOT NULL DEFAULT 'USER' COMMENT 'ADMIN / USER',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 启用 / 0 禁用',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS sys_role;
CREATE TABLE sys_role (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL COMMENT '角色编码',
  name VARCHAR(50) NOT NULL COMMENT '角色名称',
  sort_order INT NOT NULL DEFAULT 0,
  status TINYINT NOT NULL DEFAULT 1,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS sys_menu;
CREATE TABLE sys_menu (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  parent_id BIGINT NOT NULL DEFAULT 0 COMMENT '本项目全部为 0（扁平一级菜单）',
  name VARCHAR(50) NOT NULL,
  path VARCHAR(100) NOT NULL,
  icon VARCHAR(50) DEFAULT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  roles VARCHAR(100) NOT NULL DEFAULT 'ADMIN' COMMENT '逗号分隔，如 ADMIN',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS sys_login_log;
CREATE TABLE sys_login_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) DEFAULT NULL,
  ip VARCHAR(64) DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 成功 / 0 失败',
  message VARCHAR(255) DEFAULT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS sys_operation_log;
CREATE TABLE sys_operation_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) DEFAULT NULL,
  module VARCHAR(50) DEFAULT NULL,
  action VARCHAR(50) DEFAULT NULL,
  method VARCHAR(10) DEFAULT NULL,
  url VARCHAR(255) DEFAULT NULL,
  ip VARCHAR(64) DEFAULT NULL,
  cost_ms INT DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 1,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 旅行者档案域
-- =====================================================================

DROP TABLE IF EXISTS traveler_profile;
CREATE TABLE traveler_profile (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10) DEFAULT NULL,
  birth_date DATE DEFAULT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  id_card_no VARCHAR(30) DEFAULT NULL,
  dietary_restrictions VARCHAR(255) DEFAULT NULL COMMENT '忌口',
  allergies VARCHAR(255) DEFAULT NULL COMMENT '过敏',
  mobility_notes VARCHAR(255) DEFAULT NULL COMMENT '行动不便说明',
  preferences VARCHAR(500) DEFAULT NULL COMMENT '出行偏好文本',
  preference_tags VARCHAR(255) DEFAULT NULL COMMENT '偏好标签，逗号分隔（固定 9 个词表）',
  preference_summary VARCHAR(500) DEFAULT NULL COMMENT '偏好摘要（由旅游记录提炼）',
  preference_updated_at DATETIME DEFAULT NULL,
  emergency_contact VARCHAR(50) DEFAULT NULL,
  emergency_phone VARCHAR(20) DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 正常 / 0 停用',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS family_member;
CREATE TABLE family_member (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  traveler_id BIGINT NOT NULL,
  relation VARCHAR(20) DEFAULT NULL COMMENT '儿子/女儿/配偶/本人 等',
  is_primary TINYINT NOT NULL DEFAULT 0 COMMENT '1 主要联系人 / 0 非主要',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_family_traveler (traveler_id),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 行程规划域
-- =====================================================================

DROP TABLE IF EXISTS trip_plan;
CREATE TABLE trip_plan (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  traveler_id BIGINT NOT NULL,
  title VARCHAR(100) DEFAULT NULL,
  destination VARCHAR(100) DEFAULT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  budget DECIMAL(12,2) DEFAULT NULL,
  remark VARCHAR(500) DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 进行中 / 0 已归档',
  source_template_id BIGINT DEFAULT NULL COMMENT '来源模板 id（从模板复制时回填）',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_traveler (traveler_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS trip_todo;
CREATE TABLE trip_todo (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  trip_id BIGINT NOT NULL,
  traveler_id BIGINT NOT NULL,
  item_name VARCHAR(200) NOT NULL,
  due_time DATETIME DEFAULT NULL,
  category VARCHAR(20) NOT NULL DEFAULT 'other' COMMENT 'visa/insurance/vaccine/luggage/transfer/other',
  status TINYINT NOT NULL DEFAULT 2 COMMENT '1 已完成 / 2 待办；逾期由 status=2 AND due_time<NOW() 动态判定，不落库',
  done_time DATETIME DEFAULT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_trip (trip_id),
  KEY idx_traveler (traveler_id),
  KEY idx_status_due (status, due_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 行程模板域
-- =====================================================================

DROP TABLE IF EXISTS trip_template;
CREATE TABLE trip_template (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  destination VARCHAR(100) DEFAULT NULL,
  day_count INT NOT NULL DEFAULT 1,
  description VARCHAR(500) DEFAULT NULL,
  author_user_id BIGINT DEFAULT NULL,
  author_name VARCHAR(50) DEFAULT NULL,
  cover VARCHAR(255) DEFAULT NULL,
  use_count INT NOT NULL DEFAULT 0 COMMENT '被使用次数',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 已发布 / 0 下架',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS trip_template_item;
CREATE TABLE trip_template_item (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  template_id BIGINT NOT NULL,
  day_index INT NOT NULL DEFAULT 1 COMMENT '第几天',
  time_slot VARCHAR(20) DEFAULT NULL COMMENT '09:00/14:00/19:00/全天',
  item_name VARCHAR(200) NOT NULL,
  category VARCHAR(20) NOT NULL DEFAULT 'other' COMMENT '复用 trip_todo.category 词表',
  remark VARCHAR(500) DEFAULT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  KEY idx_template (template_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 预约域
-- =====================================================================

DROP TABLE IF EXISTS booking_catalog;
CREATE TABLE booking_catalog (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  item_type VARCHAR(20) NOT NULL COMMENT 'guide/homestay/experience/ticket',
  description VARCHAR(500) DEFAULT NULL,
  duration_minutes INT DEFAULT NULL,
  price DECIMAL(12,2) DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 上架 / 0 下架',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS booking_order;
CREATE TABLE booking_order (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  traveler_id BIGINT NOT NULL,
  catalog_id BIGINT NOT NULL,
  booking_time DATETIME DEFAULT NULL,
  guest_count INT NOT NULL DEFAULT 1,
  status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'pending/confirmed/cancelled/done',
  source VARCHAR(20) NOT NULL DEFAULT 'manual' COMMENT 'manual/agent',
  slot_lock VARCHAR(50) DEFAULT NULL COMMENT '目录ID:yyyyMMddHHmm，唯一约束防超卖；取消/完成置 NULL 释放',
  version INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  remark VARCHAR(500) DEFAULT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_booking_slot_lock (slot_lock),
  KEY idx_traveler (traveler_id),
  KEY idx_catalog (catalog_id),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 拼团活动域
-- =====================================================================

DROP TABLE IF EXISTS group_tour;
CREATE TABLE group_tour (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  content VARCHAR(2000) DEFAULT NULL,
  destination VARCHAR(100) DEFAULT NULL,
  start_time DATETIME DEFAULT NULL,
  end_time DATETIME DEFAULT NULL,
  capacity INT NOT NULL DEFAULT 0,
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 报名中 / 0 结束',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS group_tour_signup;
CREATE TABLE group_tour_signup (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  tour_id BIGINT NOT NULL,
  traveler_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'registered' COMMENT 'registered/cancelled',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_tour_traveler (tour_id, traveler_id),
  KEY idx_tour (tour_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 旅途求助域
-- =====================================================================

DROP TABLE IF EXISTS travel_alert;
CREATE TABLE travel_alert (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  traveler_id BIGINT NOT NULL,
  location VARCHAR(255) DEFAULT NULL,
  message VARCHAR(500) DEFAULT NULL,
  alert_type VARCHAR(20) NOT NULL DEFAULT 'other' COMMENT 'lost/illness/document/accident/other',
  status VARCHAR(20) NOT NULL DEFAULT 'open' COMMENT 'open/handling/closed',
  notify_family TINYINT NOT NULL DEFAULT 0,
  notify_staff TINYINT NOT NULL DEFAULT 0,
  source VARCHAR(20) NOT NULL DEFAULT 'manual' COMMENT 'manual/agent/system',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_traveler (traveler_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 旅游记录域
-- =====================================================================

DROP TABLE IF EXISTS travel_record;
CREATE TABLE travel_record (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  traveler_id BIGINT NOT NULL,
  trip_id BIGINT DEFAULT NULL,
  destination VARCHAR(100) DEFAULT NULL,
  visited_date DATE DEFAULT NULL,
  rating TINYINT DEFAULT NULL COMMENT '1-5',
  content VARCHAR(1000) DEFAULT NULL,
  photos VARCHAR(1000) DEFAULT NULL COMMENT '逗号分隔路径',
  visibility TINYINT NOT NULL DEFAULT 0 COMMENT '1 公开 / 0 仅自己可见',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_traveler (traveler_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 攻略知识库域（RAG）
-- =====================================================================

DROP TABLE IF EXISTS guide_document;
CREATE TABLE guide_document (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  doc_type VARCHAR(20) NOT NULL COMMENT 'visa/document/destination/tips',
  destination VARCHAR(100) DEFAULT NULL,
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0 待向量化 / 1 已就绪',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS guide_chunk;
CREATE TABLE guide_chunk (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  document_id BIGINT NOT NULL,
  chunk_index INT NOT NULL DEFAULT 0,
  content VARCHAR(2000) DEFAULT NULL,
  embedding_id VARCHAR(100) DEFAULT NULL,
  KEY idx_document (document_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 通知域
-- =====================================================================

DROP TABLE IF EXISTS notify_inbox;
CREATE TABLE notify_inbox (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  traveler_id BIGINT DEFAULT NULL,
  title VARCHAR(200) DEFAULT NULL,
  content VARCHAR(1000) DEFAULT NULL,
  msg_type VARCHAR(20) NOT NULL DEFAULT 'system' COMMENT 'agent_notify/trip_reminder/booking/alert/system',
  source VARCHAR(20) NOT NULL DEFAULT 'system',
  related_id BIGINT DEFAULT NULL,
  is_read TINYINT NOT NULL DEFAULT 0,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_user (user_id),
  KEY idx_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 智能助手域
-- =====================================================================

DROP TABLE IF EXISTS agent_conversation;
CREATE TABLE agent_conversation (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  traveler_id BIGINT DEFAULT NULL,
  session_id VARCHAR(64) NOT NULL,
  role VARCHAR(20) NOT NULL COMMENT 'user/assistant/system/pending_book',
  content VARCHAR(4000) DEFAULT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_session (session_id),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS agent_tool_call_log;
CREATE TABLE agent_tool_call_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(64) DEFAULT NULL,
  user_id BIGINT DEFAULT NULL,
  tool_name VARCHAR(50) NOT NULL,
  request_args VARCHAR(2000) DEFAULT NULL,
  response_data VARCHAR(8000) DEFAULT NULL COMMENT '截断到 8000 字符',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 成功 / 0 失败',
  cost_ms INT DEFAULT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_session (session_id),
  KEY idx_tool (tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- 种子数据
-- =====================================================================

-- 角色
INSERT INTO sys_role (code, name, sort_order, status) VALUES
('ADMIN', '管理员', 1, 1),
('USER', '普通用户', 2, 1);

-- 账号（admin/admin；aaa~ggg 密码统一 123，均存 bcrypt 哈希）
INSERT INTO sys_user (username, password, role, status) VALUES
('admin', '$2b$12$Hhdr/MW1SBb/XWg6AamqZObVOeRKB7YcVKsqNut2LqVL64McVgpka', 'ADMIN', 1),
('aaa', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('bbb', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('ccc', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('ddd', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('eee', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('fff', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1),
('ggg', '$2b$12$9NHHz2Qc4fyWuDl8da6Xy.ClvkqbluNtykwQOZhASn.CoTgFnw6Ry', 'USER', 1);

-- 后台菜单（14 条，全部 parent_id=0、roles=ADMIN）
INSERT INTO sys_menu (parent_id, name, path, icon, sort_order, roles) VALUES
(0, '数据概览', '/admin/dashboard', 'DataLine', 1, 'ADMIN'),
(0, '旅行者档案', '/admin/travelers', 'User', 2, 'ADMIN'),
(0, '行程管理', '/admin/trips', 'MapLocation', 3, 'ADMIN'),
(0, '行程模板', '/admin/templates', 'Files', 4, 'ADMIN'),
(0, '预约管理', '/admin/bookings', 'Calendar', 5, 'ADMIN'),
(0, '拼团活动', '/admin/groups', 'Flag', 6, 'ADMIN'),
(0, '旅途求助', '/admin/alerts', 'Bell', 7, 'ADMIN'),
(0, '攻略库', '/admin/guides', 'Reading', 8, 'ADMIN'),
(0, '旅游记录', '/admin/records', 'Notebook', 9, 'ADMIN'),
(0, '助手工具', '/admin/agent-tools', 'MagicStick', 10, 'ADMIN'),
(0, '助手日志', '/admin/agent-logs', 'List', 11, 'ADMIN'),
(0, '用户管理', '/admin/users', 'UserFilled', 12, 'ADMIN'),
(0, '系统日志', '/admin/logs', 'Document', 13, 'ADMIN'),
(0, '菜单管理', '/admin/menus', 'Menu', 14, 'ADMIN');

-- 旅行者档案（7 位，偏好各不相同）
INSERT INTO traveler_profile
(name, gender, birth_date, phone, id_card_no, dietary_restrictions, allergies, mobility_notes, preferences, preference_tags, emergency_contact, emergency_phone, status) VALUES
('陈小雨', '女', '1998-06-15', '13800000001', '330100199806150021', '素食', '无', '无', '喜欢海岛与海边发呆，重视当地饮食体验', '海岛,美食', '陈父', '13900000001', 1),
('李建国', '男', '1965-03-20', '13800000002', '330100196503200032', '无', '青霉素', '左膝不便，需慢行', '偏爱历史人文景点，喜欢摄影', '人文,摄影', '李母', '13900000002', 1),
('王芳', '女', '1988-11-02', '13800000003', '330100198811020043', '无', '花生', '无', '带孩子出游，节奏要慢，关注亲子设施', '亲子,休闲', '王先生', '13900000003', 1),
('张伟', '男', '1992-09-08', '13800000004', '330100199209080054', '无', '无', '无', '喜欢徒步与自然探险，追求小众路线', '探险,自然', '张父', '13900000004', 1),
('刘洋', '男', '1990-01-25', '13800000005', '330100199001250065', '忌辣', '海鲜', '无', '美食打卡与购物，偏好都市游', '美食,购物', '刘母', '13900000005', 1),
('赵敏', '女', '1995-05-30', '13800000006', '330100199505300076', '无', '无', '无', '摄影与人文古镇，喜欢出片点位', '摄影,人文', '赵父', '13900000006', 1),
('孙悦', '女', '2000-12-12', '13800000007', '330100200012120087', '无', '无', '无', '海岛度假，休闲放松', '海岛,休闲', '孙母', '13900000007', 1);

-- 绑定关系（7 条，一一对应，is_primary=1）
INSERT INTO family_member (user_id, traveler_id, relation, is_primary) VALUES
(2, 1, '女儿', 1),
(3, 2, '本人', 1),
(4, 3, '本人', 1),
(5, 4, '配偶', 1),
(6, 5, '儿子', 1),
(7, 6, '本人', 1),
(8, 7, '本人', 1);

-- 行程计划（含演示场景：陈小雨有逾期待办 + 本周预约需求）
INSERT INTO trip_plan (traveler_id, title, destination, start_date, end_date, budget, remark, status, source_template_id) VALUES
(1, '大理 3 日慢游', '大理', DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 3000.00, '本周出发，想体验当地美食', 1, NULL),
(1, '申根 7 日自由行', '法国', DATE_ADD(CURDATE(), INTERVAL 20 DAY), DATE_ADD(CURDATE(), INTERVAL 26 DAY), 18000.00, '签证待办', 1, NULL),
(3, '成都 4 日亲子游', '成都', DATE_ADD(CURDATE(), INTERVAL 10 DAY), DATE_ADD(CURDATE(), INTERVAL 13 DAY), 6000.00, NULL, 1, NULL);

-- 行程待办（刻意造 4 条逾期：status=2 且 due_time 早于当前）
INSERT INTO trip_todo (trip_id, traveler_id, item_name, due_time, category, status, done_time) VALUES
(1, 1, '预订接送机', DATE_ADD(NOW(), INTERVAL 2 DAY), 'transfer', 2, NULL),
(1, 1, '收拾行李', DATE_ADD(NOW(), INTERVAL 3 DAY), 'luggage', 2, NULL),
(1, 1, '预订民宿', DATE_SUB(NOW(), INTERVAL 2 DAY), 'other', 1, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(2, 1, '申根签证', DATE_SUB(NOW(), INTERVAL 5 DAY), 'visa', 2, NULL),
(2, 1, '购买旅行保险', DATE_SUB(NOW(), INTERVAL 3 DAY), 'insurance', 2, NULL),
(2, 1, '疫苗接种', DATE_ADD(NOW(), INTERVAL 10 DAY), 'vaccine', 2, NULL),
(3, 3, '预订门票', DATE_SUB(NOW(), INTERVAL 4 DAY), 'other', 1, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(3, 3, '收拾行李', DATE_SUB(NOW(), INTERVAL 1 DAY), 'luggage', 2, NULL),
(2, 1, '办理护照换发', DATE_SUB(NOW(), INTERVAL 2 DAY), 'document', 2, NULL);

-- 行程模板（2 个已发布）
INSERT INTO trip_template (title, destination, day_count, description, author_user_id, author_name, cover, use_count, status) VALUES
('大理 4 日慢游', '大理', 4, '环洱海 + 古城 + 喜洲，适合休闲慢游', 2, 'aaa', NULL, 3, 1),
('成都 3 日亲子', '成都', 3, '大熊猫基地 + 宽窄巷子，节奏舒缓适合带娃', 4, 'ccc', NULL, 1, 1);

INSERT INTO trip_template_item (template_id, day_index, time_slot, item_name, category, remark, sort_order) VALUES
(1, 1, '09:00', '抵达大理，入住洱海民宿', 'transfer', NULL, 1),
(1, 1, '14:00', '洱海骑行', 'other', '沿海西路景色最佳', 2),
(1, 2, '09:00', '大理古城漫步', 'other', NULL, 1),
(1, 2, '19:00', '古城夜市小吃', 'other', NULL, 2),
(1, 3, '全天', '喜洲古镇 + 海舌公园', 'other', NULL, 1),
(2, 1, '09:00', '大熊猫繁育研究基地', 'other', '上午熊猫活跃', 1),
(2, 2, '14:00', '宽窄巷子 + 人民公园', 'other', NULL, 1),
(2, 3, '09:00', '返程', 'transfer', NULL, 1);

-- 可预约项目（3 个：导游 / 民宿 / 当地体验）
INSERT INTO booking_catalog (name, item_type, description, duration_minutes, price, status) VALUES
('古城深度导览', 'guide', '专业导游带队，讲解古城历史与人文', 180, 280.00, 1),
('洱海海景民宿', 'homestay', '洱海景观房，含早餐', 1440, 520.00, 1),
('当地美食体验', 'experience', '跟随当地人逛早市并亲手制作特色菜', 120, 180.00, 1);

-- 拼团活动（3 个）
INSERT INTO group_tour (title, content, destination, start_time, end_time, capacity, status) VALUES
('大理古城文化行走', '跟着讲解员走读古城，了解白族建筑与历史', '大理', DATE_ADD(NOW(), INTERVAL 6 DAY), DATE_ADD(DATE_ADD(NOW(), INTERVAL 6 DAY), INTERVAL 3 HOUR), 20, 1),
('洱海骑行亲子营', '环洱海亲子骑行，含补给与保障车', '大理', DATE_ADD(NOW(), INTERVAL 8 DAY), DATE_ADD(DATE_ADD(NOW(), INTERVAL 8 DAY), INTERVAL 5 HOUR), 15, 1),
('苍山徒步摄影团', '苍山玉带路徒步，摄影领队指导出片', '大理', DATE_ADD(NOW(), INTERVAL 12 DAY), DATE_ADD(DATE_ADD(NOW(), INTERVAL 12 DAY), INTERVAL 6 HOUR), 12, 1);

-- 旅途求助工单（1 open + 1 handling）
INSERT INTO travel_alert (traveler_id, location, message, alert_type, status, notify_family, notify_staff, source) VALUES
(1, '西湖景区', '在西湖景区与队伍走散', 'lost', 'open', 1, 1, 'agent'),
(2, '酒店大堂', '身体不适，需要工作人员协助', 'illness', 'handling', 1, 1, 'manual');

-- 预约订单（约 30 条；slot_lock 用相对时间，取消/完成置 NULL 释放时段）
INSERT INTO booking_order (traveler_id, catalog_id, booking_time, guest_count, status, source, slot_lock, version, remark) VALUES
(1, 3, NOW(), 2, 'pending', 'agent', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 5 DAY), '%Y%m%d'), '0900'), 0, '助手待确认'),
(1, 1, NOW(), 2, 'pending', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 4 DAY), '%Y%m%d'), '1400'), 0, NULL),
(1, 2, DATE_SUB(NOW(), INTERVAL 10 DAY), 2, 'confirmed', 'manual', CONCAT('2:', DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 10 DAY), '%Y%m%d'), '1900'), 0, NULL),
(1, 1, DATE_SUB(NOW(), INTERVAL 20 DAY), 2, 'done', 'manual', NULL, 0, NULL),
(1, 3, DATE_SUB(NOW(), INTERVAL 25 DAY), 2, 'cancelled', 'manual', NULL, 0, NULL),
(2, 1, NOW(), 1, 'confirmed', 'agent', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 3 DAY), '%Y%m%d'), '0900'), 0, '助手代订'),
(2, 2, NOW(), 1, 'pending', 'manual', CONCAT('2:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 6 DAY), '%Y%m%d'), '1900'), 0, NULL),
(2, 1, DATE_SUB(NOW(), INTERVAL 15 DAY), 1, 'done', 'manual', NULL, 0, NULL),
(3, 3, NOW(), 3, 'pending', 'agent', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 7 DAY), '%Y%m%d'), '0900'), 0, '亲子体验'),
(3, 1, NOW(), 3, 'confirmed', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 5 DAY), '%Y%m%d'), '1400'), 1, NULL),
(3, 2, DATE_SUB(NOW(), INTERVAL 12 DAY), 3, 'done', 'manual', NULL, 0, NULL),
(4, 1, NOW(), 2, 'pending', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 8 DAY), '%Y%m%d'), '0900'), 0, NULL),
(4, 3, NOW(), 2, 'confirmed', 'agent', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 9 DAY), '%Y%m%d'), '1400'), 0, '助手代订'),
(4, 2, DATE_SUB(NOW(), INTERVAL 8 DAY), 2, 'cancelled', 'manual', NULL, 0, NULL),
(5, 3, NOW(), 1, 'pending', 'manual', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 10 DAY), '%Y%m%d'), '1900'), 0, NULL),
(5, 1, NOW(), 1, 'confirmed', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 11 DAY), '%Y%m%d'), '0900'), 0, NULL),
(5, 2, DATE_SUB(NOW(), INTERVAL 6 DAY), 1, 'done', 'manual', NULL, 0, NULL),
(6, 1, NOW(), 2, 'pending', 'agent', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 12 DAY), '%Y%m%d'), '1400'), 0, '摄影团讲解'),
(6, 3, NOW(), 2, 'confirmed', 'manual', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 13 DAY), '%Y%m%d'), '0900'), 0, NULL),
(6, 2, DATE_SUB(NOW(), INTERVAL 5 DAY), 2, 'cancelled', 'manual', NULL, 0, NULL),
(7, 3, NOW(), 1, 'pending', 'manual', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 14 DAY), '%Y%m%d'), '0900'), 0, NULL),
(7, 1, NOW(), 1, 'confirmed', 'agent', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 15 DAY), '%Y%m%d'), '0900'), 0, '助手代订'),
(7, 2, DATE_SUB(NOW(), INTERVAL 4 DAY), 1, 'done', 'manual', NULL, 0, NULL),
(1, 1, NOW(), 2, 'pending', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 16 DAY), '%Y%m%d'), '1900'), 0, NULL),
(2, 3, NOW(), 1, 'pending', 'manual', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 17 DAY), '%Y%m%d'), '1400'), 0, NULL),
(3, 2, NOW(), 3, 'confirmed', 'agent', CONCAT('2:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 18 DAY), '%Y%m%d'), '1900'), 0, '助手代订'),
(4, 1, NOW(), 2, 'confirmed', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 19 DAY), '%Y%m%d'), '0900'), 0, NULL),
(5, 3, NOW(), 1, 'pending', 'manual', CONCAT('3:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 20 DAY), '%Y%m%d'), '0900'), 0, NULL),
(6, 1, NOW(), 2, 'confirmed', 'manual', CONCAT('1:', DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 21 DAY), '%Y%m%d'), '1400'), 0, NULL),
(7, 3, NOW(), 1, 'done', 'agent', NULL, 0, '助手代订已完成');

-- 旅游记录（覆盖不同偏好，供偏好提炼演示）
INSERT INTO travel_record (traveler_id, trip_id, destination, visited_date, rating, content, photos, visibility) VALUES
(1, NULL, '三亚', DATE_SUB(CURDATE(), INTERVAL 90 DAY), 5, '海景很美，海鲜新鲜，节奏放松', NULL, 1),
(1, NULL, '厦门', DATE_SUB(CURDATE(), INTERVAL 60 DAY), 4, '环岛骑行体验好，文艺小店多', NULL, 1),
(1, NULL, '青岛', DATE_SUB(CURDATE(), INTERVAL 30 DAY), 4, '海边发呆很舒服，啤酒海鲜不错', NULL, 0),
(2, NULL, '西安', DATE_SUB(CURDATE(), INTERVAL 120 DAY), 5, '古城墙与兵马俑，历史底蕴深厚', NULL, 1),
(2, NULL, '洛阳', DATE_SUB(CURDATE(), INTERVAL 80 DAY), 4, '龙门石窟震撼，适合慢慢逛', NULL, 1),
(6, NULL, '乌镇', DATE_SUB(CURDATE(), INTERVAL 50 DAY), 5, '江南水乡出片，夜景很美', NULL, 1);

-- 工具调用日志（覆盖多个工具名，供管理端图表）
INSERT INTO agent_tool_call_log (session_id, user_id, tool_name, request_args, response_data, status, cost_ms) VALUES
('s1', 2, 'query_traveler_profile', '{"traveler_id":1}', '{"name":"陈小雨"}', 1, 12),
('s1', 2, 'check_trip_schedule', '{"traveler_id":1}', '{"overdue":2}', 1, 8),
('s1', 2, 'query_available_booking', '{"item_type":"experience"}', '{"slots":6}', 1, 15),
('s1', 2, 'book_item', '{"catalog_id":3}', '{"status":"pending"}', 1, 20),
('s2', 2, 'notify_companions', '{"traveler_id":1}', '{"notified":1}', 1, 6),
('s2', 2, 'query_guide_knowledge', '{"q":"申根签证"}', '{"hits":3}', 1, 18),
('s3', 3, 'query_traveler_profile', '{"traveler_id":2}', '{"name":"李建国"}', 1, 11),
('s3', 3, 'recommend_itinerary', '{"traveler_id":2}', '{"tags":["人文"]}', 1, 25),
('s4', 4, 'distill_preferences', '{"traveler_id":3}', '{"tags":["亲子"]}', 1, 30),
('s5', 2, 'copy_trip_template', '{"template_id":1}', '{"trip_id":4}', 1, 22);

-- 攻略文档（9 篇，file_path 前缀 seed/）
INSERT INTO guide_document (title, file_path, doc_type, destination, status) VALUES
('申根签证材料与注意事项', 'seed/visa_shengen.txt', 'visa', NULL, 0),
('落地签与免签的适用与限制', 'seed/visa_visa_on_arrival.txt', 'visa', NULL, 0),
('护照有效期与签证页常见问题', 'seed/doc_passport.txt', 'document', NULL, 0),
('古城类目的地游玩建议与避坑', 'seed/dest_ancient_town.txt', 'destination', NULL, 0),
('海岛游的季节、防晒与水上安全', 'seed/dest_island.txt', 'destination', NULL, 0),
('淡旺季差异与错峰出行建议', 'seed/tips_season.txt', 'tips', NULL, 0),
('旅途常见身体不适与应对', 'seed/tips_health.txt', 'tips', NULL, 0),
('带老人与小孩出行的注意事项', 'seed/tips_family.txt', 'tips', NULL, 0),
('常见旅游消费陷阱与防骗要点', 'seed/tips_scam.txt', 'tips', NULL, 0);

-- 攻略切片（9 篇 × 3 = 27 条）
INSERT INTO guide_chunk (document_id, chunk_index, content) VALUES
(1, 0, '申根签证需提前准备有效护照、行程单、住宿证明与旅行保险。保险需覆盖医疗费用且保额达到申根要求。'),
(1, 1, '申根签证通常按首个入境国或停留最长的国家申请，建议提前一到两个月预约递签。'),
(1, 2, '签证材料务必真实完整，行程与酒店订单需能相互印证，避免因材料矛盾被拒签。'),
(2, 0, '落地签需满足目的地国规定的入境条件，部分国家要求返程机票与足够现金。'),
(2, 1, '免签不等于无条件入境，需注意免签停留天数的上限，逾期停留会产生处罚。'),
(2, 2, '出行前应通过官方渠道核实最新签证政策，政策可能因形势变化而调整。'),
(3, 0, '护照有效期不足六个月可能被拒绝入境，出行前应检查有效期与空白签证页数量。'),
(3, 1, '签证页不足时需提前换发新护照，避免在机场或边检遇到麻烦。'),
(3, 2, '护照应妥善保管并留存复印件，遗失后及时向使领馆报失并办理旅行证。'),
(4, 0, '古城游玩建议避开人流高峰时段，清晨与傍晚光线好、人也相对较少。'),
(4, 1, '古城内多为石板路，建议穿舒适防滑的鞋子，注意保管随身财物。'),
(4, 2, '品尝小吃选择有本地人排队的店铺更稳妥，注意饮食卫生与过敏源。'),
(5, 0, '海岛游注意防晒与补水，正午紫外线强烈，建议避开长时间暴晒。'),
(5, 1, '参与水上项目务必穿好救生衣，遵守安全指引，量力而行。'),
(5, 2, '海岛出行关注天气与潮汐，恶劣天气避免出海，安全第一。'),
(6, 0, '淡旺季价格差异明显，错峰出行可显著降低机票与住宿成本。'),
(6, 1, '节假日人流密集，热门景点需提前预约，否则可能白跑一趟。'),
(6, 2, '淡季部分项目可能停运，出行前应确认景点开放时间与交通安排。'),
(7, 0, '旅途中出现轻微肠胃不适时注意补水与清淡饮食，情况严重应及时就医。'),
(7, 1, '晕车晕船可提前准备常用药，长途行程注意规律作息与适当活动。'),
(7, 2, '本内容为一般性建议，不能替代专业医疗诊断，出现急症请立即就医。'),
(8, 0, '带老人出行应放缓节奏，每天安排一到两个核心景点即可，预留休息时间。'),
(8, 1, '带小孩出行注意安全与作息，备好常用药品与零食，避免过度疲劳。'),
(8, 2, '选择有无障碍设施与母婴室的场所，提前确认厕所与休息点位置。'),
(9, 0, '警惕低价旅行团与免费体验的诱导，谨防强制购物与隐形消费。'),
(9, 1, '景区附近高价特产需货比三家，付款前确认价格单位与计量方式。'),
(9, 2, '遇到消费纠纷保留凭证，及时向景区或市场监管部门投诉维权。');
