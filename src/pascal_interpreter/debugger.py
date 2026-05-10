import sys


class SourceMap:
    def __init__(self, filename, source):
        self.filename = filename or "<main>"
        self.lines = source.splitlines()

    def render_window(self, line, radius=2):
        if line is None or line < 1:
            return []

        start = max(1, line - radius)
        end = min(len(self.lines), line + radius)
        rendered = []
        for line_number in range(start, end + 1):
            marker = "=>" if line_number == line else "  "
            rendered.append(f"{marker}{line_number:4}  {self.lines[line_number - 1]}")
        return rendered


class DebuggerQuit(Exception):
    pass


class Debugger:
    def __init__(self, source_map, *, input_stream=None, output_stream=None):
        self.source_map = source_map
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stderr
        self.breakpoints = set()
        self.stepping = True
        self.last_node = None
        self.use_ansi = self.output_stream.isatty()

    def before_statement(self, node, call_stack):
        line = getattr(node, "line", None)
        if line is None:
            return

        if self.stepping or line in self.breakpoints:
            self.last_node = node
            self.show_location(node, call_stack)
            self.command_loop(call_stack)

    def show_location(self, node, call_stack):
        self.clear_screen()
        line = getattr(node, "line", None)
        frame = call_stack.peek() if call_stack._records else None
        routine = frame.name if frame is not None else "<none>"
        routine_kind = frame.ar_type.value if frame is not None else "UNKNOWN"

        self.write(f"Paused at {routine_kind} {routine}, line {line}")
        for rendered_line in self.source_map.render_window(line):
            self.write(rendered_line)
        self.show_compact_stack(call_stack)

    def program_finished(self, final_record):
        self.clear_screen()
        self.write("Program finished.")
        if final_record is not None:
            self.write(f"Final frame: {final_record.ar_type.value} {final_record.name}")
        self.write("Press Enter to exit the debugger.")
        self.input_stream.readline()

    def command_loop(self, call_stack):
        while True:
            command = self.read_command()
            if command is None:
                raise DebuggerQuit()

            parts = command.split()
            if not parts:
                continue

            action = parts[0].lower()
            if action in ["step", "s"]:
                self.stepping = True
                return
            if action in ["continue", "c"]:
                self.stepping = False
                return
            if action in ["break", "b"]:
                self.handle_break(parts)
                continue
            if action == "clear":
                self.handle_clear(parts)
                continue
            if action == "locals":
                self.show_locals(call_stack)
                continue
            if action in ["print", "p"]:
                self.handle_print(parts, call_stack)
                continue
            if action == "stack":
                self.show_stack(call_stack)
                continue
            if action in ["where", "w"]:
                if self.last_node is not None:
                    self.show_location(self.last_node, call_stack)
                continue
            if action in ["quit", "q"]:
                raise DebuggerQuit()

            self.write(f"Unknown command: {command}")

    def handle_break(self, parts):
        if len(parts) == 1:
            if self.breakpoints:
                for line in sorted(self.breakpoints):
                    self.write(f"breakpoint {line}")
            else:
                self.write("No breakpoints")
            return

        try:
            line = int(parts[1])
        except ValueError:
            self.write(f"Invalid breakpoint line: {parts[1]}")
            return

        self.breakpoints.add(line)
        self.write(f"Breakpoint set at line {line}")

    def handle_clear(self, parts):
        if len(parts) != 2:
            self.write("Usage: clear <line>")
            return

        try:
            line = int(parts[1])
        except ValueError:
            self.write(f"Invalid breakpoint line: {parts[1]}")
            return

        self.breakpoints.discard(line)
        self.write(f"Breakpoint cleared at line {line}")

    def show_locals(self, call_stack):
        if not call_stack._records:
            self.write("No active frame")
            return

        frame = call_stack.peek()
        if not frame.members:
            self.write("No locals")
            return

        for name, value in frame.members.items():
            self.write(f"{name} = {value}")

    def handle_print(self, parts, call_stack):
        if len(parts) != 2:
            self.write("Usage: print <name>")
            return

        name = parts[1].upper()
        value = call_stack.peek().get(name) if call_stack._records else None
        self.write(f"{name} = {value}")

    def show_stack(self, call_stack):
        if not call_stack._records:
            self.write("No active frame")
            return

        for index, frame in enumerate(reversed(call_stack._records)):
            self.write(f"#{index} {frame.ar_type.value} {frame.name}")

    def show_compact_stack(self, call_stack):
        if len(call_stack._records) <= 1:
            return

        self.write("")
        self.write("Call stack:")
        records = list(reversed(call_stack._records))
        for index, frame in enumerate(records):
            text = f"#{index} {frame.ar_type.value} {frame.name}"
            if index == 0:
                self.write(f"=> {text}")
            else:
                self.write(self.dim(f"   {text}"))

    def read_command(self):
        self.output_stream.write("(pasdbg) ")
        self.output_stream.flush()
        line = self.input_stream.readline()
        if line == "":
            return None
        return line.strip()

    def write(self, text):
        print(text, file=self.output_stream)

    def clear_screen(self):
        if self.use_ansi:
            self.output_stream.write("\033[2J\033[H")
            self.output_stream.flush()

    def dim(self, text):
        if not self.use_ansi:
            return text
        return f"\033[2m{text}\033[0m"
