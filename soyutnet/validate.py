from typing_extensions import Any, Type, Union


_PTCommon: Any = None
_Place: Any = None
_Transition: Any = None
_Arc: Any = None


class ModelError(Exception): ...


def init_validator(classes: list[Type[Any]]) -> None:
    global _PTCommon, _Place, _Transition
    for cls in classes:
        match cls.__name__:
            case "PTCommon":
                _PTCommon = cls
            case "Place":
                _Place = cls
            case "Transition":
                _Transition = cls
            case "Arc":
                _Arc = cls


def validate_arc_connection_types(start: _PTCommon, end: _PTCommon) -> None:
    match start, end:
        case _Place(), _Place():
            raise ModelError(f"Can not connect {start} to {end}")
        case _Transition(), _Transition():
            raise ModelError(f"Can not connect {start} to {end}")
        case _, _:
            match start:
                case _Place() | _Transition() | None:
                    ...
                case _:
                    raise ModelError(f"Arc can not start from {type(start)}")
            match end:
                case _Place() | _Transition() | None:
                    ...
                case _:
                    raise ModelError(f"Arc can not start from {type(start)}")

    if start is not None and end is not None:
        if start.net != end.net:
            raise ModelError("Can not connect to a PT in an other net")


def validate_arc(obj: _Arc, attr: Any, output: Any, *args: Any, **kwargs: Any) -> None:
    attr_name: str = attr.__name__
    match attr_name:
        case "start" | "end":
            validate_arc_connection_types(obj.start, obj.end)
        case "__rshift__" | "__lshift__" | "__gt__" | "__lt__":
            if not isinstance(obj.start, _PTCommon) or isinstance(obj.end, _PTCommon):
                raise ModelError


def validate_net(obj: Any, attr: Any, output: Any, *args: Any, **kwargs: Any) -> None:
    match obj:
        case _Arc:
            validate_arc(obj, attr, output, *args, **kwargs)
