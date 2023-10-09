class OssError(Exception):
    def __init__(self, msg):
        super(OssError, self).__init__(msg)
