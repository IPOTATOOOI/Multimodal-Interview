package com.example.spr_swcup.service.Impl.questionBank;

import com.example.spr_swcup.dto.questionBank.*;
import com.example.spr_swcup.service.questionBank.QuestionBankService;
import com.example.spr_swcup.service.questionBank.Neo4jUtils;
import lombok.extern.slf4j.Slf4j;
import org.neo4j.driver.*;
import org.neo4j.driver.Record;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class QuestionBankServiceImpl implements QuestionBankService {

    @Autowired
    private Driver neo4jDriver;

    @Override
    public TopicsResponse getTopics(String rootCategoryName, String subCategoryName) {
        try {
            log.info("查询Topic: rootCategoryName={}, subCategoryName={}", rootCategoryName, subCategoryName);

            // 校验RootCategory和SubCategory是否存在
            if (!validateCategories(rootCategoryName, subCategoryName)) {
                throw new RuntimeException("RootCategory或SubCategory不存在");
            }

            // 查询SubCategory下所有Topic及题目数量
            String query = """
                MATCH (r:RootCategory {name: $root_name})-[:HAS_SUB]->(s:SubCategory {name: $sub_name})-[:CONTAINS_TOPIC]->(t:Topic)
                OPTIONAL MATCH (t)-[:INCLUDES]->(q:Question)
                WITH t, count(q) AS question_count
                RETURN t.id AS id, t.name AS name, question_count ORDER BY t.name ASC
                """;

            List<TopicDTO> topics = new ArrayList<>();

            try (Session session = neo4jDriver.session()) {
                Result result = session.run(query,
                        Values.parameters("root_name", rootCategoryName, "sub_name", subCategoryName));

                while (result.hasNext()) {
                    Record record = result.next();
                    TopicDTO topic = new TopicDTO();
                    topic.setId(record.get("id").asString());
                    topic.setName(record.get("name").asString());
                    // 处理question_count字段，Neo4j返回Long类型
                    topic.setQuestionCount((int) record.get("question_count").asLong());
                    topics.add(topic);
                }
            }

            TopicsResponse response = new TopicsResponse();
            response.setTopics(topics);

            log.info("查询Topic成功: count={}", topics.size());
            return response;

        } catch (Exception e) {
            String errorMsg = "查询Topic失败: " + e.getMessage();
            log.error(errorMsg, e);
            throw new RuntimeException(errorMsg);
        }
    }

    @Override
    public QuestionsResponse getQuestionsByTopic(String topicId) {
        try {
            log.info("查询Question: topicId={}", topicId);

            // Cypher: 随机15题，带Tag和KnowledgePoint，只取前5个标签
            String query = """
                MATCH (t:Topic {id: $topic_id})-[:INCLUDES]->(q:Question)
                OPTIONAL MATCH (q)-[:MARKED_AS]->(tag:Tag)
                OPTIONAL MATCH (q)-[:TESTS]->(kp:KnowledgePoint)
                WITH q, collect(DISTINCT tag) AS allTags, collect(DISTINCT kp) AS kps
                WITH q, allTags[0..5] AS tags, kps
                WITH q, tags, kps ORDER BY rand() LIMIT 15
                RETURN
                  q.id            AS id,
                  q.title         AS title,
                  q.content       AS content,
                  q.choice        AS choice,
                  q.type          AS type,
                  q.difficulty    AS difficulty,
                  q.answer        AS answer,
                  [tag IN tags | {id: tag.id, name: tag.name}]                    AS tags,
                  [kp  IN kps  | {id: kp.id,   name: kp.name, level: kp.level}] AS knowledge_points
                """;

            List<QuestionDTO> questions = new ArrayList<>();

            try (Session session = neo4jDriver.session()) {
                Result result = session.run(query, Values.parameters("topic_id", topicId));

                while (result.hasNext()) {
                    Record record = result.next();
                    QuestionDTO question = new QuestionDTO();
                    question.setId(record.get("id").asString());
                    question.setTitle(record.get("title").asString());
                    question.setContent(record.get("content").asString());
                    question.setChoice(record.get("choice").asString());
                    question.setType(record.get("type").asString());
                    question.setDifficulty(record.get("difficulty").asString());
                    question.setAnswer(record.get("answer").asString());

                                        // 处理tags
                    List<TagDTO> tags = new ArrayList<>();
                    List<Object> tagValues = record.get("tags").asList();
                    for (Object tagValue : tagValues) {
                        if (tagValue instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> tagMap = (Map<String, Object>) tagValue;
                            TagDTO tag = new TagDTO();
                            tag.setId((String) tagMap.get("id"));
                            tag.setName((String) tagMap.get("name"));
                            tags.add(tag);
                        }
                    }
                    question.setTags(tags);
                    
                    // 处理knowledge_points
                    List<KnowledgePointDTO> knowledgePoints = new ArrayList<>();
                    List<Object> kpValues = record.get("knowledge_points").asList();
                    for (Object kpValue : kpValues) {
                        if (kpValue instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> kpMap = (Map<String, Object>) kpValue;
                            KnowledgePointDTO kp = new KnowledgePointDTO();
                            kp.setId((String) kpMap.get("id"));
                            kp.setName((String) kpMap.get("name"));
                            // 使用工具类安全转换level字段
                            kp.setLevel(Neo4jUtils.safeToInteger(kpMap.get("level")));
                            knowledgePoints.add(kp);
                        }
                    }
                    question.setKnowledgePoints(knowledgePoints);

                    questions.add(question);
                }
            }

            QuestionsResponse response = new QuestionsResponse();
            response.setQuestions(questions);

            log.info("查询Question成功: count={}", questions.size());
            return response;

        } catch (Exception e) {
            log.error("查询Question失败", e);
            throw new RuntimeException("查询Question失败: " + e.getMessage());
        }
    }

    /**
     * 校验RootCategory和SubCategory是否存在
     */
    private boolean validateCategories(String rootCategoryName, String subCategoryName) {
        try (Session session = neo4jDriver.session()) {
            // 检查RootCategory
            Result rootResult = session.run(
                    "MATCH (r:RootCategory {name: $name}) RETURN r",
                    Values.parameters("name", rootCategoryName)
            );
            if (!rootResult.hasNext()) {
                log.info("RootCategory不存在: {}", rootCategoryName);
                return false;
            }

            // 检查SubCategory
            Result subResult = session.run(
                    "MATCH (s:SubCategory {name: $name}) RETURN s",
                    Values.parameters("name", subCategoryName)
            );
            if (!subResult.hasNext()) {
                log.info("SubCategory不存在: {}", subCategoryName);
                return false;
            }

            return true;
        }
    }
}
