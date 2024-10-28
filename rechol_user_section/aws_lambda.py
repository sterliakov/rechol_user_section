from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from django.core.management import call_command

from mangum import Mangum

from rechol_user_section.asgi import application

if TYPE_CHECKING:
    from mangum.types import LambdaContext, LambdaEvent


class MangumExtended(Mangum):
    def _patch_event_path(self, event: LambdaEvent) -> None:
        real_path = event["rawPath"]
        split_path = event["requestContext"]["http"]["path"]
        # Lambda Function URL decides to remove trailing slash for some reason.
        if urlparse(real_path).path.endswith("/") and not split_path.endswith("/"):
            event["requestContext"]["http"]["path"] += "/"

    def __call__(self, event: LambdaEvent, context: LambdaContext) -> dict[str, object]:
        action = event.get("action")
        if action == "MANAGE":  # pragma: no cover
            args = event.get("args", [])
            kwargs = event.get("kwargs", {})
            call_command(event["command"], *args, **kwargs)
            return {"success": True}
        if action == "MIGRATE":  # pragma: no cover
            args = event.get("args", [])
            call_command("migrate", *args)
            return {"success": True}
        if action == "PING":
            # Warmup event
            return {"success": True}
        if action is not None:
            raise ValueError(f"Unknown action: {action}.")

        self._patch_event_path(event)
        return super().__call__(event, context)


handler = MangumExtended(
    application,  # type: ignore[arg-type]
    lifespan="off",
    api_gateway_base_path="/prod",
)
