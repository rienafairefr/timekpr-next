from timekpr.common.utils.misc import splitConfigValueNameParam


def test_splitConfigValueNameParam():
    assert ("!22", "00-15") == splitConfigValueNameParam("!22[00-15]")
    assert ("3600", "3") == splitConfigValueNameParam("3600[3]")
    assert ("3600", "3") == splitConfigValueNameParam('3600("3")')
