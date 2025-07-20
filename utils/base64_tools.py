import base64
import io
import matplotlib.pyplot as plt


def fig_to_base64(fig, format="png", max_size=100_000):
    """
    Convert a Matplotlib figure to a base64-encoded image URI.

    Args:
        fig (matplotlib.figure.Figure): The Matplotlib figure.
        format (str): Image format (default: "png").
        max_size (int): Maximum byte size for the image.

    Returns:
        str: Base64 data URI (e.g., "data:image/png;base64,...")
    
    Raises:
        ValueError: If encoded image exceeds max_size.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight')
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode("utf-8")
    data_uri = f"data:image/{format};base64,{encoded}"

    if len(data_uri.encode("utf-8")) > max_size:
        raise ValueError(f"Encoded image exceeds {max_size} bytes.")

    return data_uri
