import datetime, asyncio, discord, json, logging, random, sys, os
from pytz import timezone, utc
from typing import NoReturn, Iterable, Callable, List, Union
from discord.ext.commands import AutoShardedBot
import sqlite3
from lavalink import Client as LavalinkClient

from utils import recursive_container_loop, recursive_cog_loop, surpress_exceptions, surpress_cog_exceptions


class Latte(AutoShardedBot):
    """
    class Latte:
    class for latte, the discord bot. It extends :class:`discord.ext.commands.AutoShardedBot` to automatically perform sharding.
    This class not only stores several configuration datas, but also add some features into bot
    so developers can develop this bot in convinient ways.
    """
    # Configuration Storage
    bot_config: dict = {}
    test_mode: bool = False
    initial_color: discord.Color = discord.Color.from_rgb(236, 202, 179)
    warning_color: discord.Color = discord.Color.gold()
    error_color: discord.Color = discord.Color.red()
    db_dir: str = "./DB/datas.db"
    do_reboot: bool = False

    # Music Client
    lavalink: LavalinkClient = None
    lavalink_host = None

    presence_msg_list: List[str] = []
    discord_base_invite: str = "https://discord.gg/"
    official_community_invite: str = "duYnk96"
    bug_report_invite: str = "t6vVSYX"

    def __init__(self, test_mode: bool = False, *args, **kwargs):
        """
        Initialize `Latte` instance.
        :param test_mode: boolean value which indicates whether latte should run as test mode.
        :param args: arguments which is required to call superclass`s __init__() method.
        :param kwargs: keyword-arguments which is required to call superclass`s __init__() method.
        """
        if "command_prefix" in kwargs:
            kwargs.pop("command_prefix")
        super().__init__(command_prefix=";", *args, **kwargs)

        # Set bot`s test mode
        self.test_mode = test_mode

        # Set discord & bot`s logger
        self._set_logger(level=logging.INFO)
        self.logger = self.__get_logger()

        # Setup bot
        self._setup()

        # DEBUG
        print(f"Current guilds list : {self.guilds}")

    def run(self, *args, **kwargs):
        """
        Run latte.
        :param args: arguments which is required to call superclass`s run() method.
        :param kwargs: keyword-arguments which is required to call superclass`s run() method.
        """

        # Token is provided in Latte Class`s overrided run method, so pop token arg in args/kwargs
        # Argument pass => run(*args, **kwargs)
        # -> start(*args, **kwargs)
        # -> login(token, *, bot=True) & connect(reconnect=reconnect)

        # Keyword arguments :
        # [ bot: bool (run -> start -> login) / reconnect: bool (run -> start -> connect) ]
        # Additional Keyword arguments are not used in run() process, but I want to make it clear taht `token` is not
        # in kwargs.
        if "token" in kwargs.keys():
            kwargs.pop("token")

        # Positional arguments :
        # [ token: str (run -> start -> login) ]
        # We can pop all str args to remove token in positional args,
        # because run() method only require one string arguement, token.
        for arg in args:
            if type(arg) == str:
                del args[args.index(arg)]

        # Initialize Bot
        self._init()

        # Start Lavalink server
        self.lavalink_host = os.popen("java -jar Lavalink.jar")
        print(self.lavalink_host)
        print(self.lavalink_host.name)
        print(self.lavalink_host.encoding)
        print(self.lavalink_host.errors)

        # Run bot using Super-class (discord.ext.commands.AutoSharedBot).
        if self.test_mode:
            self.command_prefix = self.bot_config["test"]["prefix"]
            super().run(self.bot_config["test"]["token"], *args, **kwargs)

        else:
            self.command_prefix = self.bot_config["prefix"]
            super().run(self.bot_config["token"], *args, **kwargs)

        # Save Datas
        self._save()

    def check_reboot(self) -> bool:
        return self.do_reboot and self.is_closed()

    @staticmethod
    def __get_logger() -> logging.Logger:
        """
        Get latte`s logger. Simpler command of `logging.getLogger(name="discord")
        :return: logging.Logger instance which latte uses as logger.
        """
        return logging.getLogger(name="discord")

    @surpress_exceptions
    def _set_logger(self, level=logging.INFO):
        """
        Set some options of latte`s loggeer.
        """
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
        logger: logging.Logger = self.__get_logger()
        logger.setLevel(level=level)

        console_handler: logging.Handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=console_handler)

        KST = timezone("Asia/Seoul")
        current_dt_KST: datetime.datetime = utc.localize(datetime.datetime.now()).astimezone(KST)
        current_dt_KST_month: str = '0' + (str(current_dt_KST.month) if (0 < current_dt_KST.month < 10) else str(current_dt_KST.month))
        log_filedir = f"./logs/Latte/{current_dt_KST.tzname()}%"
        log_filedir += f"{current_dt_KST.year}-{current_dt_KST_month}-{current_dt_KST.day}% "
        log_filedir += f"{current_dt_KST.hour}-{current_dt_KST.minute}-{current_dt_KST.second}.txt"
        file_handler: logging.Handler = logging.FileHandler(filename=log_filedir, mode="x", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=file_handler)

        import os
        log_files: List[str] = os.listdir("./logs/Latte")
        if len(log_files) > 7:
            """
            If logs files are stored more than 7, latte will automatically delete logs except recent 7 ones.
            """
            logger.info(msg="Too many logs files are stored! Deleting except recent 7 logs...")
            for log_file in sorted(log_files, reverse=True)[7:]:
                logger.info(msg=f"Deleting lof file ./logs/Latte/{log_file}")
                os.remove(path=f'./logs/Latte/{log_file}')

    @surpress_exceptions
    def _setup(self):
        """
        Setup latte.
        :raise: Exception occured during setup phase
        """
        self.logger.info(msg="Setup Phase Started :")
        self.load_bot_config()
        self.check_guild_DB()
        self.logger.info(msg="Setup Phase Finished.")

    @surpress_exceptions
    def check_guild_DB(self):
        """
        Check bot`s database. If required .db file not exists, this method will create it. If required table not exists, this method will create it.
        :raise: sqlite3.Error or subclass instances.
        """
        self.logger.info(msg="Checking bot`s database...")

        datas_db = sqlite3.connect(database=self.db_dir)
        datas_db.execute('CREATE TABLE IF NOT EXISTS  "config" ('
                         '"id"	INTEGER NOT NULL UNIQUE, '
                         '"name"    TEXT NOT NULL, '
                         '"logs" INTEGER NOT NULL, '
                         '"auth_enabled"    TEXT,'
                         '"help_dm"    TEXT,'
                         'PRIMARY KEY("id")'
                         ') WITHOUT ROWID;')

        datas_db.execute('CREATE TABLE IF NOT EXISTS "user_level" ('
                             '"id"	NUMERIC NOT NULL,'
                             '"level"	INTEGER NOT NULL,'
                             '"xp"	REAL NOT NULL,'
                             '"rank"	TEXT NOT NULL,'
                             '"title"	TEXT,'
                             'PRIMARY KEY("id")'
                             ') WITHOUT ROWID;')
        datas_db.close()

    @surpress_exceptions
    def load_bot_config(self):
        """
        load latte`s config file (config.json)
        """
        self.logger.info(msg="Loading bot`s configuration file...")
        with open(file="config.json", mode="rt", encoding="utf-8") as config_file:
            self.bot_config = json.load(fp=config_file)

    @surpress_exceptions
    async def connect_db(self) -> Union[sqlite3.Connection, NoReturn]:
        """
        connect bot`s database.
        :return: sqlite3.Connection instance of target database if connection was successful. If not, then ValueError will be raised.
        """
        return sqlite3.connect(database=self.db_dir)

    @surpress_exceptions
    def _init(self):
        """
        Initialize latte.
        :raise: Exception occured during initialization process.
        """
        self.logger.info(msg="Initialization Phase Started :")
        self.event(coro=self.on_ready)
        self.load_cogs(dir=self.bot_config["cogs_dir"], exclude=self.bot_config["cogs_exceptions"])

        self.presence_msg_list: List[str] = [
            "'라떼야 도움말' 로 라떼봇을 이용해보세요!",
            "라떼봇은 라떼를 좋아하는 개발자가 개발했습니다 :P",
            "라떼봇 개발자 : sleepylapis#1608",
            "라떼봇은 현재 개발중입니다!",
            "버그 제보는 언제나 환영이에요 :D"
        ]

        self.lavalink = LavalinkClient(user_id=self.user.id if self.user is not None else self.bot_config["id"])

        self.logger.info(msg="Initialization Phase Finished")

    @surpress_cog_exceptions
    @recursive_cog_loop
    def load_cogs(self, cog_name: str):
        """
        Original method : call :method load_cog: using given :param cog_name:

        Decirated method : Loop thorugh list of cog directory and load all Cogs into bot using original method.

        :param cog_name: String value which indicates Cog`s path.
        """
        self.load_cog(cog_name=cog_name)

    @surpress_cog_exceptions
    def load_cog(self, cog_name: str):
        """
        Load Cog using given parameter :param cog_name:

        :param cog_name: String value which indicates Cog`s path.
        """
        self.logger.info(msg=f"Adding the Cog `{cog_name}` into bot ..")
        self.load_extension(name=cog_name)

    @surpress_cog_exceptions
    @recursive_cog_loop
    def unload_cogs(self, cog_name: str):
        """
        Original method : call :method unload_cog: using given :param cog_name:

        Decirated method : Loop thorugh list of cog directory and unload all Cogs into bot using original method.

        :param cog_name: String value which indicates Cog`s path.
        """
        self.unload_cog(cog_name=cog_name)

    @surpress_cog_exceptions
    def unload_cog(self, cog_name: str):
        """
        Unload Cog using given parameter :param cog_name:

        :param cog_name: String value which indicates Cog`s path.
        """
        self.logger.info(msg=f"Removing the Cog `{cog_name}` into bot ..")
        self.unload_extension(name=cog_name)

    @surpress_cog_exceptions
    @recursive_cog_loop
    def reload_cogs(self, cog_name: str):
        """
        Original method : call :method reload_cog: using given :param cog_name:

        Decirated method : Loop thorugh list of cog directory and reload all Cogs into bot using original method.

        :param cog_name: String value which indicates Cog`s path.
        """
        self.reload_cog(cog_name=cog_name)

    @surpress_cog_exceptions
    def reload_cog(self, cog_name: str):
        """
        Reload Cog using given parameter :param cog_name:

        :param cog_name: String value which indicates Cog`s path.
        """
        self.logger.info(msg=f"Removing the Cog `{cog_name}` into bot ..")
        self.reload_extension(name=cog_name)

    @surpress_exceptions
    def _save(self):
        """
        save bot`s datas.
        """
        self.logger.info(msg="Save Phase :")
        self.save_bot_config()

    @surpress_exceptions
    def save_bot_config(self):
        self.logger.info(msg="Saving bot`s configuration file...")
        with open(file="./config.json", mode="wt", encoding="utf-8") as config_file:
            json.dump(obj=self.bot_config, fp=config_file)

    async def presence_loop(self):
        """
        Change bot`s presence info using asyncio event loop
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
        event listener for latte`s on_ready event.
        """
        self.logger.info("봇 온라인!")
        self.logger.info(f"self.owner_id : {self.owner_id}")
        self.logger.info(f"self.owner_ids : {self.owner_ids}")
        self.logger.info(f"self.user.id : {self.user.id}")

        # 봇의 상태메세지를 지속적으로 변경합니다.
        self.loop.create_task(self.presence_loop())

    @surpress_exceptions
    async def send_log(self, guild_id: int, log: str):
        datas_db = await self.connect_db()
        exec_con: sqlite3.Cursor = datas_db.execute(sql="SELECT logs FROM config WHERE id=?", parameters=(guild_id,))
        await self.get_channel(id=exec_con.fetchall()[0]).send(content=log)
