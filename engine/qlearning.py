"""Agen Q-Learning tabular (Kontrak 4). Dilatih di engine.rl_env.MaintenanceEnv. Pemilik: Orang 2."""
import numpy as np

ALPHA, GAMMA, EPISODE = 0.1, 0.99, 5000
EPS_AWAL, EPS_AKHIR, DECAY = 1.0, 0.01, 0.001


def epsilon(ep):
    """Peluang aksi acak: turun eksponensial dari 1,0 menuju 0,01."""
    return EPS_AKHIR + (EPS_AWAL - EPS_AKHIR) * np.exp(-DECAY * ep)


def latih(env, episode=EPISODE, alpha=ALPHA, gamma=GAMMA, seed=42):
    """Kembalikan (Q-table berukuran (n_state, 2), total reward per episode)."""
    rng = np.random.default_rng(seed)
    q = np.zeros((env.n_state, 2))
    reward_ep = np.zeros(episode)
    for ep in range(episode):
        s, selesai, total = env.reset(), False, 0.0
        eps = epsilon(ep)
        while not selesai:
            a = int(rng.integers(2)) if rng.random() < eps else int(q[s].argmax())
            s2, r, selesai, _ = env.step(a)
            target = r if selesai else r + gamma * q[s2].max()
            q[s, a] += alpha * (target - q[s, a])
            s, total = s2, total + r
        reward_ep[ep] = total
    return q, reward_ep


def kurva(reward_ep, setiap=100):
    """Rata-rata reward per blok episode, bentuk Kontrak 6 (kurva_reward)."""
    n = len(reward_ep) // setiap
    return [{'episode': (i + 1) * setiap, 'rata2': round(float(reward_ep[i * setiap:(i + 1) * setiap].mean()), 2)}
            for i in range(n)]
