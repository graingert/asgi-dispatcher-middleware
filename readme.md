# asgi-dispatcher-middleware

Middleware to Dispatch to multiple ASGI applications, extracted from hypercorn.

## Dispatch to multiple ASGI applications

It is often useful serve multiple ASGI applications at once, under differing root paths.
This middleware allows multiple applications to be served on different mounts.

The `DispatcherMiddleware` takes a dictionary of applications keyed by the root path.
The order of entry in this dictionary is important, as the root paths will be checked in
this order. Hence it is important to add `/a/b` before `/a` or the latter will match
everything first. Also note that the root path should not include the trailing slash.

An example usage is to to serve a graphql application alongside a static file serving
application. Using the graphql app is called `graphql_app` serving everything with the
root path `/graphql` and a static file app called `static_app` serving everything else
i.e. a root path of `/` the `DispatcherMiddleware` can be setup as,

```{.sourceCode .python}
from asgi_dispatcher_middleware import DispatcherMiddleware

dispatcher_app = DispatcherMiddleware({
    "/graphql": graphql_app,
    "/": static_app,
})
```

which can then be served by any asgi framework,

```{.sourceCode .shell}
$ hypercorn module:dispatcher_app
$ uvicorn module:dispatcher_app
```

## See also

- hypercorn: <https://pgjones.gitlab.io/hypercorn/how_to_guides/dispatch_apps.html>
