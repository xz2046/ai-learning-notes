# 06 Agent实战 — 知识点学习笔记

> 项目：业务运维排查助手（CDN 节点运维智能体）
> 框架：LangChain ReAct Agent + Streamlit + ChromaDB RAG

---

## 一、项目架构全景

```
┌──────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)               │
│  ┌──────────┐  ┌──────────────────┐  ┌──────────┐   │
│  │ 用户输入  │→│  ReAct Agent      │→│ 流式输出    │   │
│  └──────────┘  └────────┬─────────┘  └──────────┘   │
│                         │                            │
│                  ┌──────┴──────┐                     │
│                  │ Middleware   │                     │
│                  │ (日志/提示词)│                     │
│                  └──────┬──────┘                     │
└─────────────────────────┼────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Tools    │ │ RAG 知识  │ │ Prompt   │
        │ (6个工具)│ │ 库检索   │ │ 模板     │
        └──────────┘ └──────────┘ └──────────┘
```

### 核心流程

```
用户提问 → Agent 思考(ReAct循环)
   → 判断需要什么信息
   → 调用工具获取数据
   → 观察工具返回结果
   → 再思考：信息够了吗？
     → 不够则继续调工具体
     → 够了则生成最终回答
   → 流式输出到前端
```

---

## 二、LangChain Agent 体系

### 2.1 `create_agent` — 创建 Agent

```python
from langchain.agents import create_agent

self.agent = create_agent(
    model=chat_model,          # 大语言模型
    system_prompt=prompt,       # 系统提示词
    tools=tool_list,            # 可用工具列表
    middleware=[...]            # 中间件(可选)
)
```

**知识点：**
- `create_agent` 是 LangChain 1.3.11 的自定义构建函数，封装了 ReAct 循环
- 返回的是 `CompiledStateGraph`（底层依赖 LangGraph 的状态图）
- 参数 `system_prompt`：定义了 Agent 的行为准则和思考流程
- 参数 `tools`：Agent 可调用的全部工具，自动注入到提示词中
- 参数 `middleware`：在 Agent 执行流程中插入自定义逻辑

### 2.2 流式输出 — `stream()`

```python
for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
    latest_message = chunk["messages"][-1]
    if latest_message:
        yield latest_message.content.strip() + "\n"
```

**知识点：**
- `stream_mode="values"`：每次 yield 完整的状态字典
- `chunk["messages"][-1]`：取最新一条消息（可能是 AI 回复 或 Tool 返回）
- `context` 参数：向 Runtime 注入上下文，middleware 可读取修改

---

## 三、中间件系统

### 3.1 三件中间件

```python
middleware = [monitor_tool, log_before_model, report_prompt_switch]
```

### 3.2 `@wrap_tool_call` — 工具执行监控

```python
@wrap_tool_call
def monitor_tool(request, handler):
    # 前置：记录工具名和参数
    logger.info(f"执行工具:{request.tool_call['name']}")
    logger.info(f"传入参数:{request.tool_call['args']}")
    
    result = handler(request)  # 执行实际工具
    
    # 后置：检查是否为报告触发工具
    if request.tool_call['name'] == "fill_context_for_report":
        request.runtime.context["report"] = True
    
    return result
```

**知识点：**
- `@wrap_tool_call`：装饰器模式，包装工具调用函数
- `handler(request)`：执行原始工具逻辑
- `request.runtime.context`：跨工具、跨模型的上下文共享字典
- 适用场景：日志、鉴权、上下文注入、错误处理

### 3.3 `@before_model` — 模型调用前

```python
@before_model
def log_before_model(state, runtime):
    logger.info(f"即将调用模型,带有{len(state['messages'])}条消息。")
    logger.debug(f"{type(state['messages'][-1]).__name__} {state['messages'][-1].content.strip()}")
```

**知识点：**
- `state["messages"]`：当前对话消息列表，包含所有历史
- 可用作：token 计数、上下文窗口预警、对话历史审计

### 3.4 `@dynamic_prompt` — 动态切换提示词

```python
@dynamic_prompt
def report_prompt_switch(request):
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()   # 报告生成模式
    else:
        return load_system_prompts()   # 普通对话模式
```

**知识点：**
- Agent 可拥有多套提示词，根据上下文动态切换
- 切换触发方式：通过某个工具（如 `fill_context_for_report`）修改 context
- 应用场景：普通问答 vs 报告生成、多语言切换、角色切换

---

## 四、工具系统

### 4.1 工具定义规范

```python
from langchain_core.tools import tool

@tool(description="工具的明确描述，Agent 据此决定何时调用")
def tool_name(param1: str) -> str:
    """
    入参：param1 (str) — 参数说明
    返回：JSON 或文本描述
    """
    try:
        result = do_something(param1)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

**知识点：**
- `@tool` 装饰器将普通函数注册为 Agent 可用工具
- `description` 字段至关重要——Agent 根据它选择工具
- 参数类型提示影响 Agent 的参数生成质量
- 推荐返回 JSON 字符串，便于 Agent 解析
- 工具内部必须 try/except 兜底，不可让 Agent 见到未处理的异常

### 4.2 工具注册与导出

```python
# __init__.py
@tool
def fill_context_for_report():
    return "fill_context_for_report已调用"

def get_all_tools():
    return [
        node_detail_query,
        node_traffic_query,
        node_status_query,
        node_cmd_execute,
        rag_summarize,
        fill_context_for_report,
    ]
```

**知识点：**
- `get_all_tools()` 统一注册：新增工具体只需加入列表
- `fill_context_for_report` 是"虚拟工具"：不获取数据，只修改 context 切换提示词

### 4.3 五种工具体类型

| 工具 | 类型 | 核心原理 | 数据源 |
|------|------|----------|--------|
| `node_detail_query` | Web 爬虫 | BeautifulSoup 解析 HTML | 监控平台页面 |
| `node_traffic_query` | API 查询 | PromQL + Grafana API | Prometheus 时序库 |
| `node_status_query` | API 查询 | PromQL 实时查询 | Prometheus |
| `node_cmd_execute` | API 调用 | 隧道接口 POST | 隧道代理 |
| `rag_summarize` | RAG 检索 | 向量库相似度搜索 → LLM 总结 | ChromaDB |

---

## 五、RAG 知识检索

### 5.1 知识库构建流程

```
原始文档(.txt/.md/.pdf)
    → 文本分割器(RecursiveCharacterTextSplitter)
    → 向量化(HuggingFaceEmbeddings bge-m3)
    → 存入 ChromaDB
    → MD5 去重（避免重复导入）
```

### 5.2 向量存储配置

```yaml
# chroma.yaml
chunk_size: 800          # 每个块大小（字符数）
chunk_overlap: 100       # 块重叠
top_k: 3                 # 检索返回最相关3个块
max_distance: 0.8        # 距离阈值过滤（>0.8的丢弃）
separators: ["\n\n","\n","。","?","！"," ",""]  # 分割优先级
```

**知识点：**
- `chunk_size` 与 `chunk_overlap`：影响检索质量的关键参数
  - 太小：丢失上下文
  - 太大：含噪声，token 消耗大
- `max_distance`：相关性过滤，低质量文档不进入 LLM 上下文
- 分割优先级：段落 > 句子 > 标点 > 词 > 字符

### 5.3 检索链

```python
chain = prompt_template | model | StrOutputParser()
# 输入: {"input": user_query, "context": retrieved_docs}
# 输出: LLM 基于参考资料生成的总结
```

**知识点：**
- LangChain Expression Language (LCEL)：`|` 管道操作符
- `StrOutputParser`：将 LLM 的 ChatMessage 输出转为纯文本字符串
- RAG 提示词约束：要求 LLM "仅基于参考资料回答，不编造"

### 5.4 自定义检索器

```python
def _search(query: str):
    docs_with_scores = vector_store.similarity_search_with_relevance_scores(
        query, k=chroma_conf["top_k"]
    )
    filtered = [doc for doc, score in docs_with_scores if score < max_distance]
    return filtered

return RunnableLambda(_search)
```

**知识点：**
- `similarity_search_with_relevance_scores`：返回文档 + 关联度分数
- `RunnableLambda`：将普通函数包装为 LangChain Runnable，融入 LCEL

---

## 六、Prometheus 数据查询

### 6.1 通过 Grafana API 查询 Prometheus

```python
def query_prometheus(expr, from_ms, to_ms, step="15m"):
    url = f"{GRAFANA_BASE_URL}/api/ds/query"
    payload = {
        "queries": [{
            "datasource": {"type": "prometheus", "uid": "xxx"},
            "rawQuery": True,
            "expr": expr,
            "step": step,
            "maxDataPoints": 300,
        }],
        "from": str(from_ms),
        "to": str(to_ms),
    }
    resp = requests.post(url, headers={"Cookie": GRAFANA_COOKIE}, json=payload)
    # 解析返回的 DataFrame 格式
    for frame in data["results"][*]["frames"]:
        times, values = frame["data"]["values"]
```

**知识点：**
- Grafana API 不是直接暴露 Prometheus 接口，而是通过 `/api/ds/query` 代理
- 请求体中的 `datasource.uid` 对应 Grafana 数据源配置
- 返回格式为 DataFrame 结构：`{schema, data: {values: [time[], value[]]}}`
- Grafana 的 Cookie 认证方式（`grafana_session`）

### 6.2 分时段统计

```python
# 晚高峰 18:00~24:00
evening_start = from_ms + 18 * 3600 * 1000
evening_end = from_ms + 24 * 3600 * 1000
evening_points = [v for t, v in all_points if evening_start <= t < evening_end]

# 计算 95 百分位
def _calc_95th(values):
    sorted_vals = sorted(values, reverse=True)
    idx = int(len(sorted_vals) * 0.05)
    return sorted_vals[idx]
```

**知识点：**
- 毫秒时间戳运算：`从当天0点开始 + 小时数×3600×1000`
- 95 百分位计算：降序排列后取前 5% 位置的边界值
- 总流量计算：`sum(每秒字节数 × 300秒) / 1024³ → GB`

---

## 七、Streamlit 交互界面

### 7.1 会话状态管理

```python
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()  # 只创建一次

if "message" not in st.session_state:
    st.session_state["message"] = []          # 对话历史
```

**知识点：**
- `st.session_state`：Streamlit 的持久化字典，跨 rerun 保持
- Agent 实例放入 session_state 避免每次操作重新初始化
- 消息列表用于渲染对话记录

### 7.2 流式输出实现

```python
def capture(generator, cache_list):
    for chunk in generator:
        cache_list.append(chunk)
        for char in chunk:
            time.sleep(0.01)    # 控制打字速度
            yield char

st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
```

**知识点：**
- `write_stream(generator)`：Streamlit 的流式渲染，逐字符显示
- `cache_list`：边消费边收集，事后可获取完整内容
- `time.sleep(0.01)`：人为延迟，制造打字效果
- 注意：空生成器情况下需保护 `response_messages[-1]`

### 7.3 rerun 的作用

```python
st.rerun()  # 主动重渲染，去除 Agent 思考过程的文字痕迹
```

Agent 的 ReAct 思考过程在流式输出时会被前端看到。`st.rerun()` 让页面重新运行，此时 `chat_input` 为空，`if prompt:` 不执行，仅渲染历史消息列表，从而使思考过程消失。

---

## 八、模型工厂模式

### 8.1 抽象工厂

```python
class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self):
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self):
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],
            api_key=rag_conf["api_key"],
            base_url=rag_conf["base_url"],
            streaming=True,
        )

class EmbeddingsFactory(BaseModelFactory):
    def generator(self):
        return HuggingFaceEmbeddings(
            model_name=rag_conf["embeddings_model_local_path"],
        )

chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingsFactory().generator()
```

**知识点：**
- 工厂模式：将模型实例化逻辑集中管理
- 模块级实例化：`chat_model` 在 import 时创建，全局单例
- `ChatOpenAI` 支持任意 OpenAI 兼容接口（DeepSeek、通义千问等）

---

## 九、配置管理

### 9.1 YAML 配置加载

```python
import yaml

rag_conf = load_rag_config()      # config/rag.yaml
chroma_conf = load_chroma_config() # config/chroma.yaml
tools_conf = load_tools_config()   # config/tools.yaml
prompts_conf = load_prompts_config() # config/prompts.yaml
agent_conf = load_agent_config()   # config/agent.yaml
```

**知识点：**
- 点加载：各模块按需加载，职责清晰
- `get_abs_path()`：将配置中的相对路径转为项目根绝对路径
- 配置与代码分离：修改数据源地址、API Key 等无需改代码

### 9.2 共享工具函数

```python
def safe_text(el) -> str:
    """安全提取标签纯文本"""
    return el.get_text(strip=True) if el is not None else ""

def make_error(sn: str, msg: str) -> str:
    """统一错误 JSON"""
    return json.dumps({"sn": sn, "error": msg}, ensure_ascii=False)
```

**知识点：**
- 工具函数抽取到 `common.py` 避免重复代码
- 统一错误格式：Agent 工具返回结构化 JSON 而非裸字符串

---

## 十、Web 爬虫技巧（node_detail）

### 10.1 BeautifulSoup 页面解析

```python
def _find_card_by_header(soup, keyword):
    """通过 card-header 文字定位 card 容器"""
    for header in soup.find_all(["h5", "div", "span"], string=re.compile(keyword)):
        card = header.find_parent("div", class_="card")
        if card:
            return card
```

**知识点：**
- `find_parent()`：从子元素向上查找父容器
- `re.compile(keyword)`：模糊匹配卡片标题
- CSS 类选择器 `.card`、`.badge`：用于定位功能块

### 10.2 多层级表格解析

```python
for row in outer_table.find_all("tr")[1:]:    # 跳过头行
    cols = row.find_all("td", recursive=False) # 仅取直接 td
    detail = cols[-1]
    inner_table = detail.find("table")          # 嵌套表格
```

**知识点：**
- `recursive=False`：只取直接子级 td，不深入到嵌套表
- 正则提取：`re.search(r"TaskInfo\?task_id=(\d+)", html)` 提取 URL 参数
- 状态识别：根据 span 的 style 属性中的 color 判断状态

---

## 十一、日志系统

```python
def get_logger(name="agent", console_level=INFO, file_level=DEBUG):
    logger = logging.getLogger(name)
    # 控制台输出 + 文件输出（按日期分割）
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"logs/{name}_{date}.log")

logger = get_logger()  # 模块级单例
```

**知识点：**
- 双输出：控制台（INFO）+ 文件（DEBUG）
- 文件名包含日期：`agent_2026-06-29.log`
- `logger.handlers` 检查：防止重复添加 handler（幂等性）

---

## 十二、关键设计模式总结

| 模式 | 使用位置 | 作用 |
|------|----------|------|
| **工厂模式** | `model/factory.py` | 统一管理 Chat 和 Embedding 模型创建 |
| **装饰器模式** | `middleware.py` | `@wrap_tool_call`、`@before_model`、`@dynamic_prompt` |
| **管道模式(LCEL)** | `rag/rag_service.py` | `prompt \| model \| parser` 链式组合 |
| **单例模式** | `model/factory.py` | `chat_model`、`embedding_model` 模块级实例 |
| **适配器模式** | `rag/vector_store.py` | `RunnableLambda` 包装函数为 LangChain 组件 |
| **统一出口** | `agent/tools/__init__.py` | `get_all_tools()` 集中注册所有工具 |

---

## 十三、常见坑点

```
1. Cookie 过期 → 工具静默返回空数据 → Agent 以为正常
   ✅ 解决：定期更新 tools.yaml，或添加过期告警

2. Embedding 模型路径失效 → import 时直接崩溃
   ✅ 解决：配置使用 HuggingFace Hub 自动下载

3. RAG 检索结果为空 → Agent 可能产生幻觉
   ✅ 解决：提示词中强制"仅基于参考资料回答"

4. Agent 循环调用工具 → 消耗大量 token
   ✅ 解决：系统提示词中设定"多次失败即返回"的止损条件

5. streamlit.rerun() 后状态丢失
   ✅ 解决：所有持久状态放入 st.session_state
```

---

## 十四、学习路线延伸

```
本项目掌握后，可继续学习：

1. LangGraph 状态图：更精细控制 Agent 流程
2. 多 Agent 协作：主管 Agent + 多个专家 Agent
3. 记忆持久化：引入 LangGraph 的 Checkpointer
4. 结构化输出：response_format 约束 LLM 输出格式
5. 流式优化：Server-Sent Events 替代 sleep 延迟
6. 异步查询：aiohttp 并发查询大量节点
```
