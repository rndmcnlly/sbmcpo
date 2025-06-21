# /// script
# requires-python = ">=3.12"
# dependencies = ['rumps']
# ///

import rumps # type: ignore
from AppKit import NSApplication, NSApplicationActivationPolicyAccessory # type: ignore
import json
from pathlib import Path

class SBMCPOApp(rumps.App):
    def __init__(self):
        super().__init__("🦾")
        # Hide from Dock, show only in status bar
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        # Read config path only
        self.config_path = Path.home() / ".sbmcpo.json"
        # Ensure the config file exists
        if not self.config_path.exists():
            try:
                with open(self.config_path, "w") as f:
                    json.dump({}, f)
                print(f"Created empty config file at {self.config_path}")
            except Exception as e:
                print(f"Failed to create config file: {e}")

        self.menu = [
            rumps.MenuItem("Enable Server", callback=self.toggle_server),
            rumps.MenuItem("Reveal Config", callback=self.reveal_config)
        ]

    def start_server(self):
        import subprocess
        # Load config here
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                port = config.get("port")
                api_key = config.get("apiKey")
                host = config.get("host")
                cors_allow_origins = config.get("corsAllowOrigins")
        except Exception as e:
            print(f"Failed to read config: {e}")
            port = api_key = host = cors_allow_origins = None

        cmd = ["uvx", "mcpo", "--config", str(self.config_path)]
        if port is not None:
            cmd += ["--port", str(port)]
        if api_key is not None:
            cmd += ["--api-key", str(api_key)]
        if host is not None:
            cmd += ["--host", str(host)]
        if cors_allow_origins is not None:
            cmd += ["--cors-allow-origins", ",".join(cors_allow_origins)]

        print("Launching server with:", " ".join(cmd))
        self.server_process = subprocess.Popen(cmd)

    def stop_server(self):
        if hasattr(self, 'server_process') and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()
            print("Server stopped.")
        else:
            print("Server is not running.")

    def reveal_config(self, _):
        import subprocess
        subprocess.run(["open", "-R", str(self.config_path)])

    def toggle_server(self, sender):
        sender.state = not sender.state
        if sender.state:
            self.start_server()
        else:
            self.stop_server()

if __name__ == "__main__":
    SBMCPOApp().run()
