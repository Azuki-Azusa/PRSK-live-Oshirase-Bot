"""配置模块。"""

from dataclasses import dataclass

from environs import Env


_MISSING = object()


def _read(env, *keys, default=_MISSING):
    """读取环境变量。"""
    for key in keys:
        try:
            value = env(key)
        except Exception:
            continue
        if value is not None and str(value) != "":
            return value
    if default is not _MISSING:
        return default
    raise KeyError("Missing required environment variable: " + "/".join(keys))


def _csv(value):
    """解析逗号分隔值。"""
    return [item.strip() for item in value.split(',') if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    """运行配置。"""

    bot_token: str
    channel_id_remind: int
    channel_id_prsk: int
    channel_id_rank: int
    app_env: str
    members: list[str]
    virtual_live_api: str
    current_event_api: str
    game_api_url: str
    game_api_path: str
    game_api_rank_path1: str
    game_api_rank_path2: str
    game_api_header: str
    game_api_token: str
    delay: int

    @property
    def is_development(self):
        """判断开发环境。"""
        return self.app_env == "development"

    def rank_url(self, event_id):
        """构建排名 API URL。"""
        return (
            self.game_api_url
            + self.game_api_path
            + self.game_api_rank_path1
            + "/"
            + str(event_id)
            + self.game_api_rank_path2
        )

    def rank_headers(self):
        """构建 API 请求头。"""
        return {self.game_api_header: self.game_api_token}

    @classmethod
    def from_env(cls, env):
        """从环境变量创建配置。"""
        return cls(
            bot_token=_read(env, "BOT_TOKEN"),
            channel_id_remind=int(_read(env, "CHANNEL_ID_REMIND")),
            channel_id_prsk=int(_read(env, "CHANNEL_ID_PRSK")),
            channel_id_rank=int(_read(env, "CHANNEL_ID_RANK")),
            # 优先使用 APP_ENV；保留 env 是为了兼容旧的 .env 文件。
            app_env=_read(env, "APP_ENV", "env", default="production"),
            members=_csv(_read(env, "MEMBERS", default="")),
            virtual_live_api=_read(env, "VIRTUAL_LIVE_API"),
            current_event_api=_read(env, "CURRENT_EVENT_API"),
            game_api_url=_read(env, "GAME_API_URL"),
            game_api_path=_read(env, "GAME_API_PATH"),
            game_api_rank_path1=_read(env, "GAME_API_RANK_PATH1"),
            game_api_rank_path2=_read(env, "GAME_API_RANK_PATH2"),
            game_api_header=_read(env, "GAME_API_HEADER"),
            game_api_token=_read(env, "GAME_API_TOKEN"),
            delay=int(_read(env, "DELAY")),
        )


def load_config():
    """加载配置。"""
    env = Env()
    env.read_env()
    return AppConfig.from_env(env)
