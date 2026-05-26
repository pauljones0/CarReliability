import sys
import json
import time
import subprocess
import shlex
import os
from pathlib import Path
from src.cli_interface import ReliabilityCLI

# --- Layer 1: Execution Layer ---
class UnixExecutor:
    def __init__(self):
        self.cli = ReliabilityCLI()

    def execute_chain(self, command_string):
        """
        Supports a simple subset of Unix operators: | and ;
        (For a real implementation, this would be a full parser)
        """
        # For now, let's just handle single commands for simplicity, 
        # or a very basic split by ';'
        results = []
        commands = command_string.split(';')
        
        last_stdout = ""
        last_exit_code = 0
        
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd: continue
            
            # Simple piping logic: cmd1 | cmd2
            if '|' in cmd:
                # Handle pipe (very basic implementation)
                pipe_parts = cmd.split('|')
                pipe_stdin = ""
                for p_part in pipe_parts:
                    p_part = p_part.strip()
                    exit_code, stdout, stderr = self.execute_single(p_part, stdin=pipe_stdin)
                    pipe_stdin = stdout
                    if exit_code != 0: break
                last_stdout, last_exit_code = stdout, exit_code
            else:
                last_exit_code, last_stdout, last_stderr = self.execute_single(cmd)
            
            results.append(last_stdout)
            if last_exit_code != 0 and '&&' in command_string: # naive check
                break
                
        return last_exit_code, last_stdout, last_stderr

    def execute_single(self, cmd_string, stdin=""):
        try:
            parts = shlex.split(cmd_string)
            if not parts: return 0, "", ""
            
            command = parts[0]
            args = parts[1:]
            
            if command == "reliability":
                # Internal CLI call
                start_time = time.time()
                output = self.cli.run(args)
                duration = time.time() - start_time
                return 0, output, ""
            else:
                # Fallback to system shell (restricted)
                return 1, "", f"Error: Command '{command}' not allowed. Available: reliability"
        except Exception as e:
            return 1, "", str(e)

# --- Layer 2: Presentation Layer ---
class LLMPresentation:
    @staticmethod
    def wrap(exit_code, stdout, stderr, duration_ms):
        output = stdout
        
        # Binary Guard (naive)
        if '\0' in output:
            output = "[error] output contains binary data."
            
        # Truncation
        max_lines = 200
        lines = output.splitlines()
        if len(lines) > max_lines:
            truncated = "\n".join(lines[:max_lines])
            output = f"{truncated}\n\n--- output truncated ({len(lines)} lines) ---"

        # Stderr attachment
        if exit_code != 0 and stderr:
            output += f"\n[stderr]\n{stderr}"
            
        # Metadata Footer
        output += f"\n[exit:{exit_code} | {duration_ms:.1f}ms]"
        return output

# --- MCP Protocol Handler (STDIO) ---
class MCPServer:
    def __init__(self):
        self.executor = UnixExecutor()

    def serve(self):
        for line in sys.stdin:
            try:
                request = json.loads(line)
                if request.get("method") == "initialize":
                    self.send_response(request["id"], {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "car-reliability", "version": "1.0.0"}})
                elif request.get("method") == "listTools":
                    self.send_response(request["id"], {"tools": [
                        {
                            "name": "run",
                            "description": "Execute *nix-style commands for car reliability data.\nAvailable commands:\n  reliability ls [make] - List makes/models\n  reliability cat <key> - Show car data\n  reliability grep <pat> - Search cars\n  reliability fetch <make> <model> - Fetch fresh data",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command": {"type": "string", "description": "The command to run"}
                                },
                                "required": ["command"]
                            }
                        }
                    ]})
                elif request.get("method") == "callTool":
                    tool_name = request["params"]["name"]
                    if tool_name == "run":
                        cmd = request["params"]["arguments"]["command"]
                        start_time = time.time()
                        exit_code, stdout, stderr = self.executor.execute_chain(cmd)
                        duration_ms = (time.time() - start_time) * 1000
                        
                        presentation = LLMPresentation.wrap(exit_code, stdout, stderr, duration_ms)
                        self.send_response(request["id"], {"content": [{"type": "text", "text": presentation}]})
            except Exception as e:
                pass

    def send_response(self, request_id, result):
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    server.serve()
