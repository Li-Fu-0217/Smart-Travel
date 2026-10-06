"""智能体编排图（见施工规范 §6.1、§6.7、§6.8、§6.11、§6.12）。

技术分工（§6.1）：LangGraph 承载 ReAct 状态图、检查点（MemorySaver）、步数上限、状态读取；
LangChain 仅提供标准件（ChatOpenAI / StructuredTool / 消息类型 / create_agent）。

本文件职责：
  - SYSTEM_PROMPT（§6.8）
  - build_agent()：create_agent(llm, tools, system_prompt=SYSTEM_PROMPT,
    middleware=[...], checkpointer=MemorySaver(), name="travel_react")
  - 中间件（§6.11）：写库工具二次校验 + 每轮用量统计 + traveler_id 兜底（按 LangChain 1.x 真实 API）
  - _extract_steps()：从消息轨迹还原「思考 → 行动 → 观察」步骤（§6.7）
  - 行程卡片结构化抽取（§6.12）：ItineraryCard 模型 + 按需 with_structured_output

编排/中间件/步骤抽取的落地在阶段 6.1；本文件 6.0 先落 SYSTEM_PROMPT 与结构契约。
"""

# —— 系统提示词（§6.8：必须写清工具使用规则）——
SYSTEM_PROMPT = """你是「智能旅行助手」，通过调用工具为绑定旅行者的用户办理行程相关事务。

可用的 11 个工具与使用规则：
1. 涉及时效性/待办的问题，先调用 check_trip_schedule 查行程待办与逾期情况
2. 想预约必须先调用 query_available_booking 查可约时段，把可选时段告诉用户，等用户明确确认后再调用 book_item 下单
3. 预约成功后可调用 notify_companions 通知同行人
4. 用户明确表达求助、走失、身体不适、证件丢失等紧急情况时，调用 trigger_travel_alert 求助告警工具
5. 涉及签证政策、出行注意事项等常识问题，先调用 query_guide_knowledge 检索攻略库再回答
6. 回答用简洁中文，不要编造工具未返回的数据
7. 用排除法建立意图互斥：紧急意图只走告警工具；政策类问题只走知识库检索，不与预约链路混合
8. 用户想要行程推荐时，调用 recommend_itinerary（它基于偏好标签与历史记录）
9. 用户表达「记录一下去过哪/评价」时调用 save_travel_record；表达「总结/更新偏好」时调用 distill_preferences
10. 用户说「按模板复制成行程」时调用 copy_trip_template

需要 traveler_id 时，用消息前缀里标注的「当前旅行者ID」。"""
