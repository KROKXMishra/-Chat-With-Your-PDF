def clean_text(text):

    if not isinstance(text, str):
        return ""

    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u00ad": "",
        "\u00a0": " ",
        "\ufffd": "",
        "\u2022": "-",
        "\u25aa": "-",
        "\u25cf": "-",
        "\u25a0": ""
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text.strip()