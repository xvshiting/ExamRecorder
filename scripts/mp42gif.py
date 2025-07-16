import subprocess

def mp4_to_gif(mp4_path, gif_path, fps=10, scale=600):
    """
    用ffmpeg将mp4转为gif，适合插入README
    :param mp4_path: 输入视频路径
    :param gif_path: 输出gif路径
    :param fps: gif帧率
    :param scale: gif宽度（像素），高度自适应
    """
    cmd = [
        'ffmpeg',
        '-i', mp4_path,
        '-vf', f'fps={fps},scale={scale}:-1:flags=lanczos',
        '-y',  # 覆盖输出
        gif_path
    ]
    print(' '.join(cmd))
    subprocess.run(cmd, check=True)

# 示例用法
mp4_to_gif('../docs/demo_collect.mp4', '../docs/demo_collect.gif')
mp4_to_gif('../docs/demo_replay.mp4', '../docs/demo_replay.gif')