import os
import sys
import subprocess
import zipfile
import shutil

SDK = r"C:\Users\den22\AppData\Local\Android\Sdk"
BUILD_TOOLS = os.path.join(SDK, "build-tools", "36.0.0")
ANDROID_JAR = os.path.join(SDK, "platforms", "android-36", "android.jar")

AAPT2 = os.path.join(BUILD_TOOLS, "aapt2.exe")
D8 = os.path.join(BUILD_TOOLS, "d8.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner.bat")

JAVA_HOME = r"C:\Program Files\Java\jdk-21.0.10"
JAVAC = os.path.join(JAVA_HOME, "bin", "javac.exe")
KEYTOOL = os.path.join(JAVA_HOME, "bin", "keytool.exe")

PROJECT_DIR = r"c:\Users\den22\gemini\cytset-android"
BUILD_DIR = os.path.join(PROJECT_DIR, "build")

os.environ["JAVA_HOME"] = JAVA_HOME

def run_cmd(cmd, desc):
    print(f"[*] {desc}...")
    print(f"    Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=PROJECT_DIR, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[!] Error in {desc}:")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    print(f"[+] {desc} complete.")
    return res.stdout

def main():
    print("==================================================")
    print("   BUILDING CYTSET ANDROID APK                    ")
    print("==================================================")

    # 1. Clean build directory
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(os.path.join(BUILD_DIR, "compiled_res"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "gen"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "obj"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "dex"), exist_ok=True)

    # 2. Keystore check / generation
    keystore = os.path.join(PROJECT_DIR, "debug.keystore")
    if not os.path.exists(keystore):
        cmd = [
            f'"{KEYTOOL}"',
            "-genkey", "-v",
            "-keystore", f'"{keystore}"',
            "-storepass", "android",
            "-alias", "androiddebugkey",
            "-keypass", "android",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-dname", '"CN=Cytset,O=Cytset,C=RU"'
        ]
        run_cmd(" ".join(cmd), "Generating debug keystore")

    # 3. AAPT2 compile resources
    compiled_res_zip = os.path.join(BUILD_DIR, "compiled_res.zip")
    res_dir = os.path.join(PROJECT_DIR, "res")
    cmd_compile = f'"{AAPT2}" compile --dir "{res_dir}" -o "{compiled_res_zip}"'
    run_cmd(cmd_compile, "Compiling resources with aapt2")

    # 4. AAPT2 link resources + assets + manifest
    unaligned_apk = os.path.join(BUILD_DIR, "unaligned.apk")
    manifest = os.path.join(PROJECT_DIR, "AndroidManifest.xml")
    assets_dir = os.path.join(PROJECT_DIR, "assets")
    gen_dir = os.path.join(BUILD_DIR, "gen")
    
    cmd_link = f'"{AAPT2}" link -I "{ANDROID_JAR}" --manifest "{manifest}" -o "{unaligned_apk}" --java "{gen_dir}" -A "{assets_dir}" "{compiled_res_zip}"'
    run_cmd(cmd_link, "Linking APK package with aapt2")

    # 5. Compile Java files
    r_java = os.path.join(gen_dir, "com", "cytset", "app", "R.java")
    main_activity = os.path.join(PROJECT_DIR, "src", "com", "cytset", "app", "MainActivity.java")
    obj_dir = os.path.join(BUILD_DIR, "obj")

    java_files = [f'"{main_activity}"']
    if os.path.exists(r_java):
        java_files.append(f'"{r_java}"')

    cmd_javac = f'"{JAVAC}" -source 17 -target 17 -cp "{ANDROID_JAR}" -d "{obj_dir}" {" ".join(java_files)}'
    run_cmd(cmd_javac, "Compiling Java sources with javac")

    # 6. D8 DEX compilation
    class_files = []
    for root, _, files in os.walk(obj_dir):
        for f in files:
            if f.endswith(".class"):
                class_files.append(f'"{os.path.join(root, f)}"')

    dex_dir = os.path.join(BUILD_DIR, "dex")
    cmd_d8 = f'"{D8}" --release --output "{dex_dir}" {" ".join(class_files)}'
    run_cmd(cmd_d8, "Compiling DEX bytecode with d8")

    # 7. Add classes.dex into unaligned.apk
    classes_dex = os.path.join(dex_dir, "classes.dex")
    print("[*] Packaging classes.dex into APK...")
    with zipfile.ZipFile(unaligned_apk, "a") as z:
        z.write(classes_dex, "classes.dex")
    print("[+] Packaged classes.dex into unaligned APK.")

    # 8. Zipalign
    aligned_apk = os.path.join(BUILD_DIR, "aligned.apk")
    cmd_align = f'"{ZIPALIGN}" -f -p 4 "{unaligned_apk}" "{aligned_apk}"'
    run_cmd(cmd_align, "Aligning APK with zipalign")

    # 9. Apksigner
    final_apk = os.path.join(PROJECT_DIR, "cytset.apk")
    cmd_sign = f'"{APKSIGNER}" sign --ks "{keystore}" --ks-pass pass:android --ks-key-alias androiddebugkey --key-pass pass:android --out "{final_apk}" "{aligned_apk}"'
    run_cmd(cmd_sign, "Signing APK with apksigner")

    # 10. Verify signature
    cmd_verify = f'"{APKSIGNER}" verify "{final_apk}"'
    run_cmd(cmd_verify, "Verifying signed APK signature")

    apk_size = os.path.getsize(final_apk)
    print("\n==================================================")
    print("   BUILD SUCCESSFUL!                              ")
    print(f"   Output APK: {final_apk}")
    print(f"   Size: {apk_size} bytes ({apk_size / (1024*1024):.2f} MB)")
    print("==================================================")

if __name__ == "__main__":
    main()
