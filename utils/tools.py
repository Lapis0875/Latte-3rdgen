import traceback
from discord import Embed, Color, Colour
from typing import Type, NoReturn, Dict, Tuple, List
from argparse import ArgumentTypeError


def cast_to_bool(arg: str):
    # True case
    if arg in ["True", "true", "1"]:
        return True

    # False case
    elif arg in ["False", "false", "0"]:
        return False

    # Not suitable args
    else:
        msg = f"Cannot cast an argument `{arg}` into boolean : Not a boolean indicator"
        raise ArgumentTypeError(msg)


def parse_traceback(exception: Type[Exception]) -> NoReturn:
    print("Exception details :")
    print(exception.with_traceback(exception.__traceback__))
    print("Traceback details :")
    traceback_list = traceback.extract_tb(exception.__traceback__).format()
    for tb in traceback_list:
        print(tb)


class EmbedFactory:
    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> NoReturn:
        self._title = str(value)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> NoReturn:
        self._description = str(value)

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, value: Color) -> NoReturn:
        if isinstance(value, (Colour, Color)):
            self._color = value
        else:
            raise InvalidColorError(embed_factory=self)

    @property
    def author(self) -> Dict[str, str]:
        return self._author

    @author.setter
    def author(self, value: Dict[str, str]) -> NoReturn:
        self._author = value

    @property
    def footer(self) -> Dict[str, str]:
        return self._footer

    @footer.setter
    def footer(self, value: Dict[str, str]) -> NoReturn:
        self._footer = value

    @property
    def thumbnail_url(self) -> str:
        return self._thumbnail_url

    @thumbnail_url.setter
    def thumbnail_url(self, value: str) -> NoReturn:
        self._thumbnail_url = value

    @property
    def image_url(self) -> str:
        return self._image_url

    @image_url.setter
    def image_url(self, value: str) -> NoReturn:
        self._image_url = value

    @property
    def fields(self) -> list:
        return self._fields

    @fields.setter
    def fields(self, value: List[Dict[str, str]]) -> NoReturn:
        self._fields = value

    def __init__(self, **attrs):
        # Initialize class variables
        self._title = attrs.pop("title") if "title" in attrs.keys() else ""
        self._description = attrs.pop("description") if "description" in attrs.keys() else ""
        self._color = attrs.pop("color") if "color" in attrs.keys() else Color.blurple()
        self._author = attrs.pop("author") if "author" in attrs.keys() else {"name": "", "icon_url": ""}
        self._footer = attrs.pop("footer") if "footer" in attrs.keys() else {"text": "", "icon_url": ""}
        self._thumbnail_url = attrs.pop("thumbnail_url") if "thumbnail_url" in attrs.keys() else ""
        self._image_url = attrs.pop("image_url") if "image_url" in attrs.keys() else ""
        self._fields = attrs.pop("fields") if "fields" in attrs.keys() else []

        if attrs:
            raise UnexpectedKwargsError(embed_factory=self)

    async def add_field(self, name: str, value: str):
        self.fields.append({"name": name, "value": value})

    async def add_fields(self, *fields: Dict[str, str]) -> NoReturn:
        for field in fields:
            if "name" in field.keys() and "value" in field.keys():
                self.fields.append(field)
            else:
                raise InvalidFieldError(embed_factory=self)

    async def build(self) -> Embed:
        embed = Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

        if self.thumbnail_url != "":
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.image_url != "":
            embed.set_image(url=self.image_url)

        if self.author["name"] != "" and self.author["icon_url"] != "":
            embed.set_author(name=self.author["name"], icon_url=self.author["icon_url"])

        for field in self.fields:
            embed.add_field(name=field["name"], value=field["value"])

        if self.footer["text"] != "" and self.footer["icon_url"] != "":
            embed.set_footer(text=self.footer["text"], icon_url=self.footer["icon_url"])

        return embed


class EmbedFactoryException(Exception):
    @property
    def msg(self) -> str:
        return self._msg

    @property
    def embed_factory(self) -> EmbedFactory:
        return self._embed_factory

    def __init__(self, *args, **kwargs):
        self._msg = kwargs.pop("msg") if "msg" in kwargs.keys() else "An Exception caught during using EmbedFactory"
        self._embed_factory = kwargs.pop("embed_factory") if "embed_factory" in kwargs.keys() else None
        super().__init__(*args, **kwargs)


class UnexpectedKwargsError(EmbedFactoryException):
    def __init__(self, *args, **kwargs):
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        super().__init__(*args, msg="`EmbedFactory.__init__()` caught unexpected keyword arguments!", **kwargs)


class InvalidColorError(EmbedFactoryException):
    def __init__(self, *args, **kwargs):
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        super().__init__(*args, msg="`EmbedFactory.color` property only accpets instance of `discord.Colour` or `discord.Color`!", **kwargs)


class InvalidFieldError(EmbedFactoryException):
    def __init__(self, *args, **kwargs):
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        super().__init__(*args, msg='"`EmbedFactory.fields` property only accepts instance which has structure of `{"name": name, "value": value}`"', **kwargs)
