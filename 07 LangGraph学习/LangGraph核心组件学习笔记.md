# LangGraph 核心组件学习笔记（含代码对照）

## 1. 总体理解：LangGraph 不是“多次调 LLM”，而是“状态驱动的图执行框架”

LangGraph 的核心抽象不是 prompt，而是 **Graph = State + Node + Edge**。State 承载共享数据，Node 执行业务步骤，Edge 决定状态如何流动。LLM 只是某类节点中的一种能力实现，因此 LangGraph 的真正价值不在“调用模型”，而在 **显式建模复杂流程、状态演化、路由逻辑和可观测执行过程**。

从工程视角看，它更像一个面向智能应用的状态工作流引擎，而不是传统意义上的链式调用封装。

---

## 2. State：共享状态面，也是短期记忆容器

### 2.1 State 的定位

State 是图运行过程中的共享数据结构，所有节点都围绕它读写。它不只是输入输出参数容器，而是整个 graph 的“工作区”。

通常可以保存三类信息：**输入型字段**（如 `user_input`、`query`）、**过程型字段**（如 `task_stage`、`tool_result`、`summary`）、**输出型字段**（如 `final_answer`）。这三类字段分层越清晰，graph 越容易维护。

---

### 2.2 State 的更新机制：不是简单覆盖，而是可声明 reducer

LangGraph 的关键点之一，是字段更新可以声明合并策略。也就是说，节点返回的不是完整 state，而是一个 **更新片段**；LangGraph 再根据字段 reducer 决定如何合并。

你上传的 `12 LangGraph-State.py` 正好对应这个知识点：

```python
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    list_field: Annotated[list[int], add]
    extra_field: int
```

这里有三种不同语义：

- `messages` 用 `add_messages`，表示消息按消息规则追加
- `list_field` 用 `add`，表示列表拼接
- `extra_field` 没写 reducer，默认是覆盖

对应节点代码：

```python
def node1(state: State):
    new_message = AIMessage("Hello!")
    return {"messages": [new_message], "list_field": [10], "extra_field": 10}


def node2(state: State):
    new_message = AIMessage("LangGraph!")
    return {"messages": [new_message], "list_field": [20], "extra_field": 20}
```

这段代码的真正教学点不是“加两条消息”，而是：**State 字段的不同 reducer 决定了图运行时的数据演化方式。**

- `messages` 最终会在原用户消息基础上继续追加 AIMessage
- `list_field` 会从 `[1, 2, 3]` 逐步变成 `[1, 2, 3, 10, 20]`
- `extra_field` 会先被设成 `10`，再被 `20` 覆盖

因此，State 不是一个普通 dict，而是一个带“字段更新语义”的共享状态模型。

---

### 2.3 `MessagesState` 的意义

如果你的 graph 主要就是围绕消息流转，可以直接用 `MessagesState`。它本质上是 LangGraph 提前定义好的：

- `messages` 字段
- `add_messages` 合并策略

它适合聊天机器人、工具调用 Agent 等场景；但一旦业务中有 `task_stage`、`summary`、`profile`、`tool_result` 等字段，就应回到自定义 State。

一句话：**`MessagesState` 是聊天场景快捷版，自定义 State 才是复杂业务常态。**

---

## 3. Node：图中的业务步骤，而不是 prompt 容器

### 3.1 Node 的本质

Node 是图中的处理单元，通常就是 Python 函数。它读取当前 state，执行业务逻辑，然后返回 state 的更新片段。

Node 能做的事非常广：调 LLM、调工具、调数据库、做摘要、做路由判断前置处理、做格式转换、做 reduce 汇总。LangGraph 不关心你具体做了什么，只关心：**你根据当前状态返回了什么更新。**

因此，Node 本质上是 **业务动作单元**，不是“包装 prompt 的函数”。

---

### 3.2 Node 的输入输出语义

Node 典型长这样：

```python
def node(state: State):
    return {"field": "new_value"}
```

重点在于：**它返回的是更新，不是完整 state。** 这个设计让状态流转更透明，也更适合并行执行与 reducer 合并。

---

### 3.3 Node 可以读取 config/context

你上传的 `13 LangGraph-Node.py` 给了一个很典型的例子：

```python
class State(TypedDict):
    number: int
    user_id: str

class ConfigSchema(TypedDict):
    user_id: str


def node_1(state: State, config: RunnableConfig):
    time.sleep(3)
    user_id = config["configurable"]["user_id"]
    return {"number": state["number"] + 1, "user_id": user_id}
```

这里体现了两个边界：

- `state` 承载业务共享状态
- `config` 承载调用期配置

更直白一点说：**稳定参与 graph 流转的信息放 state，只在本次调用时提供的外部配置放 config。**

`user_id` 这种字段在教学示例里既可通过 `config` 传，也可回写进 `state`；但正式项目里要先想清楚它到底属于“运行上下文”还是“业务状态”。

---

### 3.4 Node 的缓存：LangGraph 在往产品级执行框架走

同一个示例里还有一个关键点：缓存。

```python
builder.add_node("node1", node_1, cache_policy=CachePolicy(ttl=5))
graph = builder.compile(cache=InMemoryCache())
```

它说明 LangGraph 并不只是组织流程，还在增强执行稳定性和性能控制能力。这个示例里两次调用输入 `number=5`，第二次会走缓存。

但这里要保持专业判断：**缓存键到底是否包含 `configurable.user_id`，要以你本地版本实现为准，不能想当然。** 这个示例用于理解“节点可缓存”没问题，但项目里如果涉及权限、用户隔离、时效性，缓存设计要更谨慎。

---

### 3.5 Node 的设计原则

一个好的 Node 应尽量职责单一。像 `extract_user_info`、`call_tool`、`summarize_history`、`reduce_results` 这种粒度通常是比较合适的。Node 拆得太粗，graph 失去可读性；拆得太碎，也会让流程图噪音过大。判断标准不是“一个函数几行”，而是 **这个步骤在业务语义上是不是一个独立动作**。

---

## 4. Edge：控制流，不只是连线

### 4.1 普通边

普通边表示固定流程，比如：

```python
builder.add_edge("node1", "node2")
```

它的含义很直接：`node1` 执行完后进入 `node2`。当流程在设计期就确定时，普通边最清晰、最稳定，也最适合排查。

图的入口和出口通常用 `START` 与 `END`。这也是你在 PDF 和示例里一直看到的基础结构。

---

### 4.2 条件边：在固定分支中动态选路

你上传的 `14 LangGraph-Edge-条件边.py` 对应的是条件边：

```python
def routing_func(state: State) -> bool:
    if state["number"] > 5:
        return True
    else:
        return False

builder.add_conditional_edges(START, routing_func, {True: "node_1", False: "node_2"})
```

这里的本质是：**先定义好几个候选分支，再根据当前 state 选择其中一个。**

这个例子里：

- `number > 5` 就走 `node_1`
- 否则走 `node_2`

它适合处理这类问题：

- 是否需要工具调用
- 是否继续循环
- 是否命中错误分支
- 不同策略的切换

条件边是 LangGraph 中最典型的 **控制流分叉** 机制，本质上接近 if/else。

---

## 5. `Send`：动态路由与并行分发，不是普通条件边的升级版

这是最容易和条件边混淆的点。**条件边解决“走哪条路”，`Send` 解决“把多少个子任务派发出去”。**

你上传的 `15 LangGraph-Edge-send动态路由.py` 是一个标准 `Send + reduce` 示例：

```python
def dispatcher(state: MapState):
    return [Send("square_node", {"number": n}) for n in state["numbers"]]
```

这句话的含义不是“下一步去 `square_node`”，而是：

- 把 `numbers` 里的每个元素都拆成一个子任务
- 每个子任务都送去 `square_node`
- 每个子任务带自己的私有输入 `{ "number": n }`

对应 worker：

```python
def square_node(state: WorkerState):
    n = state["number"]
    return {"results": [n * n]}
```

对应 reduce：

```python
def reduce_node(state: MapState):
    return {"total": sum(state["results"])}
```

这里真正要学的是两个机制：

1. `Send` 可以在运行时动态生成多个任务
2. `results: Annotated[list[int], operator.add]` 让多个 worker 的输出能自动汇总

所以这个例子不是“动态边”的简单变体，而是 LangGraph 中很重要的 **map-reduce / scatter-gather** 模式。

典型应用包括：

- 多文档并行摘要
- 多查询并行搜索
- Planner 生成多个 worker task
- 多候选结果并行评估后汇总

一句话概括：**条件边是分支控制，`Send` 是任务分发。**

---

## 6. `Command`：把“更新状态 + 控制跳转”合并到节点内部

正常情况下，LangGraph 的默认节奏是：Node 更新 state，Edge 决定下一步。`Command` 则允许一个节点在返回时同时声明：

- 我要更新哪些字段
- 下一步跳到哪里

你上传的 `15 LangGraph-Edge-Command命令.py` 就是这个模式：

```python
def node_1(state: State):
    new_message = []
    for message in state["messages"]:
        new_message.append(message + "!")
    return Command(goto=END, update={"messages": new_message})
```

这里 `node_1` 做了两件事：

- 把所有消息加 `!`
- 直接指定 `goto=END`

这说明 `Command` 的核心价值是：**把节点处理结果和路由决策捏成一个返回对象。**

适合场景：

- 节点处理完就已明确知道下一步去哪
- 不想再为这个逻辑单独写路由函数
- 流程比较短，路由和业务天然耦合

但也要明确它的代价：**`Command` 会让业务逻辑和控制逻辑更紧耦合。** 简单流程用起来很顺手，复杂图里如果到处都是 `Command`，维护成本会上升。

---

## 7. 子图（Subgraph）：图也是可复用模块

你上传的 `16 LangGraph-Edge-子图.py` 对应的是子图机制：

```python
subgraph_builder = StateGraph(State)
subgraph_builder.add_node("sub_node_1", sub_node_1)
subgraph_builder.add_edge(START, "sub_node_1")
subgraph_builder.add_edge("sub_node_1", END)
subgraph = subgraph_builder.compile()

builder = StateGraph(State)
builder.add_node("subgraph_node", subgraph)
```

这说明：**一个 graph 编译后的对象本身就可以被当成另一个 graph 的节点使用。**

它的工程意义很大：

- 把复杂流程封成模块复用
- 主图负责编排，子图负责局部业务闭环
- 多团队协作时，各自维护自己的子图

你这个示例里还有一个很重要的观察点：

```python
print(graph.invoke({"messages": ["hello subgraph"]}))
# {'messages': ['hello subgraph', 'hello subgraph', 'response from subgraph']}
```

这里消息出现两次，说明 **父图和子图共享状态时，状态合并语义必须理解清楚**。这也是子图在正式项目里最需要警惕的地方：

- 父图和子图的状态契约是否一致
- reducer 是否会导致意外重复追加
- 子图输出字段是否会污染父图状态

因此，子图不是简单“封装一下流程”就完事，真正难点在 **状态边界和合并语义**。

---

## 8. Stream：Graph 的流式输出本质上是“执行过程可视化”

虽然你上传的示例文件没单独给 stream 代码，但 PDF 里这部分很关键。Graph 的 `stream()` / `astream()` 流出的不是单纯 token，而是执行过程中的状态变化。

常见模式：

- `values`：每一步后的完整 state
- `updates`：每一步返回的更新片段
- `messages`：LLM token / 元信息
- `custom`：节点手动写入的调试数据
- `debug`：更全的执行细节

这意味着 LangGraph 比很多传统链式框架更适合做：

- 可观测 Agent
- 实时前端展示“系统正在干什么”
- 多步骤问题排查

这一点和你前面看的 `13 LangGraph-Node.py` 里 `stream_mode="updates"` 是一致的：更新流能帮助你观察节点到底回写了什么。

---

## 9. compile：从“声明图”到“可执行图”

你这些示例里都有一个共同步骤：`builder.compile()`。它的意义不是语法收尾，而是把前面定义好的 State、Node、Edge 组织成可执行 graph。

同时，`compile()` 也经常是挂接执行能力的入口，例如：

- `checkpointer`
- `cache`
- 中断控制
- 运行配置

因此，Graph 的执行能力很多是在 compile 阶段真正确定的。定义图只是“声明结构”，compile 才是“生成可运行对象”。

---

## 10. 一条更工程化的理解主线

把 LangGraph 核心组件翻译成工程语言，会更容易形成稳定认知：

- **State**：共享数据模型，也是线程内短期记忆容器
- **Node**：业务动作单元，负责读 state、产出 update
- **Edge**：控制流与调度关系，不只是连线
- **Conditional Edge**：固定分支中的动态选路
- **Send**：运行时任务分发与并行汇总
- **Command**：把更新与跳转收敛到节点返回值中
- **Subgraph**：模块复用与流程分层
- **Stream**：执行过程的观测面
- **Compile**：把声明式图转成可运行系统

这套理解方式比单看 API 更接近实际开发。

---

## 11. 最容易混淆的几个点

### 11.1 State 和 config

- `state`：图运行期间共享、可流转、可持久化的数据
- `config`：某次调用传入的配置上下文

不要把所有东西都塞进 `config`，也不要把纯运行配置长期保存在 `state`。

### 11.2 条件边和 Send

- 条件边：**选哪条路**
- `Send`：**派多少个子任务出去**

这俩不是同一层次的东西。

### 11.3 Node 返回值和完整状态

Node 返回的是更新片段，不是完整 state。真正的全局 state 由 LangGraph 根据 reducer 合并出来。

### 11.4 子图复用和状态污染

子图可复用，但父图和子图共享状态时，字段合并策略必须先想清楚，否则很容易出现重复追加、字段冲突或隐性耦合。

---

## 12. 总结

LangGraph 的核心不是“有几个 API”，而是下面这套建模能力：

- **State 决定系统记住什么**
- **Node 决定系统做什么**
- **Edge 决定系统怎么走**
- **Reducer 决定状态怎么合并**
- **Send 决定系统如何拆批并发**
- **Command 决定节点是否同时承担控制职责**
- **Subgraph 决定系统如何模块化复用**
- **Stream 决定系统如何被观察和调试**

结合你这几个示例文件看，最值得真正吃透的不是某一段代码能不能跑，而是：**为什么这个字段要追加、为什么这个分支要用条件边、为什么这个场景要用 Send、为什么这里用 Command 而不是再写一条 Edge。**

理解到这层，LangGraph 才不是“会用”，而是“会设计”。