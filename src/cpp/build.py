import os
import subprocess
import platform
import sys

def build():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    src_file = os.path.join(src_dir, "analytics.cpp")

    system = platform.system()
    if system == "Windows":
        output_file = os.path.join(src_dir, "analytics.dll")
        cmd_msvc = ["cl", "/LD", "/O2", src_file, f"/Fe{output_file}"]

        cmd_mingw = ["g++", "-shared", "-o", output_file, src_file, "-O3", "-static"]

        commands = [("MinGW (g++)", cmd_mingw), ("MSVC (cl)", cmd_msvc)]
    else:
        output_file = os.path.join(src_dir, "analytics.so")
        cmd_gcc = ["g++", "-shared", "-fPIC", "-o", output_file, src_file, "-O3"]
        cmd_clang = ["clang++", "-shared", "-fPIC", "-o", output_file, src_file, "-O3"]
        commands = [("GCC", cmd_gcc), ("Clang", cmd_clang)]

    success = False
    for name, cmd in commands:
        print(f"Trying to compile with {name}...")
        try:
            subprocess.check_call(cmd)
            print(f"Successfully compiled to {output_file}")
            success = True
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Failed with {name}")

    if not success:
        print("Could not compile the C++ library. Please ensure you have a C++ compiler installed (g++, clang++, or MSVC).")
        print("On Windows, you can install MinGW or Visual Studio Build Tools.")
        sys.exit(1)

if __name__ == "__main__":
    build()
