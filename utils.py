import os


def get_latest_file(directory, file_extension):
    """Get the most recently created file from a directory with specific extension.

    Args:
        directory (str): Directory path to search in
        file_extension (str): File extension to filter by (e.g., '.txt')

    Returns:
        tuple: (file_path, file_content) or (None, None) if no files found
    """
    files = [f for f in os.listdir(directory) if f.endswith(file_extension)]

    if not files:
        return None, None

    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(directory, x)))
    file_path = os.path.join(directory, latest_file)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    return file_path, content
