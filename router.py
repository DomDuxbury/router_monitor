# class Router:
#     hostname: str
#     phonename: str

#     def __init__(self, config_file: str):
#         config = configparser.ConfigParser()
#         config.read(".router_config.ini")

#         self.hostname = config.get("General", "hostname")
#         self.phonename = config.get("General", "phonename")

#         username = config.get("Secret", "username")
#         password = config.get("Secret", "password")
