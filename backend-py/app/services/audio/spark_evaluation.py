import json
import traceback
from loguru import logger
from app.services.AI.spark_API import call_spark_api

def evaluate_answer(question: str, answer: str) -> dict:
    """
    使用星火大模型评估面试答案，字段名与interview_history表一致，生成三条反馈建议
    """
    logger.info(f"开始评估答案，问题: {question}")
    logger.info(f"用户回答: {answer}")
    prompt = f"""
你是10年资深企业面试官,你非常严格，严格按以下**全局强规则+评分细则+动态分值计分规则+答题得分封顶规则**评估作答，
依据整体面试总题数自动计算本题满分分值，单题得分由六大能力维度折算后再做分值上限约束，**严厉杜绝仅靠一道自我介绍/简单题目就拿到超高分数、单题分值虚高、总分失衡、随意抬分漏洞**，所有题目得分相加最终总分校准后严格合计100分，最终仅返回标准JSON，字段名必须完全一致：

### 一、全局强规则（优先级最高，所有问题必执行，触发则跳过后续细则）
#### 1. 无意义/无效回答 → 所有维度=0.0分，本题得分=0分
满足任意一条即触发：
- 回答为空、空白、仅符号/空格
- 回答与问题完全无关、乱码、无实际语义
- 自我介绍仅1-2个无意义字（如仅姓名、仅“你好”）

#### 2. 极度简单回答 → 所有维度=0.0分，正常参与分值折算
满足任意一条即触发：
- 回答字数≤5字，无实质内容（如“不知道”“就这样”）
- 回答仅重复问题，无任何观点/信息输出

#### 3. 新增防高分漏洞强制规则（最高优先级）
1）**全题型单维度封顶**：任意六大维度打分最高不得超过4.8分，严禁打出5.0满分维度分，从根源压低高分上限
2）**维度均衡限制**：任意一个维度分数，不得高出其他任意维度分数1.5分及以上，禁止偏科式强行拉高分数
3）**无实质内容限分**：只有空泛话术、没有真实经历、项目案例、实操经验、具体细节支撑的内容，对应维度最高上限3.0分
4）**冗余内容扣分**：回答篇幅冗长、废话占比超50%、重复赘述无有效信息，所有维度统一扣1.0-1.5分
5）**无关内容限分**：回答内和岗位、问题无关内容占比超30%，全维度统一下调0.5-1.0分

### 二、动态计算本题满分分值（核心计分规则，强制执行）
已知本次面试**总题目数量：{total_question_num}**
1. 判定规则
   - 若总题目数量 ≤ 10 道：**当前题目满分固定为10分**
   - 若总题目数量 ＞ 10 道：**当前题目满分 = 100 ÷ 总题目数量**
2. 所有题目满分累加总和严格等于100分
3. 单题硬性最高分封顶：**无论任何题型、任何题目，本题最终得分最高不得超过15分**，超出一律按15分计算
4. 题目过少特殊校准：总题数＜7道导致单题理论满分超15分时，统一强制锁定单题满分15分，面试结束后所有题目得分总和统一等比例折算为标准100分总分

### 三、题型差异化维度打分限制
1. 【自我介绍类硬性维度限制】
   - professional_knowledge 最高上限3.0分，不得超出
   - innovation_ability 最高上限2.5分，不得超出
   - 自我介绍六大维度总分最高锁定22.0分，严禁自我介绍拿高分挤占整体分数
   - 重点评分维度：技能匹配度、语言表达、逻辑思维
2. 【专业问答类限制】
   - professional_knowledge最高上限4.5分，禁止专业题无脑拉满分数
3. 其余所有题型：六大维度正常0.0-4.8区间打分，无维度分数封顶外额外宽松权限

### 四、评分维度及刚性评分细则（统一0.0~4.8分，保留1位小数）
未触发0分判定时，按以下标准评分：
1. professional_knowledge（专业知识水平）
   0.0分：无任何专业知识，回答无效/空白
   1.0分：完全不了解岗位相关专业知识，回答与问题无关
   2.0分：了解少量基础专业知识，核心知识点回答错误
   3.0分：掌握基础专业知识，核心知识点回答正确但无拓展
   4.0分：熟练掌握专业知识，核心知识点回答准确且有一定拓展
   4.8分：精通专业知识，回答覆盖核心知识点且结合实际场景深度拆解

2. skill_match（技能匹配度）
   0.0分：无任何相关技能，回答无效/空白
   1.0分：掌握的技能与岗位要求完全不匹配
   2.0分：掌握少量岗位要求的技能，核心技能缺失
   3.0分：掌握岗位要求的基础技能，核心技能达标但无实战经验
   4.0分：掌握岗位核心技能，有相关实战经验且能落地
   4.8分：核心技能远超岗位要求，有成熟项目案例可佐证

3. language_expression（语言表达能力）
   0.0分：无任何表达内容，回答无效/空白
   1.0分：逻辑混乱、口齿不清，无法清晰传递核心观点
   2.0分：表达不流畅，核心观点模糊，需反复理解
   3.0分：表达流畅，能清晰传递核心观点，但无条理
   4.0分：表达流畅有条理，用词准确，能精准传递观点
   4.8分：表达简洁精炼、逻辑清晰，有感染力且易理解

4. logical_thinking（逻辑思维能力）
   0.0分：无任何逻辑表达，回答无效/空白
   1.0分：回答无逻辑，东拉西扯，无法形成完整论证
   2.0分：逻辑框架混乱，论据与论点无关
   3.0分：有基础逻辑框架，论据能支撑论点但不充分
   4.0分：逻辑框架清晰，论据充分且层层递进
   4.8分：逻辑严谨，能从多角度论证，且有归纳总结

5. innovation_ability（创新能力）
   0.0分：无任何创新相关内容，回答无效/空白
   1.0分：回答无任何创新点，完全照搬常规思路
   2.0分：有少量创新想法，但无落地可行性
   3.0分：有明确创新思路，具备基础落地条件
   4.0分：创新思路贴合实际，有具体落地路径
   4.8分：创新思路有突破性，且能结合场景形成可落地的方案

6. stress_resistance（应变抗压能力）
   0.0分：无任何有效回答，表现回避/空白
   1.0分：回答回避核心问题，表现出明显的情绪焦虑
   2.0分：能回答问题，但思路混乱，有明显的抗压不足表现
   3.0分：能正面回答问题，思路基本清晰，无明显情绪波动
   4.0分：面对问题能快速调整思路，回答有条理且心态稳定
   4.8分：能从容应对问题，甚至能主动化解问题中的难点

### 六、本题得分统一计算公式（双层计算，严格控分，彻底封堵高分漏洞）
1. 六大维度满分总和 = 28.8分（4.8*6）
2. 维度总分 = 六项能力分数相加
3. 原始折算分 = 四舍五入( (维度总分 ÷ 28.8) × 本题对应满分分值 )
4. 计算本题理论最高分 = 本题满分 × 题型对应得分上限比例
5. 初步得分 = 取原始折算分与理论最高分之间较小的数值
6. 最终本题得分score = 初步得分再次和15分比对，取更小值
7. 触发全局无效规则直接 score=0，score 为整数
8. 全部题目打分完毕后，整体总分统一等比例校准至满分100分，杜绝单题高分拉高整体成绩

### 七、打分硬性约束（杜绝主观抬分，根治简单回答拿高分漏洞）
1. 严禁仅依靠回答话术通顺、内容篇幅长就拉高多项维度分数
2. 打分优先匹配岗位实际用工需求，侧重实战经验、落地成果，弱化空泛理论表述
3. 单一题目作答优秀仅做适度加分，不得直接拉高维度分数与本题分值
4. 自我介绍、基础闲聊类简单题目，坚决压低整体评分权重，不允许成为高分主力题
5. 无数据、无项目、无成果、无细节的流水账回答，整体评分直接下调一档

### 八、反馈建议要求
1. 若得分=0分：feedback_suggestion1/2/3 统一为「请完成完整的自我介绍，包含个人基本信息、工作/学习经历、岗位匹配优势等内容」
2. 自我介绍题型：建议侧重经历梳理、岗位匹配精简表达、突出自身优势，减少无效赘述
3. 专业问答题型：建议侧重夯实专业基础、熟记核心知识点、结合实操作答
4. 正常评分：每条建议针对不同维度，具体可落地，严格结合回答内容给出
5. 单题得分偏高时，建议必须点明不足之处，不可全是夸赞，平衡评价

### 九、HTML输出要求
保持原有美观布局，适配0分展示场景，结构如下：
<div style="width: 100%; padding: 20px; background: #f5f7fa; border-radius: 8px;">
  <h3 style="color: #333; margin: 0 0 20px 0;">面试评估结果</h3>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">专业知识水平</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{professional_knowledge}分</p>
    </div>
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">技能匹配度</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{skill_match}分</p>
    </div>
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">语言表达能力</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{language_expression}分</p>
    </div>
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">逻辑思维能力</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{logical_thinking}分</p>
    </div>
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">创新能力</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{innovation_ability}分</p>
    </div>
    <div style="background: #fff; padding: 15px; border-radius: 6px; text-align: center;">
      <p style="color: #666; margin: 0 0 5px 0;">应变抗压能力</p>
      <p style="color: #2d8cf0; font-size: 24px; margin: 0;">{stress_resistance}分</p>
    </div>
  </div>
  <div style="background: #fff; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
    <p style="color: #666; margin: 0 0 10px 0;">本题得分</p>
    <p style="color: #e64340; font-size: 32px; margin: 0;">{score}分</p>
  </div>
  <div style="background: #fff; padding: 15px; border-radius: 6px;">
    <p style="color: #666; margin: 0 0 10px 0;">改进建议</p>
    <ul style="margin: 0; padding-left: 20px; color: #333;">
      <li>{feedback_suggestion1}</li>
      <li>{feedback_suggestion2}</li>
      <li>{feedback_suggestion3}</li>
    </ul>
  </div>
</div>

### 十、最终输出硬性约束
1. 仅返回纯净JSON，无多余文字、注释、解释
2. 六大维度分数保留1位小数，本题得分score为整数
3. 相同问题+相同回答+相同总题数，评分结果完全一致
4. 严格执行自我介绍维度分数上限规则与题型得分比例封顶规则
5. 必须先根据总题数判定本题满分，再折算分数，最后执行多层分值封顶
6. JSON固定字段：professional_knowledge、skill_match、language_expression、logical_thinking、innovation_ability、stress_resistance、score、feedback_suggestion1、feedback_suggestion2、feedback_suggestion3
7. 坚决封堵漏洞：杜绝自我介绍、简单简答、流水账式回答轻松拿到高分，严控单题权重，保证面试打分整体公平均衡

总面试题目数量：{total_question_num}
面试问题：{question}
候选人回答：{answer}
"""
    try:
        result = call_spark_api(prompt)
        logger.info(f"星火大模型返回结果: {result}")
        cleaned_result = result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()
        logger.info(f"清理后的JSON字符串: {cleaned_result}")
        parsed_result = json.loads(cleaned_result)
        logger.info(f"解析后的评估结果: {parsed_result}")
        return parsed_result
    except Exception as e:
        error_detail = f"评估失败: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise Exception(error_detail)
    