# Python 进阶语法知识点整理

## 1. 类、对象、实例方法

类可以理解成一种“模板”或“蓝图”，对象则是根据这个模板创建出来的具体实例。比如“学生”是一个抽象概念，而“张三”这个具体学生对象才是真正参与程序运行的实体。类里可以定义属性和方法，属性描述对象的数据，方法描述对象的行为。

实例方法是最常见的一种方法，它的第一个参数通常写成 `self`，表示当前对象本身。调用实例方法时，Python 会自动把当前对象传进去，所以你通常只需要写 `obj.method()`，不用手动传 `self`。

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁"


s1 = Student("张三", 18)
print(s1.name)
print(s1.introduce())
```

这段代码里，`Student` 是类，`s1` 是对象，`introduce` 是实例方法。`__init__` 是初始化方法，在对象创建时自动执行，用来给对象设置初始状态。

理解类和对象时，关键是分清两层：类定义的是“规则”，对象承载的是“具体数据”。同一个类可以创建很多对象，每个对象的数据可以不同，但都共享类定义的方法。

---

## 2. 继承、多态

继承表示子类可以复用父类的属性和方法。它解决的是“代码重复”和“层次关系”两个问题。如果多个类有一部分共同特征，就可以把公共部分抽到父类里，子类只保留自己特有的逻辑。

```python
class Animal:
    def eat(self):
        return "吃东西"


class Dog(Animal):
    def bark(self):
        return "汪汪"


d = Dog()
print(d.eat())
print(d.bark())
```

这里 `Dog` 继承了 `Animal`，所以 `Dog` 对象可以直接调用 `eat()`。这就是继承最直接的效果：子类天然拥有父类已有能力。

多态的重点不是语法，而是同一个调用动作，在不同对象上表现出不同结果。比如不同对象都实现了 `speak()` 方法，外部统一调用 `obj.speak()`，但最终输出不同，这就是多态。

```python
class Dog:
    def speak(self):
        return "汪汪"


class Cat:
    def speak(self):
        return "喵喵"


def make_sound(animal):
    print(animal.speak())


make_sound(Dog())
make_sound(Cat())
```

从效果上看，调用方式是统一的，变化的是对象本身。多态的价值在于让代码更容易扩展，因为调用方不需要为每种对象都写一套分支逻辑，只要约定好行为接口即可。

继承和多态经常一起出现，但它们不是一回事。继承强调“子类获得父类能力”，多态强调“统一调用接口，不同对象有不同表现”。很多时候多态可以基于继承实现，也可以不依赖继承实现。

---

## 3. 鸭子类型

鸭子类型是 Python 很典型的一种设计风格，它不太关心一个对象是不是某个指定类的实例，而更关心这个对象有没有你需要的方法。简单说就是：只要它行为上能完成任务，就可以拿来用。

```python
class Dog:
    def speak(self):
        return "汪汪"


class Person:
    def speak(self):
        return "你好"


def say(obj):
    print(obj.speak())


say(Dog())
say(Person())
```

这里 `say()` 不要求参数必须是 `Dog` 或某个父类，只要对象能调用 `speak()` 就行。`Dog` 和 `Person` 明明没有继承关系，但都可以被 `say()` 正常处理，这就是鸭子类型。

它的优点是灵活，代码不容易被死板的类型关系绑住。尤其在 Python 这种动态语言里，很多时候与其强制对象来自同一个父类，不如直接关注它是否具备某种能力。

它的风险也很明显：如果传进来的对象没有 `speak()`，那错误不会在定义阶段暴露，而是在运行时才报出来。所以鸭子类型很适合灵活开发，但在大型项目里，往往需要配合抽象类或类型提示来增加约束。

鸭子类型和多态关系很近。你可以理解为，在 Python 里，多态很多时候不是靠严格继承体系建立的，而是靠“对象具备相同行为”实现的。

---

## 4. 魔法函数

魔法函数是 Python 里一类特殊方法，名字通常是前后各两个下划线，比如 `__init__`、`__str__`、`__len__`。它们的作用不是让代码更花哨，而是告诉 Python：当对象遇到某种语法场景时，应该怎么响应。

最常见的一个是 `__init__`，它负责对象初始化。另一个常见的是 `__str__`，它控制 `print(obj)` 时显示什么内容。如果不写 `__str__`，打印对象通常只会看到一串内存地址风格的信息；写了之后，对象可以更友好地展示出来。

```python
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User(name={self.name})"


u = User("Tom")
print(u)
```

除了这两个，还有 `__len__`，可以让对象支持 `len(obj)`；`__getitem__`，可以让对象支持 `obj[index]`；`__call__`，可以让对象像函数一样调用。这些能力本质上都是在定义“对象如何像 Python 内置对象那样工作”。

```python
class MyList:
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


nums = MyList([10, 20, 30])
print(len(nums))
print(nums[1])
```

学习魔法函数时要抓住一点：它们不是随便写着玩的，而是在某些语言机制下会被自动调用。只有当对象确实需要支持某种自然语义时，才值得实现对应的魔法函数。比如一个“订单对象”适不适合实现 `__len__`，就要看“长度”对它来说有没有明确意义。如果没有，硬加只会让代码语义变怪。

---

## 5. `abc` 抽象类

`abc` 是 Python 标准库里的抽象基类工具，用来定义“规范型父类”。它的重点不在于复用代码，而在于规定：某些子类必须实现哪些方法。

```python
from abc import ABC, abstractmethod


class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass


class Dog(Animal):
    def speak(self):
        return "汪汪"
```

这里 `Animal` 继承了 `ABC`，说明它是抽象基类；`speak()` 被 `@abstractmethod` 标记后，就表示这是一个抽象方法，子类必须实现。如果某个子类没有实现这个方法，那么这个子类就不能正常实例化。

抽象类最重要的价值是把“约定”变成“强制规则”。如果没有抽象类，团队里大家只能靠口头约定：“所有模型工厂都要有 `generator()` 方法”。但口头约定很容易失效，有人可能写成 `build()`，有人可能漏写。抽象类可以在实例化阶段就直接报错，迫使子类遵守统一接口。

它特别适合用在框架层、基类层、工厂层这类“要约束多个实现”的地方。如果只是简单脚本，只有一两个类，也没有统一接口需求，那抽象类往往没有必要，反而会让代码层级变多。

抽象类和鸭子类型看起来像两种相反思路，但其实是两种不同场景下的取舍。鸭子类型更灵活，抽象类更严格。前者强调“有这个能力就能用”，后者强调“必须按这个规范实现”。

---

## 6. `classmethod`、`staticmethod`、`property`

这三个经常放在一起讲，因为它们都和“方法怎么绑定”“属性怎么访问”有关。

### 6.1 `classmethod`

类方法的第一个参数通常写成 `cls`，表示当前类本身，而不是某个对象。它适合处理与“类”相关的逻辑，比如读取类属性，或者提供备用构造方式。

```python
class User:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"])


u = User.from_dict({"name": "Tom"})
print(u.name)
```

这里 `from_dict()` 不依赖某个已存在的对象，而是根据字典创建新对象，所以很适合写成类方法。它本质上是一种“备用构造器”。

### 6.2 `staticmethod`

静态方法既不依赖对象，也不依赖类状态。它只是逻辑上属于这个类，所以放在类里面。

```python
class MathTool:
    @staticmethod
    def add(a, b):
        return a + b


print(MathTool.add(1, 2))
```

如果一个函数和类有关联，但里面完全用不到 `self` 和 `cls`，就可以考虑写成静态方法。它的主要意义是组织代码，而不是访问状态。

### 6.3 `property`

`property` 允许你把方法伪装成属性访问。外部看起来像在读写字段，内部实际上可以运行逻辑，比如校验、转换、只读控制。

```python
class Student:
    def __init__(self, score):
        self._score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not 0 <= value <= 100:
            raise ValueError("分数必须在 0 到 100 之间")
        self._score = value


s = Student(80)
print(s.score)
s.score = 95
```

这里外部写 `s.score`，像在访问普通属性，但内部其实经过了方法控制。这种写法的好处是：对外接口保持自然，对内逻辑保留控制权。

理解这三个概念时，可以用一句话区分：实例方法处理对象状态，类方法处理类层级逻辑，静态方法只是放在类里的普通工具函数，`property` 则是在保持属性写法的同时，对访问过程进行封装。

---

## 7. 工厂函数、工厂类、组合

工厂函数和工厂类解决的是“对象怎么创建更合理”这个问题。组合解决的是“类和类之间怎么协作更灵活”这个问题。这三个概念经常一起出现，因为它们都和“设计结构”有关。

### 7.1 工厂函数

工厂函数就是由一个函数统一负责对象创建，而不是让外部到处直接实例化具体类。调用方只需要告诉它需求，不需要关心具体创建过程。

```python
class Dog:
    pass

class Cat:
    pass


def animal_factory(animal_type):
    if animal_type == "dog":
        return Dog()
    elif animal_type == "cat":
        return Cat()
    raise ValueError("未知类型")
```

工厂函数适合对象创建逻辑开始有分支、默认值、参数处理的时候。它最大的价值是把“创建逻辑”集中起来，避免业务代码里到处写实例化细节。

### 7.2 工厂类

当创建逻辑更复杂，或者你希望不同创建器遵守统一规范时，就可以把工厂做成类。比如不同模型工厂都提供 `create()` 或 `generator()` 方法，这样外部调用方式统一，后续扩展也更稳。

```python
from abc import ABC, abstractmethod


class BaseFactory(ABC):
    @abstractmethod
    def create(self):
        pass


class DogFactory(BaseFactory):
    def create(self):
        return Dog()
```

工厂类相比工厂函数，优势不在“能不能创建对象”，而在“能不能形成统一结构”。当项目里创建逻辑越来越多时，类的组织能力会比散落函数更强。

### 7.3 组合

组合是指一个对象内部持有另一个对象，并借助它完成工作。它表达的不是“是什么”，而是“拥有什么能力”。

```python
class Engine:
    def start(self):
        return "引擎启动"


class Car:
    def __init__(self):
        self.engine = Engine()

    def run(self):
        return self.engine.start() + "，汽车开始行驶"
```

这里 `Car` 不是 `Engine` 的子类，但它内部组合了一个 `Engine` 对象。这样做比继承更灵活，因为你可以替换内部组件，而不必强行建立父子关系。

什么时候用继承，什么时候用组合，可以用一句话判断：如果是“本质上属于同一类事物”，考虑继承；如果只是“想复用某种能力”，优先组合。很多时候组合比继承更灵活，也更符合现实建模。

---

## 8. 装饰器

装饰器的本质是在不改原函数代码的前提下，给函数增加额外能力。它常被用来做日志、权限校验、计时、重试、缓存这些“和业务无关但经常重复”的逻辑。

```python
def log(func):
    def wrapper(*args, **kwargs):
        print("函数开始执行")
        result = func(*args, **kwargs)
        print("函数执行结束")
        return result
    return wrapper


@log
def add(a, b):
    return a + b


print(add(1, 2))
```

这里 `@log` 就是在给 `add()` 外面包一层壳。调用 `add(1, 2)` 时，实际上先进入 `wrapper()`，执行额外逻辑后再调用原函数。

装饰器解决的是“横切逻辑复用”问题。所谓横切逻辑，就是很多函数都需要，但它又不属于函数本身的核心业务。如果把日志、计时这些逻辑直接写进每个函数，代码会很重复，也容易污染主流程。装饰器可以把这些共性逻辑抽出来，让业务函数保持更干净。

不过装饰器也不要滥用。装饰器层层嵌套后，调试会变麻烦，调用链也会变复杂。所以一个简单原则是：当某种增强逻辑有复用价值时再抽成装饰器，如果只在一个地方临时用一下，直接写清楚反而更合适。

---

## 9. 生成器

生成器是一种“按需产生数据”的机制。它和列表最大的区别是：列表会一次性把所有结果都算出来放进内存，而生成器是你要一个，它给一个。

```python
def count_up(n):
    i = 1
    while i <= n:
        yield i
        i += 1


for x in count_up(3):
    print(x)
```

这里的 `yield` 是关键。只要函数里出现了 `yield`，这个函数就不再是普通函数，而会变成一个生成器函数。调用它不会立刻执行完整逻辑，而是返回一个生成器对象。每次迭代时，函数才继续往下执行，产出下一个值。

生成器的核心价值是节省内存，特别适合大量数据处理、流式读取、逐步计算等场景。比如读取大文件时，如果一口气读完所有内容，内存压力会很大；如果一行一行产出，就会轻很多。

它的另一个价值是“惰性计算”。也就是说，很多结果只有在真正需要时才会被计算出来。这在数据管道、分页处理、流式输出等场景里很有用。

学习生成器时，重点不是背 `yield` 的语法，而是理解：它把“先全部准备好再交付”改成了“边生产边交付”。这是它和普通函数、普通列表之间最本质的区别。

---

## 10. 上下文管理器

上下文管理器主要是为了解决资源管理问题。最常见的例子就是文件操作：文件打开后，正常情况下要记得关闭；如果中间报错，也一样要关闭。手动写这套清理逻辑很容易遗漏，所以 Python 提供了 `with` 机制。

```python
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

这段代码的好处不是少写一行 `close()`，而是无论读取过程是否异常，文件最终都会被正确关闭。也就是说，上下文管理器把“进入资源使用阶段”和“退出资源使用阶段”统一管理起来了。

你也可以自己定义上下文管理器，本质上是实现 `__enter__` 和 `__exit__` 两个方法。

```python
class MyContext:
    def __enter__(self):
        print("进入上下文")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("退出上下文")


with MyContext():
    print("处理中")
```

进入 `with` 代码块时会调用 `__enter__`，离开时会调用 `__exit__`。即使中间发生异常，也会执行退出逻辑。这种机制特别适合管理文件、数据库连接、网络连接、锁等“拿到后必须释放”的资源。

上下文管理器的价值不只是语法优雅，更重要的是它让资源管理变得可靠。很多 bug 不是业务逻辑错了，而是资源没有正确释放，时间一长就会拖垮系统。`with` 的意义就在于把这件事标准化。

---

## 11. 总结

如果把这几个知识点串起来看，它们其实都在解决两个核心问题：一是对象如何被设计和使用，二是代码如何在变复杂时仍然保持清晰。类、对象、实例方法是基础；继承、多态、鸭子类型是在讨论对象之间如何协作；魔法函数是在定义对象和 Python 语法之间的交互方式；抽象类是在约束结构；类方法、静态方法、`property` 是在细化类内部接口；工厂函数、工厂类、组合是在优化代码组织；装饰器、生成器、上下文管理器则是在提升复用性、性能和资源安全性。

这些知识点不需要一口气全记住。真正重要的是理解每个概念解决的是什么问题。只要你知道它为什么存在，后面遇到具体场景时，自然会知道该不该用。