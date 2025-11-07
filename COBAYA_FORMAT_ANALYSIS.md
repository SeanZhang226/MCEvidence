# Cobaya MCMC 输出格式分析

## 📊 格式特征

### 文件结构

```
数据目录/
├── MODEL.1.txt      # Chain 1
├── MODEL.2.txt      # Chain 2
├── MODEL.3.txt      # Chain 3
├── MODEL.4.txt      # Chain 4
├── MODEL.5.txt      # Chain 5
├── MODEL.6.txt      # Chain 6
├── MODEL.input.yaml      # 输入配置
├── MODEL.updated.yaml    # 更新后的配置
├── MODEL.covmat          # 协方差矩阵
├── MODEL.checkpoint      # 检查点
└── MODEL.progress        # 进度信息
```

---

## 🔍 Cobaya vs CosmoMC 格式对比

### **1. 文件命名**

| Format      | Chain Files                | Pattern          |
| ----------- | -------------------------- | ---------------- |
| **CosmoMC** | `name_1.txt`, `name_2.txt` | `{root}_{n}.txt` |
| **Cobaya**  | `NAME.1.txt`, `NAME.2.txt` | `{root}.{n}.txt` |

**关键差异：** Cobaya 使用 `.` 而不是 `_` 分隔

---

### **2. 文件内容格式**

#### **列结构**

```
# 第1列: weight         - 样本权重
# 第2列: minuslogpost   - 负对数后验 (-log posterior)
# 第3+列: 参数值        - H0, logA, ns, ombh2, omch2, tau, ...
# 后续列: 派生参数      - sigma8, omegam, S8, etc.
# 最后列: chi2          - 各似然函数的chi2值
```

#### **CosmoMC 格式：**

```
weight  -logL  param1  param2  param3  ...
  1.0   1234.5  0.022   0.12    0.96   ...
```

- 列顺序：`weight, -logL, parameters...`
- 第 2 列是 `-log(Likelihood)`

#### **Cobaya 格式：**

```
weight  minuslogpost  H0  logA  ns  ombh2  omch2  tau  ...  chi2  chi2__BAO  chi2__CMB  ...
  4.0   5520.028     71.89  3.07  0.99  0.023  0.128  0.062  ...  11043.5  10.4  11014.2  ...
```

- 列顺序：`weight, -logPost, parameters, derived, chi2s`
- 第 2 列是 `-log(Posterior)` (包含先验)
- 包含大量派生参数和 chi2 分解

---

### **3. 关键差异总结**

| 特征         | CosmoMC         | Cobaya                   |
| ------------ | --------------- | ------------------------ |
| **列名**     | 无表头 / 简单   | 详细表头 (首行)          |
| **第 2 列**  | `-log L` (似然) | `-log Post` (后验)       |
| **权重**     | 整数权重        | 浮点数权重               |
| **派生参数** | 较少            | 非常多 (sigma8, S8, etc) |
| **Chi2**     | 无              | 详细分解 (每个似然)      |
| **文件名**   | `name_N.txt`    | `name.N.txt`             |

---

## 🎯 适配策略

### **需要实现的功能**

#### 1. **文件名识别**

```python
# CosmoMC 模式
files = glob("chain_?.txt")  # chain_1.txt, chain_2.txt

# Cobaya 模式
files = glob("chain.?.txt")   # chain.1.txt, chain.2.txt
```

#### 2. **表头处理**

```python
# Cobaya 文件第一行是表头，以 '#' 开头
# 需要跳过或解析这一行
```

#### 3. **列索引调整**

```python
# CosmoMC:
# iw=0 (weight), ilike=1 (-logL), itheta=2 (parameters start)

# Cobaya:
# iw=0 (weight), ipost=1 (-logPost), itheta=2 (parameters start)
# 注意：minuslogpost = -log(Likelihood) - log(Prior)
```

#### 4. **权重处理**

```python
# CosmoMC: 整数权重 (1, 2, 3, ...)
# Cobaya: 浮点数权重 (4.0, 8.0, 15.0, ...)
# MCEvidence 已支持浮点权重
```

---

## 💡 实现方案

### **选项 A：扩展现有 MCSamples 类**

在 `load_from_file()` 中添加格式检测：

```python
def load_from_file(self, fname, **kwargs):
    # 检测格式
    if self._is_cobaya_format(fname):
        return self._load_cobaya(fname, **kwargs)
    else:
        return self._load_cosmomc(fname, **kwargs)
```

### **选项 B：创建新的 CobayaSamples 类**

```python
class CobayaSamples(SamplesMixin):
    def load_from_file(self, fname, **kwargs):
        # Cobaya specific loading
        ...
```

**推荐：选项 A** - 统一接口，自动检测格式

---

## 🔧 关键代码修改点

### 1. **文件名模式匹配**

```python
# 当前
flist = glob.glob(fname + '_?.txt')

# 需要同时支持
flist = glob.glob(fname + '.?.txt')  # Cobaya
if not flist:
    flist = glob.glob(fname + '_?.txt')  # CosmoMC fallback
```

### 2. **表头跳过**

```python
# 读取时检查首行
with open(file) as f:
    first_line = f.readline()
    if first_line.startswith('#'):
        # Cobaya format - skip header
        skiprows = 1
    else:
        skiprows = 0

data = np.loadtxt(file, skiprows=skiprows)
```

### 3. **Log-Likelihood 计算**

```python
# Cobaya 给的是 -log(Posterior)
# 如果需要 -log(Likelihood)，需要减去 prior:
# -logL = -logPost - (-logPrior)

# 但对于 MCEvidence，我们可以直接使用 -logPost
# 因为算法只需要相对概率
```

---

## 📝 测试计划

### 测试数据集

```
✅ ΛCDM 模型:
   - CMBBAO (6 chains)
   - CMBPANBAO (6 chains)
   - DESY5 (6 chains)
   - Union3 (6 chains)

✅ EDE+PPF 模型:
   - sCMBBAO (6 chains)
   - sCMBPANBAO (5 chains)
   - sDESY5 (5 chains)
   - sUnion3 (5 chains)
```

### 验证指标

1. **文件读取成功率** - 所有链文件正确加载
2. **样本数统计** - 与原始文件行数一致
3. **权重求和** - 验证权重正确读取
4. **参数范围** - 检查参数值在合理范围内
5. **证据估算** - 计算 ln(Z) 并比较模型

---

## 🚀 下一步

1. ✅ 分析格式差异 (完成)
2. ⏭️ 实现 Cobaya 格式加载器
3. ⏭️ 编写测试脚本
4. ⏭️ 验证证据计算
5. ⏭️ 比较模型贝叶斯因子
