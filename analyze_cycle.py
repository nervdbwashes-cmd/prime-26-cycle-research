import sympy as sp  # 用于更强大的质因数分解和质数检测
import matplotlib.pyplot as plt
import numpy as np

# 1. 定义循环（您发现的26步循环）
CYCLE = [
    137, 17, 59, 599, 857, 953, 9533, 13619, 19457, 821,
    23, 233, 2333, 23333, 661, 601, 6011, 6679, 997, 907,
    313, 241, 2411, 47, 53, 41
]

def detailed_cycle_analysis(cycle):
    """对循环进行详细的逐步分析"""
    
    analysis_data = []
    print("="*80)
    print("26步循环详细分析报告")
    print("="*80)
    
    for i, p in enumerate(cycle):
        step_num = i + 1
        d = p % 10
        N = p * 10 + d
        # 使用sympy获取标准最大质因数
        factors = sp.factorint(N)
        largest_prime = max(factors.keys())
        next_p = cycle[(i + 1) % len(cycle)]
        
        # 计算关键指标
        ratio = next_p / p  # 扩张/收缩比率
        digit_growth = len(str(N)) - len(str(p))  # 数字长度变化
        
        # 存储分析数据
        step_info = {
            'step': step_num,
            'p': p,
            'd': d,
            'N': N,
            'N_factors': factors,
            'largest_prime': largest_prime,
            'next_p': next_p,
            'ratio': ratio,
            'digit_growth': digit_growth,
            'op_type': '扩张' if ratio > 1.5 else '收缩' if ratio < 0.67 else '平稳'
        }
        analysis_data.append(step_info)
        
        # 打印本步信息
        print(f"\n步骤 {step_num:2d}:")
        print(f"  当前 p = {p:5d} (个位 d={d})")
        print(f"  生成 N = 10*{p} + {d} = {N}")
        print(f"  N的质因数分解: {sp.factorint(N, visual=True) if hasattr(sp.factorint(N, visual=True), '__str__') else factors}")
        print(f"  最大质因数 q = {largest_prime:5d}")
        print(f"  下一项 p_next = {next_p:5d} (变化比率: {ratio:.3f}, 类型: {step_info['op_type']})")
    
    return analysis_data

def generate_analysis_charts(analysis_data):
    """生成分析图表"""
    
    steps = [d['step'] for d in analysis_data]
    ratios = [d['ratio'] for d in analysis_data]
    p_values = [d['p'] for d in analysis_data]
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('26步循环内部结构分析', fontsize=16, fontweight='bold')
    
    # 1. 扩张/收缩比率图
    ax1 = axes[0, 0]
    colors = ['red' if r > 1.5 else 'green' if r < 0.67 else 'blue' for r in ratios]
    ax1.bar(steps, ratios, color=colors, edgecolor='black')
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_xlabel('循环步骤')
    ax1.set_ylabel('变化比率 (p_next / p)')
    ax1.set_title('每一步的扩张/收缩比率')
    ax1.set_xticks(range(1, 27, 2))
    
    # 2. 循环数值大小图
    ax2 = axes[0, 1]
    ax2.plot(steps, p_values, 'o-', linewidth=2, markersize=6)
    ax2.set_xlabel('循环步骤')
    ax2.set_ylabel('数值 (p)')
    ax2.set_title('循环数值变化趋势')
    ax2.set_xticks(range(1, 27, 2))
    ax2.set_yscale('log')  # 对数尺度更能看清数量级变化
    
    # 3. 操作类型统计
    ax3 = axes[1, 0]
    op_types = [d['op_type'] for d in analysis_data]
    type_counts = {'扩张': op_types.count('扩张'), 
                   '收缩': op_types.count('收缩'), 
                   '平稳': op_types.count('平稳')}
    ax3.bar(type_counts.keys(), type_counts.values(), color=['red', 'green', 'blue'])
    ax3.set_xlabel('操作类型')
    ax3.set_ylabel('出现次数')
    ax3.set_title(f'操作类型分布 (总计: {sum(type_counts.values())}步)')
    for i, (k, v) in enumerate(type_counts.items()):
        ax3.text(i, v + 0.1, str(v), ha='center')
    
    # 4. 数字位数变化
    ax4 = axes[1, 1]
    digit_changes = [d['digit_growth'] for d in analysis_data]
    unique_changes = sorted(set(digit_changes))
    change_counts = [digit_changes.count(uc) for uc in unique_changes]
    ax4.bar([str(uc) for uc in unique_changes], change_counts)
    ax4.set_xlabel('数字位数变化 (+N表示增加N位)')
    ax4.set_ylabel('出现次数')
    ax4.set_title('生成数N的位数变化分布')
    
    plt.tight_layout()
    plt.savefig('cycle_internal_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n分析图表已保存至: cycle_internal_analysis.png")
    plt.show()

def find_mathematical_patterns(analysis_data):
    """寻找数学模式"""
    
    print("\n" + "="*80)
    print("数学模式分析")
    print("="*80)
    
    # 1. 检查循环的乘积是否≈1（动态平衡）
    product_of_ratios = np.prod([d['ratio'] for d in analysis_data])
    print(f"1. 动态平衡分析:")
    print(f"   所有比率的乘积 = {product_of_ratios:.10f}")
    print(f"   几何平均数 = {product_of_ratios**(1/len(analysis_data)):.6f}")
    
    # 2. 分析频繁出现的质因数
    all_factors = []
    for d in analysis_data:
        all_factors.extend(d['N_factors'].keys())
    
    from collections import Counter
    factor_counts = Counter(all_factors)
    print(f"\n2. 频繁出现的质因数 (在26个N中):")
    for factor, count in sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   质因数 {factor:4d}: 出现 {count:2d} 次 ({count/26*100:.1f}%)")
    
    # 3. 检查模余数模式
    print(f"\n3. 模余数分析 (p mod 小整数):")
    for mod in [2, 3, 4, 5, 6, 7, 10]:
        residues = [d['p'] % mod for d in analysis_data]
        unique_residues = set(residues)
        print(f"   p mod {mod}: 出现余数集合 {sorted(unique_residues)}")
        if len(unique_residues) <= 3:
            print(f"      → 可能具有规律性!")

# 执行分析
if __name__ == "__main__":
    # 执行详细分析
    data = detailed_cycle_analysis(CYCLE)
    
    # 生成图表
    generate_analysis_charts(data)
    
    # 寻找数学模式
    find_mathematical_patterns(data)
    
    # 额外：验证循环的稳定性（可选）
    print("\n" + "="*80)
    print("循环稳定性验证")
    print("="*80)
    print("对循环中每个点添加微小扰动后重新迭代:")
    stable_count = 0
    for p in CYCLE[:5]:  # 只测试前5个点以节省时间
        perturbed = p + 1 if p % 2 == 0 else p - 1
        # 简单追踪几步看看是否回到循环
        current = perturbed
        for _ in range(50):
            d = current % 10
            N = current * 10 + d
            factors = sp.factorint(N)
            current = max(factors.keys())
            if current in CYCLE:
                stable_count += 1
                break
    print(f"  测试了5个扰动点，{stable_count}个回到了原循环")
