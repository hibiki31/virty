from __future__ import annotations

import json
import os
import signal
from collections.abc import Mapping
from pprint import pformat
from typing import Any, Dict

import ansible_runner

from mixin.log import setup_logger
from mixin.schemas import BaseModel
from mixin.timestamp import get_timestamp
from settings import APP_ROOT, DATA_ROOT

logger = setup_logger(__name__)


class AnsibleRunResult(BaseModel):
    status: str
    rc: int
    events_ok: list
    events_failed: list
    playbook_on_stats: dict

class AnsibleManager():
    def __init__(self, user, domain):
        self.user = user
        self.domain = domain
        os.environ['ANSIBLE_LIBRARY'] = os.path.join(APP_ROOT, "ansible")
        
    def run(
        self,
        playbook_name: str,
        extravars: dict[str, Any] | None = None,
        timeout: int = 900,
        *,
        sensitive_keys: set[str] | None = None,
    ) -> AnsibleRunResult:
        extravars = extravars or {}
        sensitive_keys = sensitive_keys or set()
        sensitive_values = tuple(
            str(value)
            for key, value in extravars.items()
            if key in sensitive_keys and value is not None
        )
        safe_extravars = _redact_sensitive_values(extravars, sensitive_values)
        hosts = f"{self.user}@{self.domain}"
        
        logger.info(
            f"[Ansible Start] {hosts} name={playbook_name} "
            f"extravars={safe_extravars}"
        )
        
        # Ctrl+CがAnsibleに持っていかれるので対応
        saved_handlers = _capture_handlers()
        try:
            res = ansible_runner.run(
                timeout=timeout,
                private_data_dir=f'{DATA_ROOT}/ansible/',
                inventory={ 'all':{
                    'hosts': hosts
                    }
                },
                playbook=self.get_playbook_path(playbook_name),
                extravars=extravars,
                host_pattern='all',
                quiet=True,
            )
        finally:
            _restore_handlers(saved_handlers)

        events = list(res.events)
        safe_events = _redact_sensitive_values(events, sensitive_values)
        
        save_path = os.path.join(DATA_ROOT, "node", f'{self.user}@{self.domain}')
        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, f"{get_timestamp()}_{playbook_name.replace('/','-')}.json"), 'w') as f:
            json.dump(
                {"status": res.stats, "rc": res.rc, "events": safe_events},
                f,
                indent=4,
            )
        
        
        runner_on_ok = []
        runner_on_failed = []
        playbook_on_stats = None
        for event in safe_events:
            if event['event'] == 'runner_on_ok':
                runner_on_ok.append(event)
            if event['event'] == 'runner_on_failed':
                runner_on_failed.append(event)
            
            if event['event'] == 'playbook_on_stats':
                playbook_on_stats = event['event_data']
                logger.debug(pformat(playbook_on_stats))
        
        msg = (
            f"[Ansible Finish] {hosts} name={playbook_name} "
            f"extravars={safe_extravars} res.rc={res.rc} res.status={res.status}"
        )
        if res.rc == 0:
            logger.info(msg)
        else:
            logger.error(msg)
            exe = Exception(msg)
            exe.add_note("------ addtional info ------")
            for event_error in runner_on_failed:
                exe.add_note(pformat(event_error['event_data']))
            if runner_on_failed == []:
                exe.add_note(pformat(safe_events))
            raise exe
    
        return AnsibleRunResult(status=res.status, rc=res.rc, events_ok=runner_on_ok, events_failed=runner_on_failed, playbook_on_stats=playbook_on_stats)


    def get_playbook_path(self, playbook_name:str):
        playbook_path = f"{APP_ROOT}/static/ansible/{playbook_name}.yml"
        if not os.path.exists(playbook_path):
            raise Exception(f"Playbook not found: {playbook_path}")
        return playbook_path
    
    def node_infomation(self):
        result  = self.run(playbook_name="test")
        try:
            node_info = result.events_ok[0]["event_data"]["res"]["ansible_facts"]
        except Exception:
            raise Exception("Failed get node information by Ansible")
        
        logger.info(f'Get node infomation successfull {self.user}@{self.domain}')
        return node_info


def _capture_handlers() -> Dict[int, signal.Handlers]:
    """現在の SIGINT/SIGTERM ハンドラを dict として返す。"""
    return {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}


def _redact_sensitive_values(value: Any, secrets: tuple[str, ...]) -> Any:
    """Ansible event/logからcaller指定の秘密値を再帰的に除去する。"""

    if isinstance(value, Mapping):
        return {
            key: _redact_sensitive_values(child, secrets)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive_values(child, secrets) for child in value]
    if isinstance(value, tuple):
        return tuple(_redact_sensitive_values(child, secrets) for child in value)
    if isinstance(value, str):
        result = value
        for secret in secrets:
            if result == secret:
                return "[REDACTED]"
            if len(secret) >= 8:
                result = result.replace(secret, "[REDACTED]")
        return result
    return value


def _restore_handlers(handlers: Dict[int, signal.Handlers]) -> None:
    """保存しておいたハンドラを元に戻す。"""
    for sig, handler in handlers.items():
        signal.signal(sig, handler)


def first_n_lines(text: str, n: int = 10) -> str:
    # 行区切りで分割し、先頭 n 行だけ取り出して再結合
    if not isinstance(text, str):
        text = pformat(text)
    if len(text.splitlines()) >= n:
        res = text.splitlines()[:n]
        res.append(f"..... {len(text.splitlines())} lines of text shortened to {n} lines .....")
        return "\n".join(res)
    else:
        return text
