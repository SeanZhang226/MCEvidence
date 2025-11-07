# MCEvidence 架构分析与改进建议

## 📊 当前架构概览

### 核心类结构

```
MCEvidence (主类 - 证据计算)
    └── MCSamples (MCMC样本管理)
            └── SamplesMIXIN (样本处理工具方法)
                    ├── data_set (数据容器)
                    └── LoggingHandler (日志处理)
```

---

## 🔍 详细分析

### 1️⃣ **类设计分析**

#### ✅ **优点：**

- **职责分离清晰**：`SamplesMIXIN` 处理样本操作，`MCEvidence` 负责证据计算
- **灵活的输入**：支持文件路径、数组、字典多种输入格式
- **可扩展性**：MIXIN 模式便于添加新功能

#### ⚠️ **可改进点：**

**A. 过时的类继承方式**

```python
# 当前 (Python 2 风格)
class MCEvidence(object):
    pass

# 建议改为 (Python 3 风格)
class MCEvidence:
    pass
```

**为什么改？** Python 3 中所有类都默认继承自 object，显式写出是冗余的。

---

**B. LoggingHandler 类设计问题**

```python
# 当前：定义了但从未使用
class LoggingHandler(object):
    def set_logger(self):
        self.logger = logging.getLogger(self.log_message())
    def log_message(self):
        import inspect
        stack = inspect.stack()
        return str(stack[2][4])
```

**建议：** 删除这个类，因为代码中实际使用的是直接的 `logging.getLogger(__name__)`

---

**C. data_set 类应该是 dataclass**

```python
# 当前
class data_set(object):
    def __init__(self, d):
        self.samples = d['samples']
        self.weights = d['weights']
        self.loglikes = d['loglikes']
        self.adjusted_weights = d['aweights']

# 建议使用 dataclass (更现代、更简洁)
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class ChainData:
    """Container for MCMC chain data."""
    samples: np.ndarray
    weights: np.ndarray
    loglikes: np.ndarray
    adjusted_weights: np.ndarray
    ichain: Optional[np.ndarray] = None
```

**为什么改？**

- 自动生成 `__init__`, `__repr__`, `__eq__` 等方法
- 类型提示更清晰
- 代码更简洁、更易维护

---

### 2️⃣ **异常处理问题**

#### ⚠️ **裸 except 语句 (反模式)**

```python
# 当前 - 在多处出现
try:
    from getdist import MCSamples
    use_getdist = True
except:  # ❌ 捕获所有异常，包括KeyboardInterrupt
    use_getdist = False
```

**建议改进：**

```python
# 更好的做法
try:
    from getdist import MCSamples
    use_getdist = True
except ImportError:  # ✅ 只捕获导入错误
    use_getdist = False
    logger.info("getdist not available, using built-in chain reader")
```

**为什么改？**

- 裸 except 会捕获 `KeyboardInterrupt`, `SystemExit` 等不应该被捕获的异常
- 明确指定异常类型让代码意图更清晰
- 便于调试

---

### 3️⃣ **文件路径处理**

#### ⚠️ **使用字符串拼接路径**

```python
# 当前
if not os.path.isfile(flist[0]):
    if '*' in fname or '?' in fname:
        flist = glob.glob(fname)
    else:
        flist = [fname + '_{}.txt'.format(idchain)]
```

**建议使用 pathlib：**

```python
from pathlib import Path

# 更现代的方式
fname_path = Path(fname)
if not fname_path.is_file():
    if '*' in str(fname) or '?' in str(fname):
        flist = list(fname_path.parent.glob(fname_path.name))
    else:
        flist = [fname_path.parent / f"{fname_path.stem}_{idchain}.txt"]
```

**为什么改？**

- 跨平台兼容性更好
- 代码更清晰易读
- 避免路径分隔符错误

---

### 4️⃣ **命名规范问题**

#### ⚠️ **不一致的命名**

```python
# 混合使用
gsape()      # 拼写错误？应该是 get_shape?
SamplesMIXIN # 应该是 SamplesMixin (驼峰命名)
data_set     # 应该是 DataSet (类名应该是驼峰)
```

**建议统一命名规范：**

- **类名**：UpperCamelCase (`ChainData`, `SamplesMixin`)
- **函数/方法**：snake_case (`get_shape`, `load_from_file`)
- **常量**：UPPER_SNAKE_CASE (`COSMO_PARAMS_LIST`)

---

### 5️⃣ **代码组织与模块化**

#### ⚠️ **单文件包含所有内容 (1700 行)**

**当前结构：**

```
MCEvidence.py (1700 lines)
├── Imports & Constants
├── Helper Classes (LoggingHandler, data_set, SamplesMIXIN)
├── MCSamples Class
├── MCEvidence Class
├── Utility Functions
└── Main Script
```

**建议重构为模块化结构：**

```
MCEvidence/
├── __init__.py              # 导出主要API
├── core.py                  # MCEvidence核心计算类
├── samples.py               # MCSamples, SamplesMixin
├── data_structures.py       # ChainData等数据类
├── io/
│   ├── __init__.py
│   ├── cosmomc.py          # CosmoMC格式读取
│   ├── montepython.py      # MontePython格式读取
│   └── cobaya.py           # Cobaya格式读取 (新增)
├── utils/
│   ├── __init__.py
│   ├── params.py           # 参数处理函数
│   └── thinning.py         # 链稀疏化算法
└── cli.py                   # 命令行接口
```

**为什么改？**

- 易于维护和测试
- 便于添加新功能（如 cobaya 支持）
- 降低单个文件的复杂度
- 更好的代码重用

---

### 6️⃣ **类型提示缺失**

#### ⚠️ **没有类型注解**

```python
# 当前
def get_samples(self, nsamples, istart=0, rand=False, name="s1", prewhiten=True):
    # ...
    return s, lnp, w, {'J': Jacobian, 'eVec': eigenVec, 'eVal': eigenVal}
```

**建议添加类型提示：**

```python
from typing import Tuple, Dict, Optional
import numpy as np

def get_samples(
    self,
    nsamples: int,
    istart: int = 0,
    rand: bool = False,
    name: str = "s1",
    prewhiten: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, any]]:
    """
    Get samples from the chain.

    Parameters
    ----------
    nsamples : int
        Number of samples to retrieve
    istart : int, optional
        Starting index (default: 0)
    rand : bool, optional
        Random sampling if True (default: False)
    name : str, optional
        Partition name ('s1' or 's2', default: 's1')
    prewhiten : bool, optional
        Apply prewhitening transformation (default: True)

    Returns
    -------
    samples : np.ndarray
        Parameter samples
    loglikes : np.ndarray
        Log-likelihood values
    weights : np.ndarray
        Sample weights
    diagnostics : dict
        Dictionary containing Jacobian and eigenvalue/vector info
    """
    # ...
```

**为什么改？**

- 更好的 IDE 支持（自动补全）
- 编译时类型检查
- 自文档化代码
- 减少 bugs

---

### 7️⃣ **配置管理**

#### ⚠️ **硬编码的常量**

```python
# 散落在代码各处
cosmo_params_list = ['omegabh2', 'omegach2', ...]
FORMAT = "%(levelname)s:%(filename)s.%(funcName)s():%(lineno)-8s %(message)s"
```

**建议集中管理配置：**

```python
# config.py
from dataclasses import dataclass
from typing import List

@dataclass
class MCEvidenceConfig:
    """Configuration for MCEvidence."""

    # Logging
    log_format: str = "%(levelname)s:%(filename)s.%(funcName)s():%(lineno)-8s %(message)s"
    default_log_level: int = logging.INFO

    # MCMC Parameters
    cosmo_params: List[str] = None
    default_kmax: int = 5
    default_burnin: float = 0.0
    default_thin: float = 0.0

    def __post_init__(self):
        if self.cosmo_params is None:
            self.cosmo_params = [
                'omegabh2', 'omegach2', 'theta', 'tau', 'omegak',
                # ... 其他参数
            ]

# 使用
config = MCEvidenceConfig()
```

---

### 8️⃣ **文档字符串改进**

#### ⚠️ **不一致的文档风格**

```python
# 有些有详细文档，有些没有
def thin_indices(self, factor, name='s1', weights=None):
    """
    Ref:
    http://getdist.readthedocs.io/en/latest/_modules/getdist/chains.html#WeightedSamples.thin
    ...
    """
```

**建议统一使用 NumPy/Google 风格：**

```python
def thin_indices(
    self,
    factor: int,
    name: str = 's1',
    weights: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Thin samples to reduce chain size while preserving information.

    Parameters
    ----------
    factor : int
        Thinning factor. Must be an integer.
    name : str, optional
        Partition name ('s1' or 's2'), by default 's1'
    weights : np.ndarray, optional
        Weight array. If None, uses self.data[name].weights

    Returns
    -------
    indices : np.ndarray
        Indices of samples to keep after thinning
    weights : np.ndarray
        Corresponding weights

    Raises
    ------
    ValueError
        If weights are not integers or factor is not an integer

    References
    ----------
    .. [1] GetDist documentation: https://getdist.readthedocs.io/

    Examples
    --------
    >>> indices, weights = self.thin_indices(factor=10)
    """
```

---

## 🎯 推荐的改进优先级

### 🔴 **高优先级（不影响核心计算逻辑）**

1. ✅ **移除 LoggingHandler 类** - 未使用的代码
2. ✅ **修复裸 except 语句** - 改进错误处理
3. ✅ **统一类命名** - `object` → 移除，`data_set` → `ChainData`
4. ✅ **添加类型提示** - 从公共 API 开始

### 🟡 **中优先级**

5. ✅ **使用 pathlib** - 改进文件路径处理
6. ✅ **使用 dataclass** - 简化数据类
7. ✅ **统一文档字符串** - 提高可维护性
8. ✅ **配置管理** - 集中管理常量

### 🟢 **低优先级（可选）**

9. ⚪ **模块化重构** - 拆分大文件（可以在 cobaya 适配后进行）
10. ⚪ **添加单元测试** - 提高代码质量
11. ⚪ **性能优化** - 分析瓶颈并优化

---

## 💡 具体实施建议

### 阶段 4 改进计划（不影响核心逻辑）

#### 步骤 1: 清理未使用代码

- 删除 `LoggingHandler` 类
- 移除显式的 `(object)` 继承

#### 步骤 2: 改进异常处理

- 所有裸 `except:` 改为具体异常类型
- 添加适当的日志记录

#### 步骤 3: 现代化数据结构

- `data_set` → `ChainData` (使用 dataclass)
- `namedtuple` → `dataclass` (如果需要可变性)

#### 步骤 4: 添加类型提示

- 先为主要公共方法添加
- 使用 `typing` 模块的类型

#### 步骤 5: 改进路径处理

- `os.path` → `pathlib.Path`
- 字符串拼接 → Path 对象操作

---

## 📝 保持不变的部分（核心算法）

**这些方法包含核心计算逻辑，不应修改：**

- ✅ `evidence()` - 主要证据计算算法
- ✅ `diagonalise_chain()` - 链对角化
- ✅ `get_covariance()` - 协方差计算
- ✅ k-NN 距离计算部分
- ✅ 后验概率计算公式

**可以安全改进的辅助功能：**

- ✅ 文件 I/O 操作
- ✅ 日志记录
- ✅ 参数验证
- ✅ 错误消息
- ✅ 数据结构封装

---

## 🚀 下一步行动

您希望我从哪个改进开始？

**选项 A:** 先进行高优先级的代码清理（移除冗余、修复异常处理）
**选项 B:** 直接跳到 Cobaya 格式适配
**选项 C:** 让我先做几个示例性的改进，您看看效果再决定

请告诉我您的选择！ 😊
