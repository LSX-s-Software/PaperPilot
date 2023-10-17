"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import google.protobuf.empty_pb2
import google.protobuf.wrappers_pb2
import grpc
import grpc.aio
import paperpilot_common.protobuf.project.project_pb2
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class ProjectServiceStub:
    """项目接口"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    CheckUserJoinedProject: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.CheckUserJoinedProjectRequest,
        google.protobuf.wrappers_pb2.BoolValue,
    ]
    """检查用户是否加入项目"""

class ProjectServiceAsyncStub:
    """项目接口"""

    CheckUserJoinedProject: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.CheckUserJoinedProjectRequest,
        google.protobuf.wrappers_pb2.BoolValue,
    ]
    """检查用户是否加入项目"""

class ProjectServiceServicer(metaclass=abc.ABCMeta):
    """项目接口"""

    @abc.abstractmethod
    def CheckUserJoinedProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.CheckUserJoinedProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.wrappers_pb2.BoolValue, collections.abc.Awaitable[google.protobuf.wrappers_pb2.BoolValue]
    ]:
        """检查用户是否加入项目"""

def add_ProjectServiceServicer_to_server(
    servicer: ProjectServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...

class ProjectPublicServiceStub:
    """项目公开接口"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    ListUserJoinedProjects: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ListProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ListProjectResponse,
    ]
    """获取用户参与的项目列表"""
    GetProjectInfo: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """获取项目信息"""
    CreateProject: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.CreateProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """创建项目"""
    UpdateProjectInfo: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.UpdateProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """修改项目信息"""
    DeleteProject: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        google.protobuf.empty_pb2.Empty,
    ]
    """删除项目"""
    JoinProject: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectInviteCode,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """加入项目"""
    QuitProject: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        google.protobuf.empty_pb2.Empty,
    ]
    """退出项目"""

class ProjectPublicServiceAsyncStub:
    """项目公开接口"""

    ListUserJoinedProjects: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ListProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ListProjectResponse,
    ]
    """获取用户参与的项目列表"""
    GetProjectInfo: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """获取项目信息"""
    CreateProject: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.CreateProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """创建项目"""
    UpdateProjectInfo: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.UpdateProjectRequest,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """修改项目信息"""
    DeleteProject: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        google.protobuf.empty_pb2.Empty,
    ]
    """删除项目"""
    JoinProject: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectInviteCode,
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
    ]
    """加入项目"""
    QuitProject: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.project.project_pb2.ProjectId,
        google.protobuf.empty_pb2.Empty,
    ]
    """退出项目"""

class ProjectPublicServiceServicer(metaclass=abc.ABCMeta):
    """项目公开接口"""

    @abc.abstractmethod
    def ListUserJoinedProjects(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ListProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ListProjectResponse,
        collections.abc.Awaitable[paperpilot_common.protobuf.project.project_pb2.ListProjectResponse],
    ]:
        """获取用户参与的项目列表"""
    @abc.abstractmethod
    def GetProjectInfo(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[paperpilot_common.protobuf.project.project_pb2.ProjectInfo],
    ]:
        """获取项目信息"""
    @abc.abstractmethod
    def CreateProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.CreateProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[paperpilot_common.protobuf.project.project_pb2.ProjectInfo],
    ]:
        """创建项目"""
    @abc.abstractmethod
    def UpdateProjectInfo(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.UpdateProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[paperpilot_common.protobuf.project.project_pb2.ProjectInfo],
    ]:
        """修改项目信息"""
    @abc.abstractmethod
    def DeleteProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """删除项目"""
    @abc.abstractmethod
    def JoinProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectInviteCode,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[paperpilot_common.protobuf.project.project_pb2.ProjectInfo],
    ]:
        """加入项目"""
    @abc.abstractmethod
    def QuitProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """退出项目"""

def add_ProjectPublicServiceServicer_to_server(
    servicer: ProjectPublicServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...