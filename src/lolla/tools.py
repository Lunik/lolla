def parse_model(text):
    args = text.split(":")

    model_name = args[0]
    model_version = args[1] if len(args) >= 2 else "latest"

    return {
        "name": model_name,
        "version": model_version,
        "full": f"{model_name}:{model_version}",
    }
