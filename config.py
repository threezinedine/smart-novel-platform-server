from utils.configure.configure import Configure

config = Configure("config.json")


def initialize_config(dev: bool = True):
    config.Load()

    if dev:
        overiddenConfig = Configure("config.development.json")
        overiddenConfig.Load()
        config.OverridenBy(overiddenConfig)


def get_config():
    return config
