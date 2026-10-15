SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建领域表
DROP TABLE IF EXISTS domains;
CREATE TABLE domains (
                         domain_id INT PRIMARY KEY AUTO_INCREMENT,
                         domain_name VARCHAR(50) NOT NULL UNIQUE COMMENT '领域名称'
);

-- 创建岗位表
DROP TABLE IF EXISTS positions;
CREATE TABLE positions (
                           position_id INT PRIMARY KEY AUTO_INCREMENT,
                           position_name VARCHAR(50) NOT NULL COMMENT '岗位名称',
                           domain_id INT NOT NULL COMMENT '所属领域ID',
                           FOREIGN KEY (domain_id) REFERENCES domains(domain_id),
                           UNIQUE KEY unique_position_in_domain (domain_id, position_name)
);

-- 创建岗位核心能力表
DROP TABLE IF EXISTS core_competences;
CREATE TABLE core_competences (
                                  competence_id INT PRIMARY KEY AUTO_INCREMENT,
                                  position_id INT NOT NULL COMMENT '关联岗位ID',
                                  competence_name VARCHAR(255) NOT NULL COMMENT '能力名称',
                                  competence_description TEXT NOT NULL COMMENT '能力描述',
                                  FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

-- 创建岗位术语表
DROP TABLE IF EXISTS terms;
CREATE TABLE terms (
                       term_id INT PRIMARY KEY AUTO_INCREMENT,
                       position_id INT NOT NULL COMMENT '关联岗位ID',
                       term_name VARCHAR(255) NOT NULL COMMENT '术语名称',
                       term_explanation TEXT NOT NULL COMMENT '术语解释',
                       frequency ENUM('高频', '中频', '低频') NOT NULL COMMENT '出现频率',
                       FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

-- 创建高频题型表
CREATE TABLE high_freq_questions (
                                     question_type_id INT PRIMARY KEY AUTO_INCREMENT,
                                     position_id INT NOT NULL COMMENT '关联岗位ID',
                                     question_type_name TEXT NOT NULL COMMENT '题型名称',
                                     question_example TEXT NOT NULL COMMENT '题型示例',
                                     scoring_focus TEXT NOT NULL COMMENT '评分重点',
                                     answer_template TEXT NOT NULL COMMENT '优秀回答模板',
                                     FOREIGN KEY (position_id) REFERENCES positions(position_id)
);


-- 插入领域数据
INSERT INTO domains (domain_name) VALUES
                                      ('人工智能领域'),
                                      ('大数据领域'),
                                      ('物联网领域'),
                                      ('软件开发领域');

-- 插入岗位数据
INSERT INTO positions (position_name, domain_id) VALUES
                                                     ('机器学习算法工程师', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('深度学习算法工程师', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('计算机视觉工程师', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('AI系统架构师', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('机器人算法工程师', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('AI产品经理', (SELECT domain_id FROM domains WHERE domain_name = '人工智能领域')),
                                                     ('大数据开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('数据工程师（ETL）', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('数据分析师', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('商业智能（BI）分析师', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('大数据运维工程师', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('数据安全工程师', (SELECT domain_id FROM domains WHERE domain_name = '大数据领域')),
                                                     ('物联网工程师', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('嵌入式系统开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('传感器工程师', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('物联网解决方案架构师', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('边缘计算工程师', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('物联网产品经理', (SELECT domain_id FROM domains WHERE domain_name = '物联网领域')),
                                                     ('前端开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('UI/UX设计师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('后端开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('全栈开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('Android开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('iOS开发工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('软件测试工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('质量保证（QA）工程师', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域')),
                                                     ('项目经理', (SELECT domain_id FROM domains WHERE domain_name = '软件开发领域'));

-- 插入岗位核心能力数据
-- 人工智能领域岗位核心能力数据插入
INSERT INTO core_competences (position_id, competence_name, competence_description) VALUES
-- 机器学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '数学基础能力', '掌握线性代数、概率论、统计学等数学知识，能够理解和推导机器学习算法的数学原理。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '算法设计与优化能力', '能够设计和优化机器学习算法，提高算法的准确性和效率。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '数据处理与特征工程能力', '能够对原始数据进行清洗、预处理和特征提取，提高数据质量和模型性能。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '模型选择与调优能力', '能够根据业务需求和数据特点选择合适的机器学习模型，并进行调优和评估。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '编程实现能力', '熟练掌握至少一种编程语言（如Python）和机器学习框架（如TensorFlow、PyTorch），能够实现和部署机器学习模型。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '问题解决与创新能力', '能够独立分析和解决机器学习中的复杂问题，并提出创新的解决方案。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '业务理解与应用能力', '能够理解业务需求，将机器学习技术应用到实际业务场景中，解决实际问题。'),

-- 深度学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '深度学习理论基础', '深入理解神经网络、卷积神经网络（CNN）、循环神经网络（RNN）、Transformer等深度学习模型的原理和架构。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '模型训练与优化', '掌握深度学习模型的训练技巧和优化方法，能够解决过拟合、梯度消失等问题。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '计算机视觉/NLP应用能力', '能够将深度学习技术应用于计算机视觉（如图像识别、目标检测）或自然语言处理（如文本分类、机器翻译）等领域。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '大规模数据处理与并行计算', '能够处理大规模数据集，并利用GPU/TPU等并行计算资源加速模型训练。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '模型部署与工程化', '了解深度学习模型的部署和优化技术，能够将训练好的模型集成到实际应用系统中。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '创新能力与研究能力', '跟踪深度学习领域的最新研究进展，能够提出创新性的解决方案和模型架构。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '跨学科协作能力', '能够与计算机视觉、自然语言处理等领域的专家合作，共同解决复杂的问题。'),

-- 计算机视觉工程师
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '图像处理与分析', '掌握图像处理的基本算法和技术，如图像滤波、特征提取、目标检测等。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '计算机视觉算法', '熟悉常见的计算机视觉算法，如卷积神经网络（CNN）、目标检测、语义分割、图像生成等。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '深度学习框架应用', '熟练使用深度学习框架（如TensorFlow、PyTorch）实现计算机视觉模型。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '数据集构建与标注', '能够构建和管理计算机视觉数据集，掌握数据标注工具和方法。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '模型优化与部署', '能够对计算机视觉模型进行优化和压缩，使其在边缘设备上高效运行。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '硬件协同设计', '了解计算机视觉硬件加速技术（如GPU、FPGA、ASIC），能够进行硬件协同设计。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '跨领域应用能力', '能够将计算机视觉技术应用于自动驾驶、安防监控、医疗影像分析等不同领域。'),

-- AI系统架构师
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), 'AI技术栈选型与评估', '能够根据业务需求和技术特点，选择合适的AI技术栈（如框架、算法、硬件平台）。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '系统设计与架构规划', '设计可扩展、高可用、高性能的AI系统架构，包括数据处理、模型训练、推理服务等模块。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '分布式计算与集群管理', '掌握分布式计算技术和集群管理工具，能够构建和维护大规模AI训练和推理集群。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '模型部署与服务化', '了解模型部署的最佳实践，能够将训练好的模型转化为可扩展的在线服务。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '性能优化与调优', '能够对AI系统的性能进行分析和优化，提高系统的吞吐量和响应速度。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '数据安全与隐私保护', '关注AI系统的数据安全和隐私保护问题，能够设计相应的安全机制和策略。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '技术团队管理与协作', '能够带领和管理技术团队，协调不同角色之间的工作，推动项目顺利进行。'),

-- 机器人算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '机器人运动学与动力学', '掌握机器人运动学和动力学原理，能够设计和实现机器人的运动控制算法。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '路径规划与导航', '熟悉机器人路径规划和导航算法，如A*算法、Dijkstra算法、SLAM（同步定位与地图构建）等。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '传感器数据处理', '能够处理和融合机器人各种传感器（如激光雷达、摄像头、IMU）的数据，实现环境感知和状态估计。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '机器学习与机器人结合', '将机器学习技术应用于机器人领域，如机器人自主学习、行为决策等。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '控制理论与算法', '掌握控制理论的基本原理和方法，能够设计和实现机器人的控制算法。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '机器人仿真与验证', '熟悉机器人仿真工具（如Gazebo、Webots），能够进行机器人算法的仿真和验证。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '嵌入式系统开发', '了解嵌入式系统开发技术，能够将算法部署到机器人硬件平台上。'),

-- AI产品经理
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'AI技术理解与应用', '理解人工智能的基本概念、技术和应用场景，能够判断AI技术在产品中的适用性。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '用户需求分析与挖掘', '能够深入了解用户需求，将用户需求转化为AI产品的功能和特性。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '产品规划与roadmap制定', '制定AI产品的发展规划和路线图，协调各方资源推动产品落地。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '数据驱动决策', '善于利用数据进行产品决策，通过数据分析优化产品性能和用户体验。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '跨团队协作与沟通', '能够与研发、算法、设计等团队有效沟通和协作，确保产品目标的实现。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '商业模式创新', '探索AI产品的商业模式和盈利方式，推动产品的商业化落地。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '伦理与法律意识', '关注AI产品的伦理和法律问题，确保产品的开发和使用符合相关法规和道德标准。');

-- 大数据领域岗位核心能力数据插入
INSERT INTO core_competences (position_id, competence_name, competence_description) VALUES
-- 大数据开发工程师
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '分布式计算框架', '掌握Hadoop、Spark等分布式计算框架的原理和应用，能够开发高效的分布式数据处理程序。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '数据存储与管理', '熟悉HBase、Cassandra等NoSQL数据库和分布式文件系统，能够设计和实现高效的数据存储方案。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '实时数据处理', '掌握Flink、Storm等实时数据处理框架，能够开发实时数据处理系统。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '数据仓库与ETL', '能够设计和实现企业级数据仓库，掌握ETL工具和技术，进行数据抽取、转换和加载。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '编程语言与开发工具', '熟练掌握Java、Scala等编程语言，熟悉Maven、Git等开发工具。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '性能优化与调优', '能够对大数据系统的性能进行分析和优化，提高系统的吞吐量和响应速度。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '分布式系统设计', '了解分布式系统的设计原则和方法，能够设计和实现高可用、可扩展的大数据系统。'),

-- 数据工程师（ETL）
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), 'ETL工具与技术', '熟练掌握Informatica、Talend、Sqoop等ETL工具和技术，能够设计和实现数据抽取、转换和加载流程。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据清洗与预处理', '能够对原始数据进行清洗、去重、标准化等预处理操作，提高数据质量。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据建模与设计', '掌握数据建模的方法和技巧，能够设计合理的数据模型，满足业务需求。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据库技术', '熟悉关系型数据库和NoSQL数据库的原理和操作，能够编写高效的SQL语句。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据集成与同步', '能够实现不同数据源之间的数据集成和同步，确保数据的一致性和准确性。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '自动化与脚本编程', '掌握Shell、Python等脚本语言，能够编写自动化脚本，提高工作效率。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据质量监控与管理', '建立数据质量监控体系，对数据质量进行实时监控和管理，及时发现和解决数据质量问题。'),

-- 数据分析师
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据分析工具与技术', '熟练掌握SQL、Python、R等数据分析工具和技术，能够进行数据清洗、分析和可视化。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '统计学与机器学习基础', '掌握统计学的基本原理和方法，了解机器学习的基本算法和应用场景。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '业务理解与需求分析', '能够理解业务需求，将业务问题转化为数据分析问题，并提出相应的解决方案。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据可视化与报告', '能够使用Tableau、Power BI等工具进行数据可视化，制作清晰、有洞察力的数据报告。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据挖掘与探索', '能够运用数据挖掘技术，发现数据中的潜在模式和价值，为业务决策提供支持。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据 storytelling', '能够将数据分析结果以故事的形式呈现给业务 stakeholders，帮助他们理解数据和做出决策。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据驱动决策', '能够基于数据分析结果，为业务决策提供数据支持和建议，推动业务发展。'),

-- 商业智能（BI）分析师
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), 'BI工具与技术', '熟练掌握Power BI、Tableau、QlikView等商业智能工具，能够设计和开发数据可视化报表和仪表盘。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据仓库与建模', '了解数据仓库的架构和设计方法，能够设计和实现维度模型，支持业务分析。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '业务流程与需求分析', '深入了解企业的业务流程和需求，能够将业务需求转化为BI解决方案。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), 'SQL与数据库技术', '熟练掌握SQL语言，能够编写复杂的SQL查询，从数据库中提取所需的数据。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据可视化设计', '掌握数据可视化的原则和方法，能够设计出美观、易用、有洞察力的数据可视化界面。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据分析与洞察', '能够对业务数据进行深入分析，发现业务问题和机会，提供有价值的业务洞察。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '项目管理与沟通', '能够协调BI项目的实施，与业务部门和技术团队有效沟通，确保项目顺利交付。'),

-- 大数据运维工程师
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '大数据平台架构', '熟悉Hadoop、Spark、Kafka等大数据平台的架构和组件，能够进行平台的安装、配置和维护。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '集群管理与监控', '能够管理和监控大数据集群的运行状态，及时发现和解决集群故障和性能问题。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '自动化运维工具', '掌握Ansible、Puppet等自动化运维工具，能够实现大数据平台的自动化部署和管理。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '故障排查与处理', '具备良好的故障排查能力，能够快速定位和解决大数据平台的故障和问题。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '性能优化与调优', '能够对大数据平台的性能进行分析和优化，提高平台的吞吐量和稳定性。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '数据备份与恢复', '建立数据备份和恢复策略，确保大数据平台的数据安全和可恢复性。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '安全与权限管理', '管理大数据平台的安全和权限，确保数据的安全性和合规性。'),

-- 数据安全工程师
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据安全策略与标准', '制定和实施数据安全策略和标准，确保企业数据的安全性和合规性。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据加密与隐私保护', '掌握数据加密技术和隐私保护方法，能够对敏感数据进行加密和保护。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '访问控制与权限管理', '设计和实施数据访问控制和权限管理机制，确保数据的访问安全。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据安全审计与监控', '建立数据安全审计和监控体系，对数据访问和操作进行实时监控和审计。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据泄露检测与响应', '能够检测和响应数据泄露事件，采取有效的措施减少损失。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '合规与风险管理', '了解数据安全相关的法规和标准，能够进行合规性评估和风险管理。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '安全技术与工具', '熟悉防火墙、入侵检测系统（IDS）、数据防泄漏（DLP）等安全技术和工具的使用。');

-- 物联网领域岗位核心能力数据插入
INSERT INTO core_competences (position_id, competence_name, competence_description) VALUES
-- 物联网工程师
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '物联网架构与协议', '了解物联网的三层架构（感知层、网络层、应用层）和常见协议（MQTT、CoAP、HTTP等）。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '嵌入式系统开发', '掌握嵌入式系统开发技术，能够进行硬件选型、电路设计和软件开发。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '传感器技术与应用', '熟悉各种传感器的原理和应用，能够进行传感器数据采集和处理。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '无线通信技术', '了解Wi-Fi、蓝牙、ZigBee、LoRa、NB-IoT等无线通信技术的特点和应用场景。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '云平台与数据处理', '熟悉AWS IoT、阿里云IoT、华为云IoT等物联网云平台，能够进行设备接入和数据处理。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '数据分析与应用开发', '能够对物联网数据进行分析和挖掘，开发物联网应用和服务。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '物联网安全', '关注物联网安全问题，能够设计和实现物联网系统的安全机制。'),

-- 嵌入式系统开发工程师
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '嵌入式系统原理', '掌握嵌入式系统的硬件架构和软件系统，了解处理器、存储器、外设等组件的工作原理。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '嵌入式编程语言', '熟练掌握C、C++等嵌入式编程语言，能够进行底层驱动开发和应用程序开发。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '实时操作系统（RTOS）', '熟悉FreeRTOS、uC/OS、RT-Thread等实时操作系统，能够进行RTOS的移植和应用开发。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '硬件设计与调试', '能够进行嵌入式系统的硬件设计和调试，包括原理图设计、PCB设计等。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '驱动开发', '掌握嵌入式系统驱动开发技术，能够开发各种外设的驱动程序。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '低功耗设计', '了解嵌入式系统的低功耗设计方法，能够设计和实现低功耗的嵌入式系统。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '通信接口开发', '熟悉UART、SPI、I2C、USB、Ethernet等通信接口，能够进行通信接口的开发和调试。'),

-- 传感器工程师
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器原理与技术', '深入了解各种传感器的工作原理和技术，如温度传感器、压力传感器、加速度传感器、光电传感器等。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器信号处理', '掌握传感器信号处理技术，能够对传感器输出的微弱信号进行放大、滤波、数字化等处理。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器设计与开发', '能够进行传感器的选型、设计和开发，满足特定的应用需求。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器标定与校准', '掌握传感器标定和校准技术，能够提高传感器的测量精度和可靠性。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '嵌入式系统集成', '能够将传感器与嵌入式系统进行集成，实现传感器数据的采集和处理。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '微机电系统（MEMS）技术', '了解微机电系统（MEMS）技术，能够设计和开发基于MEMS的传感器。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器应用与创新', '能够将传感器技术应用于不同领域，提出创新性的解决方案和应用场景。'),

-- 物联网解决方案架构师
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '物联网架构设计', '能够设计端到端的物联网解决方案架构，包括设备层、网络层、平台层和应用层。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '技术选型与评估', '根据业务需求和技术特点，选择合适的物联网技术和产品，如传感器、通信技术、云平台等。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '系统集成与整合', '能够将不同厂商的物联网设备、平台和应用进行集成和整合，实现系统的协同工作。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '数据处理与分析', '设计物联网数据处理和分析方案，包括数据采集、存储、处理、分析和可视化。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '安全与隐私设计', '关注物联网系统的安全和隐私问题，设计相应的安全机制和策略，保障系统和数据的安全。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '可扩展性与可靠性设计', '设计具有良好可扩展性和可靠性的物联网系统，满足业务发展和变化的需求。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '项目管理与技术指导', '能够带领团队进行物联网项目的实施，提供技术指导和支持，确保项目顺利交付。'),

-- 边缘计算工程师
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘计算架构与技术', '了解边缘计算的架构和技术，包括边缘节点、边缘网关、边缘云等组件。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘节点开发与部署', '能够进行边缘节点的硬件选型、软件安装和配置，部署边缘计算应用。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '分布式计算与存储', '掌握分布式计算和存储技术，能够在边缘节点之间实现数据和计算资源的协同。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘数据处理与分析', '能够在边缘节点上进行数据处理和分析，减少数据传输延迟，提高系统响应速度。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘与云端协同', '设计边缘节点与云端之间的数据同步和协同机制，实现边缘计算与云计算的优势互补。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '低功耗与资源优化', '了解边缘设备的低功耗设计和资源优化技术，提高边缘计算系统的能效比。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘计算安全', '关注边缘计算系统的安全问题，设计相应的安全机制，保障边缘设备和数据的安全。'),

-- 物联网产品经理
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '物联网技术与应用', '理解物联网的基本技术和应用场景，能够判断物联网技术在产品中的适用性。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '用户需求分析与挖掘', '能够深入了解用户需求，将用户需求转化为物联网产品的功能和特性。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '产品规划与roadmap制定', '制定物联网产品的发展规划和路线图，协调各方资源推动产品落地。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '硬件与软件协同设计', '能够协调硬件和软件团队，进行物联网产品的协同设计和开发。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '数据驱动决策', '善于利用数据进行产品决策，通过数据分析优化产品性能和用户体验。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '供应链与生产管理', '了解物联网产品的供应链和生产流程，能够进行供应链管理和生产协调。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '商业模式创新', '探索物联网产品的商业模式和盈利方式，推动产品的商业化落地。');

-- 软件开发领域岗位核心能力数据插入
INSERT INTO core_competences (position_id, competence_name, competence_description) VALUES
-- 前端开发工程师
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), 'HTML/CSS/JavaScript', '熟练掌握HTML、CSS、JavaScript等前端基础技术，能够实现响应式布局和交互效果。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '前端框架与库', '熟悉React、Vue、Angular等前端框架和相关库，能够快速上手并开发复杂的前端应用。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '前端工程化', '了解前端工程化流程，掌握Webpack、Vite等构建工具，能够进行项目的打包、优化和部署。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '性能优化', '能够对前端应用的性能进行分析和优化，提高页面加载速度和用户体验。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '跨端开发', '了解小程序、Flutter、React Native等跨端开发技术，能够开发多平台兼容的应用。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '前端安全', '关注前端安全问题，了解XSS、CSRF等安全漏洞的防范方法，确保前端应用的安全性。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), 'UI/UX设计', '具备一定的UI/UX设计能力，能够理解设计稿并实现高质量的视觉效果。'),

-- UI/UX设计师
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '用户研究与需求分析', '能够进行用户研究和需求分析，了解用户行为和需求，为产品设计提供依据。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '交互设计', '掌握交互设计的原则和方法，能够设计出直观、易用、有趣的用户交互体验。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '视觉设计', '具备良好的视觉设计能力，能够设计出美观、有吸引力的界面，包括色彩搭配、排版、图标设计等。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '原型设计工具', '熟练使用Figma、Sketch、Adobe XD等原型设计工具，能够制作高保真原型，展示产品功能和交互流程。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '用户测试与反馈', '能够进行用户测试，收集用户反馈，根据反馈优化产品设计。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '设计系统与组件库', '了解设计系统和组件库的概念，能够设计和维护统一的设计语言和组件库。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '产品思维与商业意识', '具备产品思维和商业意识，能够将用户需求与业务目标相结合，设计出有价值的产品体验。'),

-- 后端开发工程师
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '编程语言与框架', '熟练掌握至少一种后端编程语言（如Java、Python、Node.js）和相关框架（如Spring、Django、Express）。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '数据库设计与开发', '熟悉关系型数据库和NoSQL数据库的设计和开发，能够编写高效的SQL语句和数据库查询。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), 'API设计与开发', '能够设计和开发RESTful API，遵循API设计规范，确保API的可用性和可维护性。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '微服务架构', '了解微服务架构的设计原则和方法，能够设计和实现微服务系统。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '系统设计与架构', '能够进行系统设计和架构规划，考虑系统的可扩展性、高可用性和性能。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '安全与权限管理', '关注后端系统的安全问题，能够设计和实现安全机制，如身份验证、授权、数据加密等。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '缓存与消息队列', '了解缓存和消息队列技术，能够使用Redis、RabbitMQ等中间件提高系统性能和可靠性。'),

-- 全栈开发工程师
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '前后端技术栈', '掌握前端和后端开发技术，能够独立完成从前端到后端的全流程开发。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '数据库设计与开发', '熟悉关系型数据库和NoSQL数据库的设计和开发，能够编写高效的SQL语句和数据库查询。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '系统架构与设计', '能够进行系统架构设计，考虑前后端的协同工作和整体性能。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), 'DevOps与部署', '了解DevOps流程和工具，能够进行项目的自动化部署和运维。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '性能优化', '能够对前后端应用的性能进行分析和优化，提高系统的响应速度和吞吐量。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '问题排查与解决', '具备良好的问题排查能力，能够快速定位和解决前后端开发中的问题。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '技术选型与评估', '能够根据项目需求，选择合适的前后端技术栈和工具，确保项目的可行性和可维护性。'),

-- Android开发工程师
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Java/Kotlin编程', '熟练掌握Java或Kotlin编程语言，了解Android开发的基本原理和流程。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Android SDK与框架', '熟悉Android SDK和相关框架，能够开发Android应用的各种功能模块。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'UI开发与布局', '能够实现Android应用的UI设计和布局，包括Activity、Fragment、RecyclerView等组件的使用。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), '性能优化', '能够对Android应用的性能进行分析和优化，包括内存优化、UI渲染优化等。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), '数据存储与网络通信', '掌握Android应用的数据存储方式（如SQLite、SharedPreferences）和网络通信技术（如Retrofit、Volley）。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Android安全', '关注Android应用的安全问题，了解Android安全机制和防范措施，确保应用的安全性。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), '应用发布与维护', '能够进行Android应用的打包、签名和发布，以及后续的版本更新和维护。'),

-- iOS开发工程师
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'Swift/Objective-C编程', '熟练掌握Swift或Objective-C编程语言，了解iOS开发的基本原理和流程。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'iOS SDK与框架', '熟悉iOS SDK和相关框架，能够开发iOS应用的各种功能模块。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'UI开发与布局', '能够实现iOS应用的UI设计和布局，包括ViewController、TableView、CollectionView等组件的使用。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), '性能优化', '能够对iOS应用的性能进行分析和优化，包括内存优化、UI渲染优化等。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), '数据存储与网络通信', '掌握iOS应用的数据存储方式（如Core Data、UserDefaults）和网络通信技术（如Alamofire、URLSession）。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'iOS安全', '关注iOS应用的安全问题，了解iOS安全机制和防范措施，确保应用的安全性。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), '应用发布与维护', '能够进行iOS应用的打包、签名和发布，以及后续的版本更新和维护。'),

-- 软件测试工程师
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '测试理论与方法', '掌握软件测试的基本理论和方法，包括功能测试、性能测试、自动化测试等。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '测试用例设计', '能够根据需求文档和设计文档，设计全面、有效的测试用例，覆盖各种场景和边界条件。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '缺陷管理与跟踪', '熟悉缺陷管理流程和工具，能够准确记录、报告和跟踪软件缺陷，确保缺陷得到及时解决。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '自动化测试框架', '掌握至少一种自动化测试框架（如Selenium、Appium、JUnit），能够编写自动化测试脚本。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '性能测试工具', '熟悉性能测试工具（如JMeter、LoadRunner），能够进行软件的性能测试和分析。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '测试流程与团队协作', '了解软件开发流程和测试流程，能够与开发团队、产品团队等有效协作，确保软件质量。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '安全测试', '了解安全测试的基本方法和技术，能够进行软件的安全漏洞检测和评估。'),

-- 质量保证（QA）工程师
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '质量管理体系', '熟悉质量管理体系和标准，如ISO 9001、CMMI等，能够建立和维护组织的质量管理体系。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '测试策略与计划', '能够制定测试策略和计划，根据项目需求和风险，确定测试范围、方法和资源。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '过程改进', '分析和评估软件开发过程，识别过程中的问题和改进点，推动过程改进和优化。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '缺陷分析与预防', '对软件缺陷进行统计和分析，找出缺陷产生的原因，提出预防措施，减少类似缺陷的再次发生。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '测试自动化', '推动测试自动化工具和框架的引入和应用，提高测试效率和覆盖率。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '质量度量与报告', '建立质量度量指标体系，定期收集和分析质量数据，生成质量报告，为管理层提供决策支持。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '团队培训与指导', '为测试团队提供培训和指导，提高团队成员的技术水平和质量意识。'),

-- 项目经理
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '项目管理知识体系', '掌握项目管理的知识体系和方法，包括项目启动、规划、执行、监控和收尾等过程。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '项目计划与进度控制', '能够制定详细的项目计划，跟踪项目进度，及时发现和解决项目中的问题，确保项目按时交付。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '资源管理与协调', '合理分配项目资源，协调团队成员之间的工作，解决资源冲突和问题。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '风险管理与应对', '识别项目中的风险，制定风险应对计划，监控风险状态，降低风险对项目的影响。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '沟通与团队协作', '具备良好的沟通能力和团队协作能力，能够与项目团队成员、客户、管理层等有效沟通。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '质量管理与控制', '关注项目质量，确保项目交付的成果符合质量标准和客户需求。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '成本管理与预算控制', '制定项目预算，监控项目成本，确保项目在预算范围内完成。');

-- 插入岗位术语数据

-- 人工智能领域岗位术语数据插入
INSERT INTO terms (position_id, term_name, term_explanation, frequency) VALUES
-- 机器学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '过拟合', '模型在训练数据上表现良好，但在未见过的数据上表现较差的现象，通常由于模型过于复杂或训练数据不足导致。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '梯度下降', '一种优化算法，通过迭代更新模型参数，沿着梯度的反方向寻找函数的最小值。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '特征工程', '将原始数据转换为更适合模型学习的特征的过程，包括特征选择、提取和转换等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '交叉验证', '一种评估模型性能的方法，将数据集划分为多个子集，轮流作为训练集和测试集，以减少评估结果的方差。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '正则化', '通过在模型训练过程中添加惩罚项，防止模型过拟合，提高模型泛化能力的技术。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '集成学习', '将多个弱学习器组合成一个强学习器的方法，如随机森林、梯度提升等。', '低频'),

-- 深度学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '神经网络', '一种模仿人类神经系统的计算模型，由大量神经元组成，可以自动从数据中学习特征和模式。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '卷积神经网络(CNN)', '一种专门用于处理具有网格结构数据如图像的神经网络，通过卷积层自动提取空间特征。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '循环神经网络(RNN)', '一种能够处理序列数据的神经网络，通过隐藏状态保存序列中的历史信息。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), 'Transformer', '一种基于注意力机制的神经网络架构，广泛应用于自然语言处理任务，能够并行处理序列数据。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '预训练模型', '在大规模数据上预先训练好的模型，可以通过微调快速适应特定任务。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '生成对抗网络(GAN)', '由生成器和判别器组成的神经网络，通过对抗训练生成与真实数据相似的新数据。', '低频'),

-- 计算机视觉工程师
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '目标检测', '在图像或视频中识别特定对象的位置和类别的任务，如YOLO、Faster R-CNN等算法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '语义分割', '将图像中的每个像素分配到特定类别的任务，常用于场景理解和自动驾驶等领域。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '特征提取', '从图像中提取有意义的特征，如边缘、角点、纹理等，用于后续分析和识别。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '图像分类', '将图像分配到预定义类别的任务，是计算机视觉的基础任务之一。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '实例分割', '同时识别图像中每个对象的类别和实例的任务，是目标检测和语义分割的结合。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '光流估计', '计算图像序列中物体运动的任务，用于视频分析和动作识别。', '低频'),

-- AI系统架构师
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '分布式训练', '将模型训练任务分配到多个计算设备或节点上并行进行的技术，提高训练效率。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '模型量化', '将模型参数从高精度表示（如32位浮点数）转换为低精度表示（如8位整数）的技术，减少模型大小和计算量。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '推理优化', '对训练好的模型进行优化，提高模型在生产环境中的推理速度和效率。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), 'MLOps', '将机器学习模型从开发到部署和维护的全生命周期管理，结合DevOps和机器学习最佳实践。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '异构计算', '利用不同类型的计算设备（如CPU、GPU、FPGA）协同工作，提高系统性能和能效。', '中频'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '联邦学习', '一种在多个参与方之间协作训练模型的技术，数据保留在本地，仅共享模型参数，保护数据隐私。', '低频'),

-- 机器人算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), 'SLAM', '同步定位与地图构建，机器人在未知环境中创建地图并确定自身位置的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '路径规划', '为机器人规划从起点到终点的最优路径的算法，如A*、Dijkstra等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '运动控制', '控制机器人执行特定运动任务的算法，如PID控制、轨迹跟踪等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '传感器融合', '将来自多个传感器的数据整合，提高机器人对环境感知能力的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '逆运动学', '根据机器人末端执行器的位置和姿态，计算各个关节角度的算法。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '强化学习控制', '利用强化学习算法训练机器人执行复杂任务，通过试错学习最优策略。', '低频'),

-- AI产品经理
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'AI产品落地', '将AI技术转化为实际产品和服务，满足用户需求并创造商业价值的过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '用户画像', '根据用户行为和特征构建的虚拟用户模型，用于指导产品设计和优化。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '数据标注', '为训练AI模型准备标注数据的过程，是AI产品开发的关键环节。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'A/B测试', '比较两个或多个产品版本，确定哪个版本表现更好的实验方法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '技术债务', '由于采用短期解决方案而不是长期最优方案，导致后续需要额外工作的积累。', '中频'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), '可解释AI', '开发能够解释其决策和预测的AI系统的方法和技术，提高用户信任度。', '低频');

-- 大数据领域岗位术语数据插入
INSERT INTO terms (position_id, term_name, term_explanation, frequency) VALUES
-- 大数据开发工程师
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), 'MapReduce', '一种分布式计算模型，将大规模数据处理任务分解为Map和Reduce两个阶段。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), 'Hadoop', '一个开源的分布式计算平台，包括HDFS分布式文件系统和MapReduce计算框架。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), 'Spark', '一个快速通用的集群计算系统，支持内存计算，比Hadoop MapReduce更快。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '分布式文件系统', '将数据分散存储在多个节点上的文件系统，如HDFS、Ceph等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), 'ETL', '提取、转换和加载，将数据从源系统提取，转换为适合分析的格式，加载到目标系统的过程。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '列式存储', '一种数据库存储方式，按列而不是按行存储数据，适合数据分析和查询。', '低频'),

-- 数据工程师（ETL）
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据管道', '将数据从源系统传输到目标系统的一系列处理步骤和技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据清洗', '识别和纠正数据中的错误、不完整或不一致记录的过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据集成', '将来自不同来源的数据整合到一个统一视图中的过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '增量更新', '只更新自上次更新以来发生变化的数据的方法，提高效率。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), 'CDC', '变更数据捕获，跟踪和捕获数据库中的数据变更，用于数据同步和复制。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '数据湖', '一个存储原始、未处理数据的存储库，支持各种数据分析和处理。', '低频'),

-- 数据分析师
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '描述性统计', '对数据进行总结和描述的统计方法，如均值、中位数、标准差等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '相关性分析', '衡量两个或多个变量之间关联程度的统计方法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '数据可视化', '将数据以图形或图表形式呈现，帮助理解和分析数据的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), 'A/B测试', '比较两个或多个变体，确定哪个表现更好的统计实验方法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '回归分析', '建立因变量与一个或多个自变量之间关系的统计方法。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '聚类分析', '将数据对象分组为相似对象类别的过程，用于发现数据中的自然分组。', '低频'),

-- 商业智能（BI）分析师
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据仓库', '一个用于存储企业历史数据的中央存储库，支持决策分析。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), 'OLAP', '联机分析处理，支持复杂数据分析和多维查询的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), 'KPI', '关键绩效指标，用于衡量组织或项目绩效的量化指标。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '仪表盘', '一个可视化界面，展示关键业务指标和数据，支持实时监控和决策。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), 'ETL', '提取、转换和加载，将数据从源系统提取，转换为适合分析的格式，加载到目标系统的过程。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据集市', '数据仓库的一个子集，针对特定业务部门或主题领域。', '低频'),

-- 大数据运维工程师
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '集群管理', '管理和维护分布式计算集群的过程，包括节点监控、资源分配等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), 'Hadoop生态系统', '围绕Hadoop平台的一系列开源项目和工具，如Hive、Pig、HBase等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '自动化部署', '使用工具自动配置和部署软件系统的过程，提高效率和一致性。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '性能调优', '优化系统性能，提高吞吐量和降低延迟的过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '高可用性', '确保系统在故障情况下仍能正常运行的设计和实现策略。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '日志分析', '收集、存储和分析系统日志，用于故障排查和性能监控。', '低频'),

-- 数据安全工程师
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据加密', '将数据转换为密文，防止未授权访问的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '访问控制', '管理和控制对系统资源访问的机制，确保只有授权用户可以访问。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据泄露', '未经授权访问或披露敏感数据的事件。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '合规性', '确保组织的数据处理活动符合相关法律法规和标准的要求。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '渗透测试', '通过模拟攻击评估系统安全性的方法。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '零信任架构', '一种安全模型，默认不信任任何内部或外部用户，始终验证访问请求。', '低频');

-- 物联网领域岗位术语数据插入
INSERT INTO terms (position_id, term_name, term_explanation, frequency) VALUES
-- 物联网工程师
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), 'MQTT', '一种轻量级消息传输协议，专为资源受限的设备和低带宽、高延迟网络设计。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '边缘计算', '在靠近数据源的边缘设备上进行数据处理和分析的计算模式。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '设备管理', '管理和维护物联网设备的过程，包括设备注册、配置、监控和升级。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), 'LoRaWAN', '一种低功耗广域网协议，适用于远距离、低速率的物联网应用。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '数字孪生', '物理实体的虚拟模型，通过实时数据更新反映物理实体的状态和行为。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), 'CoAP', '一种应用层协议，专为受限节点和网络设计，用于物联网设备之间的通信。', '低频'),

-- 嵌入式系统开发工程师
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), 'RTOS', '实时操作系统，能够满足严格的时间约束和实时响应要求的操作系统。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), 'GPIO', '通用输入输出，微控制器上的可编程引脚，用于连接外部设备。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), 'SPI', '串行外设接口，一种高速同步串行通信协议，用于短距离通信。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), 'I2C', '一种串行通信协议，使用两根线（数据线和时钟线）连接多个设备。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), 'Bootloader', '一段代码，负责初始化硬件并加载操作系统或应用程序。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '低功耗设计', '优化嵌入式系统功耗，延长电池寿命的设计技术。', '低频'),

-- 传感器工程师
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), 'ADC', '模拟-to-数字转换器，将连续的模拟信号转换为离散的数字信号。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '采样率', '每秒对模拟信号进行采样的次数，影响数字信号对原始信号的还原精度。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '分辨率', '传感器能够检测到的最小变化量，通常用位数表示。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '精度', '传感器测量值与真实值的接近程度，是传感器性能的重要指标。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '校准', '调整传感器输出，使其与已知标准一致的过程，提高测量准确性。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), 'MEMS传感器', '微机电系统传感器，利用微加工技术制造的小型化传感器。', '低频'),

-- 物联网解决方案架构师
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '端到端架构', '从物联网设备到云平台的完整技术架构，包括设备层、网络层、平台层和应用层。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), 'API网关', '作为所有API请求的入口点，处理请求路由、协议转换、安全认证等功能的组件。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '数据湖', '一个存储原始、未处理数据的存储库，支持各种数据分析和处理。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '可扩展性', '系统能够处理增长的工作负载和用户数量的能力，是架构设计的重要考虑因素。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '安全性设计', '在架构层面考虑安全需求，设计安全机制和策略，保障系统安全。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '雾计算', '一种分布式计算模型，将计算和数据存储靠近数据源，但比边缘计算更集中。', '低频'),

-- 边缘计算工程师
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘节点', '位于网络边缘的计算设备，靠近数据源，执行数据处理和分析任务。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘网关', '连接边缘设备和云端的中间设备，负责数据聚合、协议转换和边缘决策。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘缓存', '在边缘设备上缓存数据，减少数据传输延迟，提高响应速度的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘推理', '在边缘设备上执行AI模型推理，减少对云端依赖的技术。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘编排', '管理和协调多个边缘节点的资源和任务分配的技术。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘安全', '保障边缘计算环境安全的技术和策略，包括设备安全、数据安全等。', '低频'),

-- 物联网产品经理
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '物联网平台', '提供设备连接、数据管理、应用开发等功能的云服务平台，支持物联网应用的快速开发和部署。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '设备认证', '验证物联网设备身份的过程，确保只有合法设备可以连接到系统。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), 'OTA升级', '空中下载技术，允许远程更新物联网设备的固件和软件。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '用户体验设计', '设计物联网产品的交互和界面，确保用户能够轻松使用和从中获得价值的过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '产品生命周期管理', '管理产品从概念到退役的整个生命周期的过程，包括规划、开发、营销、支持等。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '数字孪生', '物理实体的虚拟模型，通过实时数据更新反映物理实体的状态和行为，用于产品监控和优化。', '低频');

-- 软件开发领域岗位术语数据插入
INSERT INTO terms (position_id, term_name, term_explanation, frequency) VALUES
-- 前端开发工程师
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '响应式设计', '一种设计方法，使网页能够自适应不同屏幕尺寸和设备类型。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), 'SPA', '单页应用，一种在单个页面上动态加载内容的Web应用，提供类似原生应用的用户体验。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '组件化开发', '将UI拆分为独立、可复用组件的开发方法，提高代码可维护性和开发效率。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '虚拟DOM', '轻量级JavaScript对象，是真实DOM的抽象表示，通过对比差异高效更新DOM。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), 'Webpack', '一个模块打包工具，将各种资源（如JavaScript、CSS、图片）打包成一个或多个文件。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), 'PWA', '渐进式Web应用，结合了Web技术和原生应用特性的Web应用，提供离线支持和推送通知等功能。', '低频'),

-- UI/UX设计师
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '用户体验(UX)', '用户与产品或服务交互过程中的整体体验和感受。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '界面设计(UI)', '设计产品的视觉元素和交互界面，包括布局、色彩、图标等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '线框图', '产品界面的简化视觉表示，展示页面结构和内容布局，不包含细节设计。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '原型', '产品的可交互模型，展示产品的功能和交互流程，用于测试和验证设计。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '用户测试', '通过观察真实用户使用产品的过程，收集反馈和发现问题的方法。', '中频'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '信息架构', '组织和结构信息的方式，帮助用户理解和找到所需信息。', '低频'),

-- 后端开发工程师
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), 'RESTful API', '遵循REST架构风格的API，使用HTTP协议的标准方法（GET、POST、PUT、DELETE）进行资源操作。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '微服务', '一种架构风格，将应用拆分为小型、自治的服务，每个服务专注于特定业务功能。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '数据库索引', '一种数据结构，提高数据库查询效率，类似于书籍的索引。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '事务处理', '一组不可分割的数据库操作，要么全部执行成功，要么全部回滚。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '中间件', '位于操作系统和应用程序之间的软件，提供通用服务和功能，如身份验证、日志记录等。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '负载均衡', '将工作负载分布到多个服务器上的技术，提高系统可用性和性能。', '低频'),

-- 全栈开发工程师
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '前后端分离', '一种开发模式，前端和后端独立开发，通过API进行通信，提高开发效率和可维护性。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), 'JWT', 'JSON Web Token，一种用于在网络应用间安全传输声明的开放标准。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '数据库范式', '数据库设计的规范和原则，用于减少数据冗余和提高数据完整性。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), 'CI/CD', '持续集成/持续部署，自动化软件开发流程，从代码提交到部署的全过程。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '容器化', '将应用及其依赖打包到容器中的技术，确保应用在不同环境中一致运行。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '服务发现', '在分布式系统中自动发现和注册服务实例的机制。', '低频'),

-- Android开发工程师
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Activity', 'Android应用的基本组件，代表一个屏幕的用户界面。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Fragment', 'Activity中的模块化组件，可复用和独立管理自己的生命周期。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'RecyclerView', '用于高效显示大量数据的视图组件，通过回收和重用视图提高性能。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Intent', '用于在组件间传递消息的对象，可用于启动Activity、Service等。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'ViewModel', '一种设计模式，负责为UI准备和管理数据，具有生命周期感知能力。', '中频'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'Jetpack Compose', 'Android的声明式UI工具包，简化UI开发，提高开发效率。', '低频'),

-- iOS开发工程师
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'ViewController', 'iOS应用的基本组件，管理屏幕上的内容和交互。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'UITableView', '用于显示列表数据的视图组件，是iOS应用中最常用的UI组件之一。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'UICollectionView', '灵活的网格布局视图组件，可自定义单元格大小和排列方式。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'Delegate', '一种设计模式，允许一个对象将某些任务委托给另一个对象处理。', '高频'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'SwiftUI', 'Apple的声明式UI框架，简化iOS、macOS等平台的UI开发。', '中频'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'Core Data', 'Apple的对象图管理和持久化框架，用于在iOS应用中存储和检索数据。', '低频'),

-- 软件测试工程师
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '单元测试', '对软件中的最小可测试单元进行测试的方法，确保每个单元正常工作。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '集成测试', '测试多个组件或模块之间的交互和协作的方法，确保它们能正确集成。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '自动化测试', '使用测试工具自动执行测试用例的方法，提高测试效率和可靠性。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '回归测试', '在修改代码后重新执行测试，确保修改没有引入新问题的方法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '性能测试', '测试系统在特定负载下的性能表现，包括响应时间、吞吐量等指标。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '安全测试', '测试系统的安全性，识别潜在的安全漏洞和风险的方法。', '低频'),

-- 质量保证（QA）工程师
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '质量标准', '定义产品或服务应满足的要求和规范的文档。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '测试计划', '描述测试活动的范围、方法、资源和进度的文档。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '缺陷管理', '识别、记录、跟踪和解决软件缺陷的过程和工具。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '过程改进', '分析和优化软件开发过程，提高产品质量和开发效率的方法。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '测试覆盖率', '衡量测试用例覆盖软件功能和代码的程度的指标。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '质量度量', '量化评估产品质量的指标和方法，如缺陷密度、修复率等。', '低频'),

-- 项目经理
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '敏捷开发', '一种以人为核心、迭代、循序渐进的开发方法，强调快速响应变化。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), 'Scrum', '一种敏捷框架，使用短周期迭代（Sprint）进行开发，强调团队协作和透明度。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), 'KPI', '关键绩效指标，用于衡量项目进度和绩效的量化指标。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '风险管理', '识别、评估和应对项目风险的过程，降低风险对项目的影响。', '高频'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '利益相关者管理', '识别和管理项目利益相关者的期望和需求的过程。', '中频'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '挣值分析', '一种项目绩效测量技术，通过比较计划价值、实际成本和挣值来评估项目进度和成本绩效。', '低频');

-- 插入岗位高频题型
-- 人工智能领域岗位高频题型
INSERT INTO high_freq_questions (position_id, question_type_name, question_example, scoring_focus, answer_template) VALUES
-- 机器学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '过拟合处理实践', '在你之前的项目中，遇到模型过拟合时采取了哪些解决措施？请举例说明。', '1. 对过拟合原因的分析深度；2. 解决方案的针对性（如正则化/数据增强/简化模型等）；3. 实际效果的数据支撑', '背景：项目中使用[模型类型]处理[数据场景]时，发现[过拟合表现，如训练集准确率95%但测试集仅70%]；\n问题：分析原因是[数据量不足/特征维度过高/模型复杂度超需求]；\n行动：采取[L1正则化+5倍数据增强+早停策略]，具体操作包括[调整正则化系数至0.01/使用SMOTE生成样本/设置验证集准确率下降3轮停止训练]；\n结果：测试集准确率提升至88%，泛化能力显著增强。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '特征工程实践', '描述一个你主导的特征工程案例，如何从原始数据中提取有效特征？', '1. 特征提取的逻辑性；2. 对业务与数据关联性的理解；3. 特征选择方法的合理性', '原始数据：[数据类型，如用户行为日志/传感器时序数据]，包含[关键字段]；\n业务目标：[如预测用户留存/设备故障预警]；\n特征设计：基于[业务逻辑/统计规律]，构建了[3类特征：时间序列特征（如滑动窗口均值）、交互特征（如用户行为组合）、领域特征（如设备运行状态编码）]；\n筛选方法：使用[特征重要性排序+方差膨胀因子(VIF)去除多重共线性]，最终保留[20个核心特征]；\n效果：模型AUC提升[0.12]，特征维度降低[40%]。'),
((SELECT position_id FROM positions WHERE position_name = '机器学习算法工程师'), '算法选型决策', '面对一个分类任务（如用户 churn 预测），你会如何选择合适的算法？请说明决策过程。', '1. 对不同算法特性的掌握；2. 结合数据特点的选型逻辑；3. 验证方法的严谨性', '任务分析：[数据规模10万样本，15个特征，类别不平衡比例1:5]；\n候选算法筛选：基于[数据量（排除需要超大规模数据的深度学习）、可解释性要求（排除黑盒模型）、类别不平衡适应性]，初步筛选[逻辑回归、随机森林、XGBoost]；\n验证过程：使用[5折交叉验证]，对比[准确率、召回率、F1值、训练效率]；\n最终选择：[XGBoost]，理由是[在不平衡数据上F1值比随机森林高8%，且训练时间可接受]；\n优化：后续通过[类别权重调整]进一步提升 minority 类召回率。'),

-- 深度学习算法工程师
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '神经网络架构设计', '请描述一个你设计的神经网络架构，为什么这样设计？解决了什么问题？', '1. 架构设计与任务的匹配度；2. 对网络层功能的理解；3. 创新点的合理性', '任务场景：[如细粒度图像分类（区分不同品种的花卉）/长文本情感分析]；\n核心挑战：[特征细微差异难捕捉/长距离依赖建模不足]；\n架构设计：基于[CNN+注意力机制]，具体包括[输入层→3层残差卷积（提取局部特征）→自注意力模块（聚焦关键区域）→全局平均池化→全连接层]；\n设计依据：[残差连接解决梯度消失，注意力机制增强关键特征权重]；\n效果：较基准模型（如ResNet50）准确率提升[5.3%]，推理速度提升[20%]。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '大规模数据训练优化', '当训练数据量超过1000万时，你如何优化模型训练过程？请举例说明。', '1. 对分布式训练原理的理解；2. 优化策略的多样性；3. 资源利用率的考量', '数据规模：[1500万图像数据，单样本1MB]，训练目标[目标检测模型]；\n核心问题：[单卡训练需30天，内存溢出风险]；\n优化措施：\n1. 数据层面：[使用TFRecord格式+预处理管道并行+数据分片存储]；\n2. 计算层面：[8卡数据并行（同步SGD）+混合精度训练（FP16）]；\n3. 模型层面：[冻结 backbone 前10层预训练权重，仅训练头部层]；\n效果：训练时间缩短至[5天]，GPU利用率从[40%]提升至[85%]，模型精度损失<1%。'),
((SELECT position_id FROM positions WHERE position_name = '深度学习算法工程师'), '模型部署工程化', '如何将训练好的深度学习模型（如CNN）部署到边缘设备（如嵌入式终端）？关键步骤是什么？', '1. 部署流程的完整性；2. 模型压缩技术的应用；3. 与硬件的适配性', '原始模型：[ResNet18，大小100MB，推理耗时500ms]，目标设备[算力1TOPS的嵌入式芯片]；\n部署步骤：\n1. 模型压缩：[量化（INT8）+剪枝（移除30%冗余卷积核）]，模型缩小至[15MB]；\n2. 格式转换：[PyTorch模型→ONNX→TensorRT优化]；\n3. 硬件适配：[使用设备SDK开发C++推理接口，绑定硬件加速指令]；\n4. 性能测试：[推理耗时降至30ms，准确率损失0.5%]；\n效果：满足设备[实时性（<50ms）和功耗（<5W）]要求。'),

-- 计算机视觉工程师
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '目标检测精度优化', '在目标检测项目中，如何提升小目标（如<30x30像素）的检测精度？', '1. 对小目标特性的理解；2. 多维度优化策略；3. 实际数据支撑', '项目背景：[监控视频中的行人检测，小目标占比30%，原始mAP 62%]；\n优化措施：\n1. 数据层面：[小目标样本过采样+数据增强（缩放/平移/马赛克拼接）]；\n2. 模型层面：[在特征金字塔（FPN）中新增小目标专用检测头，使用更大的锚框尺度]；\n3. 损失层面：[对小目标分配更高的损失权重，使用CIoU损失函数]；\n效果：小目标mAP提升至[81%]，整体mAP提升至[79%]。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '图像分割边缘优化', '如何解决语义分割中物体边缘模糊的问题？请分享你的实践经验。', '1. 对分割误差来源的分析；2. 边缘优化技术的应用；3. 结果的视觉效果', '项目场景：[自动驾驶场景的道路分割，边缘误差导致车道线识别不准确]；\n问题原因：[下采样丢失边缘细节，卷积操作的平滑效应]；\n解决方法：\n1. 模型改进：[在U-Net架构中加入边缘检测分支，与分割分支联合训练]；\n2. 后处理：[使用条件随机场（CRF）优化分割结果，细化边缘]；\n3. 数据增强：[添加边缘标注，增强边缘样本的训练权重]；\n效果：边缘像素准确率提升[25%]，道路边界定位误差从[10像素]降至[3像素]。'),
((SELECT position_id FROM positions WHERE position_name = '计算机视觉工程师'), '复杂场景鲁棒性提升', '如何让视觉模型在光照变化、遮挡等复杂场景下保持鲁棒性？', '1. 场景适应性策略的多样性；2. 数据覆盖的全面性；3. 模型泛化能力的设计', '应用场景：[超市货架商品识别，存在灯光变化、商品遮挡问题]；\n鲁棒性优化：\n1. 数据采集：[覆盖早中晚不同光照+不同遮挡程度（0-60%）的样本]；\n2. 预处理：[光照归一化（CLAHE算法）+动态阈值分割去除反光]；\n3. 模型：[使用注意力机制聚焦可见区域，加入场景自适应BatchNorm]；\n效果：复杂场景下识别准确率从[68%]提升至[92%]。'),

-- AI系统架构师
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '分布式训练架构设计', '如何设计一个支持100节点以上的大规模分布式训练系统？关键挑战和解决方案是什么？', '1. 对分布式训练原理的理解；2. 系统扩展性设计；3. 故障恢复机制', '设计要点：\n1. 架构选型：[参数服务器架构 vs 全规约架构（AllReduce）]，选择[全规约]，理由是[通信效率更高，适合大规模集群]；\n2. 关键挑战与解决：\n   - 通信瓶颈：[使用NVLink+InfiniBand网络，实现节点间高速互联]；\n   - 同步延迟：[混合同步策略，小批次异步更新，大批次同步聚合]；\n   - 故障恢复：[基于Checkpoint机制（每1000步保存模型）+弹性调度（节点故障时自动重新分配任务）]；\n3. 资源管理：[基于Kubernetes定制调度器，优先分配同机架节点，减少跨交换机通信]；\n效果：[在128节点集群上，模型训练速度比单机提升92%，故障恢复时间<5分钟]。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), 'AI模型服务化设计', '如何设计一个支持1000+QPS的AI模型在线推理服务？请说明关键组件和优化策略。', '1. 高并发服务设计；2. 模型推理优化；3. 弹性伸缩策略', '系统设计：\n1. 整体架构：[负载均衡层（Nginx）→服务层（TensorFlow Serving集群）→缓存层（Redis）→监控层（Prometheus+Grafana）]；\n2. 优化策略：\n   - 模型优化：[量化（FP16）+剪枝，推理速度提升3倍]；\n   - 并发处理：[异步请求处理+批处理（动态Batch），QPS提升200%]；\n   - 弹性伸缩：[基于请求量自动扩缩容（HPA），资源利用率提升60%]；\n3. 容灾方案：[多可用区部署+熔断降级（Sentinel），保障99.99%可用性]；\n效果：[单模型支持1200QPS，平均延迟<50ms，P99<100ms]。'),
((SELECT position_id FROM positions WHERE position_name = 'AI系统架构师'), '异构计算资源调度', '在包含GPU/TPU/FPGA的混合集群中，如何高效调度AI计算任务？', '1. 对不同硬件特性的理解；2. 调度算法的设计；3. 资源隔离策略', '调度系统设计：\n1. 资源抽象：[将各类硬件抽象为算力单元（CU），统一度量标准]；\n2. 任务分类：[训练任务（批处理）、推理任务（实时）、数据处理任务（CPU密集）]；\n3. 调度策略：\n   - 训练任务：[优先分配GPU/TPU，采用抢占式调度，利用碎片资源]；\n   - 推理任务：[基于QoS要求，分配专用FPGA/边缘GPU，保证低延迟]；\n   - 数据处理：[优先CPU节点，使用容器化隔离]；\n4. 优化：[基于历史数据的预测调度，提前预留资源应对高峰]；\n效果：[集群资源利用率从50%提升至85%，任务平均等待时间减少60%]。'),

-- 机器人算法工程师
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '复杂环境SLAM优化', '在动态环境（如人群密集场景）中，如何提高SLAM算法的定位精度？', '1. 对SLAM原理的理解；2. 动态环境适应性；3. 多传感器融合能力', '解决方案：\n1. 算法选择：[选择基于图优化的SLAM（如Cartographer/LIO-SAM），而非滤波方法，理由是图优化对动态点更鲁棒]；\n2. 动态点处理：\n   - 检测：[基于光流法检测运动区域，计算像素运动一致性]；\n   - 剔除：[将动态点标记为outlier，不参与地图构建]；\n3. 多传感器融合：[激光雷达+视觉+IMU融合，视觉提供纹理特征，激光提供几何约束]；\n4. 回环检测：[加入语义信息（如物体类别）辅助回环，减少动态物体干扰]；\n效果：[在人流量50人/分钟的场景中，定位误差从2米降至0.3米，地图构建成功率从60%提升至95%]。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '机器人路径规划策略', '在存在动态障碍物（如移动的人）的环境中，如何设计机器人的实时路径规划算法？', '1. 路径规划算法的选择；2. 动态避障能力；3. 计算效率与安全性的平衡', '算法设计：\n1. 分层规划：\n   - 全局规划：[A*算法生成初始路径，考虑静态障碍物]；\n   - 局部规划：[采用TEB（Timed Elastic Band）算法，实时调整路径避开动态障碍物]；\n2. 动态障碍物预测：[基于卡尔曼滤波器预测障碍物运动轨迹，预测未来3秒位置]；\n3. 约束条件：[速度约束（<1m/s）、加速度约束（<0.5m/s²）、安全距离（≥0.5m）]；\n4. 优化目标：[路径最短+平滑度+避障安全性的加权优化]；\n效果：[在动态障碍物速度≤0.8m/s的场景下，避障成功率98%，平均路径延迟<100ms]。'),
((SELECT position_id FROM positions WHERE position_name = '机器人算法工程师'), '多机器人协作控制', '如何实现5台以上机器人在同一空间的协作任务（如仓库货物搬运）？', '1. 协作架构的设计；2. 资源分配策略；3. 冲突解决机制', '系统设计：\n1. 架构选择：[分布式架构 vs 集中式架构]，选择[分布式+中央调度]，理由是[容错性好且可扩展性强]；\n2. 任务分配：[基于拍卖机制的任务分配，机器人根据自身状态（电量、负载）竞拍任务]；\n3. 路径协调：\n   - 优先级：[按任务紧急程度分配优先级，高优先级机器人优先通行]；\n   - 冲突解决：[预测路径冲突点，低优先级机器人提前等待或绕行]；\n4. 通信机制：[基于ROS2的DDS通信，实现低延迟消息传递，通信频率≥10Hz]；\n效果：[5台机器人协作完成100个搬运任务，任务完成时间比单机器人减少75%，路径冲突率<5%]。'),

-- AI产品经理
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'AI产品落地路径规划', '如何将一个实验室中的AI模型（如图像识别算法）转化为面向企业客户的产品？请说明关键步骤。', '1. 产品化路径的设计；2. 客户需求的转化；3. 技术与业务的平衡', '产品化流程：\n1. 需求验证：[通过客户访谈（如制造业质检部门），明确核心需求是[金属表面缺陷检测，精度要求≥99%]]；\n2. 模型适配：\n   - 数据：[采集工业场景缺陷样本（10000+），标注20类常见缺陷]；\n   - 算法：[在实验室模型基础上，加入迁移学习，适应工业环境光照变化]；\n3. 产品形态设计：[设计为SaaS平台+边缘设备方案，客户可上传图片或接入生产线摄像头]；\n4. 商业化：[按检测次数收费，提供免费试用版（每月限100次检测）]；\n效果：[产品上线6个月，获得20家企业客户，月收入达50万元]。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'AI产品数据闭环设计', '如何设计AI产品的数据反馈闭环，持续提升模型性能？', '1. 数据收集策略；2. 标注流程管理；3. 迭代优化机制', '闭环设计：\n1. 数据收集：\n   - 用户行为：[记录用户对模型输出的修正（如人工审核时的标注调整）]；\n   - 异常案例：[自动捕获模型置信度<0.7的案例，标记为待验证]；\n2. 标注管理：\n   - 流程：[初级标注员标注→资深标注员审核→领域专家抽查]；\n   - 工具：[使用内部标注平台，支持半自动标注（预填充模型预测结果）]；\n3. 模型迭代：\n   - 周期：[每周一次小迭代（增量训练），每月一次大迭代（全量训练）]；\n   - 评估：[AB测试新旧模型，对比准确率、召回率等指标]；\n效果：[产品上线1年后，核心模型准确率从85%提升至93%，用户满意度提升40%]。'),
((SELECT position_id FROM positions WHERE position_name = 'AI产品经理'), 'AI产品伦理风险评估', '在开发一个人脸识别门禁系统时，如何评估并降低潜在的伦理风险？', '1. 伦理风险的识别；2. 风险控制措施；3. 合规性保障', '风险评估与控制：\n1. 风险识别：\n   - 隐私泄露：[人脸数据存储、传输过程中的泄露风险]；\n   - 偏见歧视：[对不同种族、性别识别准确率差异]；\n   - 滥用风险：[未经授权的监控和数据二次使用]；\n2. 控制措施：\n   - 隐私：[采用活体检测+数据脱敏（仅存储特征向量而非原始图像）+本地化存储]；\n   - 公平性：[使用平衡数据集训练，定期评估不同群体准确率差异]；\n   - 合规：[通过ISO 27001认证，签订数据使用协议，明确数据用途]；\n3. 用户控制：[提供数据删除按钮，用户可随时删除自己的人脸数据]；\n效果：[通过伦理设计，获得隐私保护认证，客户信任度提升60%]。');

-- 大数据领域岗位高频题型
INSERT INTO high_freq_questions (position_id, question_type_name, question_example, scoring_focus, answer_template) VALUES
-- 大数据开发工程师
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), 'Spark性能调优', '当Spark作业出现Shuffle阶段卡顿（耗时>1小时）时，你会从哪些方面进行优化？', '1. 对Shuffle原理的理解；2. 调优参数的针对性；3. 资源配置的合理性', '问题场景：[TPC-DS 100G数据集，GroupBy+Join操作，Shuffle写数据100GB]；\n优化方向：\n1. 参数调优：[spark.shuffle.file.buffer=64k→256k；spark.reducer.maxSizeInFlight=96m→256m]；\n2. 数据层面：[预聚合（map-side combine）+过滤无效数据，减少Shuffle数据量至40GB]；\n3. 资源层面：[Executor数量从5→10，每个Executor内存从4G→8G]；\n效果：Shuffle阶段耗时从[75分钟]降至[18分钟]。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '实时数据链路设计', '如何设计一个支持每秒10万条数据写入的实时数据处理链路？关键组件是什么？', '1. 链路架构的合理性；2. 高并发处理能力；3. 容错机制的设计', '业务需求：[电商实时交易数据，要求延迟<1秒，可靠性99.99%]；\n链路设计：\n1. 接入层：[Kafka（3副本，10分区），生产者使用批量发送+压缩]；\n2. 处理层：[Flink（并行度10），使用状态后端RocksDB，开启Checkpoint（间隔1分钟）]；\n3. 存储层：[HBase（预分区）+Redis（热点数据缓存）]；\n4. 监控层：[Flink Metrics+Kafka Lag监控+告警机制]；\n效果：峰值处理能力[15万条/秒]，平均延迟[300ms]，无数据丢失。'),
((SELECT position_id FROM positions WHERE position_name = '大数据开发工程师'), '数据倾斜解决方案', '在Hadoop/Spark处理中，如何识别并解决数据倾斜（如某节点处理90%数据）问题？', '1. 数据倾斜的诊断方法；2. 解决方案的针对性；3. 对性能的提升效果', '问题现象：[Spark作业中某Executor耗时1小时，其余10分钟，Shuffle Read数据倾斜比100:1]；\n诊断步骤：[查看Stage日志→定位倾斜Key→分析该Key数据量（占比80%）]；\n解决措施（针对热点Key）：\n1. [将热点Key拆分（添加随机前缀），分散到多个Reducer处理后再合并]；\n2. [对热点Key单独处理（广播小表Join）]；\n效果：各Executor耗时差异缩小至[12-15分钟]，总作业时间从[65分钟]降至[18分钟]。'),

-- 数据工程师（ETL）
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '复杂ETL流程设计', '如何设计一个处理多源异构数据（如关系型数据库、日志文件、API数据）的ETL流程？', '1. 数据源整合能力；2. 数据清洗策略；3. 流程监控与异常处理', '流程设计：\n1. 数据源适配：\n   - 关系型数据库：[使用Sqoop增量导入，基于时间戳抽取变化数据]；\n   - 日志文件：[Flume实时采集+正则表达式解析字段]；\n   - API数据：[编写自定义连接器，支持分页获取+限流控制]；\n2. 数据清洗：\n   - 质量校验：[空值检查、数据类型校验、业务规则校验（如年龄>0）]；\n   - 异常处理：[异常数据写入死信队列，记录错误日志]；\n3. 调度：[Airflow编排DAG，设置依赖关系，配置重试机制（失败重试3次）]；\n效果：[数据处理准时率99.8%，清洗后数据质量达标率99.9%]。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '海量历史数据迁移', '如何将PB级历史数据从传统数据仓库迁移到Hadoop集群？关键挑战和解决方案是什么？', '1. 大数据迁移策略；2. 数据一致性保障；3. 迁移效率优化', '迁移方案：\n1. 迁移策略：[采用“双写+比对”策略，迁移期间新旧系统同时写入，确保业务连续性]；\n2. 分阶段执行：\n   - 阶段1：[全量迁移历史数据（按时间倒序，优先迁移最近3年数据）]；\n   - 阶段2：[增量迁移（基于binlog/CDC捕获变化数据）]；\n   - 阶段3：[数据验证（比对新旧系统关键指标，差异率控制在0.01%以内）]；\n3. 优化措施：\n   - 并行：[100个并发任务，使用DistCp工具]；\n   - 压缩：[迁移前对数据进行Snappy压缩，减少传输量]；\n效果：[迁移PB级数据耗时30天，数据准确率100%，业务无感知]。'),
((SELECT position_id FROM positions WHERE position_name = '数据工程师（ETL）'), '实时ETL链路优化', '在实时ETL流程中，如何保证数据处理延迟<1秒且不丢数据？', '1. 低延迟技术选型；2. Exactly-once语义保障；3. 性能监控', '技术方案：\n1. 架构选择：[Kafka（消息队列）→Flink（流处理）→HBase（存储）]；\n2. 关键配置：\n   - Kafka：[acks=all，min.insync.replicas=2，确保消息不丢失]；\n   - Flink：[开启Checkpoint（间隔500ms），使用 RocksDB 状态后端，设置并行度=分区数]；\n   - 端到端：[使用Flink的TwoPhaseCommitSinkFunction，保证端到端Exactly-once]；\n3. 监控：[Prometheus监控各组件Metrics，设置延迟告警阈值（>500ms）]；\n效果：[平均延迟200ms，峰值延迟<800ms，7×24小时运行无数据丢失]。'),

-- 数据分析师
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '业务指标异常诊断', '当“日活跃用户数（DAU）”突然下降10%时，如何定位原因？请说明分析思路。', '1. 分析维度的全面性；2. 数据链路的严谨性；3. 与业务的结合度', '分析步骤：\n1. 确认数据准确性：[检查埋点日志→排除数据采集故障，确认异常真实存在]；\n2. 维度拆解：\n   - 时间维度：[小时级趋势，定位异常开始时间点（如凌晨2点）]；\n   - 用户维度：[新/老用户、用户等级、地域分布，发现某区域老用户下降显著]；\n   - 渠道维度：[排查该区域的主要渠道（如Android应用商店）是否异常]；\n3. 根因定位：[确认该区域Android版本更新后出现兼容性问题，导致老用户无法登录]；\n结论：[建议紧急回滚版本，24小时内DAU恢复至正常水平]。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), '用户行为转化分析', '如何分析用户从“浏览商品”到“完成购买”的转化漏斗流失原因？请举例说明。', '1. 漏斗拆解的逻辑性；2. 各环节流失的归因能力；3. 改进建议的可行性', '项目背景：[电商平台，浏览→加购→下单→支付的整体转化率8%，行业平均15%]；\n分析过程：\n1. 漏斗量化：[浏览→加购（25%）→下单（15%）→支付（21%）]，发现加购→下单流失最严重；\n2. 细分分析：[按商品类别（低价商品转化率20% vs 高价3%）、用户新老（老用户18% vs 新用户5%）]；\n3. 定性验证：[用户访谈+页面热力图，发现高价商品缺少评价、新用户支付流程复杂]；\n建议：[增加高价商品评价体系，新用户简化支付步骤（跳过地址填写默认值）]；\n效果：[整体转化率提升至12%]。'),
((SELECT position_id FROM positions WHERE position_name = '数据分析师'), 'AB测试设计实施', '如何设计一个验证“新推荐算法”效果的AB测试？关键注意事项是什么？', '1. 测试设计的科学性；2. 变量控制的严谨性；3. 结果解读的准确性', '测试目标：[验证新推荐算法能否提升用户点击率（CTR）]；\n设计要点：\n1. 分组：[随机分配用户，对照组（旧算法）10万用户，实验组（新算法）10万用户，确保用户特征一致]；\n2. 指标：[核心指标CTR，辅助指标（停留时长、人均点击数）]；\n3. 周期：[2周，覆盖完整用户行为周期]；\n4. 注意事项：[屏蔽其他活动干扰；确保样本量统计显著（预期CTR提升10%，需样本量8万）]；\n结果：[实验组CTR 5.2% vs 对照组4.5%，统计显著，建议全量上线]。'),

-- 商业智能（BI）分析师
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '复杂报表性能优化', '当BI报表查询响应时间超过10秒时，如何进行优化？', '1. 对数据库查询原理的理解；2. 多维优化策略；3. 实际效果验证', '优化步骤：\n1. 分析瓶颈：[使用Explain分析SQL执行计划，发现全表扫描+排序操作]；\n2. 优化措施：\n   - 索引：[添加复合索引（如date+category+amount），覆盖查询条件和排序字段]；\n   - 分区：[按日期分区，减少每次查询扫描的数据量]；\n   - 缓存：[对高频查询（如昨日报表）设置Redis缓存，有效期1小时]；\n3. 架构调整：[将实时性要求不高的报表迁移至数据集市（Data Mart）]；\n效果：[查询响应时间从12秒降至1.5秒，用户满意度提升70%]。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '数据可视化设计', '如何设计一组展示公司季度业绩的BI仪表盘？关键设计原则是什么？', '1. 数据可视化理论；2. 业务指标理解；3. 交互设计能力', '设计方案：\n1. 明确目标：[直观展示季度营收、成本、利润变化趋势及部门贡献]；\n2. 图表选型：\n   - 趋势：[折线图展示季度同比/环比变化]；\n   - 占比：[旭日图展示各部门收入占比]；\n   - 分布：[箱线图展示产品销量分布]；\n3. 交互设计：[支持下钻（从季度→月→日）、筛选（按部门/产品）、对比（同比/环比切换）]；\n4. 设计原则：[使用对比色区分关键指标，数据墨水比最大化，避免3D效果干扰]；\n效果：[管理层决策效率提升30%，关键指标理解准确率提升50%]。'),
((SELECT position_id FROM positions WHERE position_name = '商业智能（BI）分析师'), '业务预测模型构建', '如何构建一个预测未来3个月销售额的模型？需要考虑哪些因素？', '1. 预测算法选型；2. 特征工程能力；3. 模型评估方法', '建模流程：\n1. 数据准备：\n   - 历史数据：[3年销售额数据，按日/月聚合]；\n   - 特征：[时间特征（季节、节假日）、促销活动、竞品动态、经济指标]；\n2. 算法选择：[对比ARIMA、Prophet、LSTM模型，选择Prophet，理由是对季节性和节假日处理更好]；\n3. 评估验证：[使用滚动预测（Rolling Forecast），用前2年数据训练，预测第3年，误差率控制在8%以内]；\n4. 应用：[每月更新模型，输出未来3个月预测区间（置信度95%）]；\n效果：[预测准确率85%，帮助供应链优化库存水平，降低15%库存成本]。'),

-- 大数据运维工程师
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), 'Hadoop集群故障排查', '当Hadoop集群的NameNode出现频繁重启时，如何排查并解决问题？', '1. 对Hadoop架构的理解；2. 故障诊断流程；3. 系统调优能力', '排查步骤：\n1. 收集日志：[查看NameNode日志，发现“OutOfMemoryError”异常]；\n2. 分析内存使用：[使用Jstat监控JVM内存，发现Full GC频率过高（每分钟3次）]；\n3. 定位原因：\n   - 堆内存不足：[NameNode堆内存配置为8G，但集群规模扩大后元数据量增长3倍]；\n   - 垃圾回收策略不合理：[使用CMS收集器，不适合大内存场景]；\n4. 解决方案：\n   - 调整参数：[NameNode堆内存从8G→24G，改用G1收集器]；\n   - 优化元数据：[清理过期文件，合并小文件]；\n效果：[Full GC频率降至每小时1次，NameNode稳定运行超过3个月]。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '集群容量规划', '如何为一个日增1TB数据的电商平台规划Hadoop集群规模？', '1. 容量评估方法；2. 硬件选型策略；3. 扩展性设计', '规划方案：\n1. 数据增长预估：\n   - 当前数据量：[500TB]，日增量：[1TB]，年增长率：[50%]；\n   - 3年预估：[500TB + 1TB×365×3×1.5 = 2.1PB]；\n2. 硬件配置：\n   - DataNode：[每节点12×16TB HDD + 2×1.6TB SSD，配置64核CPU + 256GB RAM，共100节点]；\n   - NameNode：[双机热备，每节点24核CPU + 1TB RAM]；\n3. 存储策略：[HDFS副本系数3，启用Erasure Coding（RS-6-3）存储冷数据，节省50%空间]；\n4. 扩展性：[预留30%硬件资源，支持在线扩缩容]；\n效果：[集群可支撑3年数据增长，硬件成本降低20%]。'),
((SELECT position_id FROM positions WHERE position_name = '大数据运维工程师'), '自动化部署方案', '如何实现Hadoop/Spark集群的自动化部署和配置管理？', '1. 自动化工具选型；2. 部署流程设计；3. 配置管理策略', '技术方案：\n1. 工具链：[Ansible（部署）+ SaltStack（配置管理）+ Docker（容器化）+ Kubernetes（编排）]；\n2. 部署流程：\n   - 基础环境：[Ansible执行系统初始化（防火墙、内核参数、NTP）]；\n   - 组件安装：[Docker打包Hadoop/Spark组件，Kubernetes部署到集群]；\n   - 配置管理：[SaltStack集中管理配置文件，支持灰度发布]；\n3. 监控告警：[Prometheus监控集群指标，Grafana可视化，告警阈值动态调整]；\n效果：[集群部署时间从3天缩短至4小时，配置变更成功率从85%提升至99%]。'),

-- 数据安全工程师
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '敏感数据保护方案', '如何设计一个保护用户个人信息（如身份证号、手机号）的安全方案？', '1. 数据安全技术；2. 合规性考量；3. 全生命周期防护', '保护方案：\n1. 数据分类分级：[将数据分为公开/内部/敏感/核心敏感，用户个人信息属于核心敏感]；\n2. 防护措施：\n   - 存储：[透明加密（TDE）+字段级加密（AES-256），密钥定期轮换]；\n   - 传输：[HTTPS强制加密，API接口双向认证]；\n   - 使用：[脱敏处理（手机号显示前3位+后4位），关键操作审计日志]；\n3. 合规：[符合GDPR/等保2.0要求，数据跨境传输做匿名化处理]；\n效果：[敏感数据泄露风险降低90%，通过第三方安全审计]。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据访问权限管控', '如何设计一个精细化的数据访问权限控制系统，防止越权访问？', '1. 权限模型设计；2. 技术实现方案；3. 审计与监控', '系统设计：\n1. 权限模型：[基于RBAC+ABAC混合模型，角色（如分析师/管理员）+属性（数据敏感度/访问时间）]；\n2. 实现方案：\n   - 数据源层：[Hive Metastore ACL控制表级访问]；\n   - SQL层：[Apache Sentry实现列级权限]；\n   - 应用层：[自定义拦截器，基于用户上下文动态过滤数据]；\n3. 审计：[记录所有数据访问行为，对异常访问（如凌晨访问）实时告警]；\n效果：[权限违规事件下降85%，审计响应时间从24小时缩短至5分钟]。'),
((SELECT position_id FROM positions WHERE position_name = '数据安全工程师'), '数据泄露应急响应', '当发现用户数据泄露事件时，应采取哪些应急措施？', '1. 应急响应流程；2. 技术处置手段；3. 合规处理要求', '应急响应方案：\n1. 事件确认：[验证泄露真实性，评估影响范围（如10万用户数据泄露）]；\n2. 应急处理：\n   - 阻断：[立即切断泄露源（如封禁异常IP）]；\n   - 保护：[对剩余数据紧急加密，提升访问权限级别]；\n   - 取证：[备份相关日志，保留证据链]；\n3. 后续措施：\n   - 通知：[按法规要求72小时内通知监管机构和受影响用户]；\n   - 补偿：[提供身份保护服务，如免费信用监控]；\n   - 改进：[漏洞修复+安全加固，定期演练应急流程]；\n效果：[将数据泄露影响降到最低，未引发重大声誉损失]。');

-- 物联网领域岗位高频题型
INSERT INTO high_freq_questions (position_id, question_type_name, question_example, scoring_focus, answer_template) VALUES
-- 物联网工程师
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '多协议设备通信集成', '如何实现支持MQTT、LoRaWAN、ZigBee三种协议的物联网设备互联互通？', '1. 协议转换逻辑设计；2. 网关架构合理性；3. 通信稳定性保障', '解决方案：\n1. 网关设计：[采用模块化网关架构，每种协议对应独立接入模块，核心层统一数据格式（JSON）]；\n2. 转换策略：\n   - 数据上行：[LoRaWAN/ZigBee数据经网关解析后转为MQTT消息上传云端]；\n   - 指令下行：[云端MQTT指令经网关转换为对应协议指令下发设备]；\n3. 冲突处理：[设置优先级（ZigBee实时指令 > LoRaWAN数据上报），避免信道冲突]；\n4. 稳定性优化：[添加心跳检测+断线重连机制，通信成功率≥99.5%]；\n效果：[实现100+种设备跨协议通信，平均延迟<200ms]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '低功耗设备续航优化', '如何延长电池供电的物联网设备（如智能水表）的续航时间至5年以上？', '1. 功耗分析深度；2. 软硬件协同优化能力；3. 实际续航数据支撑', '优化方案：\n1. 硬件选型：[选用低功耗MCU（如STM32L0系列，待机电流<1uA）+休眠型传感器]；\n2. 通信策略：\n   - 周期：[默认每小时唤醒一次上报数据，异常时触发即时上报]；\n   - 传输：[LoRa调制参数优化（扩频因子SF=12，降低发射功率至14dBm）]；\n3. 软件优化：[深度休眠模式（仅保留RTC时钟），唤醒后快速完成数据处理与传输]；\n4. 电源管理：[采用两节AA电池（3V）+低功耗LDO，电压跌落至2.4V仍可正常工作]；\n效果：[实测续航6.2年，远超5年设计目标]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网工程师'), '设备固件远程升级', '如何设计物联网设备的OTA升级方案，确保升级过程中不出现设备变砖？', '1. 升级流程完整性；2. 容错机制设计；3. 版本管理能力', 'OTA方案：\n1. 升级架构：[采用“云端→网关→设备”三级推送，支持断点续传]；\n2. 安全验证：[固件包数字签名（RSA2048）+设备身份认证，防止恶意固件]；\n3. 容错机制：\n   - 双分区：[设备划分为A/B两个固件分区，升级失败自动回滚至A区]；\n   - 心跳检测：[升级过程中每30秒发送心跳，超时未响应则重启设备]；\n4. 灰度策略：[按设备批次（10%→50%→100%）推送，实时监控升级成功率]；\n效果：[累计升级10万台设备，成功率99.8%，变砖率0.01%]。'),

-- 嵌入式系统开发工程师
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '实时任务调度优化', '在RTOS中如何处理10个以上周期性任务的调度，确保高优先级任务响应时间<10ms？', '1. 任务调度算法理解；2. 优先级设计合理性；3. 中断处理策略', '调度方案：\n1. 任务分类：[按优先级分为3级：紧急（<10ms，如传感器数据采集）、常规（100ms，如数据处理）、低优（1s，如日志上传）]；\n2. 算法选择：[采用抢占式调度+时间片轮转，紧急任务可抢占常规任务]；\n3. 优化措施：\n   - 栈空间：[为每个任务分配独立栈空间，避免栈溢出]；\n   - 中断管理：[紧急任务通过中断唤醒，中断服务程序（ISR）仅做标记，处理在任务层完成]；\n   - 避免阻塞：[高优任务不调用阻塞API，使用信号量/事件标志组同步]；\n效果：[高优先级任务响应时间稳定在5-8ms，CPU利用率控制在70%以内]。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '硬件驱动兼容性开发', '如何开发兼容3种不同型号传感器的SPI驱动程序？', '1. 驱动架构设计；2. 寄存器抽象能力；3. 错误处理机制', '驱动设计：\n1. 分层架构：[硬件抽象层（HAL）+设备驱动层，HAL封装SPI总线操作]；\n2. 适配策略：\n   - 寄存器映射：[为每种传感器创建寄存器映射表（地址+功能），通过宏定义切换]；\n   - 初始化参数：[设计通用初始化结构体，包含采样率、精度等可配置参数]；\n3. 兼容性处理：[添加设备ID识别逻辑，上电时自动检测传感器型号并加载对应驱动]；\n4. 健壮性：[每次SPI通信添加CRC校验，错误时自动重试（最多3次）]；\n效果：[单驱动程序支持3种传感器，代码复用率提升60%，通信错误率<0.1%]。'),
((SELECT position_id FROM positions WHERE position_name = '嵌入式系统开发工程师'), '嵌入式内存优化', '当嵌入式系统出现内存泄漏导致程序崩溃时，如何定位并解决问题？', '1. 内存调试工具使用；2. 泄漏分析方法；3. 长期稳定性保障', '排查方案：\n1. 工具选型：[使用Valgrind（仿真环境）+内存池监控（实际设备）定位泄漏点]；\n2. 分析步骤：\n   - 监控：[在malloc/free处添加钩子函数，记录内存分配/释放地址和调用栈]；\n   - 定位：[对比内存快照，发现周期性任务中未释放的缓冲区（每次泄漏128字节）]；\n   - 根因：[动态申请的JSON解析缓冲区在异常分支未释放]；\n3. 解决措施：\n   - 修复：[使用RAII机制自动释放资源，异常时触发析构函数]；\n   - 预防：[改用静态内存池（大小固定），限制最大分配量]；\n效果：[内存使用稳定，连续运行30天无泄漏，崩溃率降为0]。'),

-- 传感器工程师
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器精度校准', '如何校准工业压力传感器，使其测量误差从±2%降至±0.5%以内？', '1. 校准流程设计；2. 环境补偿能力；3. 数据拟合精度', '校准方案：\n1. 设备准备：[标准压力源（精度±0.05%）+恒温箱（控制温度25±0.5℃）]；\n2. 校准步骤：\n   - 多点校准：[在0-100kPa范围内均匀选取8个校准点，每个点采集20组数据]；\n   - 线性拟合：[使用最小二乘法计算拟合直线，生成校准系数（斜率+截距）]；\n   - 温度补偿：[在-10℃、25℃、60℃三个温度点重复校准，建立温度补偿模型]；\n3. 验证：[用10个验证点测试，计算误差并调整，直至所有点误差<0.5%]；\n效果：[校准后传感器测量误差稳定在±0.3%，满足工业级要求]。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器信号噪声抑制', '如何处理加速度传感器的高频噪声，提高振动监测精度？', '1. 噪声分析能力；2. 滤波算法选择；3. 实时性与精度平衡', '降噪方案：\n1. 噪声分析：[通过频谱分析确定噪声主要分布在1kHz以上高频段，信号频率50-500Hz]；\n2. 滤波设计：\n   - 硬件：[在传感器输出端添加RC低通滤波器（截止频率800Hz）]；\n   - 软件：[实现二阶巴特沃斯数字滤波器，通过滑动窗口平滑处理]；\n   - 自适应：[设计噪声阈值，当噪声超过阈值时自动提高滤波阶数]；\n3. 验证：[对比滤波前后的振动波形，计算信噪比（SNR）从20dB提升至45dB]；\n效果：[振动峰值测量误差从±5%降至±1%，满足设备故障预警需求]。'),
((SELECT position_id FROM positions WHERE position_name = '传感器工程师'), '传感器数据融合算法', '如何融合加速度传感器和陀螺仪数据，提高设备姿态测量精度？', '1. 融合算法原理；2. 误差补偿策略；3. 动态响应性能', '融合方案：\n1. 算法选择：[采用卡尔曼滤波（KALMAN Filter）融合，加速度计提供静态姿态参考，陀螺仪提供动态角速度]；\n2. 实现细节：\n   - 状态模型：[定义姿态角（roll/pitch/yaw）+角速度为状态变量，加速度计/陀螺仪数据为观测值]；\n   - 噪声矩阵：[动态调整过程噪声Q和观测噪声R，静态时增大加速度计权重]；\n   - 漂移补偿：[每10秒用加速度计数据校准陀螺仪漂移，消除累积误差]；\n3. 优化：[加入磁力计数据修正航向角（yaw），解决长时间漂移问题]；\n效果：[姿态测量误差从5°降至0.5°，动态响应延迟<10ms]。'),

-- 物联网解决方案架构师
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '大规模设备接入架构设计', '如何设计支持100万台设备接入的物联网平台架构？', '1. 架构扩展性设计；2. 负载均衡策略；3. 高可用保障', '架构设计：\n1. 整体架构：[采用“接入层→处理层→存储层→应用层”微服务架构，基于K8s容器化部署]；\n2. 接入层优化：\n   - 多集群：[按地域划分3个接入集群，每个集群支持40万台设备]；\n   - 协议网关：[MQTT网关集群（支持QoS 0/1），每节点并发连接≥10万]；\n   - 负载均衡：[基于设备ID哈希分片，确保设备连接稳定映射到固定节点]；\n3. 高可用设计：\n   - 冗余：[核心组件3副本部署，跨可用区部署避免单点故障]；\n   - 限流：[每设备每秒消息数≤10条，突发流量通过消息队列缓冲]；\n效果：[平台稳定支持120万台设备接入，消息处理成功率99.99%， downtime<1小时/年]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '工业物联网安全架构设计', '如何设计工业物联网（IIoT）的安全架构，防止生产网络被入侵？', '1. 安全域划分；2. 纵深防御策略；3. 合规性考量', '安全方案：\n1. 域隔离：[划分OT区（生产设备）、DMZ区（边缘网关）、IT区（平台），各区之间部署防火墙]；\n2. 分层防护：\n   - 设备层：[固件签名验证+设备身份证书（X.509），禁止未认证设备接入]；\n   - 通信层：[OT区用OPC UA over TLS，IT区用MQTT+SSL，所有通信加密]；\n   - 应用层：[基于角色的访问控制（RBAC），操作日志审计留存6个月]；\n3. 异常防护：[部署工业防火墙，白名单机制限制通信端口和协议，检测异常报文]；\n效果：[通过IEC 62443认证，拦截率100%，未发生安全入侵事件]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网解决方案架构师'), '物联网数据中台设计', '如何设计物联网数据中台，实现设备数据的统一管理和价值挖掘？', '1. 数据模型设计；2. 存储分层策略；3. 服务化能力', '中台架构：\n1. 数据模型：[采用“设备孪生”模型，包含静态属性（型号/厂商）、动态属性（实时状态）、事件（故障报警）]；\n2. 存储分层：\n   - 实时层：[Redis存储秒级实时数据，TTL=1小时]；\n   - 历史层：[时序数据库（InfluxDB/TimescaleDB）存储分钟级聚合数据，保留1年]；\n   - 归档层：[对象存储（S3）存储原始数据，按设备ID分区，保留5年]；\n3. 服务化：[封装数据API（查询/订阅）、分析服务（异常检测）、可视化服务（仪表盘）]；\n效果：[支持10万+设备数据接入，数据查询响应<500ms，数据分析效率提升40%]。'),

-- 边缘计算工程师
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘节点资源调度', '如何在边缘节点（如算力受限的工业网关）上调度3个以上AI推理任务？', '1. 资源隔离能力；2. 任务优先级设计；3. 算力分配策略', '调度方案：\n1. 资源抽象：[将CPU（ARM Cortex-A53）、内存（2GB）、存储（16GB）抽象为可量化资源单元]；\n2. 任务分类：\n   - 高优：[设备故障检测（YOLO轻量版，占40%CPU），响应时间<100ms]；\n   - 中优：[能耗分析（线性回归，占20%CPU），周期1分钟]；\n   - 低优：[日志分析（词袋模型，占10%CPU），后台异步执行]；\n3. 调度策略：[基于Linux cgroups实现资源隔离，高优任务可抢占低优任务资源]；\n4. 动态调整：[当CPU利用率>80%时，自动降低低优任务频率]；\n效果：[所有任务均满足时间约束，资源利用率提升至75%，无任务超时]。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘与云端协同', '如何设计边缘节点与云端的数据协同策略，平衡实时性与数据完整性？', '1. 数据分级能力；2. 协同机制设计；3. 断网容错处理', '协同方案：\n1. 数据分级：\n   - 边缘级：[实时控制数据（如设备指令），本地处理不上传]；\n   - 边缘优先：[异常数据（如故障报警），本地处理后立即上传]；\n   - 云端级：[统计数据（如日运行报表），定时（每小时）批量上传]；\n2. 同步机制：[基于MQTT QoS 1协议，边缘维护未同步数据队列，网络恢复后自动续传]；\n3. 冲突解决：[采用“边缘时间戳+版本号”机制，云端以最新版本为准，保留历史记录]；\n效果：[断网时边缘可独立运行48小时，网络恢复后数据同步成功率99.9%]。'),
((SELECT position_id FROM positions WHERE position_name = '边缘计算工程师'), '边缘AI模型轻量化', '如何将500MB的CNN模型部署到仅支持100MB内存的边缘设备？', '1. 模型压缩技术应用；2. 精度与性能平衡；3. 部署适配能力', '轻量化方案：\n1. 压缩策略：\n   - 量化：[FP32→INT8量化，模型体积减少75%（125MB），精度损失<1%]；\n   - 剪枝：[移除30%冗余卷积核，体积降至88MB，推理速度提升2倍]；\n   - 知识蒸馏：[用大模型指导小模型训练，保留关键特征提取能力]；\n2. 部署优化：[模型参数按页对齐存储，减少内存碎片化，加载时间从5s降至1s]；\n3. 验证：[在目标设备（ARM Cortex-A7）测试，推理耗时<200ms，满足实时性要求]；\n效果：[模型体积压缩82%，成功部署到边缘设备，精度保持在92%（原93%）]。'),

-- 物联网产品经理
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '物联网硬件产品定义', '如何定义一款面向农业大棚的温湿度监测设备？需考虑哪些关键因素？', '1. 需求转化能力；2. 技术与成本平衡；3. 场景适配性', '产品定义：\n1. 核心需求：[基于农户访谈，明确核心需求为“远程监测（±0.5℃精度）、低维护（电池续航2年）、耐高湿（95%RH）”]；\n2. 技术参数：\n   - 硬件：[SHT30传感器（精度±0.3℃）+LoRa模块（传输距离3km）+2节AA电池]；\n   - 软件：[支持远程校准、低电量报警、数据加密传输]；\n3. 成本控制：[BOM成本控制在50元以内，采用批量采购降低传感器成本]；\n4. 场景适配：[IP65防护等级，支持-30℃~70℃工作温度，防农药腐蚀外壳]；\n效果：[产品上市后3个月销量5000台，用户满意度92%，退货率<1%]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '物联网产品迭代策略', '如何制定物联网设备的迭代路线图？需平衡硬件更新与用户成本。', '1. 迭代规划能力；2. 兼容性设计；3. 用户价值评估', '迭代策略：\n1. 版本划分：\n   - 硬件版：[1.5年一次大迭代（如V1→V2），兼容旧配件]；\n   - 固件版：[3个月一次小迭代，通过OTA推送，新增功能/修复漏洞]；\n2. 兼容性保障：[硬件接口（如传感器接口）保持向后兼容，旧设备可升级核心模块]；\n3. 成本平衡：[推出“以旧换新”计划，折旧抵扣新设备费用，降低用户换机成本]；\n4. 迭代依据：[用户反馈（占60%）+技术趋势（占30%）+竞品分析（占10%）]；\n效果：[用户设备更新率提升40%，老用户留存率85%，新品毛利率维持在35%]。'),
((SELECT position_id FROM positions WHERE position_name = '物联网产品经理'), '物联网产品数据价值挖掘', '如何设计物联网设备的数据变现模式，避免单纯依赖硬件销售？', '1. 数据场景洞察；2. 商业模式设计；3. 隐私合规平衡', '变现方案：\n1. 数据分层：\n   - 基础层：[设备运行数据（免费，含在硬件售价中）]；\n   - 增值层：[分析报告（如能耗优化建议，按次收费）]；\n   - 定制层：[行业解决方案（如农业大棚增产方案，年度订阅）]；\n2. 商业模式：[硬件+服务（HaaS），硬件平价销售，服务收入占比60%]；\n3. 隐私保障：[用户授权后才采集数据，数据匿名化处理（去除设备标识）]；\n4. 落地案例：[为食品厂提供冷链监测设备+温度异常预警服务，年费200元/台]；\n效果：[服务收入占比从10%提升至55%，用户LTV（生命周期价值）提升3倍]。');

-- 软件开发领域岗位高频题型
INSERT INTO high_freq_questions (position_id, question_type_name, question_example, scoring_focus, answer_template) VALUES
-- 前端开发工程师
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '框架性能优化', '如何优化React应用的渲染性能？当列表渲染超过1000条数据时如何避免卡顿？', '1. 对虚拟DOM原理的理解；2. 优化策略的针对性；3. 实际性能指标提升', '优化方案：\n1. 列表渲染优化：\n   - 虚拟列表：[使用react-window实现可视区域渲染，仅渲染当前窗口30条数据]；\n   - 稳定key：[使用唯一ID作为key，避免每次渲染重建DOM]；\n2. 组件优化：\n   - 懒加载：[React.lazy+Suspense拆分组件，非首屏组件按需加载]；\n   - 记忆化：[useMemo缓存计算结果，useCallback缓存事件处理函数]；\n3. 渲染优化：[避免不必要的重渲染，使用shouldComponentUpdate/PureComponent]；\n效果：[1000条数据列表渲染时间从800ms降至120ms，滚动帧率保持60fps]。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '跨端适配方案', '如何设计同时兼容PC端、平板和手机的响应式布局？关键适配点是什么？', '1. 适配策略的完整性；2. 设备特性的利用；3. 交互一致性保障', '适配方案：\n1. 布局系统：[采用CSS Grid+Flexbox混合布局，基于12列网格系统设计]；\n2. 断点设计：[设置3个关键断点：360px（手机）、768px（平板）、1200px（PC）]；\n3. 组件适配：\n   - 导航栏：[PC端水平导航，移动端折叠为汉堡菜单]；\n   - 数据表格：[PC端完整表格，移动端转为卡片列表+下拉详情]；\n   - 表单控件：[移动端增大点击区域（≥44px），优化触摸体验]；\n4. 图片适配：[使用srcset+size加载不同分辨率图片，WebP格式节省带宽]；\n效果：[全端适配覆盖率100%，各设备交互一致性评分92%]。'),
((SELECT position_id FROM positions WHERE position_name = '前端开发工程师'), '前端安全防护', '如何防范XSS攻击和CSRF攻击？请结合实际场景说明。', '1. 对攻击原理的理解；2. 防护措施的全面性；3. 工程化防护能力', '防护方案：\n1. XSS防护：\n   - 输入过滤：[使用DOMPurify净化用户输入的HTML内容]；\n   - 输出编码：[React自动转义文本，避免dangerouslySetInnerHTML滥用]；\n   - 安全策略：[设置Content-Security-Policy（CSP），限制脚本来源]；\n2. CSRF防护：\n   - 令牌验证：[请求头携带CSRF Token，后端验证有效性]；\n   - 同源检查：[验证Referer/Origin字段，拒绝跨域非法请求]；\n3. 工程化保障：[ESLint配置security插件，自动检测不安全API使用]；\n效果：[上线后未发生安全漏洞，渗透测试防护评分95分]。'),

-- UI/UX设计师
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '用户旅程地图设计', '如何为电商APP设计"商品从浏览到下单"的用户旅程地图？关键触点是什么？', '1. 用户场景的完整性；2. 痛点识别的准确性；3. 设计方案的针对性', '设计流程：\n1. 场景拆解：[将旅程分为5个阶段：发现商品→查看详情→加入购物车→填写地址→支付完成]；\n2. 痛点分析：\n   - 关键痛点：[详情页加载慢、地址填写繁琐、支付步骤多]；\n   - 情绪曲线：[绘制用户情绪波动图，识别最低谷（支付失败）]；\n3. 优化方案：\n   - 详情页：[预加载+骨架屏，加载时间从3s→1s]；\n   - 地址：[智能推荐常用地址，减少3个输入步骤]；\n   - 支付：[保存支付方式，一键支付，步骤从4步→2步]；\n效果：[用户下单转化率提升28%，平均下单时间缩短40%]。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '交互设计逻辑', '如何设计复杂表单（如保险投保表单）的交互流程，降低用户填写错误率？', '1. 信息架构的合理性；2. 引导设计的有效性；3. 错误处理的友好性', '设计方案：\n1. 分步设计：[将15项内容分为3步（基本信息→健康信息→投保确认），每步不超过5项]；\n2. 智能引导：\n   - 实时校验：[输入时即时提示格式错误（如身份证号）]；\n   - 示例提示：[在输入框下方提供格式示例（如"YYYY-MM-DD"）]；\n   - 帮助入口：[关键项旁添加"?"图标，点击显示详细说明]；\n3. 错误处理：[错误提示文字具体（如"请填写正确的手机号，需11位数字"），定位到对应字段]；\n效果：[用户填写错误率从35%降至8%，表单完成率提升52%]。'),
((SELECT position_id FROM positions WHERE position_name = 'UI/UX设计师'), '设计系统构建', '如何构建一套企业级设计系统（Design System）？核心组成部分是什么？', '1. 系统架构的完整性；2. 组件设计的复用性；3. 团队协作的适配性', '系统构建：\n1. 核心组成：\n   - 设计语言：[定义色彩系统（主色/辅助色/功能色）、排版规则（字体/字号/行高）、图标库]；\n   - 组件库：[40+基础组件（按钮/输入框）+20+业务组件（订单卡片/支付弹窗）]；\n   - 规范文档：[组件用法、交互规则、动效参数，支持Figma+Web版本]；\n2. 落地保障：[设计插件自动检查规范一致性，开发组件库（React+Vue版本）]；\n3. 迭代机制：[每季度更新一次，收集设计师/开发反馈优化组件]；\n效果：[团队设计效率提升50%，UI一致性评分从65分→92分]。'),

-- 后端开发工程师
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '微服务拆分策略', '如何将单体电商系统拆分为微服务？拆分后如何解决服务间依赖问题？', '1. 拆分原则的理解；2. 服务边界的清晰度；3. 依赖治理的有效性', '拆分方案：\n1. 拆分维度：[按领域驱动设计（DDD）拆分，划分为5个核心服务：用户服务、商品服务、订单服务、支付服务、库存服务]；\n2. 边界定义：[通过限界上下文明确服务职责，如订单服务仅处理订单生命周期，不直接操作库存]；\n3. 依赖处理：\n   - 同步：[REST API调用（用户服务→订单服务），超时设置1s，重试2次]；\n   - 异步：[Kafka消息队列（订单创建→库存扣减），确保最终一致性]；\n   - 熔断：[使用Sentinel设置熔断阈值，服务异常时返回降级结果]；\n效果：[服务独立部署，发布频率从每月1次→每周3次，故障影响范围缩小80%]。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), '数据库高并发优化', '如何优化MySQL数据库，支持每秒1000+写操作（如秒杀场景）？', '1. 读写分离设计；2. 锁策略优化；3. 缓存分层设计', '优化方案：\n1. 架构调整：\n   - 读写分离：[1主2从，写主库，读从库，通过MyCat中间件路由]；\n   - 分库分表：[按用户ID哈希分表（8张表），减少单表数据量至1000万以内]；\n2. 锁优化：\n   - 行锁：[使用主键更新（WHERE id=?），避免表锁]；\n   - 乐观锁：[版本号机制（version字段）处理并发更新，减少锁等待]；\n3. 缓存策略：\n   - 多级缓存：[本地缓存（Caffeine）+分布式缓存（Redis），热点商品缓存10分钟]；\n   - 缓存预热：[秒杀前将商品库存加载至Redis，减少DB访问]；\n效果：[系统支持1500 TPS写入，响应时间<200ms，无数据不一致]。'),
((SELECT position_id FROM positions WHERE position_name = '后端开发工程师'), 'API接口设计规范', '如何设计RESTful API接口，确保其易用性、安全性和可扩展性？', '1. 规范的完整性；2. 安全性考量；3. 版本管理策略', '设计规范：\n1. 接口设计：\n   - 命名：[资源路径用名词复数（/users），动作通过HTTP方法表达（GET查询，POST创建）]；\n   - 参数：[URL路径传资源ID（/users/123），查询参数传过滤条件（?status=active）]；\n   - 响应：[统一格式（{code, msg, data}），分页响应固定包含total/page/size/list]；\n2. 安全设计：[Token认证（JWT），权限校验（RBAC），接口限流（IP+用户维度）]；\n3. 版本管理：[URL路径包含版本（/v1/users），兼容旧版本至v1停用后3个月]；\n效果：[接口文档可读性评分90分，第三方接入效率提升50%，无兼容性投诉]。'),

-- 全栈开发工程师
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '前后端协作流程', '如何优化全栈开发的前后端协作流程，减少联调时间？', '1. 协作工具的选型；2. 接口契约的规范性；3. 并行开发的效率', '协作方案：\n1. 工具链：[Swagger（API文档）+Mock Server（接口模拟）+GitLab CI（自动化测试）]；\n2. 流程设计：\n   - 阶段1：[前后端共同定义API契约（请求参数、响应格式），生成Swagger文档]；\n   - 阶段2：[前端基于Mock Server并行开发，后端实现接口，无需等待]；\n   - 阶段3：[联调时通过契约测试工具（Pact）自动验证接口一致性]；\n3. 自动化：[提交代码触发自动化测试，接口不符时即时告警]；\n效果：[联调时间从5天缩短至1天，接口问题率从30%降至5%]。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '技术栈选型决策', '为企业内部管理系统选择全栈技术栈时，需考虑哪些因素？如何平衡开发效率和维护成本？', '1. 选型维度的全面性；2. 团队适配性；3. 长期演进考量', '选型方案：\n1. 评估维度：[团队熟悉度、开发效率、性能需求、社区活跃度、学习成本]；\n2. 技术栈选择：\n   - 前端：[Vue3+Element Plus，理由：团队熟悉度高，组件丰富，开发效率快]；\n   - 后端：[Spring Boot+MyBatis-Plus，理由：稳定成熟，ORM简化CRUD]；\n   - 数据库：[MySQL+Redis，理由：适配业务复杂度，运维成本低]；\n3. 平衡策略：[优先选择团队熟悉的技术，预留20%时间学习新技术，关键模块做技术验证]；\n效果：[项目开发周期缩短25%，后期维护成本降低30%，团队满意度90%]。'),
((SELECT position_id FROM positions WHERE position_name = '全栈开发工程师'), '全栈性能瓶颈分析', '当全栈应用（如CRM系统）出现响应慢时，如何定位瓶颈在前端、后端还是数据库？', '1. 性能分析工具的使用；2. 瓶颈定位的逻辑性；3. 端到端优化能力', '分析流程：\n1. 分层排查：\n   - 前端：[Chrome DevTools分析：Network看接口耗时（<200ms正常），Performance看渲染耗时（长任务>50ms需优化）]；\n   - 后端：[APM工具（SkyWalking）看接口耗时分布，定位慢方法（如循环查询DB）]；\n   - 数据库：[Explain分析SQL执行计划，识别全表扫描、缺少索引等问题]；\n2. 案例解决：[某列表页慢：前端长任务（300ms）→优化Vue渲染；后端SQL慢（800ms）→添加复合索引；Redis缓存未命中→调整TTL]；\n效果：[页面加载时间从3.5s降至1.2s，用户操作响应速度提升60%]。'),

-- Android开发工程师
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), '内存泄漏排查', '如何定位并解决Android应用的内存泄漏问题？请举例说明。', '1. 工具使用能力；2. 泄漏场景的熟悉度；3. 解决方案的有效性', '排查方案：\n1. 工具链：[Android Profiler（内存监控）+LeakCanary（自动检测泄漏）+MAT（内存分析）]；\n2. 典型案例：\n   - 泄漏场景：[Activity销毁后被静态集合持有，导致无法回收]；\n   - 定位：[LeakCanary生成泄漏路径：MyApplication.sList → MainActivity]；\n   - 解决：[使用弱引用（WeakReference）存储Activity，或在onDestroy移除引用]；\n3. 预防措施：[编码规范禁止静态变量持有Context，使用Application Context而非Activity Context]；\n效果：[内存泄漏问题从5个降至0，应用OOM崩溃率从2%降至0.1%]。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), 'UI卡顿优化', '如何解决Android列表（RecyclerView）滑动卡顿问题？', '1. 渲染原理理解；2. 优化策略的全面性；3. 性能指标提升', '优化方案：\n1. 布局优化：\n   - 层级：[使用ConstraintLayout减少布局层级（从5层→2层），避免过度绘制]；\n   - 复用：[正确实现RecyclerView复用机制，避免每次创建ViewHolder]；\n2. 绘制优化：\n   - 图片：[使用Glide加载合适分辨率图片（如1080p图片压缩至720p），设置placeholder]；\n   - 动画：[属性动画（ObjectAnimator）替代视图动画，避免频繁触发measure/layout]；\n3. 线程优化：[异步加载数据（ViewModel+Coroutine），图片解码在子线程完成]；\n效果：[列表滑动帧率从30fps提升至55fps，卡顿次数从每100次滑动8次降至0次]。'),
((SELECT position_id FROM positions WHERE position_name = 'Android开发工程师'), '版本兼容性处理', '如何处理Android应用在不同版本（如Android 10→13）和机型上的兼容性问题？', '1. 版本特性的了解；2. 适配策略的合理性；3. 测试覆盖的全面性', '适配方案：\n1. 版本适配：\n   - Android 13：[请求通知权限（POST_NOTIFICATIONS），避免崩溃]；\n   - Android 11：[分区存储适配，使用MediaStore访问图片，不直接操作文件路径]；\n   - Android 10：[暗黑模式适配，定义day/night主题，支持系统自动切换]；\n2. 机型适配：\n   - 屏幕：[使用dp而非px，约束布局适配不同分辨率]；\n   - 厂商：[针对华为/小米定制功能（如推送通道），通过反射避免类找不到异常]；\n3. 测试保障：[使用Firebase Test Lab测试20+主流机型，覆盖Android 8-13版本]；\n效果：[兼容性问题从35个降至3个，市场占有率95%以上机型可正常运行]。'),

-- iOS开发工程师
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'ARC内存管理', '在iOS开发中，如何避免循环引用导致的内存泄漏？请结合block使用场景说明。', '1. 内存管理原理；2. 循环引用场景识别；3. 解决方案的规范性', '解决方案：\n1. 循环引用场景：[ViewController持有NetworkManager，NetworkManager的block回调又持有ViewController，形成闭环]；\n2. 解决措施：\n   - 弱引用：[在block外声明__weak typeof(self) weakSelf = self;，block内使用weakSelf]；\n   - 避免强引用：[block内如需self存活，可转为__strong typeof(weakSelf) strongSelf = weakSelf;但需确保不形成新闭环]；\n   - 其他场景：[NSTimer需在dealloc中invalidate，避免target被计时器持有]；\n3. 检测工具：[Xcode Instrument的Leaks工具定期检测，配合静态分析（Analyze）]；\n效果：[内存泄漏率从8%降至0.5%，应用内存占用降低30%]。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'UI渲染性能优化', '如何优化iOS应用的UI渲染性能，解决TableView滑动卡顿问题？', '1. 渲染流程理解；2. 优化策略的针对性；3. 性能指标提升', '优化方案：\n1. 布局优化：\n   - 减少计算：[在cellForRowAtIndexPath中避免复杂计算，提前缓存高度（estimatedRowHeight+rowHeight）]；\n   - 简化层级：[使用Auto Layout时减少约束数量（<10个/Cell），复杂布局改用纯代码]；\n2. 绘制优化：\n   - 图片：[使用Kingfisher异步加载+缓存，根据设备分辨率加载@2x/@3x图片]；\n   - 离屏渲染：[避免阴影（shadowPath替代）、圆角（layer.masksToBounds配合cornerRadius时需同设masksToBounds）]；\n3. 异步处理：[数据解析和图片解码在子线程完成，主线程只做UI更新]；\n效果：[滑动帧率从40fps提升至58fps，CPU占用率从70%降至30%]。'),
((SELECT position_id FROM positions WHERE position_name = 'iOS开发工程师'), 'App Store上架审核', '如何确保iOS应用通过App Store审核？常见被拒原因及解决方案是什么？', '1. 审核规则的熟悉度；2. 风险点的预判能力；3. 问题解决的效率', '审核策略：\n1. 常见被拒原因及解决：\n   - 隐私权限：[所有权限申请需说明用途（如"需要相机权限以拍摄头像"），不申请无关权限]；\n   - 支付问题：[虚拟商品必须使用IAP支付，不接入微信/支付宝直接支付]；\n   - 功能完整：[测试账号需有效，功能无crash，避免"测试版"描述]；\n2. 预审准备：\n   - 自查：[对照App Store审核指南自查30+项关键点，如内容分级、广告标识]；\n   - 测试：[TestFlight测试1周，覆盖iOS 15-16，iPhone/iPad机型]；\n3. 申诉技巧：[被拒后仔细阅读审核反馈，24小时内修改并提交申诉，附修改说明]；\n效果：[近5个版本均一次通过审核，审核时间从7天缩短至2天]。'),

-- 软件测试工程师
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '自动化测试框架设计', '如何设计一套Web自动化测试框架？关键组件和设计原则是什么？', '1. 框架架构的合理性；2. 可维护性设计；3. 扩展性考量', '框架设计：\n1. 核心组件：[基于Selenium+Python，包含5层：基础层（封装WebDriver）、页面对象层（PO模式）、测试用例层、数据驱动层（Excel/JSON）、报告层（Allure）]；\n2. 设计原则：\n   - 封装：[将常用操作（点击、输入）封装为公共方法，减少重复代码]；\n   - 数据分离：[测试数据与用例分离，支持多环境（dev/test/prod）配置]；\n   - 可扩展：[预留接口支持API测试、移动端测试集成]；\n3. 增强功能：[失败自动截图、重试机制（失败用例重试2次）、Jenkins持续集成]；\n效果：[自动化覆盖率从30%提升至80%，回归测试时间从5天缩短至1天]。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '性能测试场景设计', '如何设计电商APP的性能测试场景？需关注哪些关键指标？', '1. 场景设计的全面性；2. 指标选取的合理性；3. 瓶颈定位能力', '测试方案：\n1. 核心场景：\n   - 并发场景：[1000用户同时登录，500用户同时加入购物车]；\n   - 负载场景：[从100用户逐步增加至2000用户，观察系统瓶颈]；\n   - 耐久场景：[500用户持续操作8小时，检测内存泄漏/连接池耗尽]；\n2. 关键指标：\n   - 客户端：[启动时间（<3s）、页面响应（<2s）、崩溃率（<0.1%）]；\n   - 服务端：[接口响应（<500ms）、TPS（≥500）、错误率（<0.5%）、CPU/内存使用率（<80%）]；\n3. 工具链：[JMeter（接口性能）+Appium（客户端性能）+Prometheus（服务器监控）]；\n效果：[发现3个性能瓶颈（数据库连接池不足、Redis缓存穿透），优化后系统支持1500用户并发]。'),
((SELECT position_id FROM positions WHERE position_name = '软件测试工程师'), '缺陷定位与分析', '如何高效定位软件缺陷的根本原因？请结合一个复杂缺陷案例说明。', '1. 缺陷分析的逻辑性；2. 工具使用能力；3. 根因定位的准确性', '分析流程：\n1. 案例背景：[用户反馈"提交订单偶尔失败，无规律"，复现率30%]；\n2. 排查步骤：\n   - 表象：[前端提示"系统错误"，后端日志显示"数据库连接超时"]；\n   - 深入：[查看数据库监控，发现失败时刻连接数达最大值（100），连接未释放]；\n   - 根因：[代码中try-finally块未正确释放Connection，异常时连接泄漏]；\n3. 验证：[编写单元测试模拟并发场景，复现问题；修复后再次验证，连接数稳定在60以内]；\n4. 预防：[添加连接池监控告警，代码评审强制检查资源释放]；\n效果：[缺陷彻底修复，类似问题3个月内未再出现，平均缺陷定位时间缩短50%]。'),

-- 质量保证（QA）工程师
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '测试策略制定', '如何为一个大型电商平台制定完整的测试策略？需覆盖哪些测试类型？', '1. 测试类型的全面性；2. 与开发流程的结合；3. 风险控制的有效性', '策略设计：\n1. 测试类型覆盖：\n   - 功能测试：[单元测试（开发）、集成测试（QA）、系统测试（QA）、UAT（业务方）]；\n   - 非功能测试：[性能测试（JMeter）、安全测试（OWASP Top 10）、兼容性测试（多浏览器/设备）]；\n   - 专项测试：[支付流程测试、数据迁移测试、灾备演练]；\n2. 流程整合：[敏捷开发模式下，每轮Sprint（2周）包含：开发自测→自动化回归→探索性测试→Sprint评审]；\n3. 风险分级：[按影响范围（P0-P3）定义测试优先级，P0（支付功能）100%覆盖，P3（辅助功能）80%覆盖]；\n效果：[线上缺陷率从千分之5降至千分之1.2，用户投诉量减少70%]。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '质量度量体系建设', '如何建立软件质量度量体系？关键指标有哪些？', '1. 指标设计的科学性；2. 数据采集的客观性；3. 指标应用的有效性', '度量体系：\n1. 核心指标：\n   - 过程指标：[需求澄清率（≥90%）、代码评审覆盖率（≥80%）、单元测试覆盖率（≥70%）]；\n   - 产品指标：[缺陷密度（<0.5个/千行代码）、功能点通过率（≥95%）、用户满意度（≥4.5/5）]；\n   - 效率指标：[缺陷修复率（≥90%/周）、测试自动化率（≥60%）、发布周期（≤2周）]；\n2. 数据采集：[通过Jira（缺陷）、SonarQube（代码质量）、Jenkins（构建）自动采集，每周生成质量报告]；\n3. 应用机制：[指标异常时触发根因分析（如缺陷密度突增），将改进措施纳入下轮迭代]；\n效果：[质量指标可视化后，团队质量意识提升，过程改进措施落地率从40%→85%]。'),
((SELECT position_id FROM positions WHERE position_name = '质量保证（QA）工程师'), '敏捷开发质量保障', '在敏捷开发（Scrum）中，QA工程师如何平衡快速迭代和产品质量？', '1. 敏捷流程的理解；2. 质量活动的前置；3. 协作效率的提升', '保障策略：\n1. 测试左移：[需求阶段参与评审，提前识别模糊点；开发阶段编写自动化测试用例，与开发同步]；\n2. 迭代内质量控制：\n   - 每日站会：[同步测试进度和 blockers，及时解决依赖问题]；\n   - 持续测试：[每提交一次代码触发自动化测试，失败时阻断构建]；\n   - 探索性测试：[Sprint最后2天集中进行，聚焦高风险功能]；\n3. 技术手段：[自动化回归测试覆盖核心场景（80%），减少人工回归时间；可视化质量看板实时跟踪缺陷状态]；\n效果：[迭代周期从3周→2周，同时线上缺陷率保持稳定，团队交付信心提升]。'),

-- 项目经理
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '敏捷项目管理实践', '如何在10人以上团队中有效实施Scrum敏捷开发？关键挑战和解决方法是什么？', '1. 敏捷原则的理解；2. 团队协作的有效性；3. 敏捷 ceremonies 的执行质量', '实施方案：\n1. 团队结构：[划分为2个Scrum团队（6人+4人），各设Scrum Master，共享产品负责人（PO）]；\n2. 核心活动：\n   - Sprint规划：[8小时规划2周工作，明确可交付的 Sprint Goal，任务拆分为≤8小时的子任务]；\n   - 每日站会：[15分钟，每人汇报"昨天做了什么/今天计划/ blockers"，用物理看板可视化进度]；\n   - 评审与回顾：[评审会上演示可运行功能，回顾会识别3个改进点并分配负责人]；\n3. 挑战解决：\n   - 需求变更：[Sprint内拒绝非紧急变更，放入产品待办列表（Backlog）排序]；\n   - 进度滞后：[每日跟踪燃尽图，滞后时移除低优先级任务，而非延长工期]；\n效果：[团队交付频率从每月1次→每2周1次，需求响应速度提升60%，团队满意度85%]。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '项目风险管控', '如何识别和管理软件项目中的关键风险（如需求变更、资源不足）？请举例说明。', '1. 风险识别的全面性；2. 应对策略的有效性；3. 风险监控的持续性', '风险管理：\n1. 风险识别：[项目启动时组织风险研讨会，识别5类关键风险：需求风险（变更频繁）、资源风险（核心开发离职）、技术风险（新技术不成熟）、进度风险（工期紧张）、质量风险（测试不充分）]；\n2. 评估与应对：\n   - 高优风险（需求变更）：[制定变更管理流程（变更申请→影响评估→CCB审批），预留20%缓冲时间]；\n   - 中优风险（核心开发离职）：[知识共享（结对编程）+备份人员（A/B角），关键模块文档化]；\n3. 监控机制：[每周风险跟踪会，更新风险状态（可能性/影响），触发应对措施时及时执行]；\n效果：[项目关键风险发生概率从40%降至15%，风险影响范围缩小70%，项目按时交付率90%]。'),
((SELECT position_id FROM positions WHERE position_name = '项目经理'), '跨团队协作管理', '如何协调3个以上跨部门团队（如开发、设计、测试、运维）高效协作？', '1. 协作流程的清晰度；2. 沟通机制的有效性；3. 目标对齐的一致性', '协作方案：\n1. 目标对齐：[通过OKR统一目标，如"Q3末上线支付功能"，各团队目标与其关联（设计：8月中完成UI；开发：9月初完成编码）]；\n2. 流程设计：[基于价值流图设计协作流程，明确各环节输入/输出（如设计稿→开发接收标准→测试准入条件）]；\n3. 沟通机制：\n   - 同步：[每周跨团队评审会（1小时），同步进度和 blockers]；\n   - 异步：[共享项目管理工具（Jira），实时更新任务状态；Wiki维护决策记录]；\n   - 冲突解决：[明确升级路径，跨部门冲突24小时内由项目经理协调解决]；\n效果：[跨团队协作效率提升50%，信息传递误差率从25%降至5%，项目关键节点达成率95%]。');


