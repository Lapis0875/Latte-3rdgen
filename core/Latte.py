import datetime, asyncio, discord, json, logging, random, sys, os
from pytz import timezone, utc
from typing import NoReturn, Iterable, Callable, List
from discord.ext.commands import AutoShardedBot
import sqlite3

from utils import recursive_container_loop, recursive_cog_loop


class Latte(AutoShardedBot):
    bot_config: dict = {}
    test_mode: bool = False
    initial_color: discord.Color = discord.Color.from_rgb(236, 202, 179)

    discord_base_invite: str = "https://discord.gg/"
    official_community_invite: str = "duYnk96"
    bug_report_invite: str = "t6vVSYX"

    def __init__(self, test_mode: bool = False, *args, **kwargs):
        if "command_prefix" in kwargs:
            kwargs.pop("command_prefix")
        super().__init__(command_prefix=";", *args, **kwargs)

        # Set bot`s test mode
        self.test_mode = test_mode

        # Set discord & bot`s logger
        self._set_logger()
        self.logger = self._get_logger()

        # Setup bot
        self._setup()

        self.presence_msg_list: List[str] = [
            "'라떼야 도움말' 로 라떼봇을 이용해보세요!",
            "라떼봇은 라떼를 좋아하는 개발자가 개발했습니다 :P",
            "라떼봇 개발자 : sleepylapis#1608",
            "라떼봇은 현재 개발중입니다!",
            "버그 제보는 언제나 환영이에요 :D",
            f"현재 {len(self.guilds)} 개의 서버에서 활동중이에요!"
        ]

    def run(self, *args, **kwargs):
        # Token is provided in Latte Class`s overrided run method, so pop token arg in args/kwargs
        if "token" in kwargs.keys():
            kwargs.pop("token")
        # Positional args :
        # run(*args, **kwargs) -> start(*args, **kwargs) -> login(token, *, bot=True) & connect(reconnect=reconnect)
        # We can pop all str args to remove token in positional args, because other args are not received as str.
        for arg in args:
            if type(arg) == str:
                del args[(args.index(arg))]

        # Initialize Bot
        self._init()

        # Run bot using Super-class (discord.ext.commands.AutoSharedBot).
        if self.test_mode:
            self.command_prefix = self.bot_config["test"]["prefix"]
            super().run(self.bot_config["test"]["token"], *args, **kwargs)
        else:
            self.command_prefix = self.bot_config["prefix"]
            super().run(self.bot_config["token"], *args, **kwargs)

        # Save Datas
        self._save()

    def _get_logger(self) -> logging.Logger:
        logger: logging.Logger = logging.getLogger(name="discord")
        return logger

    def _set_logger(self) -> NoReturn:
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
        logger: logging.Logger = self._get_logger()
        logger.setLevel(level=logging.INFO)

        console_handler: logging.Handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=console_handler)

        KST = timezone("Asia/Seoul")
        current_dt_KST: datetime.datetime = utc.localize(datetime.datetime.now()).astimezone(KST)
        log_filedir = f"./log/Latte/{current_dt_KST.tzname()}%"
        log_filedir += f"{current_dt_KST.year}-{current_dt_KST.month}-{current_dt_KST.day}%"
        log_filedir += f"{current_dt_KST.hour}-{current_dt_KST.minute}-{current_dt_KST.second}.txt"
        file_handler: logging.Handler = logging.FileHandler(filename=log_filedir, mode="x", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=file_handler)

    def _setup(self) -> NoReturn:
        self.logger.info(msg="Setup Phase :")
        self.load_bot_config()
        self.connect_guild_db()

    def load_bot_config(self) -> NoReturn:
        self.logger.info(msg="Loading bot`s configuration file...")
        with open(file="./config.json", mode="rt", encoding="utf-8") as config_file:
            self.bot_config = json.load(fp=config_file)

    def connect_guild_db(self):
        self.logger.info(msg="Connecting to bot`s guild database...")
        guild_db = sqlite3.connect(database="./DB/guilds.sqlite")
        user_db = sqlite3.connect(database="./DB/users.sqlite")

    def _init(self):
        self.logger.info(msg="Initialization Phase :")
        self.event(coro=self.on_ready)
        self.load_cogs()

    def load_cogs(self):
        self.logger.info(msg="Loading bot`s Cogs...")
        self.load_cog(dir=self.bot_config["cogs_dir"], exclude=self.bot_config["cogs_exceptions"])

    @recursive_cog_loop
    def load_cog(self, cog_name: str):
        self.logger.info(msg=f"Adding the Cog `{cog_name}` into bot ..")
        self.load_extension(name=cog_name)

    def unload_cogs(self):
        self.logger.info(msg="Unloading bot`s Cogs...")
        self.unload_cog(container=os.listdir(self.bot_config["cogs_dir"]))

    @recursive_cog_loop
    def unload_cog(self, cog_name: str):
        self.logger.info(msg=f"Removing the Cog `{cog_name}` into bot ..")
        self.remove_cog(name=cog_name)

    def _save(self):
        self.logger.info(msg="Save Phase :")

    def save_bot_config(self) -> NoReturn:
        self.logger.info(msg="Saving bot`s configuration file...")
        with open(file="./config.json", mode="wt", encoding="utf-8") as config_file:
            json.dump(obj=self.bot_config, fp=config_file)

    async def presence_loop(self):
        """
        Change bot`s presence info using async Task & loop
        :return: None
        """
        await self.wait_until_ready()
        while not self.is_closed():
            msg: str = random.choice(self.presence_msg_list)
            # 봇이 플레이중인 게임을 설정할 수 있습니다.
            await self.change_presence(
                status=discord.Status.online, activity=discord.Game(name=msg, type=1)
            )
            await asyncio.sleep(30)

    async def on_ready(self):
        """
        Change bot`s presence info using async Task & loop
        :return: None
        """
        self.logger.info("봇 온라인!")
        self.logger.info(f"owner_id : {self.owner_id}")

        # 봇의 상태메세지를 지속적으로 변경합니다.
        self.loop.create_task(self.presence_loop())









