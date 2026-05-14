import sys


class SourceMap:
    def __init__(self, filename, source):
        self.filename = filename or "<main>"
        self.lines = source.splitlines()

    def render_window(self, line, radius=8):
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
        self.next_depth = None
        self.finish_depth = None
        self.last_node = None
        self.use_ansi = self.output_stream.isatty()
        self.last_display_line_count = 0
        self.last_display_routine = None
        self.display_invalidated = False

    def before_statement(self, node, call_stack):
        line = getattr(node, "line", None)
        if line is None:
            return

        current_depth = len(call_stack._records)
        if (
            self.stepping or
            line in self.breakpoints or
            self.should_stop_for_next(current_depth) or
            self.should_stop_for_finish(current_depth)
        ):
            self.clear_run_state()
            self.last_node = node
            self.show_location(node, call_stack)
            self.command_loop(call_stack)

    def should_stop_for_next(self, current_depth):
        return self.next_depth is not None and current_depth <= self.next_depth

    def should_stop_for_finish(self, current_depth):
        return self.finish_depth is not None and current_depth < self.finish_depth

    def clear_run_state(self):
        self.next_depth = None
        self.finish_depth = None

    def show_location(self, node, call_stack):
        line = getattr(node, "line", None)
        frame = call_stack.peek() if call_stack._records else None
        routine = frame.name if frame is not None else "<none>"
        routine_kind = frame.ar_type.value if frame is not None else "UNKNOWN"
        routine_key = (routine_kind, routine)

        lines = [f"Paused at {routine_kind} {routine}, line {line}"]
        lines.extend(self.source_map.render_window(line))
        lines.extend(self.compact_stack_lines(call_stack))

        self.redraw_previous_display_if_safe(routine_key)
        for text in lines:
            self.write(text, invalidate=False)

        self.last_display_line_count = len(lines)
        self.last_display_routine = routine_key
        self.display_invalidated = False

    def program_finished(self, final_record):
        self.display_invalidated = True
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
                self.clear_run_state()
                return
            if action in ["next", "n"]:
                self.stepping = False
                self.clear_run_state()
                self.next_depth = len(call_stack._records)
                return
            if action in ["finish", "f"]:
                self.stepping = False
                self.clear_run_state()
                self.finish_depth = len(call_stack._records)
                return
            if action in ["continue", "c"]:
                self.stepping = False
                self.clear_run_state()
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
                    self.display_invalidated = True
                    self.show_location(self.last_node, call_stack)
                continue
            if action in ["help", "h"]:
                self.show_help()
                continue
            if action in ["quit", "q"]:
                raise DebuggerQuit()

            self.write(f"Unknown command: {command}")

    def show_help(self):
        self.write("Debugger commands:")
        self.write("  step, s              step into the next statement")
        self.write("  next, n              step over calls")
        self.write("  finish, f            run until the current routine returns")
        self.write("  continue, c          run until a breakpoint or program end")
        self.write("  break, b [line]      set or list line breakpoints")
        self.write("  clear <line>         remove a line breakpoint")
        self.write("  locals               show current frame variables")
        self.write("  print, p <name>      print a visible variable")
        self.write("  stack                show active frames")
        self.write("  where, w             redisplay the current source location")
        self.write("  quit, q              stop execution")

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
        for line in self.compact_stack_lines(call_stack):
            self.write(line)

    def compact_stack_lines(self, call_stack):
        if len(call_stack._records) <= 1:
            return []

        lines = ["", "Call stack:"]
        records = list(reversed(call_stack._records))
        for index, frame in enumerate(records):
            text = f"#{index} {frame.ar_type.value} {frame.name}"
            if index == 0:
                lines.append(f"=> {text}")
            else:
                lines.append(self.dim(f"   {text}"))
        return lines

    def redraw_previous_display_if_safe(self, routine_key):
        if (
            not self.use_ansi or
            self.display_invalidated or
            self.last_display_line_count == 0 or
            self.last_display_routine != routine_key
        ):
            return

        lines_to_clear = self.last_display_line_count + 1
        self.output_stream.write(f"\033[{lines_to_clear}A")
        for _ in range(lines_to_clear):
            self.output_stream.write("\033[2K")
            self.output_stream.write("\033[1B")
        self.output_stream.write(f"\033[{lines_to_clear}A")
        self.output_stream.flush()

    def notify_program_output(self):
        self.display_invalidated = True

    def read_command(self):
        self.output_stream.write("(pasdbg) ")
        self.output_stream.flush()
        line = self.input_stream.readline()
        if line == "":
            return None
        return line.strip()

    def write(self, text, *, invalidate=True):
        if invalidate:
            self.display_invalidated = True
        print(text, file=self.output_stream)

    def dim(self, text):
        if not self.use_ansi:
            return text
        return f"\033[2m{text}\033[0m"
