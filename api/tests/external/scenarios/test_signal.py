import os

import pytest

from tests.external.support.scenario import wait_for_control, write_checkpoint


pytestmark = pytest.mark.skipif(
    os.getenv("VIRTY_INFRA_SCENARIO", "happy") not in {"signal-int", "signal-term"},
    reason="signal scenarioだけで実行します",
)


def test_signal_invokes_real_devctl_cleanup(created_storage) -> None:
    write_checkpoint("signal-resource-created")
    # host harnessが実際のdevctl processへsignalを送る。signalが届かなければ有限時間で失敗する。
    wait_for_control("unexpected-signal-continue", timeout_seconds=180)
    pytest.fail("signal scenarioでdevctl processが終了しませんでした")
