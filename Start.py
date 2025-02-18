import subprocess
import os
import Dfile as df
import Launcher
import tkinter as tk

def launch_game(version_id,username,MB):
    classpath = df.get_classpath(version_id)
    
    java_path = "java"
    main_class = "net.minecraft.client.main.Main"
    game_dir = os.path.abspath(f"versions/{version_id}")
    assets_dir = os.path.abspath(f"versions/{version_id}/assets")
    natives_dir = os.path.abspath(f"versions/{version_id}/natives")
    command = [
        java_path,
        f"-Djava.library.path={natives_dir}",
        "-cp", classpath,
        f"-Xms{MB}M",
        f"-Xmx{MB}M",
        f"-javaagent:versions/{version_id}/fakeauthlib/authlib-injector-1.2.5.jar=ely.by",
        main_class,
        "--gameDir", game_dir,
        "--assetsDir", assets_dir,
        "--version", version_id,
        "--accessToken", "0",
        "--userType", "mojang",       # Ключевой параметр!
        "--versionType", "release",
        f"--username={username}"  # Рандомный UUID
        
    ]

    subprocess.run(command)