import curses

def wrap_text(text, width):
    """Wrap text into lines that fit within the given width."""
    lines = []
    while len(text) > width:
        wrap_point = text.rfind(' ', 0, width)
        if wrap_point == -1:  # No spaces, break at width
            wrap_point = width
        lines.append(text[:wrap_point])
        text = text[wrap_point:].lstrip()  # Remove leading spaces on the new line
    lines.append(text)
    return lines

def main(stdscr):
    # Initialize curses
    curses.curs_set(1)  # Set the cursor to be visible
    stdscr.clear()
    curses.start_color()

    # Set up colors
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # User input color
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Bot response color
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # System messages
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Logo color

    # Define dimensions and positions
    max_y, max_x = stdscr.getmaxyx()
    header_height = 3
    input_height = 5
    output_height = max_y - header_height - input_height

    # Create separate windows
    header_win = curses.newwin(header_height, max_x, 0, 0)
    output_win = curses.newwin(output_height, max_x, header_height, 0)
    input_win = curses.newwin(input_height, max_x, max_y - input_height, 0)

    # Enable scrolling for output window
    output_win.scrollok(True)

    # Display the "Frame Chat" logo at the top in the header window
    header_win.addstr(1, max_x // 2 - len("Frame Chat") // 2, "Frame Chat", curses.color_pair(4) | curses.A_BOLD)
    header_win.refresh()

    # Display welcome message in the output window
    output_win.addstr("Welcome to the Chatbot! Type 'exit' to quit.\n", curses.color_pair(3))
    output_win.refresh()

    input_lines = ['']  # Store multi-line input
    wrapped_lines = []  # Store wrapped lines for rendering
    current_line = 0
    top_visible_line = 0  # Index of the top line visible in the input window
    max_visible_lines = input_height - 2  # Maximum lines visible in the input window

    # Main loop
    while True:
        # Wrap input lines based on the window width
        wrapped_lines = [line for original_line in input_lines for line in wrap_text(original_line, max_x - 3)]

        # Calculate the range of lines to display in the input window
        start_line = max(top_visible_line, 0)
        end_line = min(start_line + max_visible_lines, len(wrapped_lines))

        # Clear the input window
        input_win.clear()
        input_win.border(0)

        # Render input lines within the visible range
        for i, line in enumerate(wrapped_lines[start_line:end_line]):
            input_win.addstr(i + 1, 1, line, curses.color_pair(1))

        input_win.refresh()

        # Get user input key-by-key
        ch = input_win.getch()

        # Handle different key inputs
        if ch == curses.KEY_ENTER or ch == 10:  # Enter key
            user_input = '\n'.join(input_lines).strip()
            if user_input.lower() == 'exit':
                break
            if user_input:
                output_win.addstr(f"You: {user_input}\n", curses.color_pair(1))
                output_win.refresh()

                # Dummy response logic (replace with actual chatbot logic)
                bot_response = f"Bot: {user_input[::-1]}"  # Simple reversed text as a response

                # Display bot response
                output_win.addstr(f"{bot_response}\n", curses.color_pair(2))
                output_win.refresh()

            # Reset input lines
            input_lines = ['']
            current_line = 0
            top_visible_line = 0

        elif ch == curses.KEY_BACKSPACE or ch == 127:  # Handle backspace
            if len(input_lines[current_line]) > 0:
                # Remove the last character from the current line
                input_lines[current_line] = input_lines[current_line][:-1]
            elif current_line > 0:  # Go up if at the start of the line
                # Move to the previous line and merge the lines
                prev_line = input_lines.pop(current_line)  # Remove the current empty line
                current_line -= 1
                # Merge with the previous line
                input_lines[current_line] += prev_line
                # Adjust top visible line if necessary
                if top_visible_line > 0:
                    top_visible_line -= 1

        elif ch == curses.KEY_UP:  # Navigate up in the input lines
            if current_line > 0:
                current_line -= 1
                if current_line < top_visible_line:
                    top_visible_line -= 1

        elif ch == curses.KEY_DOWN:  # Navigate down in the input lines
            if current_line < len(input_lines) - 1:
                current_line += 1
                if current_line >= top_visible_line + max_visible_lines:
                    top_visible_line += 1

        elif ch == curses.KEY_RESIZE:  # Handle window resizing
            max_y, max_x = stdscr.getmaxyx()
            header_height = 3
            input_height = 5
            output_height = max_y - header_height - input_height

            # Resize and reposition windows
            header_win.resize(header_height, max_x)
            output_win.resize(output_height, max_x)
            input_win.resize(input_height, max_x)
            input_win.mvwin(max_y - input_height, 0)

            # Refresh the header and output windows to reflect the new size
            header_win.clear()
            header_win.addstr(1, max_x // 2 - len("Frame Chat") // 2, "Frame Chat", curses.color_pair(4) | curses.A_BOLD)
            header_win.refresh()
            output_win.refresh()
            input_win.refresh()
            max_visible_lines = input_height - 2

        elif ch == 9:  # Handle tab (add two spaces)
            input_lines[current_line] += '  '

        elif ch == 27:  # Escape key to exit
            break

        elif ch == 10:  # Handle new line within input
            if len(input_lines) < 50:  # Prevent too many lines to avoid overflow
                input_lines.insert(current_line + 1, '')
                current_line += 1
                if current_line >= top_visible_line + max_visible_lines:
                    top_visible_line += 1

        else:
            # Add character to the current line
            input_lines[current_line] += chr(ch)

            # Adjust the scrolling if the number of wrapped lines exceeds the visible range
            if len(wrapped_lines) > max_visible_lines:
                top_visible_line = max(0, len(wrapped_lines) - max_visible_lines)

    # Exit message
    output_win.addstr("\nExiting... Goodbye!", curses.color_pair(3))
    output_win.refresh()
    output_win.getch()

# Run the program
curses.wrapper(main)

