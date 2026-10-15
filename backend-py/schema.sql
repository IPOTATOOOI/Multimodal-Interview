-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: localhost    Database: swcup
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `status` int DEFAULT '1',
  `face_filename` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `core_competences`
--

DROP TABLE IF EXISTS `core_competences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_competences` (
  `competence_id` int NOT NULL AUTO_INCREMENT,
  `position_id` int NOT NULL COMMENT '关联岗位ID',
  `competence_name` varchar(255) NOT NULL COMMENT '能力名称',
  `competence_description` text NOT NULL COMMENT '能力描述',
  PRIMARY KEY (`competence_id`),
  KEY `position_id` (`position_id`),
  CONSTRAINT `core_competences_ibfk_1` FOREIGN KEY (`position_id`) REFERENCES `positions` (`position_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domains`
--

DROP TABLE IF EXISTS `domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domains` (
  `domain_id` int NOT NULL AUTO_INCREMENT,
  `domain_name` varchar(50) NOT NULL COMMENT '领域名称',
  PRIMARY KEY (`domain_id`),
  UNIQUE KEY `domain_name` (`domain_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `high_freq_questions`
--

DROP TABLE IF EXISTS `high_freq_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `high_freq_questions` (
  `question_type_id` int NOT NULL AUTO_INCREMENT,
  `position_id` int NOT NULL COMMENT '关联岗位ID',
  `question_type_name` text NOT NULL COMMENT '题型名称',
  `question_example` text NOT NULL COMMENT '题型示例',
  `scoring_focus` text NOT NULL COMMENT '评分重点',
  `answer_template` text NOT NULL COMMENT '优秀回答模板',
  PRIMARY KEY (`question_type_id`),
  KEY `position_id` (`position_id`),
  CONSTRAINT `high_freq_questions_ibfk_1` FOREIGN KEY (`position_id`) REFERENCES `positions` (`position_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `interview_history`
--

DROP TABLE IF EXISTS `interview_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interview_history` (
  `history_id` int NOT NULL AUTO_INCREMENT COMMENT '面试历史ID',
  `process_id` varchar(36) DEFAULT NULL COMMENT '处理任务ID（UUID）',
  `user_id` int NOT NULL COMMENT '用户ID，关联用户表',
  `interview_time` datetime NOT NULL COMMENT '面试时间',
  `field` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '选择的技术领域',
  `position` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '选择的岗位',
  `professional_knowledge` int DEFAULT NULL COMMENT '专业知识水平，1-5分',
  `skill_match` int DEFAULT NULL COMMENT '技能匹配度，1-5分',
  `language_expression` int DEFAULT NULL COMMENT '语言表达能力，1-5分',
  `logical_thinking` int DEFAULT NULL COMMENT '逻辑思维能力，1-5分',
  `innovation_ability` int DEFAULT NULL COMMENT '创新能力，1-5分',
  `stress_resistance` int DEFAULT NULL COMMENT '应变抗压能力，1-5分',
  `feedback_suggestion1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '反馈建议1',
  `feedback_suggestion2` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '反馈建议2',
  `feedback_suggestion3` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '反馈建议3',
  `html` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '大模型生成的HTML',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `score` int DEFAULT NULL COMMENT '面试分数',
  `end_time` timestamp NULL DEFAULT NULL COMMENT '面试结束时间',
  `current_topic` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '当前考察话题（交互式模式）',
  `follow_up_count` int DEFAULT 0 COMMENT '当前话题连续追问次数',
  `total_questions_asked` int DEFAULT 0 COMMENT '已提问总题数',
  `expression_evaluation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '表情神态评价',
  `gesture_evaluation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '肢体动作评价',
  PRIMARY KEY (`history_id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_interview_time` (`interview_time`) USING BTREE,
  KEY `idx_field_position` (`field`,`position`) USING BTREE,
  CONSTRAINT `fk_interview_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='面试历史记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `positions`
--

DROP TABLE IF EXISTS `positions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `positions` (
  `position_id` int NOT NULL AUTO_INCREMENT,
  `position_name` varchar(50) NOT NULL COMMENT '岗位名称',
  `domain_id` int NOT NULL COMMENT '所属领域ID',
  PRIMARY KEY (`position_id`),
  UNIQUE KEY `unique_position_in_domain` (`domain_id`,`position_name`),
  CONSTRAINT `positions_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`domain_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `qa`
--

DROP TABLE IF EXISTS `qa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qa` (
  `qa_id` int NOT NULL AUTO_INCREMENT COMMENT '问题回答ID',
  `history_id` int NOT NULL COMMENT '面试历史ID，关联面试历史表',
  `role` int NOT NULL COMMENT '角色，0=问题，1=回答',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '内容',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  `evaluation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '评价',
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '反馈',
  `key_words` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '回答要点关键词',
  `reference_a` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '参考答案',
  `difficulty` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '问题难度',
  `skill` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '考察的专业技能',
  `answer_rating` decimal(3,1) DEFAULT NULL COMMENT '回答评分（0.0-5.0）',
  `category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '问题所属类别',
  `speech_rate` decimal(5,1) DEFAULT NULL COMMENT '语速（音节/分钟）',
  `clarity` decimal(5,1) DEFAULT NULL COMMENT '清晰度（%）',
  `confidence` decimal(5,1) DEFAULT NULL COMMENT '自信度（%）',
  `annotation_status` varchar(20) DEFAULT NULL COMMENT '批注状态',
  PRIMARY KEY (`qa_id`) USING BTREE,
  KEY `idx_history_id` (`history_id`) USING BTREE,
  KEY `idx_role` (`role`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE,
  CONSTRAINT `fk_qa_history` FOREIGN KEY (`history_id`) REFERENCES `interview_history` (`history_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='问题与回答表';

ALTER TABLE qa
    ADD COLUMN speech_rate DECIMAL(5,1) DEFAULT NULL COMMENT '语速（音节/分钟）',
    ADD COLUMN clarity DECIMAL(5,1) DEFAULT NULL COMMENT '清晰度（%）',
    ADD COLUMN confidence DECIMAL(5,1) DEFAULT NULL COMMENT '自信度（%）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resume`
--

DROP TABLE IF EXISTS `resume`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resume` (
  `resume_id` int NOT NULL AUTO_INCREMENT COMMENT '简历ID',
  `user_id` int NOT NULL COMMENT '用户ID，关联用户表',
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '姓名',
  `age` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '年龄',
  `school` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '学校',
  `major` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '专业',
  `graduation_year` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '毕业年份',
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `project_experiences` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '项目经历',
  `internship_experiences` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '实习经历',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`resume_id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  CONSTRAINT `fk_resume_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='简历信息表';

use swcup;
ALTER TABLE `resume`
    MODIFY COLUMN `age` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '年龄',
    MODIFY COLUMN `graduation_year` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '毕业年份';

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `terms`
--

DROP TABLE IF EXISTS `terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `terms` (
  `term_id` int NOT NULL AUTO_INCREMENT,
  `position_id` int NOT NULL COMMENT '关联岗位ID',
  `term_name` varchar(255) NOT NULL COMMENT '术语名称',
  `term_explanation` text NOT NULL COMMENT '术语解释',
  `frequency` enum('高频','中频','低频') NOT NULL COMMENT '出现频率',
  PRIMARY KEY (`term_id`),
  KEY `position_id` (`position_id`),
  CONSTRAINT `terms_ibfk_1` FOREIGN KEY (`position_id`) REFERENCES `positions` (`position_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户姓名',
  `gender` tinyint(1) DEFAULT '0' COMMENT '性别：0未知, 1男, 2女',
  `age` tinyint unsigned DEFAULT '0' COMMENT '年龄',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '加密密码',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户邮箱',
  `university` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '大学名称',
  `major` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '专业名称',
  `face` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '人脸图片文件名',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_username` (`username`) USING BTREE,
  UNIQUE KEY `username_idx` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='用户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weakness`
--

DROP TABLE IF EXISTS `weakness`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weakness` (
  `weakness_id` int NOT NULL AUTO_INCREMENT COMMENT '主键，薄弱点记录ID',
  `history_id` int NOT NULL COMMENT '关联的面试历史记录 ID（interview_history.history_id）',
  `question_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题目唯一标识（如 q1001）',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '题目标题',
  `content` text COLLATE utf8mb4_unicode_ci COMMENT '题干内容',
  `choice` text COLLATE utf8mb4_unicode_ci COMMENT '题目选项，以 A. / B. / C. / D. 开头；若非选择题则可为空或空格',
  `question_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '题型，如 "single_choice","multiple_choice","essay","code"',
  `difficulty` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '难度，如 "easy","medium","hard"',
  `standard_answer` text COLLATE utf8mb4_unicode_ci COMMENT '标准答案',
  `tag_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '标签名称（如 "哈希表"）',
  `knowledgepoint_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '知识点名称（如 "线性表"）',
  `question_score` decimal(5,1) DEFAULT NULL COMMENT '题目分值（如 5.0）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间（默认当前时间）',
  PRIMARY KEY (`weakness_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='每次面试后的薄弱点题目记录（字段与 written_test 对齐，未含 user_id/扩展字段/额外索引）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `written_test`
--

DROP TABLE IF EXISTS `written_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `written_test` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `history_id` int NOT NULL COMMENT '关联的面试记录ID，外键关联interview_history',
  `question_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目唯一标识，如"q1001"',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题干内容',
  `choice` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目选项，非选择题为一个空格',
  `question_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题型：single_choice/multiple_choice/essay',
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '难度：easy/medium/hard',
  `standard_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '标准答案',
  `tag_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标签名称',
  `knowledgepoint_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '知识点名称',
  `question_score` decimal(5,1) NOT NULL COMMENT '题目分值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`record_id`) USING BTREE,
  KEY `history_id` (`history_id`) USING BTREE,
  CONSTRAINT `written_test_ibfk_1` FOREIGN KEY (`history_id`) REFERENCES `interview_history` (`history_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-12 15:13:27
