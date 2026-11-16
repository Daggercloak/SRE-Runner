from prometheus_client import Counter, Gauge, start_http_server


games_started = Counter(
    "sre_runner_games_started_total",
    "Total number of SRE Runner games started"
)

obstacles_avoided = Counter(
    "sre_runner_obstacles_avoided_total",
    "Total number of obstacles successfully avoided",
    ["type"]
)

collisions = Counter(
    "sre_runner_collisions_total",
    "Total number of collisions with obstacles",
    ["type"]
)

game_active = Gauge(
    "sre_runner_game_active",
    "Whether a game is currently active: 1 active, 0 game over"
)

current_score = Gauge(
    "sre_runner_current_score",
    "Current SRE Runner score"
)

current_speed = Gauge(
    "sre_runner_current_speed",
    "Current obstacle speed"
)


# Ensure every labeled series appears before an event occurs.
obstacles_avoided.labels(type="ground")
obstacles_avoided.labels(type="flying")

collisions.labels(type="ground")
collisions.labels(type="flying")


def start_metrics_server(port=9090):
    start_http_server(port)
