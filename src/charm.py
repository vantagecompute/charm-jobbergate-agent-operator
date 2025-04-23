#!/usr/bin/env python3
# Copyright (c) 2025 Vantage Compute Corporation
# See LICENSE file for licensing details.

"""JobbergateAgentOperator."""

import logging
import shlex
import subprocess
from typing import Any, Dict, List, Optional, Union

from ops import (
    ActionEvent,
    ActiveStatus,
    BlockedStatus,
    CharmBase,
    ConfigChangedEvent,
    InstallEvent,
    StoredState,
    UpdateStatusEvent,
    WaitingStatus,
    main,
)

from jg_ops import (
    JobbergateAgentOps,
    JobbergateAgentOpsError,
    JOBBERGATE_AGENT_SNAP_ENV_CONFIG,
    jobbergate_agent_version,
    jobbergate_agent_daemon_status,
)


logger = logging.getLogger()


class JobbergateAgentOperator(CharmBase):
    """Jobbergate Agent lifecycle events."""

    _stored = StoredState()

    def __init__(self, *args):
        """Init _stored attributes and interfaces, observe events."""
        super().__init__(*args)

        self._jg_agent_ops = JobbergateAgentOps(self)

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.update_status: self._on_update_status,
            self.on.config_changed: self._on_config_changed,
            self.on.get_jobbergate_env_config_action: self._on_get_jobbergate_env_config_action,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event: InstallEvent) -> None:
        """Perform installation operations for JobbergateAgent."""
        jobbergate_agent_snap_channel = self.config.get("snap-channel")

        self.unit.status = WaitingStatus(
            f"Installing jobbergate-agent snap from: {jobbergate_agent_snap_channel}"
        )

        try:
            self._jg_agent_ops.install(jobbergate_agent_snap_channel)
        except JobbergateAgentOpsError as e:
            logger.debug()
            event.defer()
            return

        self.unit.set_workload_version(jobbergate_agent_version())
        self.unit.status = ActiveStatus(
            f"Status: {jobbergate_agent_daemon_status()}"
        )

    def _on_config_changed(self, event: ConfigChangedEvent) -> None:
        """Perform config-changed operations."""
        oidc_client_id = self.config.get("oidc-client-id", "")
        oidc_client_secret = self.config.get("oidc-client-secret", "")

        if not (oidc_client_id != "" and oidc_client_secret != ""): 
            msg = "Configure oidc-client-id and oidc-client-secret to continue."
            logger.debug(msg)
            self.unit.status = BlockedStatus(msg)
            event.defer()
            return

        jobbergate_snap_configs = [
            "base-api-url",
            "sbatch-path",
            "scontrol-path",
            "sentry-dsn",
            "oidc-domain",
            "oidc-client-id",
            "oidc-client-secret",
            "slurm-user-mapper",
            "task-jobs-interval-seconds",
            "task-garbage-collection-hour",
            "write-submission-files",
        ]

        #JobbergateAgentOps().configure(self.config)
        for key in jobbergate_snap_configs:
            if (config_from_charm := self.config.get(key, "")) != "":
                logger.debug(f"{key}={config_from_charm}")


    def _on_update_status(self, event: UpdateStatusEvent) -> None:
        """Handle update status."""
        self.unit.status = ActiveStatus("")

    def _on_get_jobbergate_env_config_action(self, event: ActionEvent) -> None:
        """Return jobbergate-agent config."""
        event.set_results(
            {"jobbergate-agent-env-config": JOBBERGATE_AGENT_SNAP_ENV_CONFIG.read_text()}
        )


if __name__ == "__main__":
    main.main(JobbergateAgentOperator)
