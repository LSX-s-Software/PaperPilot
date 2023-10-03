from django.conf import settings

grpc_config = settings.GRPC_CLIENT

clients = grpc_config["clients"]
