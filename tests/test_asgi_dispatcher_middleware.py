from __future__ import generator_stop

import pytest

from asgi_dispatcher_middleware import DispatcherMiddleware, asgitypes


def _http_scope(path: str = "/") -> asgitypes.HTTPScope:
    return {
        "type": "http",
        "asgi": {"spec_version": "2.1", "version": "3.0"},
        "http_version": "2",
        "method": "GET",
        "scheme": "https",
        "path": path,
        "raw_path": b"/",
        "query_string": b"a=b",
        "root_path": "",
        "headers": [
            (b"User-Agent", b"Hypercorn"),
            (b"X-Hypercorn", b"Hypercorn"),
            (b"Referer", b"hypercorn"),
        ],
        "client": ("127.0.0.1", 80),
        "server": None,
        "extensions": {},
    }


@pytest.mark.anyio
async def test_dispatcher_middleware() -> None:
    class EchoFramework:
        def __init__(self, name: str) -> None:
            self.name = name

        async def __call__(
            self,
            scope: asgitypes.Scope,
            receive: asgitypes.ASGIReceiveCallable,
            send: asgitypes.ASGISendCallable,
        ) -> None:
            assert scope["type"] == "http"
            response = f"{self.name}-{scope['path']}".encode()
            await send(
                asgitypes.HTTPResponseStartEvent(
                    type="http.response.start",
                    status=200,
                    headers=[(b"content-length", b"%d" % len(response))],
                )
            )
            await send(
                asgitypes.HTTPResponseBodyEvent(
                    type="http.response.body",
                    body=response,
                    more_body=False,
                )
            )

    app = DispatcherMiddleware(
        {"/api/x": EchoFramework("apix"), "/api": EchoFramework("api")}
    )

    sent_events = []

    async def send(message: object) -> None:
        sent_events.append(message)

    async def receive() -> asgitypes.ASGIReceiveEvent:
        assert False  # pragma: no cover

    await app(_http_scope(path="/api/x/b"), receive, send)
    await app(_http_scope(path="/api/b"), receive, send)
    await app(_http_scope(path="/"), receive, send)
    assert sent_events == [
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-length", b"7")],
        },
        {"type": "http.response.body", "body": b"apix-/b", "more_body": False},
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-length", b"6")],
        },
        {"type": "http.response.body", "body": b"api-/b", "more_body": False},
        {
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-length", b"0")],
        },
        {"type": "http.response.body", "body": b"", "more_body": False},
    ]


class ScopeFramework:
    def __init__(self, name: str) -> None:
        self.name = name

    async def __call__(
        self,
        scope: asgitypes.Scope,
        receive: asgitypes.ASGIReceiveCallable,
        send: asgitypes.ASGISendCallable,
    ) -> None:
        await send(
            asgitypes.LifespanStartupCompleteEvent(type="lifespan.startup.complete")
        )


@pytest.mark.anyio
async def test_dispatcher_lifespan() -> None:
    app = DispatcherMiddleware(
        {"/apix": ScopeFramework("apix"), "/api": ScopeFramework("api")}
    )

    sent_events = []

    async def send(message: object) -> None:
        sent_events.append(message)

    async def receive() -> asgitypes.LifespanShutdownEvent:
        return {"type": "lifespan.shutdown"}

    await app(
        {"type": "lifespan", "asgi": {"spec_version": "3.0", "version": "3.0"}},
        receive,
        send,
    )
    assert sent_events == [{"type": "lifespan.startup.complete"}]
