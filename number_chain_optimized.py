import random
import math
import time

def is_prime(n):
    """判断一个数是否为质数"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

is_prime_opt = is_prime

def get_small_primes(limit=1000):
    primes = []
    is_p = [True] * (limit + 1)
    for i in range(2, limit + 1):
        if is_p[i]:
            primes.append(i)
            for j in range(i*i, limit + 1, i):
                is_p[j] = False
    return primes

SMALL_PRIMES = get_small_primes(2000) # Precompute some small primes

def small_prime_factors_of(n):
    factors = set()
    d = n
    if d < 0: d = -d
    if d == 0: return factors
    if d == 1: return factors
    
    for p in SMALL_PRIMES:
        if p * p > d:
            break
        if d % p == 0:
            factors.add(p)
            while d % p == 0:
                d //= p
    if d > 1:
        factors.add(d)
    return factors

def largest_proper_factor(n):
    """返回n的最大真因数（即除自身外的最大因数）"""
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return n // i
    return n  # 如果n是质数，按规则返回自身

def largest_prime_factor(n):
    """返回n的最大质因数"""
    i = 2
    original_n = n
    largest_prime = 2
    while i * i <= n:
        while n % i == 0:
            largest_prime = i
            n //= i
        i += 1 if i == 2 else 2
    if n > 1:
        largest_prime = n
    return largest_prime if largest_prime != original_n else original_n

fallback_largest_prime_factor = largest_prime_factor

def targeted_largest_prime_factor(p, N):
    d = p % 10
    # 候选质因数 q 很可能与 p 有简单线性关系
    candidates = set()
    # 生成候选 k，范围可根据需要调整
    for k in range(-1000, 1001):
        num = p - k
        # 对 num 进行小因数分解，将其质因数加入候选
        for q in small_prime_factors_of(num): 
            if q > 1:
                candidates.add(q)
    # 在候选集中寻找能整除 N 的最大质因数
    largest = 1
    for q in candidates:
        if N % q == 0 and q > largest and is_prime_opt(q):
            # 需要完全除尽
            temp = N
            while temp % q == 0:
                temp //= q
            # 检查剩下的是否为质数
            if temp > 1 and is_prime_opt(temp):
                largest = max(largest, temp)
            largest = max(largest, q)
            
    if largest > 1:
        return largest
    # 如果没找到，回退到原始方法（概率很低）
    return fallback_largest_prime_factor(N)

def find_preimages_fast(attractor, max_p):
    """高效找到所有可能一步到达 attractor 的质数 p"""
    preimages = []
    for d in (1, 3, 7, 9): # 质数的个位数只能是这些
        # 核心方程：largest_prime_factor(10*p + d) == attractor
        # 意味着 attractor 必须是 10*p + d 的因数，且是最大的。
        # 所以，设 M = (10*p + d) // attractor，则 M 是整数，且其最大质因数 <= attractor。
        # 枚举合理的 M...
        for M in range(1, (max_p * 10 + 9) // attractor + 1):
            candidate_N = attractor * M
            if candidate_N % 10 == d: # 检查个位数是否匹配
                candidate_p = (candidate_N - d) // 10
                if candidate_p > max_p:
                    break
                if is_prime_opt(candidate_p):
                    # 使用你的优化方法验证结果
                    if targeted_largest_prime_factor(candidate_p, candidate_N) == attractor:
                        preimages.append(candidate_p)
    return preimages

def apply_rule(start, rule_func, max_steps=100):
    """
    从start开始，反复应用规则rule_func，直到发现循环或达到最大步数。
    返回（最终结果链条列表， 终止类型描述）
    """
    seen = {}
    chain = []
    current = start

    for step in range(max_steps):
        if current in seen:
            # 发现循环，标记循环开始的位置
            loop_start = seen[current]
            chain.append(f"[循环起点: {current}]")
            return chain, f"在 {step} 步后进入循环 (从第 {loop_start} 步开始)"
        seen[current] = step
        chain.append(current)

        # 应用规则：乘以10加个位，然后求指定因数
        new_num = current * 10 + (current % 10)
        
        # Determine if rule_func takes 1 or 2 arguments
        try:
            next_num = rule_func(current, new_num)
        except TypeError:
            next_num = rule_func(new_num)

        if next_num == current:
            # 规则结果等于自身，陷入不动点
            chain.append(f"[不动点: {current}]")
            return chain, f"在 {step+1} 步后稳定于不动点"
        current = next_num

    chain.append(f"[超过最大步数{max_steps}]")
    return chain, f"超过最大步数限制 {max_steps}"

def explore_from_attractor(attractor, steps=20):
    """
    从一个已知吸引子出发，正向探索一定步数。
    目的是发现从这个吸引子开始，是否会走向另一个不同的稳定点。
    """
    current = attractor
    path = [current]
    for i in range(steps):
        N = current * 10 + (current % 10)
        next_num = targeted_largest_prime_factor(current, N) # 使用你的优化函数
        if next_num in path:
            loop_start = path.index(next_num)
            print(f"在 {attractor} 出发的链条，于第{i+1}步进入循环: {path[loop_start:]}")
            return path, 'loop', loop_start
        path.append(next_num)
        current = next_num
    print(f"在 {attractor} 出发的链条，{steps} 步内未发现循环，终点为 {current}")
    return path, 'unknown', -1

def characterize_node(node, max_steps=100):
    """深度追踪一个节点，判断其最终行为。"""
    seen = {}
    path = []
    current = node
    
    for step in range(max_steps):
        if current in seen:
            loop_type = f"循环 (长度 {step - seen[current]})"
            return path, 'loop', seen[current]
        seen[current] = step
        path.append(current)
        
        N = current * 10 + (current % 10)
        next_num = targeted_largest_prime_factor(current, N)
        
        if next_num == current:
            return path, 'fixed_point', -1
        current = next_num
        
    return path, 'unknown (可能持续增长)', -1

def is_prime_large(n):
    """用于大数的快速质数判定"""
    if n < 2: return False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def sample_and_test_cycle(sample_size=1000, max_prime=100_000_000, max_steps=200):
    """
    在指定范围内随机抽样质数，验证其是否落入已知的26步循环。
    返回 (落入循环的比例, 异常起点的列表)
    """
    # 1. 定义已知的26步循环作为“目标集”
    CYCLE_SET = {137, 17, 59, 599, 857, 953, 9533, 13619, 19457, 821,
                 23, 233, 2333, 23333, 661, 601, 6011, 6679, 997, 907,
                 313, 241, 2411, 47, 53, 41}

    # 2. 随机生成样本质数
    samples = []
    while len(samples) < sample_size:
        candidate = random.randint(2, max_prime)
        if is_prime_large(candidate):
            samples.append(candidate)

    in_cycle = 0
    anomalies = []  # 记录未进入循环的起点

    # 3. 对每个样本进行追踪
    for idx, p in enumerate(samples):
        current = p
        for step in range(max_steps):
            if current in CYCLE_SET:
                in_cycle += 1
                break
            # 应用规则
            N = current * 10 + (current % 10)
            current = targeted_largest_prime_factor(current, N)  # 使用您的优化函数
        else:
            # 循环正常结束（未进入CYCLE_SET）
            anomalies.append((p, current))  # 记录起点和终点

        # 进度报告
        if (idx + 1) % 100 == 0:
            print(f"  已测试 {idx+1}/{sample_size} 个样本...")

    ratio = in_cycle / sample_size
    return ratio, anomalies

def trace_to_cycle(start_node, max_steps=500):
    CYCLE_SET = {137, 17, 59, 599, 857, 953, 9533, 13619, 19457, 821,
                 23, 233, 2333, 23333, 661, 601, 6011, 6679, 997, 907,
                 313, 241, 2411, 47, 53, 41}
    current = start_node
    for _ in range(max_steps):
        if current in CYCLE_SET:
            return current
        N = current * 10 + (current % 10)
        current = targeted_largest_prime_factor(current, N)
    return -1 # Not found in max steps

def targeted_boundary_test():
    """测试那些在数学上可能‘反常’的质数类型。"""
    test_cases = []
    CYCLE_SET = {137, 17, 59, 599, 857, 953, 9533, 13619, 19457, 821,
                 23, 233, 2333, 23333, 661, 601, 6011, 6679, 997, 907,
                 313, 241, 2411, 47, 53, 41}

    # 1. 梅森质数 (形式 2^n - 1)
    mersenne_candidates = [3, 7, 31, 127, 8191] # 更大的如2^31-1计算量较大
    # 2. 费马质数 (形式 2^(2^n) + 1)
    fermat_candidates = [3, 5, 17, 257, 65537]
    # 3. 回文质数
    palindrome_primes = [11, 101, 131, 151, 181, 191, 313, 353, 373, 383, 727, 757, 787, 797, 919, 929]
    # 4. 已知非常大的质数（在计算可行范围内）
    large_primes = [999999937, 2147483647] # 10^9附近的质数

    all_tests = []
    all_tests.extend([(p, 'Mersenne') for p in mersenne_candidates])
    all_tests.extend([(p, 'Fermat') for p in fermat_candidates])
    all_tests.extend([(p, 'Palindrome') for p in palindrome_primes])
    all_tests.extend([(p, 'Large') for p in large_primes])

    # Remove duplicates while preserving order
    unique_tests = []
    seen = set()
    for p, type_ in all_tests:
        if p not in seen:
            seen.add(p)
            unique_tests.append((p, type_))

    results = []
    for p, type_ in unique_tests:
        if is_prime_large(p):
            # 追踪其是否进入循环
            final = trace_to_cycle(p)
            in_cycle = final in CYCLE_SET
            results.append((p, type_, in_cycle))
        else:
            results.append((p, type_, "Not Prime"))
            
    return results

def main():
    print("=" * 60)
    print("数学规则穷举测试器 (Optimized with Full Analysis)")
    print("规则: p → 10*p + (p%10) → 求指定因数")
    print("=" * 60)

    # ... (skipping the basic rule test to focus on new requests, or keep it short)
    # Keeping it as is but maybe reducing steps if needed.
    
    # ... [Previous tests code commented out or kept]
    # To save time and output space, I will focus on the new tests
    
    print("\n[Skip Basic Tests] 直接运行边界测试...")

    print(f"\n{'='*60}")
    print("运行边界质数测试 (Mersenne, Fermat, Palindrome, Large)...")
    boundary_results = targeted_boundary_test()
    for p, type_, result in boundary_results:
        print(f"质数 {p} ({type_}): {'进入循环' if result is True else '未进入循环' if result is False else result}")

    print(f"\n{'='*60}")
    print("开始小规模抽样验证循环的全局吸引力 (Sample=100)...")
    start_time = time.time()
    ratio, anomalies = sample_and_test_cycle(sample_size=100, max_prime=100_000_000)
    elapsed = time.time() - start_time

    print(f"\n结果报告:")
    print(f"测试样本数: 100")
    print(f"落入26步循环的比例: {ratio*100:.2f}%")
    print(f"发现异常起点数量: {len(anomalies)}")
    print(f"总耗时: {elapsed:.2f}秒")
    if anomalies:
        print(f"异常案例如下 (起点, 终点): {anomalies[:5]}")

    print(f"\n{'='*60}")
    print(f"测试完成！")

if __name__ == "__main__":
    main()
