import re

from loguru import logger

from secondbrain.app import configure_logging, main

TIMESTAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"


def test_main_logs_greeting(capfd, tmp_path):
    main()
    captured = capfd.readouterr()
    assert re.fullmatch(
        rf"{TIMESTAMP} \| INF \| secondbrain\.app:main:\d+ \| Hello from secondbrain!\n",
        captured.err,
    )
    assert re.fullmatch(
        rf"{TIMESTAMP}\.\d{{3}} [+-]\d{{2}}:\d{{2}} \| INFO {{4}} \| "
        r"secondbrain\.app:main:\d+ - Hello from secondbrain!\n",
        (tmp_path / "test.log").read_text(encoding="utf-8"),
    )


def test_console_level_labels(capfd, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()

    levels = {
        "TRACE": "TRA",
        "DEBUG": "DEB",
        "INFO": "INF",
        "SUCCESS": "SUC",
        "WARNING": "WAR",
        "ERROR": "ERR",
        "CRITICAL": "CRI",
    }
    for level in levels:
        logger.log(level, level)

    lines = capfd.readouterr().err.splitlines()
    assert len(lines) == len(levels)
    for line, (level, label) in zip(lines, levels.items(), strict=True):
        assert re.fullmatch(
            rf"{TIMESTAMP} \| {label} \| [\w.]+:test_console_level_labels:\d+ \| {level}",
            line,
        )


def test_log_level_filters_only_console(capfd, monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    configure_logging()

    logger.info("Below threshold")
    logger.warning("At threshold")

    console = capfd.readouterr().err
    assert "Below threshold" not in console
    assert "At threshold" in console

    file_log = (tmp_path / "test.log").read_text(encoding="utf-8")
    assert "Below threshold" in file_log
    assert "At threshold" in file_log


def test_console_preserves_exception_traceback(capfd):
    configure_logging()

    try:
        raise ValueError("invalid input")
    except ValueError:
        logger.exception("Processing failed")

    header, traceback = capfd.readouterr().err.split("\n", 1)
    assert re.fullmatch(
        rf"{TIMESTAMP} \| ERR \| [\w.]+:test_console_preserves_exception_traceback:\d+ "
        r"\| Processing failed",
        header,
    )
    assert "Traceback (most recent call last):" in traceback
    assert traceback.endswith("ValueError: invalid input\n")
