# Codex 项目说明

## 项目定位

这是一个运行在个人 NAS 上的私人 Discord Bot，用于《Project SEKAI》日服相关通知和查询。

主要功能：

- 获取当前虚拟 Live 与活动数据。
- 在指定 Discord 频道发送 Live、活动结束及每日提醒。
- 记录成员对 Live 的参与意向。
- 定期抓取活动排名，计算时速并生成排名图片。
- 响应 `SHOW`、纯数字 Live ID、`SCORE_MAIN`、`SCORE_ALL`、`SCORE_<角色ID>` 等消息。

本项目是个人用途，不需要设计多租户、后台管理系统或复杂权限体系，除非用户明确要求。

## 运行环境

- Python 3.11（Docker 镜像默认版本；README 最低要求为 Python 3.9）。
- 使用 `discord.py`、`aiohttp`、`environs` 和 `matplotlib`。
- 生产环境通过 Docker Compose 在 NAS 上长期运行。
- 时区相关逻辑以 `Asia/Tokyo` 为准。
- 容器入口：`python dcbot.py`。
- Compose 服务名：`app`；容器名：`prsk-bot`；重启策略：`unless-stopped`。

常用命令：

```shell
python -m unittest discover -s tests -v
docker compose build
docker compose up -d
docker compose logs -f app
docker compose down
```

也可以使用 `make test`、`make build`、`make up`、`make logs` 和 `make down`。

## 代码结构

- `dcbot.py`：程序入口、Discord 事件、消息分发和定时任务。
- `config.py`：从环境变量读取并校验配置，集中生成 API URL 和请求头。
- `crawler.py`：异步 HTTP/API 客户端；底部的 camelCase 函数用于兼容旧调用。
- `event.py`：活动领域对象与提醒时间判断。
- `live.py`：虚拟 Live 领域对象与日程格式化。
- `participation.py`：成员参与登记和 mention 列表维护。
- `rankLogQueue.py`：排名快照队列、时速计算和表格图片生成。
- `tests/`：不依赖真实 Discord 或公网的单元测试。
- `Dockerfile`、`docker-compose.yml`、`Makefile`：NAS 部署和运维入口。
- `.env.example`：配置键示例，不含真实凭据。

## 配置与秘密信息

- 真实配置位于 `.env`；`.env.development` 和 `.env.production` 也可能包含敏感信息。
- 不要读取、输出、提交或复制任何真实 Token、API Header、用户 ID 或频道 ID。
- 新增环境变量时，同时更新 `AppConfig`、`.env.example`、README 和相关测试桩。
- 环境模式优先使用 `APP_ENV`；小写 `env` 仅为旧配置兼容。
- 不要把秘密写入源码、测试、日志、Dockerfile 或 Compose 文件。

## 修改规则

- 保持改动小而直接，不要为个人 Bot 引入不必要的框架或服务。
- 网络访问必须使用异步方式；Discord 事件循环中不要加入阻塞 I/O 或 `time.sleep()`。
- 外部 API 可能超时、返回非 200、空数据或错误 JSON；新增调用必须安全处理这些情况，不能让长期运行的 Bot 崩溃。
- 定时任务应捕获并记录单次执行错误，使后续周期仍可继续运行。
- 启动逻辑必须保留在 `main()` 和 `if __name__ == "__main__"` 中，确保导入模块时不会连接 Discord。
- 修改定时任务前检查重复启动；维持现有 `is_running()` 防护。
- 保持 `Asia/Tokyo` 时区和毫秒时间戳约定，除非需求明确改变。
- 不要随意修改现有 Discord 指令、频道分工、日文消息或 mention 行为；这些属于用户可见接口。
- 源文件和 Markdown 使用 UTF-8。若终端出现日文或中文乱码，不要据此批量替换字符串；先确认文件实际编码。
- `crawler.py` 的 camelCase 包装函数仍被现有代码和测试使用，重构时保持向后兼容，或同步迁移所有调用及测试。
- 排名图片使用内存缓冲区，不要在项目目录留下临时图片；创建 matplotlib figure 后必须关闭。

## 测试要求

每次代码修改后运行：

```shell
python -m unittest discover -s tests -v
```

测试原则：

- 不连接真实 Discord，不发送真实消息。
- 不访问公网 API；使用 fake、mock 或 `AsyncMock`。
- 不从真实 `.env` 获取秘密；测试内提供最小假配置。
- 修改命令解析、消息格式、配置读取、API 映射、时间判断或排名计算时，补充对应回归测试。
- 涉及 Docker 或依赖变更时，除单元测试外再执行 `docker compose build`。

## 完成标准

提交结果前确认：

1. 改动符合个人 NAS 常驻 Bot 的用途，没有扩大不必要的范围。
2. 没有泄露或硬编码任何秘密信息。
3. 所有单元测试通过。
4. 用户可见指令和消息保持兼容，或已明确说明变更。
5. 部署相关改动能通过 Docker Compose 使用，并更新了必要文档。
