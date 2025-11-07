# Cobaya 格式使用指南

## 快速开始

### 1. 基本使用

```python
from MCEvidence import MCEvidence

# 自动检测 Cobaya 格式并计算证据
mce = MCEvidence(
    "/path/to/chains/basename",  # 不带 .N.txt 后缀
    kmax=5,
    burnlen=0.3,
    verbose=1
)

# 计算贝叶斯证据
ln_evidence = mce.evidence()
print(f"ln(Z) = {ln_evidence[1]:.3f}")  # k=2 通常最稳定
```

### 2. 参数选择

默认情况下，MCEvidence 会：

1. 自动检测 Cobaya 格式
2. 从 `.updated.yaml` 文件读取参数信息
3. 使用所有**采样参数**（排除 derived 参数）

#### 只使用 Cosmological 参数

```python
mce = MCEvidence("/path/to/chains/basename", kmax=5, burnlen=0.3)

# 手动设置 ndim 为 cosmological 参数数量
if hasattr(mce.gd, 'cobaya_param_info'):
    param_info = mce.gd.cobaya_param_info
    mce.ndim = param_info['n_cosmo']  # 只用 cosmological 参数
    print(f"Cosmological params: {param_info['cosmo_params']}")

ln_evidence = mce.evidence()
```

#### 包括 Nuisance 参数

```python
mce = MCEvidence("/path/to/chains/basename", kmax=5, burnlen=0.3)

# 使用所有采样参数（cosmological + nuisance）
if hasattr(mce.gd, 'cobaya_param_info'):
    param_info = mce.gd.cobaya_param_info
    mce.ndim = param_info['n_sampled']  # 全部采样参数
    print(f"All sampled params: {param_info['sampled_params']}")

ln_evidence = mce.evidence()
```

### 3. 查看参数信息

```python
mce = MCEvidence("/path/to/chains/basename", kmax=5, burnlen=0.3)

if hasattr(mce.gd, 'cobaya_param_info'):
    info = mce.gd.cobaya_param_info
    print(f"Cosmological parameters ({info['n_cosmo']}): {info['cosmo_params']}")
    print(f"Nuisance parameters ({info['n_nuisance']}): {info['nuisance_params']}")
    print(f"Total sampled: {info['n_sampled']}")
```

### 4. 模型比较

```python
import numpy as np

# 计算模型 1
mce1 = MCEvidence("model1/chains/base", kmax=5, burnlen=0.3)
ln_Z1 = mce1.evidence()[1]  # k=2

# 计算模型 2
mce2 = MCEvidence("model2/chains/base", kmax=5, burnlen=0.3)
ln_Z2 = mce2.evidence()[1]  # k=2

# 贝叶斯因子
ln_BF = ln_Z2 - ln_Z1
BF = np.exp(ln_BF)

print(f"ln(B_21) = {ln_BF:.3f}")
print(f"B_21 = {BF:.2e}")

# 解释
if ln_BF > 5:
    print("Very strong evidence for Model 2")
elif ln_BF > 2.5:
    print("Strong evidence for Model 2")
elif ln_BF > 1:
    print("Moderate evidence for Model 2")
elif ln_BF > -1:
    print("Inconclusive")
elif ln_BF > -2.5:
    print("Moderate evidence for Model 1")
elif ln_BF > -5:
    print("Strong evidence for Model 1")
else:
    print("Very strong evidence for Model 1")
```

## 文件结构要求

### Cobaya 输出文件

```
your_analysis/
├── basename.updated.yaml    # 参数配置（必需）
├── basename.input.yaml      # 输入配置（可选）
├── basename.1.txt           # 链文件 1
├── basename.2.txt           # 链文件 2
├── basename.3.txt           # 链文件 3
└── ...
```

### 链文件格式

```
# weight  minuslogpost  H0  logA  ns  ombh2  omch2  tau  ...  sigma8  omegam  ...
  4.0     5520.028      71.89  3.072  0.987  0.0228  0.128  0.062  ...  0.838  0.294  ...
  8.0     5520.252      71.83  3.072  0.987  0.0228  0.128  0.062  ...  0.837  0.294  ...
  ...
```

- 第一行：`#` 开头的 header（列名）
- 第一列：weight
- 第二列：-log(posterior) 或 -log(likelihood)
- 后续列：采样参数 + derived 参数 + chi2 组件

## 常见问题

### Q1: 如何知道使用了哪些参数？

A: 查看日志输出：

```
INFO:MCEvidence.py._get_cobaya_sampled_params():731  Found 18 sampled parameters
INFO:MCEvidence.py._get_cobaya_sampled_params():734  - Cosmological: 9 ['H0', 'logA', ...]
INFO:MCEvidence.py._get_cobaya_sampled_params():735  - Nuisance: 9 ['A_planck', 'amp_143', ...]
```

### Q2: 特征值为负怎么办？

A: 这通常意味着：

1. 使用了过多参数（包括 derived）
2. 某些参数几乎不变化（协方差接近零）

**解决方案**：

- 减少 `ndim`，只使用 cosmological 参数
- 检查是否包含了 fixed 参数
- 确保使用的是 sampled 参数，不是 derived

### Q3: Cobaya 和 CosmoMC 格式有什么区别？

A: 主要区别：

| 特性         | CosmoMC          | Cobaya          |
| ------------ | ---------------- | --------------- |
| 文件命名     | `base_1.txt`     | `base.1.txt`    |
| Header       | 无               | 有（`#` 开头）  |
| 参数信息文件 | `.ranges`        | `.updated.yaml` |
| 参数分类     | 通过 ranges 文件 | YAML 中明确标记 |

**MCEvidence 会自动检测格式，无需用户指定！**

### Q4: 如何选择 k 值？

A:

- 默认 `kmax=5` 会计算 k=1,2,3,4 的证据
- k=2 通常最稳定和可靠
- 不同 k 的结果应该相近（差异 < 1）
- 如果差异很大，可能需要：
  - 增加样本数
  - 检查 burn-in 是否充分
  - 减少参数维度

### Q5: 是否应该包括 nuisance 参数？

A: 取决于科学目标：

**包括 nuisance**（推荐用于模型比较）：

- 更保守的估计
- 考虑了系统误差的不确定性
- 对于不同 nuisance 参数的模型更公平

**不包括 nuisance**（用于理论参数约束）：

- 聚焦于 cosmological 参数
- 假设 nuisance 参数已知/固定
- 计算更快

## 性能提示

### 1. Burn-in

```python
# 建议 30% burn-in
mce = MCEvidence("chains/base", burnlen=0.3)
```

### 2. Thinning

```python
# 通常不需要 thinning（thinlen=1）
# 除非链有很强的自相关
mce = MCEvidence("chains/base", thinlen=1)
```

### 3. 批处理

```python
# 对于多个数据集，串行处理即可
# 每个计算是独立的
for dataset in datasets:
    mce = MCEvidence(f"chains/{dataset}", kmax=5, burnlen=0.3)
    ln_Z = mce.evidence()
    results[dataset] = ln_Z
```

## 示例：完整分析脚本

见 `test_cobaya.py` 获取完整的示例代码，包括：

- 批量处理多个数据集
- 模型比较和贝叶斯因子计算
- 结果导出到 CSV
- 参数模式选择

## 更多信息

- 算法论文: Heavens et al. (2017), Physical Review Letters, 119(10), 101301
- GitHub: https://github.com/yabebalFantaye/MCEvidence
- 实施详情: 见 `COBAYA_IMPLEMENTATION_SUMMARY.md`
