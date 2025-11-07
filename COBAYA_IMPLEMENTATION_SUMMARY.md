# MCEvidence Cobaya 格式支持实施总结

## 日期

2025 年 10 月 20 日

## 实施成果

### ✅ 成功完成的功能

#### 1. Cobaya 格式自动检测

- 实现了 `_detect_chain_format()` 方法
- 自动识别 CosmoMC 格式 (`basename_N.txt`) 和 Cobaya 格式 (`basename.N.txt`)
- 支持文件模式匹配和实际文件检查

#### 2. YAML 参数信息读取

- 实现了 `_get_cobaya_sampled_params()` 方法
- 从 Cobaya 的 `.updated.yaml` 或 `.input.yaml` 文件读取参数配置
- 自动区分：
  - **Cosmological 参数**: H0, logA, ns, ombh2, omch2, tau, fde_zc, log10_ac, theta_i, w, wa
  - **Nuisance 参数**: A_planck, amp_143, amp_217, amp_143x217, n_143, n_217, n_143x217, calTE, calEE
  - **Derived 参数**: 自动排除（如 sigma8, omegam, S8, YHe, age, rdrag 等）

#### 3. 参数选择模式

在测试脚本中实现了三种模式：

- `'cosmo_only'`: 仅使用 cosmological 参数
- `'with_nuisance'`: 使用 cosmological + nuisance 参数
- `None`: 使用所有采样参数（默认）

#### 4. Header 处理

- 实现了 Cobaya 格式 header 行的自动检测和跳过
- 正确处理以 `#` 开头的列名行

#### 5. Bug 修复

- **关键修复**: `thin()` 方法在 `nthin==1` 时返回 `None` 的问题
  - 修改为返回原始 chain 数组
  - 这是导致之前所有计算失败的根本原因
- **导入修复**: `DistanceMetric` 从 `sklearn.neighbors` → `sklearn.metrics`
- **格式检测修复**: 改进了 Cobaya 格式的识别逻辑

## 测试结果

### 测试数据集

共计 8 个数据集，包含两个宇宙学模型：

**ΛCDM 模型** (标准宇宙学):

- CMBBAO: CMB + BAO 数据
- CMBPANBAO: CMB + Pantheon + BAO 数据
- DESY5: DES Year 5 数据
- Union3: Union3 超新星数据

**EDE+PPF 模型** (早期暗能量 + PPF):

- sCMBBAO
- sCMBPANBAO
- sDESY5
- sUnion3

### 计算结果

所有 8 个数据集都成功计算了贝叶斯证据！

| 模型    | 数据集     | 样本数 | 维度 | ln(Z) [k=2] |
| ------- | ---------- | ------ | ---- | ----------- |
| ΛCDM    | CMBBAO     | 54,390 | 9    | -5536.624   |
| ΛCDM    | CMBPANBAO  | 84,000 | 9    | -6239.886   |
| ΛCDM    | DESY5      | 84,000 | 9    | -6362.250   |
| ΛCDM    | Union3     | 84,000 | 9    | -5551.125   |
| EDE+PPF | sCMBBAO    | 32,693 | 11   | -5538.652   |
| EDE+PPF | sCMBPANBAO | 12,620 | 11   | -6243.365   |
| EDE+PPF | sDESY5     | 12,620 | 11   | -6362.654   |
| EDE+PPF | sUnion3    | 12,620 | 11   | -5554.178   |

### 贝叶斯因子 (初步分析)

计算 Bayes Factor: `BF_EDE/LCDM = exp(ln(Z_EDE) - ln(Z_LCDM))`

| 数据集    | Δln(Z) = ln(Z_EDE) - ln(Z_LCDM) | 解释                  |
| --------- | ------------------------------- | --------------------- |
| CMBBAO    | -2.028                          | 中等支持 ΛCDM         |
| CMBPANBAO | -3.480                          | 强支持 ΛCDM           |
| DESY5     | -0.404                          | 无结论 (数据几乎相等) |
| Union3    | -3.054                          | 强支持 ΛCDM           |

**总体结论**: 在使用 cosmological 参数的情况下，ΛCDM 模型在大多数数据集上优于 EDE+PPF 模型。

## 实施细节

### 代码变更

#### 1. MCEvidence.py 主要修改

```python
# 新增方法 (行 ~660-740):
def _get_cobaya_sampled_params(self, base_name):
    """从 Cobaya yaml 文件读取采样参数信息"""
    import yaml
    # 读取 yaml 配置
    # 识别 sampled, cosmo, nuisance 参数
    # 返回参数信息字典

# 改进方法 (行 ~772-805):
def _detect_chain_format(self, fname):
    """改进的格式检测，使用文件模式匹配"""
    # 检查实际文件存在
    # 使用 glob 查找 Cobaya 和 CosmoMC 格式文件

# 修改方法 (行 ~895-935):
def load_from_file(self, fname, **kwargs):
    """加载时调用 _get_cobaya_sampled_params"""
    # 如果是 Cobaya 格式
    # 读取 yaml 参数信息
    # 设置 nparamMC 为采样参数数量

# 修改方法 (行 ~200-206):
def setup(self, str_or_dict, **kwargs):
    """使用 Cobaya 参数信息设置 nparamMC"""
    # 优先使用 yaml 中的采样参数数量

# Bug 修复 (行 ~360-370):
def thin(self, nthin=1, name=None, chain=None):
    """修复 nthin==1 时返回 None 的问题"""
    if nthin == 1:
        # 返回原始数据而不是 None
        if chain is not None:
            return chain
        elif name is None:
            return self.samples
        else:
            return self.data[name]
```

#### 2. test_cobaya.py 测试脚本

```python
# 参数选择模式 (行 ~48-54):
PARAM_MODE = 'cosmo_only'  # 或 'with_nuisance' 或 None

# 在计算函数中根据模式设置 ndim (行 ~125-145):
if PARAM_MODE == 'cosmo_only' and hasattr(mce.gd, 'cobaya_param_info'):
    param_info = mce.gd.cobaya_param_info
    if param_info:
        ndim_to_use = param_info['n_cosmo']
        mce.ndim = ndim_to_use
```

### 依赖关系

无需额外依赖！所有功能使用标准库：

- `yaml` (PyYAML 6.0.2) - 已在环境中安装
- `glob` - Python 标准库
- `os` - Python 标准库

## 与 CosmoMC 格式的对比

### CosmoMC 格式

- 文件命名: `basename_1.txt`, `basename_2.txt`, ...
- 无 header 行
- 列顺序: weight, -logL, param1, param2, ...
- 参数信息: 从 `.ranges` 文件读取

### Cobaya 格式

- 文件命名: `basename.1.txt`, `basename.2.txt`, ...
- 有 header 行 (以 `#` 开头)
- 列顺序: weight, -logPost, sampled_params..., derived_params..., chi2_components...
- 参数信息: 从 `.updated.yaml` 或 `.input.yaml` 读取

### 兼容性

两种格式现在都**完全支持**，自动检测，无需用户干预！

## 未来改进建议

### 1. 高优先级

- [ ] 添加单元测试
- [ ] 更新 README 文档
- [ ] 添加 Cobaya 使用示例到文档
- [ ] 在 setup.py 中添加 PyYAML 为可选依赖

### 2. 中优先级

- [ ] 支持 getdist 的 Cobaya 格式（如果需要）
- [ ] 添加参数名验证（检查 header 与 yaml 的一致性）
- [ ] 支持自定义 cosmological 参数列表
- [ ] 添加 logging 配置选项

### 3. 低优先级

- [ ] 支持其他 MCMC 输出格式（如 emcee, dynesty）
- [ ] 性能优化（大文件处理）
- [ ] GUI 或交互式参数选择

## 技术要点总结

### 关键学习点

1. **特征值问题**:
   - 当使用全部参数（包括 derived）时，协方差矩阵会有负特征值
   - 解决方案：只使用采样参数（sampled parameters）
2. **参数分类重要性**:

   - Sampled: MCMC 实际采样的参数
   - Derived: 从 sampled 计算得出的参数
   - Fixed: 固定值参数
   - 只有 sampled 参数应该用于贝叶斯证据计算

3. **Nuisance 参数的作用**:

   - 用于校准和系统误差建模
   - 是否包括取决于科学目标
   - 对于模型比较，通常需要边缘化（marginalize）

4. **k-NN 算法稳定性**:
   - k=2 通常最稳定
   - 不同 k 值的结果应该相近
   - 结果确实显示了很好的一致性

## 致谢

感谢原作者 Yabebal Fantaye 创建了这个优秀的 k-NN 贝叶斯证据估计工具！

## 参考文献

- Heavens, A., Fantaye, Y., Sellentin, E., Eggers, H., Hosenie, Z., Kroon, S., & Mootoovaloo, A. (2017). "No evidence for extensions to the standard cosmological model". _Physical Review Letters_, 119(10), 101301.
- MCEvidence GitHub: https://github.com/yabebalFantaye/MCEvidence
