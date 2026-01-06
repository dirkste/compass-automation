import logging
import os
from datetime import date
from enum import Enum
import inspect
import time
from typing import Any, Dict, Optional

from compass_automation.config.config_loader import get_config


class ColorFormatter(logging.Formatter):
    """Legacy color formatter kept for backwards compatibility.

    The new Two-Vector logger does not use this formatter by default.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # cyan
        "INFO": "\033[37m",  # white
        "WARNING": "\033[33m",  # yellow
        "ERROR": "\033[31m",  # red
        "CRITICAL": "\033[41m",  # red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


_VERBOSITY_RANK: Dict[str, int] = {
    "MIN": 0,
    "MED": 1,
    "FULL": 2,
}

_CRIT_ABBR: Dict[int, str] = {
    logging.DEBUG: "DBG",
    logging.INFO: "INF",
    logging.WARNING: "WRN",
    logging.ERROR: "ERR",
    # Requirement calls this "FATAL"; Python's CRITICAL/FATAL map to the same level.
    logging.CRITICAL: "FTL",
}


class Verbosity(str, Enum):
    MIN = "MIN"
    MED = "MED"
    FULL = "FULL"


def _normalize_verbosity(value: Optional[str]) -> str:
    if isinstance(value, Verbosity):
        return value.value
    if not value:
        return "MED"
    value = str(value).strip().upper()
    return value if value in _VERBOSITY_RANK else "MED"


def _verbosity_rank(value: Optional[str]) -> int:
    return _VERBOSITY_RANK[_normalize_verbosity(value)]


def _parse_level(level: Any) -> int:
    if isinstance(level, int):
        return level
    if level is None:
        return logging.INFO
    return logging._nameToLevel.get(str(level).strip().upper(), logging.INFO)


_CURRENT_MIN_LEVELNO = logging.INFO
_CURRENT_MAX_VERBOSITY = _verbosity_rank("MED")


def _should_log(levelno: int, verbosity: Optional[str]) -> bool:
    # Fast-path check used by TwoVectorLogger helpers.
    if levelno < _CURRENT_MIN_LEVELNO:
        return False
    if _verbosity_rank(verbosity) > _CURRENT_MAX_VERBOSITY:
        return False
    return True


def _default_source(logger_name: str) -> str:
    # Prefer a stable, human-friendly component tag.
    # If the logger name is namespaced, keep only the last segment.
    return "APP"


def _infer_source_from_message(message: str) -> Optional[str]:
    """Infer Source from a leading tag like '[DRIVER] ...'.

    Many existing call sites already prefix messages with component tags.
    This lets us populate the [Source] header without touching every call site.
    """

    if not message or not message.startswith("["):
        return None
    close = message.find("]")
    if close <= 1:
        return None
    tag = message[1:close].strip()
    if not tag or len(tag) > 20:
        return None
    # Keep it conservative: alnum + a few safe separators.
    for ch in tag:
        if not (ch.isalnum() or ch in "_-:"):
            return None
    return tag


def _strip_leading_source_tag(message: str, source: str) -> str:
    """Remove a leading '[SOURCE]' tag from the message if it matches `source`.

    This prevents duplication like: [LOGIN] ... appearing both in the [Source]
    header and inside the angle-bracketed message payload.
    """

    if not message or not source:
        return message
    if not message.startswith("["):
        return message
    close = message.find("]")
    if close <= 1:
        return message

    leading = message[1:close].strip()
    if leading.upper() != str(source).strip().upper():
        return message

    remainder = message[close + 1 :]
    if remainder.startswith(" "):
        remainder = remainder[1:]
    return remainder


class TwoVectorFormatter(logging.Formatter):
    """Format logs as: [HH:MM:SS][CRIT_VERB][Source][Context] <Message>"""

    def format(self, record: logging.LogRecord) -> str:
        if getattr(record, "is_session_header", False):
            session_date = getattr(record, "session_date", None) or date.today().isoformat()
            return f"=== Log Session Started: {session_date} ==="

        # Slightly cheaper than datetime.fromtimestamp(...).strftime(...)
        time_str = time.strftime("%H:%M:%S", time.localtime(record.created))

        crit_abbr = _CRIT_ABBR.get(record.levelno)
        if not crit_abbr:
            level_name = str(record.levelname or "INFO").upper()
            crit_abbr = level_name[:3]
        verbosity = _normalize_verbosity(getattr(record, "verbosity", None))
        vector = f"{crit_abbr}_{verbosity}"

        message = record.getMessage()

        source = getattr(record, "source", None)
        if not source:
            source = _infer_source_from_message(message) or _default_source(record.name)
        context = getattr(record, "context", None) or record.funcName

        message = _strip_leading_source_tag(message, source)

        # No spaces between brackets; message wrapped in angle brackets.
        line = f"[{time_str}][{vector}][{source}][{context}]<{message}>"

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            line = f"{line}\n{exc_text}"
        if record.stack_info:
            line = f"{line}\n{self.formatStack(record.stack_info)}"
        return line


class TwoVectorFilter(logging.Filter):
    """Filter messages by minimum criticality and maximum verbosity."""

    def __init__(self, min_crit: Any = logging.INFO, max_verb: str = "MED") -> None:
        super().__init__()
        self.min_levelno = _parse_level(min_crit)
        self.max_verbosity = _verbosity_rank(max_verb)

    def filter(self, record: logging.LogRecord) -> bool:
        # Always allow the session header through.
        if getattr(record, "is_session_header", False):
            return True
        if record.levelno < self.min_levelno:
            return False
        if _verbosity_rank(getattr(record, "verbosity", None)) > self.max_verbosity:
            return False
        return True


class TwoVectorLogger(logging.LoggerAdapter):
    """LoggerAdapter that sets Source/Verbosity via `extra`.

    Context defaults to the caller's function name via the formatter.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        source: str,
        verbosity: str = "MED",
        context: Optional[str] = None,
    ) -> None:
        extra: Dict[str, Any] = {
            "source": source,
            "verbosity": _normalize_verbosity(verbosity),
        }
        if context:
            extra["context"] = context
        super().__init__(logger, extra)

    def process(self, msg: str, kwargs: Dict[str, Any]):
        merged_extra: Dict[str, Any] = dict(self.extra)
        call_extra = kwargs.get("extra") or {}
        merged_extra.update(call_extra)
        merged_extra["verbosity"] = _normalize_verbosity(merged_extra.get("verbosity"))
        kwargs["extra"] = merged_extra
        # Ensure record.funcName points at the actual caller when using the adapter.
        # logging skips frames inside the logging module automatically; stacklevel=1
        # reliably lands on the function that called adapter.info()/warning()/... .
        kwargs.setdefault("stacklevel", 1)
        return msg, kwargs

    def logv(self, level: Any, verbosity: Any, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log with explicit verbosity.

        Efficiency note: if you pass `msg` + `*args` (printf-style), interpolation
        is avoided when the record is filtered out. (Avoid f-strings for expensive
        formatting if you want this guarantee.)
        """

        levelno = _parse_level(level)
        verbosity_norm = _normalize_verbosity(verbosity)
        if not _should_log(levelno, verbosity_norm):
            return
        # Merge adapter extras (e.g. source/context) with any call-site extras.
        merged_extra: Dict[str, Any] = dict(self.extra)
        call_extra = kwargs.pop("extra", {}) or {}
        merged_extra.update(call_extra)
        merged_extra["verbosity"] = verbosity_norm
        kwargs["extra"] = merged_extra
        # Call chain is usually: caller -> adapter.info_v/warning_v/... -> logv -> logger.log
        # stacklevel=2 attributes the record to the original caller.
        kwargs.setdefault("stacklevel", 2)
        self.logger.log(levelno, msg, *args, **kwargs)

    def info_v(self, verbosity: Any, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logv(logging.INFO, verbosity, msg, *args, **kwargs)

    def warning_v(self, verbosity: Any, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logv(logging.WARNING, verbosity, msg, *args, **kwargs)

    def error_v(self, verbosity: Any, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logv(logging.ERROR, verbosity, msg, *args, **kwargs)

    def fatal_v(self, verbosity: Any, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logv(logging.CRITICAL, verbosity, msg, *args, **kwargs)


def logger_from_caller(
    *,
    logger: Optional[logging.Logger] = None,
    verbosity: Any = "MED",
    context: Optional[str] = None,
    skip: int = 0,
) -> TwoVectorLogger:
    """Create a TwoVectorLogger with `source` derived from the caller function name.

    This is useful when you want Source=function (instead of Source=component).

    Notes:
    - Context already defaults to the calling function name in the formatter.
    - Prefer explicit component sources (DRIVER/NAV/LOGIN/...) for long-term value.
    """

    base_logger = logger or log
    frame = inspect.currentframe()
    try:
        # frame = logger_from_caller -> caller -> (skip)
        for _ in range(2 + max(0, skip)):
            if frame is None:
                break
            frame = frame.f_back
        func_name = frame.f_code.co_name if frame is not None else "APP"
    finally:
        # Avoid reference cycles
        del frame

    return TwoVectorLogger(base_logger, source=func_name, verbosity=_normalize_verbosity(verbosity), context=context)


_SESSION_HEADER_PRINTED = False


def _log_session_header(logger: logging.Logger) -> None:
    # Emit via logging so ordering is correct and it appears once per handler.
    logger.log(
        logging.INFO,
        "",
        extra={"is_session_header": True, "session_date": date.today().isoformat()},
        stacklevel=3,
    )


def setup_logging(
    min_crit: Any = None,
    max_verb: Any = "MED",
    *,
    log_file: str = "automation.log",
    logger_name: str = "mc.automation",
) -> logging.Logger:
    """Configure the project logger.

    - Adds a one-time session header line containing today's date.
    - Applies Two-Vector formatting: [HH:MM:SS][CRIT_VERB][Source][Context] <Message>
    - Drops messages below min criticality or above max verbosity.
    """

    global _SESSION_HEADER_PRINTED, _CURRENT_MIN_LEVELNO, _CURRENT_MAX_VERBOSITY

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # filtering is handled by TwoVectorFilter
    logger.propagate = False

    formatter = TwoVectorFormatter()

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # If something configured handlers earlier, normalize them to our formatter
        # so output is consistent (and doesn't include spaces between bracket groups).
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)

        # FileHandler is a StreamHandler subclass; don't count it as the console stream.
        has_stream = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )

        normalized_log_file = os.path.abspath(log_file)
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        matching_file_handlers = [
            h
            for h in file_handlers
            if os.path.abspath(getattr(h, "baseFilename", "")) == normalized_log_file
        ]
        # Keep only one handler pointing at our configured log file.
        if len(matching_file_handlers) > 1:
            for duplicate in matching_file_handlers[1:]:
                logger.removeHandler(duplicate)
                try:
                    duplicate.close()
                except Exception:
                    pass
        has_file = len(matching_file_handlers) >= 1

        if not has_stream:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        if not has_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    # Replace any existing TwoVectorFilter to support reconfiguration.
    logger.filters = [f for f in logger.filters if not isinstance(f, TwoVectorFilter)]
    logger.addFilter(TwoVectorFilter(min_crit=min_crit, max_verb=_normalize_verbosity(max_verb)))

    # Keep fast-path thresholds in sync for adapter helpers.
    _CURRENT_MIN_LEVELNO = _parse_level(min_crit)
    _CURRENT_MAX_VERBOSITY = _verbosity_rank(_normalize_verbosity(max_verb))

    if not _SESSION_HEADER_PRINTED:
        _log_session_header(logger)
        _SESSION_HEADER_PRINTED = True

    return logger


# Exported singleton logger (kept for backwards compatibility)
log = logging.getLogger("mc.automation")


def _setup_defaults() -> None:
    # Defaults can be overridden by calling setup_logging() explicitly.
    default_min_crit = get_config("logging.min_crit", get_config("logging.level", "INFO"))
    default_max_verb = get_config("logging.max_verb", "MED")
    default_log_file = get_config("logging.file", "automation.log")
    setup_logging(default_min_crit, default_max_verb, log_file=default_log_file)


_setup_defaults()


def _examples() -> None:
    """Three example calls with distinct vectors."""

    setup_logging(min_crit="DEBUG", max_verb="FULL")

    app = TwoVectorLogger(log, source="APP", verbosity="MIN")
    app.info("Startup complete")  # [INF_MIN]

    nav = TwoVectorLogger(log, source="NAV")
    nav.warning("Retrying navigation", extra={"verbosity": "MED"})  # [WRN_MED]

    db = TwoVectorLogger(log, source="DB", verbosity="FULL")
    db.error("Database connection failed")  # [ERR_FULL]