import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
from datetime import datetime
import os
from ttkthemes import ThemedTk
import threading
from functools import partial

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tooltip_window = None

    def enter(self, event=None):
        """Display the tooltip when mouse enters the widget"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create new window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip label
        label = ttk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("Segoe UI", 9, "normal"), padding=(5, 2))
        label.pack(ipadx=2)

    def leave(self, event=None):
        """Remove tooltip when mouse leaves the widget"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class LoadingSpinner:
    """Creates a loading spinner animation"""
    def __init__(self, parent, size=30, color='#2196F3'):
        self.parent = parent
        self.size = size
        self.color = color
        
        # Fix: Use a safe method to get background color or use a default
        try:
            bg_color = parent.cget('background')
        except:
            bg_color = '#FAFAFA'  # Default fallback color
            
        self.canvas = tk.Canvas(parent, width=size, height=size, 
                              highlightthickness=0, bg=bg_color)
        self.angle = 0
        self.spinner_id = None
        self.running = False
    
    def start(self):
        """Start the loading animation"""
        self.running = True
        self.canvas.pack()
        self._animate()
    
    def stop(self):
        """Stop the loading animation"""
        self.running = False
        if self.spinner_id:
            self.canvas.after_cancel(self.spinner_id)
            self.spinner_id = None
        self.canvas.pack_forget()
    
    def _animate(self):
        """Animate a single frame"""
        if not self.running:
            return
            
        self.canvas.delete("spinner")
        
        # Draw arc with changing start angle
        arc_extent = 100  # Size of the arc (out of 360)
        start_angle = self.angle
        self.canvas.create_arc(2, 2, self.size-2, self.size-2, 
                              start=start_angle, extent=arc_extent,
                              style='arc', width=3, tags="spinner", 
                              outline=self.color)
        
        # Update angle for next frame
        self.angle = (self.angle + 10) % 360
        
        # Schedule next animation frame
        self.spinner_id = self.canvas.after(50, self._animate)


class RawResponseWindow:
    """A window to display raw API responses"""
    def __init__(self, parent, colors):
        self.window = tk.Toplevel(parent)
        self.window.title("Raw API Response")
        self.window.geometry("700x500")
        self.window.minsize(600, 400)
        self.colors = colors
        
        # Configure the window
        self.window.configure(background=self.colors['background'])
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.window, padding="10", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Raw API Response", 
               font=('Segoe UI', 14, 'bold'),
               foreground=self.colors['primary_dark']).pack(side=tk.LEFT)
        
        # Create text widget for the raw response
        self.text_widget = scrolledtext.ScrolledText(
            main_frame, font=('Consolas', 10), wrap=tk.NONE,
            background='#f8f8f8', foreground='#333333')
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add syntax highlighting tags
        self.text_widget.tag_configure("key", foreground="#7A3E9D")
        self.text_widget.tag_configure("string", foreground="#2E7D32")
        self.text_widget.tag_configure("number", foreground="#0277BD")
        self.text_widget.tag_configure("boolean", foreground="#E64A19")
        self.text_widget.tag_configure("null", foreground="#757575")
        self.text_widget.tag_configure("brace", foreground="#616161")
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", 
                               command=self.text_widget.xview)
        self.text_widget.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(fill=tk.X)
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Copy button
        copy_button = ttk.Button(button_frame, text="Copy to Clipboard", 
                             command=self.copy_to_clipboard)
        copy_button.pack(side=tk.RIGHT)
        
        # Initially hide the window
        self.window.withdraw()
        
        # Set up window close behavior
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
    def show(self, json_data):
        """Show the window with formatted JSON data"""
        self.text_widget.delete(1.0, tk.END)
        
        if isinstance(json_data, str):
            # If already a string, format it as JSON
            try:
                formatted_json = json.dumps(json.loads(json_data), indent=2)
            except:
                formatted_json = json_data
        else:
            # Otherwise, convert to formatted JSON
            try:
                formatted_json = json.dumps(json_data, indent=2)
            except:
                formatted_json = str(json_data)
        
        self.text_widget.insert(tk.END, formatted_json)
        self._apply_json_highlighting()
        
        # Make sure window is visible and bring to front
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()
    
    def hide(self):
        """Hide the window"""
        self.window.withdraw()
    
    def copy_to_clipboard(self):
        """Copy the raw response to clipboard"""
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text_widget.get(1.0, tk.END))
        
        # Show a brief notification
        self.text_widget.tag_add("flash", "1.0", tk.END)
        self.text_widget.tag_configure("flash", background="#E3F2FD")
        self.window.after(200, lambda: self.text_widget.tag_remove("flash", "1.0", tk.END))
    
    def _apply_json_highlighting(self):
        """Apply syntax highlighting to JSON content"""
        content = self.text_widget.get(1.0, tk.END)
        
        # Reset all tags
        for tag in ["key", "string", "number", "boolean", "null", "brace"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)
        
        # Apply highlighting for different JSON elements
        in_string = False
        escape_next = False
        string_start = "1.0"
        
        for i, char in enumerate(content):
            pos = f"1.0+{i}c"
            next_pos = f"1.0+{i+1}c"
            
            # Handle strings
            if char == '"' and not escape_next:
                if not in_string:
                    in_string = True
                    string_start = pos
                else:
                    in_string = False
                    # Check if this is a key (followed by :)
                    next_chars = content[i+1:i+5].strip()
                    if next_chars and next_chars[0] == ':':
                        self.text_widget.tag_add("key", string_start, next_pos)
                    else:
                        self.text_widget.tag_add("string", string_start, next_pos)
            
            # Handle escape character
            if char == '\\':
                escape_next = not escape_next
            else:
                escape_next = False
            
            # Handle braces and brackets
            if char in "{}[]," and not in_string:
                self.text_widget.tag_add("brace", pos, next_pos)
            
            # Handle simple values (when not in a string)
            if not in_string and not char.isspace():
                # Check for boolean and null values
                if content[i:i+4] == "true":
                    self.text_widget.tag_add("boolean", pos, f"1.0+{i+4}c")
                elif content[i:i+5] == "false":
                    self.text_widget.tag_add("boolean", pos, f"1.0+{i+5}c")
                elif content[i:i+4] == "null":
                    self.text_widget.tag_add("null", pos, f"1.0+{i+4}c")
                # Check for numbers (simplistic approach)
                elif char.isdigit() or char == '-':
                    # Find the end of the number
                    j = i
                    while j < len(content) and (content[j].isdigit() or content[j] in "-.eE+"):
                        j += 1
                    if j > i:
                        self.text_widget.tag_add("number", pos, f"1.0+{j}c")


class LMSContentGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LMS AI Content Generator")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Set color scheme
        self.colors = {
            'primary': '#1976D2',     # Primary blue
            'primary_dark': '#0D47A1',
            'primary_light': '#BBDEFB',
            'secondary': '#2e7d32',   # Green for buttons
            'secondary_light': '#60ad5e',
            'secondary_dark': '#005005',
            'text': '#212121',        # Near black
            'text_secondary': '#757575',
            'background': '#FAFAFA',  # Light gray
            'surface': '#FFFFFF',     # White
            'error': '#B00020',       # Red for errors
            'divider': '#BDBDBD'      # Light gray for dividers
        }
        
        # Store the current raw response
        self.current_raw_response = None
        
        # Configure the themed style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Using 'clam' as the base theme
        
        # Configure the colors and fonts for various elements
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('TLabelframe', background=self.colors['background'])
        self.style.configure('TLabelframe.Label', 
                         background=self.colors['background'],
                         foreground=self.colors['primary_dark'],
                         font=('Segoe UI', 11, 'bold'))
        
        self.style.configure('TLabel', 
                         background=self.colors['background'],
                         foreground=self.colors['text'],
                         font=('Segoe UI', 10))
        
        self.style.configure('Header.TLabel', 
                         background=self.colors['background'],
                         foreground=self.colors['primary_dark'],
                         font=('Segoe UI', 18, 'bold'))
        
        self.style.configure('Subheader.TLabel', 
                         background=self.colors['background'],
                         foreground=self.colors['primary'],
                         font=('Segoe UI', 14))
        
        self.style.configure('TEntry', 
                         fieldbackground=self.colors['surface'],
                         foreground=self.colors['text'])
        
        self.style.configure('TButton', 
                         background=self.colors['secondary'],
                         foreground='white',
                         padding=(10, 5),
                         font=('Segoe UI', 10, 'bold'))
        
        self.style.map('TButton',
                    background=[('active', self.colors['secondary_light'])])
        
        self.style.configure('Small.TButton', 
                         font=('Segoe UI', 9))
        
        # Configure the combobox
        self.style.map('TCombobox',
                    fieldbackground=[('readonly', self.colors['surface'])],
                    selectbackground=[('readonly', self.colors['primary'])])
        
        # Set the overall background color
        self.root.configure(background=self.colors['background'])
        
        # Initialize history list
        self.history = []
        
        # Create the raw response window
        self.raw_response_window = RawResponseWindow(self.root, self.colors)
        
        # Create the main container with padding
        main_container = ttk.Frame(self.root, padding="20", style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header with logo (text-based logo for now)
        header_frame = ttk.Frame(main_container, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create a "logo" using text and styling
        logo_text = "LMS AI Content Generator"
        logo_label = ttk.Label(header_frame, text=logo_text, style='Header.TLabel')
        logo_label.pack(side=tk.LEFT)
        
        # Create the content frame with two columns
        content_frame = ttk.Frame(main_container, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column for input form
        left_column = ttk.Frame(content_frame, style='TFrame')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Input form with nice styling
        input_frame = ttk.LabelFrame(left_column, text="Generate Content", padding="15", style='TLabelframe')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # API URL with info icon
        url_frame = ttk.Frame(input_frame, style='TFrame')
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="API URL:", style='TLabel').pack(side=tk.LEFT)
        
        self.url_var = tk.StringVar()
        # Try to load the URL from a config file
        try:
            if os.path.exists("lms_config.txt"):
                with open("lms_config.txt", "r") as f:
                    saved_url = f.read().strip()
                    self.url_var.set(saved_url)
            else:
                self.url_var.set("https://lms-content-generator-188283756417.us-central1.run.app")
        except:
            self.url_var.set("https://lms-content-generator-188283756417.us-central1.run.app")
        
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        save_url_button = ttk.Button(url_frame, text="Save", command=self.save_url, style='Small.TButton')
        save_url_button.pack(side=tk.RIGHT)
        
        # Grid layout for the form fields
        form_grid = ttk.Frame(input_frame, style='TFrame')
        form_grid.pack(fill=tk.X, pady=5)
        
        # Configure grid columns
        form_grid.columnconfigure(0, weight=1)
        form_grid.columnconfigure(1, weight=3)
        
        # Topic input with nice styling
        ttk.Label(form_grid, text="Topic:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=10)
        self.topic_var = tk.StringVar()
        topic_entry = ttk.Entry(form_grid, textvariable=self.topic_var, width=50)
        topic_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=10)
        
        # Content Type dropdown
        ttk.Label(form_grid, text="Content Type:", style='TLabel').grid(row=1, column=0, sticky=tk.W, pady=10)
        self.content_type_var = tk.StringVar()
        content_types = ["paragraph", "multiple_choice_question", "quiz"]
        
        content_type_frame = ttk.Frame(form_grid, style='TFrame')
        content_type_frame.grid(row=1, column=1, sticky=tk.W+tk.E, pady=10)
        
        # Create stylized buttons for content types
        for i, content_type in enumerate(content_types):
            button = ttk.Radiobutton(content_type_frame, text=content_type.replace('_', ' ').title(),
                                  variable=self.content_type_var, value=content_type)
            button.pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))
        
        # Set default content type
        self.content_type_var.set(content_types[0])
        
        # Context Input
        ttk.Label(form_grid, text="Context:", style='TLabel').grid(row=2, column=0, sticky=tk.W+tk.N, pady=10)
        
        # Custom frame for the text area to add styling
        context_container = ttk.Frame(form_grid, style='TFrame')
        context_container.grid(row=2, column=1, sticky=tk.W+tk.E, pady=10)
        
        self.context_text = scrolledtext.ScrolledText(
            context_container, width=40, height=5, font=('Segoe UI', 10),
            background=self.colors['surface'], foreground=self.colors['text'])
        self.context_text.pack(fill=tk.BOTH, expand=True)
        
        # Add options frame for caching and conversation state
        options_frame = ttk.Frame(form_grid, style='TFrame')
        options_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Use cache checkbox - Changed default to False
        self.use_cache_var = tk.BooleanVar(value=False)  # Default is unchecked
        cache_check = ttk.Checkbutton(options_frame, text="Use Cache", 
                                  variable=self.use_cache_var,
                                  command=self.toggle_cache)  # Add command callback
        cache_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Add tooltip for cache checkbox
        cache_tooltip = ToolTip(cache_check, 
                            "Cache responses for identical requests (topic+type+context).\n" +
                            "Limited to the last 100 requests.\n" +
                            "Cannot be used with Conversation State.")
        
        # Conversation state checkbox - Default remains True
        self.use_state_var = tk.BooleanVar(value=True)  # Default is checked
        state_check = ttk.Checkbutton(options_frame, text="Conversation State", 
                                  variable=self.use_state_var,
                                  command=self.toggle_state)  # Add command callback
        state_check.pack(side=tk.LEFT)
        
        # Add tooltip for state checkbox
        state_tooltip = ToolTip(state_check, 
                            "Include previous request and response in context\n" + 
                            "to create a conversation-like interaction.\n" +
                            "Cannot be used with Cache.")
        
        # Generate Button with loading indicator container
        button_frame = ttk.Frame(input_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(15, 5))
        
        generate_frame = ttk.Frame(button_frame, style='TFrame')
        generate_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        
        self.generate_button = ttk.Button(
            generate_frame, 
            text="Generate Content", 
            command=self.generate_content,
            style='TButton',
            padding=(20, 10))
        self.generate_button.pack(side=tk.LEFT)
        
        # Loading spinner (hidden initially)
        self.spinner_frame = ttk.Frame(generate_frame, style='TFrame')
        self.spinner_frame.pack(side=tk.LEFT, padx=10)
        self.spinner = LoadingSpinner(self.spinner_frame, size=24, color=self.colors['primary'])
        
        # Right column for results
        right_column = ttk.Frame(content_frame, style='TFrame')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create the results panel with toolbar
        results_frame = ttk.LabelFrame(right_column, text="Results", padding="15", style='TLabelframe')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Results toolbar
        results_toolbar = ttk.Frame(results_frame, style='TFrame')
        results_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # View Raw Response button
        self.view_raw_button = ttk.Button(
            results_toolbar, text="View Raw Response", 
            command=self.view_raw_response, 
            style='Small.TButton')
        self.view_raw_button.pack(side=tk.RIGHT)
        self.view_raw_button.state(['disabled'])  # Initially disabled
        
        # Results display area with better styling
        self.results_text = scrolledtext.ScrolledText(
            results_frame, font=('Segoe UI', 10),
            background=self.colors['surface'], foreground=self.colors['text'])
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)
        
        # History panel with better styling
        history_frame = ttk.LabelFrame(left_column, text="History", padding="15", style='TLabelframe')
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # History tools
        history_tools = ttk.Frame(history_frame, style='TFrame')
        history_tools.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(history_tools, text="Recent Requests", style='Subheader.TLabel').pack(side=tk.LEFT)
        
        self.clear_button = ttk.Button(
            history_tools, text="Clear History", 
            command=self.clear_history, style='Small.TButton')
        self.clear_button.pack(side=tk.RIGHT)
        
        # History list with improved styling
        history_list_frame = ttk.Frame(history_frame, style='TFrame')
        history_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Custom styled listbox
        self.history_frame = ttk.Frame(history_list_frame, style='TFrame')
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        # We'll create a scrollable frame for history items
        self.history_canvas = tk.Canvas(
            self.history_frame, highlightthickness=0, 
            background=self.colors['surface'])
        scrollbar = ttk.Scrollbar(
            self.history_frame, orient="vertical", 
            command=self.history_canvas.yview)
        
        self.history_container = ttk.Frame(self.history_canvas, style='TFrame')
        self.history_container.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            )
        )
        
        self.history_canvas.create_window((0, 0), window=self.history_container, anchor="nw")
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar with modern styling
        status_frame = ttk.Frame(self.root, style='TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            status_frame, textvariable=self.status_var,
            background=self.colors['primary_light'],
            foreground=self.colors['primary_dark'],
            padding=(10, 5))
        status_bar.pack(fill=tk.X)
        
        # Set focus to the topic field
        topic_entry.focus_set()
    
    # Add the toggle methods for mutually exclusive checkboxes
    def toggle_cache(self):
        """Toggle the cache checkbox and ensure state checkbox is opposite"""
        if self.use_cache_var.get():
            # If cache is being turned on, turn off state
            self.use_state_var.set(False)
    
    def toggle_state(self):
        """Toggle the state checkbox and ensure cache checkbox is opposite"""
        if self.use_state_var.get():
            # If state is being turned on, turn off cache
            self.use_cache_var.set(False)
    
    def generate_content(self):
        """Send a request to the API and display the results"""
        # Save the URL to config file
        self.save_url()
        
        # Get the input values
        url = self.url_var.get().strip()
        if not url.endswith('/generate'):
            url = url.rstrip('/') + '/generate'
            
        topic = self.topic_var.get().strip()
        content_type = self.content_type_var.get()
        
        # Get the context and apply cache/state markers based on checkbox settings
        context = self.context_text.get("1.0", tk.END).strip()
        
        # Check character limits
        if len(topic) > 10000:
            messagebox.showerror("Error", "Topic exceeds 10,000 character limit")
            return
            
        if len(context) > 10000:
            messagebox.showerror("Error", "Context exceeds 10,000 character limit")
            return
        
        # Apply cache marker if enabled
        if self.use_cache_var.get():
            if not context.startswith("[cache=true]"):
                context = f"[cache=true] {context}"
        else:
            context = context.replace("[cache=true]", "").strip()
            
        # Apply state marker if enabled
        if self.use_state_var.get():
            if not context.endswith("[state=true]"):
                context = f"{context} [state=true]"
        else:
            context = context.replace("[state=true]", "").strip()
        
        # Validate inputs
        if not topic:
            messagebox.showerror("Error", "Please enter a topic")
            return
        
        # Update status and show spinner
        self.status_var.set("Generating content...")
        self.spinner.start()
        self.root.update_idletasks()
        
        # Disable the generate button and raw view button
        self.generate_button.configure(state=tk.DISABLED)
        self.view_raw_button.state(['disabled'])
        
        # Create a thread for the API call
        thread = threading.Thread(target=self._process_request, 
                               args=(url, topic, content_type, context))
        thread.daemon = True
        thread.start()
    
    def _process_request(self, url, topic, content_type, context):
        """Process the API request in a background thread"""
        try:
            # Prepare the request payload
            payload = {
                "topic": topic,
                "content_type": content_type
            }
            if context:
                payload["context"] = context
                
            # Send the request
            response = requests.post(url, json=payload, timeout=60)
            
            # Process the response in the main thread
            self.root.after(0, self._handle_response, response, topic, content_type, context)
                
        except Exception as e:
            # Handle exceptions in the main thread
            self.root.after(0, self._handle_error, str(e))
    
    def _handle_response(self, response, topic, content_type, context):
        """Handle the API response in the main thread"""
        # Hide spinner and enable the button
        self.spinner.stop()
        self.generate_button.configure(state=tk.NORMAL)
        
        # Clear the results area
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        # Store the raw response
        try:
            self.current_raw_response = response.json()
            # Enable the view raw button
            self.view_raw_button.state(['!disabled'])
        except json.JSONDecodeError:
            self.current_raw_response = response.text
            
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            try:
                data = self.current_raw_response if isinstance(self.current_raw_response, dict) else json.loads(self.current_raw_response)
                
                # Format the response based on content type
                if content_type == "paragraph":
                    self.display_paragraph(data)
                elif content_type == "multiple_choice_question":
                    self.display_mcq(data)
                elif content_type == "quiz":
                    self.display_quiz(data)
                else:
                    # Display raw JSON if content type is unknown
                    formatted_json = json.dumps(data, indent=2)
                    self.results_text.insert(tk.END, formatted_json)
                
                # Add to history - Store the context without markers for better display
                display_context = context
                if self.use_cache_var.get():
                    display_context = display_context.replace("[cache=true]", "").strip()
                if self.use_state_var.get():
                    display_context = display_context.replace("[state=true]", "").strip()
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                history_item = {
                    "timestamp": timestamp,
                    "topic": topic,
                    "content_type": content_type,
                    "context": display_context,  # Store cleaned context for display
                    "use_cache": self.use_cache_var.get(),
                    "use_state": self.use_state_var.get(),
                    "response": data,
                    "raw_response": self.current_raw_response
                }
                self._add_history_item(history_item)
                
                # Update the context field with the cleaned context (preserving markers)
                self.context_text.delete("1.0", tk.END)
                self.context_text.insert(tk.END, display_context)
                
                self.status_var.set("Content generated successfully")
            except json.JSONDecodeError:
                self.results_text.insert(tk.END, f"Error parsing response: {response.text}")
                self.status_var.set("Error parsing response")
        else:
            error_msg = f"Error: {response.status_code}\n{response.text}"
            self.results_text.insert(tk.END, error_msg)
            self.status_var.set(f"Error: {response.status_code}")
        
        self.results_text.config(state=tk.DISABLED)
    
    def _handle_error(self, error_msg):
        """Handle exceptions in the main thread"""
        # Hide spinner and enable the button
        self.spinner.stop()
        self.generate_button.configure(state=tk.NORMAL)
        self.view_raw_button.state(['disabled'])
        
        # Display the error
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Error: {error_msg}")
        self.status_var.set(f"Error: {error_msg}")
        self.results_text.config(state=tk.DISABLED)
        
        # Clear current raw response
        self.current_raw_response = None
    
    def view_raw_response(self):
        """Show the raw response window"""
        if self.current_raw_response:
            self.raw_response_window.show(self.current_raw_response)
    
    def _add_history_item(self, item):
        """Add an item to the history"""
        # Add to the history list
        self.history.insert(0, item)
        
        # Keep only the last 10 items
        if len(self.history) > 10:
            self.history.pop()
        
        # Update the history display
        self._refresh_history_display()
    
    def _refresh_history_display(self):
        """Refresh the history display"""
        # Clear existing items
        for widget in self.history_container.winfo_children():
            widget.destroy()
        
        # Add history items
        for i, item in enumerate(self.history):
            # Create a frame for this history item
            item_frame = ttk.Frame(self.history_container, padding=5)
            item_frame.pack(fill=tk.X, pady=2)
            
            # Add a thin separator above items (except the first)
            if i > 0:
                separator = ttk.Separator(self.history_container, orient='horizontal')
                separator.pack(fill=tk.X, pady=(0, 5))
            
            # Format the display
            content_type_display = item["content_type"].replace('_', ' ').title()
            timestamp_display = item["timestamp"]
            
            # Title with timestamp
            title_frame = ttk.Frame(item_frame)
            title_frame.pack(fill=tk.X)
            
            ttk.Label(
                title_frame, 
                text=f"{item['topic']}", 
                font=('Segoe UI', 10, 'bold'),
                foreground=self.colors['primary_dark']).pack(side=tk.LEFT)
            
            ttk.Label(
                title_frame,
                text=f"{timestamp_display}",
                font=('Segoe UI', 8),
                foreground=self.colors['text_secondary']).pack(side=tk.RIGHT)
            
            # Type and preview
            ttk.Label(
                item_frame,
                text=f"Type: {content_type_display}",
                font=('Segoe UI', 9),
                foreground=self.colors['text_secondary']).pack(anchor=tk.W)
            
            # Buttons frame
            buttons_frame = ttk.Frame(item_frame)
            buttons_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Raw response button
            raw_button = ttk.Button(
                buttons_frame, text="Raw", 
                command=partial(self._view_history_raw, i),
                style='Small.TButton')
            raw_button.pack(side=tk.RIGHT, padx=(5, 0))
            
            # Load button
            load_button = ttk.Button(
                buttons_frame, text="Load", 
                command=partial(self._load_history_item, i),
                style='Small.TButton')
            load_button.pack(side=tk.RIGHT)
    
    def _load_history_item(self, index):
        """Load a history item when selected"""
        try:
            # Get the history item
            item = self.history[index]
            
            # Populate the form with the history item's values
            self.topic_var.set(item["topic"])
            self.content_type_var.set(item["content_type"])
            self.context_text.delete("1.0", tk.END)
            self.context_text.insert(tk.END, item["context"])
            
            # Set the cache and state checkboxes if they were stored
            if "use_cache" in item:
                self.use_cache_var.set(item["use_cache"])
            if "use_state" in item:
                self.use_state_var.set(item["use_state"])
            
            # Store the raw response
            self.current_raw_response = item.get("raw_response", item["response"])
            self.view_raw_button.state(['!disabled'])
            
            # Display the results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete("1.0", tk.END)
            
            # Format the response based on content type
            content_type = item["content_type"]
            if content_type == "paragraph":
                self.display_paragraph(item["response"])
            elif content_type == "multiple_choice_question":
                self.display_mcq(item["response"])
            elif content_type == "quiz":
                self.display_quiz(item["response"])
            else:
                # Display raw JSON if content type is unknown
                formatted_json = json.dumps(item["response"], indent=2)
                self.results_text.insert(tk.END, formatted_json)
                
            self.results_text.config(state=tk.DISABLED)
            
        except (IndexError, KeyError) as e:
            pass
    
    def _view_history_raw(self, index):
        """View raw response for a history item"""
        try:
            item = self.history[index]
            raw_response = item.get("raw_response", item["response"])
            self.raw_response_window.show(raw_response)
        except (IndexError, KeyError) as e:
            pass
    
    def display_paragraph(self, data):
        """Display paragraph content with improved formatting"""
        content = data.get("content", "No content found")
        
        # Apply some basic markdown-like formatting
        self.results_text.insert(tk.END, content)
    
    def display_mcq(self, data):
        """Display multiple choice question with better formatting"""
        question_text = data.get("question_text", "No question found")
        options = data.get("options", [])
        correct_index = data.get("correct_answer_index", 0)
        
        self.results_text.tag_configure("question", font=('Segoe UI', 10, 'bold'))
        self.results_text.tag_configure("option", font=('Segoe UI', 10))
        self.results_text.tag_configure("correct", foreground=self.colors['secondary'])
        
        self.results_text.insert(tk.END, "Question: ", "question")
        self.results_text.insert(tk.END, f"{question_text}\n\n")
        
        for i, option in enumerate(options):
            option_text = f"{chr(65+i)}. {option}"
            
            if i == correct_index:
                self.results_text.insert(tk.END, f"{option_text} ✓\n", "correct")
            else:
                self.results_text.insert(tk.END, f"{option_text}\n", "option")
    
    def display_quiz(self, data):
        """Display quiz content with better formatting"""
        title = data.get("title", "Quiz")
        questions = data.get("questions", [])
        
        self.results_text.tag_configure("title", font=('Segoe UI', 12, 'bold'), foreground=self.colors['primary_dark'])
        self.results_text.tag_configure("question", font=('Segoe UI', 10, 'bold'))
        self.results_text.tag_configure("option", font=('Segoe UI', 10))
        self.results_text.tag_configure("correct", foreground=self.colors['secondary'])
        
        self.results_text.insert(tk.END, f"{title}\n\n", "title")
        
        for i, question in enumerate(questions):
            question_text = question.get("question_text", "No question found")
            options = question.get("options", [])
            correct_index = question.get("correct_answer_index", 0)
            
            self.results_text.insert(tk.END, f"Question {i+1}: ", "question")
            self.results_text.insert(tk.END, f"{question_text}\n\n")
            
            for j, option in enumerate(options):
                option_text = f"   {chr(65+j)}. {option}"
                
                if j == correct_index:
                    self.results_text.insert(tk.END, f"{option_text} ✓\n", "correct")
                else:
                    self.results_text.insert(tk.END, f"{option_text}\n", "option")
            
            self.results_text.insert(tk.END, "\n")
    
    def clear_history(self):
        """Clear the history list"""
        self.history = []
        self._refresh_history_display()
    
    def save_url(self):
        """Save the URL to a config file"""
        url = self.url_var.get().strip()
        try:
            with open("lms_config.txt", "w") as f:
                f.write(url)
        except Exception as e:
            pass


def main():
    # Try to use ThemedTk with graceful fallback to regular Tk
    try:
        root = ThemedTk(theme="arc")  # Use the 'arc' theme which is modern
    except Exception:
        # If ThemedTk is not available or fails, fall back to regular Tk
        root = tk.Tk()
        
    app = LMSContentGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()