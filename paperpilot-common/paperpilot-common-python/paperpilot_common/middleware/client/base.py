from typing import Any, Callable, Iterator, List, Optional, Tuple, Union

import grpc

GRPC_RESPONSE = Union[grpc.Call, grpc.Future]


class ClientCallDetailsType(grpc.ClientCallDetails):
    method: str
    timeout: Optional[float]
    metadata: Optional[List[Tuple[str, Union[str, bytes]]]]
    credentials: Optional[grpc.CallCredentials]
    wait_for_ready: Optional[bool]
    compression: Optional[grpc.Compression]


class BaseInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Base class for client-side interceptors.

    To implement an interceptor, subclass this class and override the intercept method.
    """

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        call_details: ClientCallDetailsType,
    ) -> GRPC_RESPONSE:
        """Override this method to implement a custom interceptor.

        This method is called for all unary and streaming RPCs. The interceptor
        implementation should call `method` using a `grpc.ClientCallDetails` and the
        `request_or_iterator` object as parameters. The `request_or_iterator`
        parameter may be type checked to determine if this is a singluar request
        for unary RPCs or an iterator for client-streaming or client-server streaming
        RPCs.

        Args:
            method: A function that proceeds with the invocation by executing the next
                interceptor in the chain or invoking the actual RPC on the underlying
                channel.
            request_or_iterator: RPC request message or iterator of request messages
                for streaming requests.
            call_details: Describes an RPC to be invoked.

        Returns:
            The type of the return should match the type of the return value received
            by calling `method`. This is an object that is both a
            `Call <https://grpc.github.io/grpc/python/grpc.html#grpc.Call>`_ for the
            RPC and a
            `Future <https://grpc.github.io/grpc/python/grpc.html#grpc.Future>`_.

            The actual result from the RPC can be got by calling `.result()` on the
            value returned from `method`.
        """
        return method(call_details, request_or_iterator)  # pragma: no cover

    def intercept_unary_unary(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request: Any,
    ) -> GRPC_RESPONSE:
        """Implementation of grpc.UnaryUnaryClientInterceptor.

        This is not part of the grpc_interceptor.ClientInterceptor API, but must have
        a public name. Do not override it, unless you know what you're doing.
        """
        return self.intercept(continuation, request, call_details)

    def intercept_unary_stream(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request: Any,
    ) -> GRPC_RESPONSE:
        """Implementation of grpc.UnaryStreamClientInterceptor.

        This is not part of the grpc_interceptor.ClientInterceptor API, but must have
        a public name. Do not override it, unless you know what you're doing.
        """
        return self.intercept(continuation, request, call_details)

    def intercept_stream_unary(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request_iterator: Iterator[Any],
    ) -> GRPC_RESPONSE:
        """Implementation of grpc.StreamUnaryClientInterceptor.

        This is not part of the grpc_interceptor.ClientInterceptor API, but must have
        a public name. Do not override it, unless you know what you're doing.
        """
        return self.intercept(continuation, request_iterator, call_details)

    def intercept_stream_stream(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request_iterator: Iterator[Any],
    ) -> GRPC_RESPONSE:
        """Implementation of grpc.StreamStreamClientInterceptor.

        This is not part of the grpc_interceptor.ClientInterceptor API, but must have
        a public name. Do not override it, unless you know what you're doing.
        """
        return self.intercept(continuation, request_iterator, call_details)
