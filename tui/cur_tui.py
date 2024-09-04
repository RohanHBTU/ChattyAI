import curses
import signal

def signal_handler(sig, frame):
    """Ignore Ctrl+C (SIGINT) to prevent the program from exiting."""
    pass

def wrap_text(text, width):
    """Wrap text into lines that fit within the given width, considering newlines."""
    lines = []
    for paragraph in text.splitlines():  # Split text by newline characters first
        while len(paragraph) > width:
            wrap_point = paragraph.rfind(' ', 0, width)
            if wrap_point == -1:  # No spaces, break at width
                wrap_point = width
            lines.append(paragraph[:wrap_point])
            paragraph = paragraph[wrap_point:].lstrip()  # Remove leading spaces on the new line
        lines.append(paragraph)
    return lines

def draw_scrollable_window(win, lines, start_line):
    """Draws a window with scrollable content, ensuring indices are in range."""
    win.clear()
    h, w = win.getmaxyx()
    # Ensure start_line is within the valid range
    start_line = min(max(start_line, 0), max(len(lines) - h + 1, 0))
    
    for i in range(start_line, min(len(lines), start_line + h - 1)):
        win.addstr(i - start_line, 0, lines[i][:w-1])
    win.refresh()

def bot_response(user_input):
    """Generate a bot response based on user input (for now, the same as input)."""
    return user_input

def main(stdscr):
    # Handle SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize curses
    curses.curs_set(0)  # DO NOT Show the cursor
    stdscr.clear()

    # Window dimensions
    height, width = stdscr.getmaxyx()
    chat_height = height - 11  # Allocate space for input window and borders
    chat_width = width - 4   # Adjust width for border

    # Create windows
    output_win = curses.newwin(chat_height, chat_width, 1, 2)
    input_win = curses.newwin(3, chat_width, chat_height + 2, 2)
    
    # Create border windows
    output_border = curses.newwin(chat_height + 2, chat_width + 2, 0, 1)
    input_border = curses.newwin(5, chat_width + 2, chat_height + 1, 1)

    # Initialize scrolling parameters
    output_lines = []
    input_text = ""
    input_scroll_pos = 0
    output_scroll_pos = 0
    cursor_x = 0  # Cursor position in input text
    current_focus = 'input'

    #logo at center
    stdscr.addstr((height//2) -5, (width//2) -30, "    ______                             ________          __  ")
    stdscr.addstr((height//2) -4, (width//2) -30, "   / ____/________ _____ ___  ___     / ____/ /_  ____  / /__")
    stdscr.addstr((height//2) -3, (width//2) -30, "  / /_  / ___/ __ `/ __ `__ \/ _ \   / /   / __ `/ __ `/  __/")
    stdscr.addstr((height//2) -2, (width//2) -30, " / __/ / /  / /_/ / / / / / /  __/  / /___/ / / / /_/ /  /   ")
    stdscr.addstr((height//2) -1, (width//2) -30, "/_/   /_/   \__,_/_/ /_/ /_/\___/  /_____/_/ /_/\__,_/__/    ")

    #Initiation
    stdscr.addstr((height//2)+3, (width//2) -9, "Press Tab to start",curses.A_BOLD)
    initiate_key=stdscr.getch()
    while initiate_key!=9:
        initiate_key=stdscr.getch()

    #logo at right
    stdscr.addstr(height-5, width-63, "    ______                             ________          __  ")
    stdscr.addstr(height-4, width-63, "   / ____/________ _____ ___  ___     / ____/ /_  ____  / /__")
    stdscr.addstr(height-3, width-63, "  / /_  / ___/ __ `/ __ `__ \/ _ \   / /   / __ `/ __ `/  __/")
    stdscr.addstr(height-2, width-63, " / __/ / /  / /_/ / / / / / /  __/  / /___/ / / / /_/ /  /   ")
    stdscr.addstr(height-1, width-63, "/_/   /_/   \__,_/_/ /_/ /_/\___/  /_____/_/ /_/\__,_/__/    ")
    
    # Instructions
    stdscr.addstr(height-4, 1, "Use Tab to switch focus between windows, Enter to add newline")
    stdscr.addstr(height-3, 1, "Use Arrow keys to scroll and move cursor, Ctrl+A for annotation")
    stdscr.addstr(height-2, 1, "Press Ctrl+R to send input, Ctrl+F for frame details, Ctrl+E to exit")

    while True:
        # Draw borders
        output_border.box()
        input_border.box()
        output_border.refresh()
        input_border.refresh()

        # Draw the output window with scroll
        draw_scrollable_window(output_win, output_lines, output_scroll_pos)

        # Wrap input text into lines that fit the input window width
        input_text_cur=input_text[:cursor_x]
        input_text_cur+="█"
        input_text_cur+=input_text[cursor_x:]
        wrapped_input_lines = wrap_text(input_text_cur, chat_width - 1)
        
        #scroll_index
        scroll_index=len(wrap_text(input_text[:cursor_x], chat_width - 1))

        # Draw the input window with scroll
        input_win.clear()
        for idx, line in enumerate(wrapped_input_lines[input_scroll_pos:input_scroll_pos + 3]):
            input_win.addstr(idx, 0, line)
        input_win.refresh()

        # Calculate cursor position
        visible_lines = wrapped_input_lines[input_scroll_pos:input_scroll_pos + 3]
        cursor_line = min(len(visible_lines) - 1, cursor_x // (chat_width - 1))
        cursor_col = cursor_x % (chat_width - 1)
        
        # Ensure the cursor stays within the visible area
        cursor_line = min(cursor_line, len(visible_lines) - 1)
        if cursor_line >= 0:
            input_win.move(cursor_line, cursor_col)

        # Switch focus and handle input
        if current_focus == 'output':
            stdscr.addstr(height-1, 1, "Focus: Output Window", curses.A_BOLD)
            key = stdscr.getch()
            if key == curses.KEY_DOWN and output_scroll_pos < len(output_lines) - chat_height + 1:
                output_scroll_pos += 1
            elif key == curses.KEY_UP and output_scroll_pos > 0:
                output_scroll_pos -= 1
            elif key == 9:  # Tab key
                current_focus = 'input'
        elif current_focus == 'input':
            stdscr.addstr(height-1, 1, "Focus: Input Window ", curses.A_BOLD)
            key = stdscr.getch()
            if key == 5:  # Ctrl+E to exit (ASCII 5)
                break  # Exit the main loop
            if key == 18:  # Ctrl+R  to send input (ASCII code 19)
                if input_text.strip():
                    output_lines.extend(wrap_text(f"You: {input_text.strip()}", chat_width))
                    
                    # Get bot response and add to output
                    bot_reply = bot_response(input_text.strip())
                    output_lines.extend(wrap_text(f"Bot: {bot_reply}", chat_width))

                    input_text = ""
                    input_scroll_pos = 0
                    cursor_x = 0
                    output_scroll_pos = len(output_lines) - chat_height + 1  # Scroll to the bottom
                    output_scroll_pos = max(0, min(output_scroll_pos, len(output_lines) - chat_height + 1))
            elif key == 9:  # Tab key
                current_focus = 'output'
            elif key == 1:  # Ctrl+A (ASCII code 1) to insert 'sample text'
                input_text = input_text[:cursor_x] + "Given the sentence [your sentence], provide the annotated output according to FrameNet guidelines." + input_text[cursor_x:]
                cursor_x += len("Given the sentence '[your sentence]', provide the annotated output according to FrameNet guidelines.")
                input_scroll_pos = max(0, scroll_index - 2)
            elif key == 6:  # Ctrl+F (ASCII code 1) to insert 'sample text'
                input_text = input_text[:cursor_x] + "Read the frame [frame name] in the provided FrameNet data, then describe the frame in terms of its definition, frame elements and other frame relations with it." + input_text[cursor_x:]
                cursor_x += len("Read the frame [frame name] in the provided FrameNet data, then describe the frame in terms of its definition, frame elements and other frame relations with it.")
                input_scroll_pos = max(0, scroll_index - 2)
            elif key == curses.KEY_BACKSPACE or key == 127:
                if cursor_x > 0:
                    input_text = input_text[:cursor_x - 1] + input_text[cursor_x:]  # Remove character at cursor
                    cursor_x -= 1
                    input_scroll_pos = max(0, scroll_index - 2)
            elif key == curses.KEY_DC:  # Delete key
                if cursor_x < len(input_text):
                    input_text = input_text[:cursor_x] + input_text[cursor_x + 1:]  # Remove character in front of cursor
                    input_scroll_pos = max(0, scroll_index - 2)
            elif key == curses.KEY_LEFT and cursor_x > 0:
                cursor_x -= 1
            elif key == curses.KEY_RIGHT and cursor_x < len(input_text):
                cursor_x += 1
            elif key == curses.KEY_DOWN and input_scroll_pos < len(wrapped_input_lines) - 3:
                input_scroll_pos += 1
            elif key == curses.KEY_UP and input_scroll_pos > 0:
                input_scroll_pos -= 1
            elif 32 <= key <= 126:  # Regular characters
                input_text = input_text[:cursor_x] + chr(key) + input_text[cursor_x:]  # Add character at cursor
                cursor_x += 1
                input_scroll_pos = max(0, scroll_index - 2)
            elif key == 10:  # Enter key (add newline)
                input_text = input_text[:cursor_x] + '\n' + input_text[cursor_x:]
                cursor_x += 1

            # Update scrolling position if input lines exceed window height
            if len(wrapped_input_lines) > 3:
                input_scroll_pos = max(0, scroll_index - 2)

curses.wrapper(main)
