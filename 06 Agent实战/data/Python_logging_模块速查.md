# Python `logging` 模块学习总结

## 1. 作用

`logging` 是 Python 标准库里的日志模块，用来替代零散的 `print()` 调试输出。

它适合做这些事：

- 记录程序运行过程
- 输出调试信息、普通信息、警告、错误、异常
- 把日志写到控制台、文件，或同时写到多个地方
- 控制不同环境下的日志详细程度

---

## 2. 基础使用

最简单的用法：

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.debug("这是一条调试日志")
logging.info("程序启动")
logging.warning("这是警告")
logging.error("发生错误")
logging.critical("严重错误")
```

说明：

- `level=logging.INFO` 表示只显示 `INFO` 及以上级别的日志
- `DEBUG` 级别因为低于 `INFO`，默认不会显示

---

## 3. 日志级别

`logging` 默认支持 5 个常用级别：

| 级别 | 数值 | 说明 |
|---|---:|---|
| `DEBUG` | 10 | 最详细的调试信息 |
| `INFO` | 20 | 正常运行信息 |
| `WARNING` | 30 | 警告，不影响继续运行 |
| `ERROR` | 40 | 错误，某个功能失败 |
| `CRITICAL` | 50 | 严重错误，程序可能无法继续 |

判断规则：

- 日志系统设置了某个级别后，只会输出 **大于等于该级别** 的日志

比如：

```python
logging.basicConfig(level=logging.WARNING)
```

这时只有：

- `WARNING`
- `ERROR`
- `CRITICAL`

会被输出。

---

## 4. `basicConfig()` 基础语法

`basicConfig()` 是最常见的快速配置入口。

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 常用参数

| 参数 | 说明 |
|---|---|
| `level` | 设置日志输出级别 |
| `format` | 设置日志格式 |
| `filename` | 把日志写入文件 |
| `filemode` | 文件打开模式，如 `a` 追加，`w` 覆盖 |
| `datefmt` | 时间格式 |
| `encoding` | 文件编码，常用 `utf-8` |
| `handlers` | 自定义处理器列表 |
| `force` | 是否强制覆盖已有配置（Python 3.8+） |

### 示例：输出到文件

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

logging.info('日志写入文件')
```

### 示例：覆盖写入文件

```python
logging.basicConfig(
    filename='app.log',
    filemode='w',
    level=logging.INFO
)
```

---

## 5. 常用日志输出函数

`logging` 模块直接提供一组快捷函数：

```python
logging.debug(msg)
logging.info(msg)
logging.warning(msg)
logging.error(msg)
logging.critical(msg)
logging.exception(msg)
logging.log(level, msg)
```

### 说明

#### `logging.debug()`

记录调试信息。

```python
logging.debug('变量 x = %s', x)
```

#### `logging.info()`

记录普通运行信息。

```python
logging.info('服务启动成功')
```

#### `logging.warning()`

记录警告信息。

```python
logging.warning('配置文件不存在，将使用默认配置')
```

#### `logging.error()`

记录错误信息。

```python
logging.error('数据库连接失败')
```

#### `logging.critical()`

记录严重错误。

```python
logging.critical('系统即将退出')
```

#### `logging.exception()`

只能在 `except` 代码块中使用，会自动附带异常堆栈。

```python
try:
    1 / 0
except ZeroDivisionError:
    logging.exception('发生除零错误')
```

#### `logging.log(level, msg)`

按指定级别记录日志。

```python
logging.log(logging.INFO, '自定义级别调用')
```

---

## 6. 日志格式 `format` 常用占位符

日志内容通常通过 `format` 参数定义。

常见写法：

```python
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### 常用字段

| 占位符 | 含义 |
|---|---|
| `%(asctime)s` | 日志时间 |
| `%(name)s` | logger 名称 |
| `%(levelname)s` | 级别名称 |
| `%(levelno)s` | 级别数值 |
| `%(message)s` | 日志消息 |
| `%(pathname)s` | 当前执行文件完整路径 |
| `%(filename)s` | 文件名 |
| `%(module)s` | 模块名 |
| `%(funcName)s` | 函数名 |
| `%(lineno)d` | 代码行号 |
| `%(process)d` | 进程号 |
| `%(thread)d` | 线程号 |

### 示例

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
)

logging.info('这是一条日志')
```

输出示例：

```text
2026-01-01 10:00:00,123 | INFO | main.py:8 | 这是一条日志
```

---

## 7. 推荐写法：使用 `Logger` 对象

实际项目里，不建议一直直接用 `logging.info()` 这种根日志器方式，更常见的是创建自己的 `logger`。

```python
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info('模块启动')
```

### `getLogger(name)`

```python
logger = logging.getLogger(name)
```

常见写法：

```python
logger = logging.getLogger(__name__)
```

含义：

- `__name__` 表示当前模块名
- 这样不同模块可以有各自的 logger，便于排查问题

### `Logger` 常用方法

| 方法 | 说明 |
|---|---|
| `logger.debug()` | 调试日志 |
| `logger.info()` | 普通日志 |
| `logger.warning()` | 警告日志 |
| `logger.error()` | 错误日志 |
| `logger.critical()` | 严重错误日志 |
| `logger.exception()` | 异常日志，带堆栈 |
| `logger.log(level, msg)` | 指定级别输出 |
| `logger.setLevel(level)` | 设置当前 logger 级别 |
| `logger.addHandler(handler)` | 添加处理器 |
| `logger.removeHandler(handler)` | 移除处理器 |

---

## 8. `Handler`：控制日志输出到哪里

`Handler` 决定日志发往哪里，比如控制台、文件、网络等。

常见处理器：

| Handler | 作用 |
|---|---|
| `StreamHandler` | 输出到控制台 |
| `FileHandler` | 输出到文件 |
| `RotatingFileHandler` | 按文件大小轮转日志 |
| `TimedRotatingFileHandler` | 按时间轮转日志 |

### 示例：同时输出到控制台和文件

```python
import logging

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug('调试信息')
logger.info('普通信息')
logger.error('错误信息')
```

说明：

- `logger` 级别是总开关
- `handler` 级别是各自通道的过滤器
- 最终是否输出，要同时满足两边的级别要求

---

## 9. `Formatter`：控制日志长什么样

`Formatter` 专门定义日志文本格式。

```python
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### 参数

| 参数 | 说明 |
|---|---|
| `fmt` | 日志文本格式 |
| `datefmt` | 时间格式 |
| `style` | 格式风格，默认 `%`，也可用 `{` 或 `$` |

### 示例：使用 `{}` 风格

```python
formatter = logging.Formatter(
    '{asctime} | {levelname} | {message}',
    style='{'
)
```

---

## 10. `Filter`：做更细粒度过滤

`Filter` 用来筛选日志记录。

```python
import logging

class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR
```

### 示例

```python
import logging

logger = logging.getLogger('demo')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.addFilter(ErrorFilter())

logger.addHandler(console)

logger.info('不会输出')
logger.error('会输出')
```

---

## 11. 参数传值推荐：不要自己 `%` 格式化字符串

推荐写法：

```python
logging.info('用户 %s 登录成功', username)
```

不推荐：

```python
logging.info('用户 %s 登录成功' % username)
logging.info(f'用户 {username} 登录成功')
```

原因：

- 推荐写法会把参数延迟到真正需要输出时再格式化
- 如果当前级别不输出这条日志，就不会白白做字符串拼接
- 性能更好，也更符合 logging 的设计方式

### 多参数示例

```python
logging.info('订单号=%s 金额=%.2f', order_id, amount)
```

---

## 12. 记录异常的常见写法

### 写法 1：只记录错误消息

```python
try:
    result = 10 / 0
except Exception as e:
    logging.error('出错了: %s', e)
```

### 写法 2：记录完整堆栈，推荐

```python
try:
    result = 10 / 0
except Exception:
    logging.exception('程序执行失败')
```

等价于：

```python
try:
    result = 10 / 0
except Exception:
    logging.error('程序执行失败', exc_info=True)
```

---

## 13. 日志配置的完整示例

### 示例 1：简单脚本日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info('程序开始')
logging.warning('这是一个警告')
logging.error('这是一个错误')
```

### 示例 2：项目中常见配置

```python
import logging

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug('debug 信息')
logger.info('info 信息')
logger.warning('warning 信息')
logger.error('error 信息')
```

### 示例 3：按大小切分日志文件

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('rotate_demo')
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024 * 1024,
    backupCount=3,
    encoding='utf-8'
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info('日志轮转示例')
```

### 示例 4：按时间切分日志文件

```python
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('time_rotate_demo')
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=7,
    encoding='utf-8'
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info('按天切分日志')
```

---

## 14. `RotatingFileHandler` 和 `TimedRotatingFileHandler` 常用参数

### `RotatingFileHandler`

```python
RotatingFileHandler(filename, maxBytes=0, backupCount=0, encoding=None)
```

| 参数 | 说明 |
|---|---|
| `filename` | 日志文件名 |
| `maxBytes` | 单个文件最大字节数，超过后轮转 |
| `backupCount` | 保留旧日志文件个数 |
| `encoding` | 文件编码 |

### `TimedRotatingFileHandler`

```python
TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=0)
```

| 参数 | 说明 |
|---|---|
| `filename` | 日志文件名 |
| `when` | 切分时间单位，如 `S` 秒、`M` 分、`H` 小时、`D` 天、`midnight` 半夜 |
| `interval` | 间隔数量 |
| `backupCount` | 保留旧日志数量 |

---

## 15. 日志配置进阶：`dictConfig`

项目稍大时，通常会把日志配置写成字典统一管理。

```python
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'app.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('app')
logger.info('dictConfig 配置成功')
```

### 常见字段

| 字段 | 说明 |
|---|---|
| `version` | 配置版本，固定为 `1` |
| `disable_existing_loggers` | 是否禁用已有 logger |
| `formatters` | 格式器配置 |
| `handlers` | 处理器配置 |
| `loggers` | 自定义 logger 配置 |
| `root` | 根 logger 配置 |

---

## 16. `propagate` 是什么

`logger` 默认会把日志继续传给父 logger，这叫传播。

如果你发现一条日志被打印了两次，通常是：

- 当前 logger 自己有 handler
- 父 logger 也有 handler
- 同一条日志传播后被重复处理

解决办法常常是：

```python
logger.propagate = False
```

或者在配置里写：

```python
'propagate': False
```

---

## 17. 常见坑

### 1）`basicConfig()` 不生效

因为它默认只在第一次配置时生效。

比如：

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
```

第二次通常不会生效。

如果你确实要强制重设：

```python
logging.basicConfig(level=logging.DEBUG, force=True)
```

### 2）日志重复输出

常见原因：

- 给同一个 logger 重复添加 handler
- `propagate=True` 导致父子 logger 重复处理

### 3）级别设置错位

```python
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.ERROR)
```

这时 `DEBUG` 和 `INFO` 仍然不会输出到这个 handler，因为 handler 只收 `ERROR` 及以上。

### 4）`exception()` 不在 `except` 中使用

虽然能调用，但没有当前异常上下文时，堆栈信息没有意义。

---

## 18. 和其他 Python 日志方案的对比

结论先说：**如果你要学日志体系本身，先学标准库 `logging`；如果你要在业务代码里更省心地写日志，`loguru` 是现在最常见的增强选择；如果你要结构化日志和可观测性接轨，`structlog` 更合适。**

Python 里常见的日志相关方案大概有这几类：

- 标准库 `logging`
- 第三方 `loguru`
- 第三方 `structlog`
- 很多框架自带的日志封装，比如 Django / FastAPI / Uvicorn / Gunicorn，本质上通常还是基于 `logging`

### 18.1 `logging` vs `print`

| 项目 | `print` | `logging` |
|---|---|---|
| 是否适合正式项目 | 不适合 | 适合 |
| 日志级别 | 没有 | 有 |
| 输出位置 | 只能简单输出 | 控制台、文件、网络等 |
| 格式控制 | 弱 | 强 |
| 异常堆栈 | 需要自己处理 | 内置支持 |
| 过滤与分流 | 几乎没有 | 完整支持 |

结论：

- 调试一两行代码可以用 `print`
- 正式项目不要拿 `print` 当日志系统

### 18.2 `logging` vs `loguru`

`loguru` 是目前 Python 社区里非常流行的第三方日志库之一，主打 **简单、好用、开箱即用**。

#### `loguru` 示例

```python
from loguru import logger

logger.add('app.log', rotation='10 MB', retention='7 days', encoding='utf-8')

logger.debug('调试信息')
logger.info('普通信息')
logger.error('错误信息')
```

#### 对比

| 维度 | `logging` | `loguru` |
|---|---|---|
| 是否标准库 | 是 | 否 |
| 学习成本 | 中等 | 很低 |
| 配置复杂度 | 偏高 | 低 |
| 默认体验 | 一般 | 很好 |
| 文件轮转 | 支持，但配置偏繁琐 | 非常方便 |
| 异常堆栈 | 支持 | 支持且更友好 |
| 结构化日志 | 一般 | 一定程度支持 |
| 三方生态兼容 | 最强 | 需要适配 |

#### `logging` 优点

- 标准库，自带，不依赖第三方
- 几乎所有 Python 框架都能兼容
- 配置能力完整，适合工程化项目
- 团队协作里更通用

#### `logging` 缺点

- API 偏老，第一次上手容易觉得啰嗦
- `logger`、`handler`、`formatter` 这些概念对新手有门槛
- 高级配置写起来不够直观

#### `loguru` 优点

- 开箱即用，代码短
- 文件切分、格式化、异常打印都很顺手
- 对个人项目、小中型服务特别友好

#### `loguru` 缺点

- 不是标准库
- 在大型团队项目中，未必所有人都愿意引入额外依赖
- 遇到一些框架或已有日志体系时，往往还是要和 `logging` 打通

结论：

- **学习日志基础：优先 `logging`**
- **个人项目 / 小中型项目想少写配置：可优先 `loguru`**
- **企业项目里如果已有统一日志规范，通常还是 `logging` 为主**

### 18.3 `logging` vs `structlog`

`structlog` 更偏向 **结构化日志**，很适合接入 ELK、OpenSearch、Datadog、Grafana Loki、云原生日志平台。

#### `structlog` 示例

```python
import structlog

logger = structlog.get_logger()
logger.info('user_login', user_id=1001, ip='127.0.0.1')
```

输出思路更接近：

```json
{"event": "user_login", "user_id": 1001, "ip": "127.0.0.1"}
```

#### 对比

| 维度 | `logging` | `structlog` |
|---|---|---|
| 核心定位 | 通用日志 | 结构化日志 |
| 文本日志支持 | 很强 | 可以 |
| JSON 日志 | 需要自己配 | 更擅长 |
| 日志字段扩展 | 可以，但不够优雅 | 很方便 |
| 可观测性平台接入 | 可以 | 更适合 |
| 学习门槛 | 中等 | 中高 |

结论：

- 如果你只是想记录文本日志，`structlog` 不一定有必要
- 如果你想要日志天然带字段、方便检索分析，`structlog` 更合适
- 很多团队会用 **`structlog` + `logging`**，而不是二选一

### 18.4 框架日志和标准库的关系

很多 Python Web 项目里，你看到的不是纯粹手写的 `logging`，而是：

- Django 配 `LOGGING`
- FastAPI / Uvicorn 输出访问日志
- Gunicorn 管理 worker 日志
- Celery 管理任务日志

但它们底层大多还是围绕标准库 `logging` 展开。

所以：

- **学会 `logging`，等于掌握 Python 生态里大部分日志系统的底层规则**
- 不管以后换 Django、FastAPI、Flask，理解都能复用

---

## 19. 当前项目里最流行的日志模块推荐

结论先说：

- **通用推荐：`logging` 仍然是主流基础方案**
- **开发体验推荐：`loguru` 是当前非常流行的增强方案**
- **可观测性 / 云原生推荐：`structlog` 更值得选**

这里的“最流行”要分场景，不是只有一个唯一答案。

### 19.1 如果你是初学者

推荐顺序：

1. **先学 `logging`**
2. 再了解 **`loguru`**
3. 有结构化日志需求时再看 **`structlog`**

原因很直接：

- `logging` 是标准库，必会
- `loguru` 是加分项，不是基础项
- `structlog` 偏工程化，不适合一上来就学

### 19.2 如果是普通后端项目

推荐：**优先 `logging`，需要更好体验时引入 `loguru`**。

适合场景：

- Flask / FastAPI / Django 常规业务系统
- 定时任务、爬虫、脚本服务
- 中小团队项目

建议：

- 团队统一规范强、框架集成要求高：用 `logging`
- 追求开发效率、代码简洁：可以考虑 `loguru`

### 19.3 如果是大一点的生产环境项目

推荐：**`logging` 或 `structlog + logging`**。

适合场景：

- 微服务
- 容器化部署
- 需要接日志平台检索分析
- 需要统一 trace_id / request_id / user_id

原因：

- 生产环境更关心结构化输出、字段检索、链路追踪
- `structlog` 在这类场景里比纯文本日志更有价值
- 但底层通常仍会和 `logging` 结合

### 19.4 现在怎么选最稳

可以直接按这个原则选：

#### 方案 A：最稳妥、最通用

**`logging`**

适合：

- 学习
- 面试
- 团队协作
- 框架集成
- 企业项目

#### 方案 B：最好上手、写起来最舒服

**`loguru`**

适合：

- 个人项目
- 小中型项目
- 追求开发效率

#### 方案 C：最适合结构化日志和日志平台

**`structlog` + `logging`**

适合：

- 微服务
- 云原生项目
- 需要 JSON 日志
- 要接 ELK / Loki / Datadog 等平台

### 19.5 一句话推荐

如果你只要一个结论：

- **必须掌握：`logging`**
- **日常开发很好用：`loguru`**
- **面向生产可观测性：`structlog`**

---

## 20. 实战建议

### 小脚本

直接用：

```python
logging.basicConfig(level=logging.INFO)
```

### 中小项目

使用：

- `getLogger(__name__)`
- `StreamHandler` + `FileHandler`
- 统一 `Formatter`

### 大项目

使用：

- `logging.config.dictConfig()`
- 日志按模块分 logger
- 文件轮转
- 异常统一记录堆栈
- 如果要结构化日志，考虑 `structlog`

---

## 21. 一个完整可运行示例

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('demo')
logger.setLevel(logging.DEBUG)
logger.propagate = False

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(
    'demo.log',
    maxBytes=1024 * 1024,
    backupCount=3,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def divide(a, b):
    logger.debug('开始计算: a=%s, b=%s', a, b)
    return a / b


try:
    logger.info('程序启动')
    result = divide(10, 2)
    logger.info('计算结果: %s', result)

    result = divide(10, 0)
    logger.info('计算结果: %s', result)
except Exception:
    logger.exception('程序运行异常')
```

---

## 22. 速记

可以先记住这几个核心点：

1. `basicConfig()`：快速配置
2. `getLogger(__name__)`：项目里常用
3. `logger + handler + formatter`：logging 核心三件套
4. `exception()`：记录异常堆栈
5. `RotatingFileHandler` / `TimedRotatingFileHandler`：管理日志文件
6. 日志推荐写法：

```python
logger.info('用户 %s 登录', username)
```

不是：

```python
logger.info(f'用户 {username} 登录')
```

7. 选型速记：

- 学基础：`logging`
- 图省事：`loguru`
- 要结构化：`structlog`

---

## 23. 一句话理解整体结构

可以把 `logging` 理解成：

- **Logger**：决定“记什么日志”
- **Handler**：决定“日志发到哪里”
- **Formatter**：决定“日志长什么样”
- **Filter**：决定“哪些日志能通过”

组合起来，就是一套完整日志系统。