from django.db import models


class RequestLog(models.Model):
    """
    Model to store request logs
    """

    user = models.IntegerField(null=True, blank=True, verbose_name="用户ID")
    ip = models.CharField(max_length=16, verbose_name="用户IP")
    method = models.CharField(max_length=8, verbose_name="请求方法")
    url = models.TextField(verbose_name="请求URL")
    headers = models.JSONField(verbose_name="请求头")
    content_type = models.CharField(max_length=34, verbose_name="请求类型")
    query_param = models.JSONField(verbose_name="请求参数")
    request_body = models.JSONField(verbose_name="请求数据")
    file_data = models.JSONField(verbose_name="文件数据")

    response = models.JSONField(verbose_name="响应数据")

    status_code = models.PositiveSmallIntegerField(db_index=True, verbose_name="响应状态码")
    execution_time = models.DecimalField(null=True, decimal_places=8, max_digits=10, verbose_name="执行时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="请求时间")

    def __str__(self):
        return self.ip

    class Meta:
        ordering = ["-create_time"]
        app_label = "logs"
        db_table = "log_request"
        verbose_name = "请求日志"
        verbose_name_plural = verbose_name


class ExceptionLog(RequestLog):
    """
    Model to store exception logs
    """

    exp_id = models.CharField(max_length=32, verbose_name="异常ID")
    exception_type = models.CharField(max_length=128, verbose_name="异常类型")
    event_id = models.CharField(max_length=32, verbose_name="Sentry事件ID")
    exception_msg = models.TextField(verbose_name="异常信息")
    exception_info = models.TextField(verbose_name="异常详情")
    stack_info = models.JSONField(verbose_name="异常栈")

    def __str__(self):
        return self.exception_type

    class Meta:
        ordering = ["-create_time"]
        app_label = "logs"
        db_table = "log_exception"
        verbose_name = "异常日志"
        verbose_name_plural = verbose_name
