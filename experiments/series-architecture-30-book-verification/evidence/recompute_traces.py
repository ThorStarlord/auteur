"""Recompute the frozen-run figures in 04-consequence-traces.md from the rules in 03-shared-crisis.md.

Rules: c = 0.6 + 0.2 * min(1, H / 60); overflow o = max(0, S - h + w - c); h_needed = S + w - c.
Frozen run: S = 1.7 CU, w = 0.1 CU. Lead factors: A and C 0.9, B 0.7.
"""
def cap(h):
    return 0.6 + 0.2 * min(1.0, h / 60.0)

def overflow(S, h, c, w=0.1):
    return max(0.0, S - h + w - c)

def h_needed(S, c, w=0.1):
    return S + w - c

rows = []
A = 44 * 0.9; cA = cap(A)
rows.append(("A delivered", A)); rows.append(("A capacity", cA))
rows.append(("A T1 shortfall", 60 - A)); rows.append(("A overflow at h=0.6, S=1.7", overflow(1.7, 0.6, cA)))
rows.append(("A overflow at h=0.6, S=1.4", overflow(1.4, 0.6, cA))); rows.append(("A overflow at h=0.4, S=1.4", overflow(1.4, 0.4, cA)))
rows.append(("A overflow at h=0.6, S=1.9", overflow(1.9, 0.6, cA))); rows.append(("A h needed at S=1.4", h_needed(1.4, cA)))
B = 66 * 0.7; cB = cap(B)
rows.append(("B delivered", B)); rows.append(("B capacity", cB)); rows.append(("B deficit", 66 - B))
rows.append(("B T1 shortfall", 60 - B)); rows.append(("B h needed at S=1.7", h_needed(1.7, cB)))
rows.append(("B overflow at h=1.05", overflow(1.7, 1.05, cB)))
rows.append(("B h needed at S=1.4", h_needed(1.4, cB))); rows.append(("B h needed at S=1.9", h_needed(1.9, cB)))
Bc = 54 * 0.7; cBc = cap(Bc)
rows.append(("B compact-refusal capacity", cBc)); rows.append(("B compact-refusal h needed", h_needed(1.7, cBc)))
C = (54 + 12) * 0.9; cC = cap(C)
rows.append(("C delivered", C)); rows.append(("C capacity", cC)); rows.append(("C deficit", 66 - C))
rows.append(("C T1 shortfall", 60 - C)); rows.append(("C h needed at S=1.7", h_needed(1.7, cC)))
rows.append(("C overflow at h=1.01", overflow(1.7, 1.01, cC)))
rows.append(("C h needed at S=1.4", h_needed(1.4, cC))); rows.append(("C h needed at S=1.9", h_needed(1.9, cC)))
Cc = 54 * 0.9; cCc = cap(Cc)
rows.append(("C compact-refusal capacity", cCc)); rows.append(("C compact-refusal h needed", h_needed(1.7, cCc)))
for name, value in rows:
    print(f"{name:34s} {value:8.3f}")
