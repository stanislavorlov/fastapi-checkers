from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import math
import time
import random

# -----------------------------
# Ratings
# -----------------------------

class Elo:
    """Simple, production-friendly Elo."""

    def __init__(self, k_base: int = 24, k_prov: int = 40, prov_games: int = 20):
        self.k_base = k_base
        self.k_prov = k_prov
        self.prov_games = prov_games

    @staticmethod
    def expected_score(ra: float, rb: float) -> float:
        return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))

    def k(self, games_played: int) -> int:
        return self.k_prov if games_played < self.prov_games else self.k_base

    def update(self, ra: float, rb: float, sa: float, games_a: int) -> float:
        k = self.k(games_a)
        ea = self.expected_score(ra, rb)
        return ra + k * (sa - ea)


class Glicko2:
    """
    Minimal Glicko-2 per paper by Glickman.
    Ratings in Glicko scale (μ, φ); public output converted to Elo-like scale (r, RD).
    This keeps API similar to Elo while giving you RD (uncertainty).
    """
    # Constants from the spec
    TAU = 0.5
    SCALE = 173.7178

    @dataclass
    class State:
        rating: float = 1500.0
        rd: float = 350.0           # rating deviation
        vol: float = 0.06           # volatility

    @staticmethod
    def _to_mu_phi(r: float, RD: float) -> Tuple[float, float]:
        return ((r - 1500.0) / Glicko2.SCALE, RD / Glicko2.SCALE)

    @staticmethod
    def _to_r_RD(mu: float, phi: float) -> Tuple[float, float]:
        return (mu * Glicko2.SCALE + 1500.0, phi * Glicko2.SCALE)

    @staticmethod
    def _g(phi: float) -> float:
        return 1.0 / math.sqrt(1.0 + 3.0 * (phi ** 2) / (math.pi ** 2))

    @staticmethod
    def _E(mu: float, mu_j: float, phi_j: float) -> float:
        return 1.0 / (1.0 + math.exp(-Glicko2._g(phi_j) * (mu - mu_j)))

    def _v(self, mu: float, opps: List[Tuple[float, float, float]]) -> float:
        inv = 0.0
        for mu_j, phi_j, s_j in opps:
            E = self._E(mu, mu_j, phi_j)
            g = self._g(phi_j)
            inv += (g ** 2) * E * (1 - E)
        return 1.0 / inv if inv > 0 else 1e9

    def _delta(self, mu: float, v: float, opps: List[Tuple[float, float, float]]) -> float:
        sum_term = 0.0
        for mu_j, phi_j, s_j in opps:
            E = self._E(mu, mu_j, phi_j)
            g = self._g(phi_j)
            sum_term += g * (s_j - E)
        return v * sum_term

    def _new_vol(self, state: "Glicko2.State", delta: float, v: float) -> float:
        a = math.log(state.vol ** 2)
        A = a
        TAU = Glicko2.TAU

        def f(x):
            ex = math.exp(x)
            num = ex * (delta ** 2 - state.phi ** 2 - v - ex)
            den = 2 * (state.phi ** 2 + v + ex) ** 2
            return (num / den) - ((x - a) / (TAU ** 2))

        # Find B
        if delta ** 2 > (state.phi ** 2 + v):
            B = math.log(delta ** 2 - state.phi ** 2 - v)
        else:
            k = 1
            while f(a - k * TAU) < 0:
                k += 1
            B = a - k * TAU

        fA = f(A)
        fB = f(B)
        # Binary search
        while abs(B - A) > 1e-6:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)
            if fC * fB < 0:
                A, fA = B, fB
            else:
                fA /= 2.0
            B, fB = C, fC
        return math.exp(A / 2.0)

    def update_player(self, st: "Glicko2.State", results: List[Tuple[float, float]]):
        """
        results: list of (opponent_rating, score) where score is 1, 0.5, 0
        Updates st in-place.
        """
        # Convert to Glicko-2 scale
        mu, phi = self._to_mu_phi(st.rating, st.rd)
        setattr(st, "mu", mu)
        setattr(st, "phi", phi)

        opps = []
        for r_j, s_j in results:
            mu_j, phi_j = self._to_mu_phi(r_j, 350.0)  # assume average RD for opp if unknown
            opps.append((mu_j, phi_j, s_j))

        if not opps:
            # No games: RD increases due to uncertainty (conservative growth)
            st.rd = min(math.sqrt(st.rd ** 2 + 50 ** 2), 350.0)
            return

        v = self._v(mu, opps)
        delta = self._delta(mu, v, opps)
        new_vol = self._new_vol(st, delta, v)

        phi_star = math.sqrt(st.phi**2 + new_vol**2)
        phi_prime_inv_sq = 0.0
        sum_term = 0.0
        for mu_j, phi_j, s_j in opps:
            E = self._E(mu, mu_j, phi_j)
            g = self._g(phi_j)
            phi_prime_inv_sq += (g ** 2) * E * (1 - E)
            sum_term += g * (s_j - E)
        phi_prime = 1.0 / math.sqrt((1.0 / (phi_star ** 2)) + phi_prime_inv_sq)
        mu_prime = mu + (phi_prime ** 2) * sum_term

        st.rating, st.rd = self._to_r_RD(mu_prime, phi_prime)
        st.vol = new_vol

# -----------------------------
# Queue entries & matcher
# -----------------------------

@dataclass
class QueueEntry:
    player_id: str
    rating: float = 1500.0
    rd: Optional[float] = None          # Glicko RD if you use it
    region: str = "global"
    ping_ms: int = 60
    join_ts: float = field(default_factory=lambda: time.time())
    games_played: int = 0
    recent_foes: Tuple[str, ...] = field(default_factory=tuple)
    flags: Dict[str, bool] = field(default_factory=dict)

class Matchmaker:
    """
    Expanding window matchmaking with scoring (rating gap, latency, wait, RD balance).
    """
    def __init__(
        self,
        latency_cap_ms: int = 120,
        base_window: int = 50,
        expand_per_5s: int = 20,
        max_window: int = 600,
        allow_cross_region_after_s: int = 20,
        hard_cap_window: int = 800
    ):
        self.latency_cap_ms = latency_cap_ms
        self.base_window = base_window
        self.expand_per_5s = expand_per_5s
        self.max_window = max_window
        self.allow_cross_region_after_s = allow_cross_region_after_s
        self.hard_cap_window = hard_cap_window
        self.queue: Dict[str, QueueEntry] = {}

    # ---- Public API
    def enqueue(self, entry: QueueEntry):
        self.queue[entry.player_id] = entry

    def dequeue(self, player_id: str):
        self.queue.pop(player_id, None)

    def tick(self) -> List[Tuple[QueueEntry, QueueEntry]]:
        """Run one matchmaking pass and return pairs."""
        now = time.time()
        players = list(self.queue.values())
        players.sort(key=lambda p: p.join_ts)  # longest waiting first

        matched: set[str] = set()
        pairs: List[Tuple[QueueEntry, QueueEntry]] = []

        for p in players:
            if p.player_id in matched:
                continue
            window = self._acceptable_window(p, now)
            cands: List[Tuple[float, QueueEntry]] = []

            for q in players:
                if q.player_id == p.player_id or q.player_id in matched:
                    continue
                if not self._region_ok(p, q, now):
                    continue
                if not self._within_rating(p, q, window):
                    continue
                if not self._latency_ok(p, q):
                    continue
                if q.player_id in p.recent_foes:
                    continue
                score = self._score(p, q, now)
                cands.append((score, q))

            if cands:
                cands.sort(key=lambda t: t[0])
                best = cands[0][1]
                matched.add(p.player_id)
                matched.add(best.player_id)
                pairs.append((p, best))

        # remove matched from queue
        for a, b in pairs:
            self.dequeue(a.player_id)
            self.dequeue(b.player_id)
        return pairs

    # ---- Internals
    def _wait_s(self, p: QueueEntry, now: float) -> int:
        return int(now - p.join_ts)

    def _acceptable_window(self, p: QueueEntry, now: float) -> int:
        wait = self._wait_s(p, now)
        expand_steps = max(0, wait // 5) * self.expand_per_5s
        rd_boost = int((p.rd or 0) * 0.3)  # if you have RD, widen a bit
        w = min(self.base_window + expand_steps + rd_boost, self.hard_cap_window)
        return w

    def _region_ok(self, p: QueueEntry, q: QueueEntry, now: float) -> bool:
        if p.region == q.region:
            return True
        waited = max(self._wait_s(p, now), self._wait_s(q, now))
        return waited >= self.allow_cross_region_after_s

    def _within_rating(self, p: QueueEntry, q: QueueEntry, window: int) -> bool:
        return abs(p.rating - q.rating) <= window

    def _latency_ok(self, p: QueueEntry, q: QueueEntry) -> bool:
        worst = max(p.ping_ms, q.ping_ms)
        return worst <= self.latency_cap_ms

    def _score(self, p: QueueEntry, q: QueueEntry, now: float) -> float:
        rating_gap = abs(p.rating - q.rating)
        latency = max(p.ping_ms, q.ping_ms)
        wait_bonus = (self._wait_s(p, now) + self._wait_s(q, now))
        rd_balance = abs((p.rd or 0) - (q.rd or 0))
        history_penalty = 800 if q.player_id in p.recent_foes else 0
        # tune weights as needed
        return 3.0 * rating_gap + 1.0 * latency - 0.12 * wait_bonus + 0.4 * rd_balance + history_penalty

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Create systems
    elo = Elo(k_base=24, k_prov=40, prov_games=20)
    g2 = Glicko2()

    # Fake queue
    mm = Matchmaker()

    # Enqueue 10 players with various ratings/latencies
    for i in range(10):
        mm.enqueue(QueueEntry(
            player_id=f"P{i}",
            rating=1500 + random.randint(-300, 300),
            rd=random.choice([None, 80, 120, 200]),
            ping_ms=random.randint(30, 140),
            region=random.choice(["EU", "US", "EU", "EU", "US"]),
            games_played=random.randint(0, 200),
            recent_foes=tuple(random.sample([f"P{j}" for j in range(10) if j != i], k=random.randint(0, 1)))
        ))

    # One matchmaking tick
    pairs = mm.tick()
    print("Pairs:")
    for a, b in pairs:
        print(a.player_id, a.rating, "vs", b.player_id, b.rating)

    # Pretend we played the games and update Elo
    for a, b in pairs:
        # simulate a result
        result = random.choice([1.0, 0.5, 0.0])  # win/draw/loss for player a
        new_ra = elo.update(a.rating, b.rating, result, a.games_played)
        new_rb = elo.update(b.rating, a.rating, 1.0 - result, b.games_played)
        print(f"Result {a.player_id} vs {b.player_id}: {result} -> {new_ra:.1f}, {new_rb:.1f}")

    # Glicko2 single-player update example
    st = Glicko2.State()  # 1500, RD 350
    g2.update_player(st, results=[(1600, 1.0), (1450, 0.5), (1550, 0.0)])
    print("Glicko2 updated:", st)