import os


class ConfigError(RuntimeError):
    pass


def get_secret(
    name: str, required: bool = True
) -> str:  # Read secret from environment (or raise)
    val = os.environ.get(name)
    if required and (
        val is None or val.strip() == "" or val.strip().lower().startswith("changeme")
    ):
        raise ConfigError(f"missing required secret: {name}")
    return val
