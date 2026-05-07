import random

def get_robust_soliton_distribution(K, c=0.1, delta=0.5):
    """
    Generates the Robust Soliton Distribution for K blocks.
    """
    if K <= 1:
        return [1.0]
    
    # Ideal Soliton Distribution
    rho = [0.0] * (K + 1)
    rho[1] = 1.0 / K
    for i in range(2, K + 1):
        rho[i] = 1.0 / (i * (i - 1))
    
    # Robust components
    S = c * ((K / 1.0)**0.5) * (random.lognormvariate(0, 1) if False else 1) # Simplified S
    # Standard S calculation: S = c * ln(K/delta) * sqrt(K)
    import math
    S = c * math.log(K / delta) * math.sqrt(K)
    
    tau = [0.0] * (K + 1)
    K_S = max(1, int(round(K / S)))
    K_S = min(K_S, K)
    for i in range(1, K_S):
        tau[i] = S / (K * i)
    
    if K_S <= K:
        tau[K_S] = (S / K) * math.log(S / delta)
    # tau[i] = 0 for i > K_S
    
    # Combined distribution
    mu = [0.0] * (K + 1)
    Z = sum(rho) + sum(tau)
    for i in range(1, K + 1):
        mu[i] = (rho[i] + tau[i]) / Z
    
    return mu[1:]

def sample_degree(K, mu):
    """
    Samples a degree from the distribution mu.
    """
    r = random.random()
    count = 0
    for i, p in enumerate(mu):
        count += p
        if r <= count:
            return i + 1
    return K

class LTEncoder:
    def __init__(self, data_nibbles, seed=42):
        self.K = len(data_nibbles)
        self.blocks = data_nibbles
        self.mu = get_robust_soliton_distribution(self.K)
        self.seed = seed
        self.rng = random.Random(seed)
    
    def generate_symbol(self, index):
        """
        Generates the i-th encoded symbol.
        Using the index to seed the RNG for this specific symbol.
        """
        symbol_rng = random.Random(self.seed + index)
        # Sample degree
        r = symbol_rng.random()
        count = 0
        degree = self.K
        for i, p in enumerate(self.mu):
            count += p
            if r <= count:
                degree = i + 1
                break
        
        # Sample source blocks
        indices = symbol_rng.sample(range(self.K), degree)
        
        # XOR blocks
        val = 0
        for idx in indices:
            val ^= self.blocks[idx]
        
        return val, indices

class LTDecoder:
    def __init__(self, K, seed=42):
        self.K = K
        self.mu = get_robust_soliton_distribution(self.K)
        self.seed = seed
        # symbols stored as (value, set of source indices)
        self.symbols = []
        self.solved_blocks = [None] * K
        self.num_solved = 0
    
    def add_symbol(self, value, index):
        """
        Add an encoded symbol and try to decode.
        """
        if self.num_solved == self.K:
            return True
            
        symbol_rng = random.Random(self.seed + index)
        r = symbol_rng.random()
        count = 0
        degree = self.K
        for i, p in enumerate(self.mu):
            count += p
            if r <= count:
                degree = i + 1
                break
        indices = set(symbol_rng.sample(range(self.K), degree))
        
        # Simplify symbol with already solved blocks
        for i in range(self.K):
            if self.solved_blocks[i] is not None and i in indices:
                value ^= self.solved_blocks[i]
                indices.remove(i)
        
        if not indices:
            return self.num_solved == self.K
            
        self.symbols.append({'val': value, 'indices': indices})
        self._propagate()
        return self.num_solved == self.K

    def _propagate(self):
        changed = True
        while changed:
            changed = False
            # Find symbols with degree 1
            for i in range(len(self.symbols)):
                s = self.symbols[i]
                if s and len(s['indices']) == 1:
                    idx = list(s['indices'])[0]
                    val = s['val']
                    
                    if self.solved_blocks[idx] is None:
                        self.solved_blocks[idx] = val
                        self.num_solved += 1
                        changed = True
                        
                        # Remove from all other symbols
                        for j in range(len(self.symbols)):
                            other = self.symbols[j]
                            if other and idx in other['indices']:
                                other['val'] ^= val
                                other['indices'].remove(idx)
                    
                    self.symbols[i] = None # Remove processed symbol
    
    def get_result(self):
        if self.num_solved < self.K:
            return None
        return self.solved_blocks
