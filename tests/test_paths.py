import os

import pytest

from timekpr.common.constants.constants import (
    TK_MAIN_CONFIG_DIR_DEV,
    TK_CONFIG_DIR_DEV,
    TK_WORK_DIR_DEV,
    TK_SHARED_DIR_DEV,
    TK_LOGFILE_DIR_DEV,
    TK_LOCALIZATION_DIR_DEV,
)
from timekpr.client import timekpra
from timekpr.client import timekprc
from timekpr.server import timekprd

elements = [
    (TK_MAIN_CONFIG_DIR_DEV,),
    (TK_CONFIG_DIR_DEV,),
    (TK_WORK_DIR_DEV,),
    (TK_SHARED_DIR_DEV,),
    (TK_LOGFILE_DIR_DEV,),
    (TK_LOCALIZATION_DIR_DEV,),
]


@pytest.mark.parametrize(
    ["element"],
    elements,
)
def test_dev_paths_timekpra(element):
    cwd = os.path.dirname(timekpra.__file__)
    assert os.path.exists(os.path.abspath(os.path.join(cwd, TK_MAIN_CONFIG_DIR_DEV)))


@pytest.mark.parametrize(
    ["element"],
    elements,
)
def test_dev_paths_timekprd(element):
    cwd = os.path.dirname(timekprd.__file__)
    assert os.path.exists(os.path.abspath(os.path.join(cwd, TK_MAIN_CONFIG_DIR_DEV)))


@pytest.mark.parametrize(
    ["element"],
    elements,
)
def test_dev_paths_timekprc(element):
    cwd = os.path.dirname(timekprc.__file__)
    assert os.path.exists(os.path.abspath(os.path.join(cwd, TK_MAIN_CONFIG_DIR_DEV)))
