import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import queue
import re
import difflib

class VirtualImageBrowser:
    def __init__(self, root, base_path):
        self.root = root
        self.base_path = base_path
        self.images = []
        self.filtered_images = []
        self.thumbnail_cache = {}  # LRU-style cache
        self.cache_max_size = 200  # Max thumbnails in memory
        self.thumbnail_size = (80, 80)
        self.columns = 8
        self.row_height = 120
        self.visible_items = {}  # Currently visible item widgets
        self.loading_set = set()  # Paths currently being loaded
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.load_queue = queue.Queue()
        self.pending_updates = {}
        self.scroll_job = None
        self.last_visible_range = (0, 0)
        
        # Placeholder image
        self.placeholder = None
        self.error_placeholder = None
        
        self.create_placeholders()
        self.setup_ui() # Modified to support tabs
        self.scan_images()
        self.start_loader_thread()
        
    def create_placeholders(self):
        """Create placeholder images"""
        img = Image.new('RGB', self.thumbnail_size, (60, 60, 60))
        self.placeholder = ImageTk.PhotoImage(img)
        img_err = Image.new('RGB', self.thumbnail_size, (80, 40, 40))
        self.error_placeholder = ImageTk.PhotoImage(img_err)
        
    def setup_ui(self):
        self.root.title("HOI4 Goal Image Browser & Script Fixer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground='white')
        style.configure('TButton', background='#3c3c3c', foreground='white', borderwidth=1)
        style.map('TButton', background=[('active', '#505050')])
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # --- TAB 1: Image Browser ---
        self.browser_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_tab, text=" 🖼️ Image Browser ")
        self.setup_browser_ui(self.browser_tab)
        
        # --- TAB 2: Script Fixer ---
        self.fixer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.fixer_tab, text=" 🛠️ Script Fixer ")
        self.setup_fixer_ui(self.fixer_tab)

    def setup_fixer_ui(self, parent):
        """UI for the script fixing tool"""
        # Controls Frame
        ctrl_frame = ttk.Frame(parent, padding=10)
        ctrl_frame.pack(fill=tk.X)
        
        ttk.Label(ctrl_frame, text="Paste your focus tree code below. The tool will replace invalid icons with the closest image filename found.", 
                 font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(parent, padding=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(btn_frame, text="✨ Auto-Fix Icons", command=self.run_script_fixer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.input_text.delete("1.0", tk.END)).pack(side=tk.RIGHT, padx=5)
        
        self.log_label = ttk.Label(btn_frame, text="Ready", foreground="#aaaaaa")
        self.log_label.pack(side=tk.LEFT)
        
        # Text Area
        text_frame = ttk.Frame(parent, padding=(10, 0, 10, 0))
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_text = tk.Text(text_frame, bg='#1e1e1e', fg='#dcdcdc', 
                                  insertbackground='white', font=('Consolas', 10), undo=True)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.input_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=scroll.set)

    def run_script_fixer(self):
            """Analyzes text and replaces icons with closest matches, adding GFX_ prefix"""
            if not self.images:
                messagebox.showwarning("Wait", "Still scanning images. Please wait a moment.")
                return
    
            text_content = self.input_text.get("1.0", tk.END)
            if not text_content.strip():
                return
    
            # 1. Create a dictionary mapping: 
            # Key = Clean Filename (what we match against)
            # Value = HOI4 Sprite Name (what we output, usually GFX_ + filename)
            valid_names = {}
            for img in self.images:
                clean_name = os.path.splitext(img['name'])[0]
                
                # CHECK: Does it already start with GFX_?
                # If yes, keep it. If no, prepend GFX_.
                if clean_name.upper().startswith("GFX_"):
                    sprite_name = clean_name
                else:
                    sprite_name = f"GFX_{clean_name}"
                    
                valid_names[clean_name] = sprite_name
                
            valid_keys = list(valid_names.keys())
            changes_count = 0
            
            def replacer(match):
                nonlocal changes_count
                prefix = match.group(1) # "icon = "
                current_val = match.group(2) # The name provided in script
                
                # Check if it exists exactly (Case sensitive check)
                if current_val in valid_keys:
                    # Even if it matches exactly, ensure we return the GFX_ version
                    return f"{prefix}{valid_names[current_val]}"
                
                # Use difflib to find closest match based on the filename
                # cutoff=0.4 means it needs to be at least 40% similar.
                closest = difflib.get_close_matches(current_val, valid_keys, n=1, cutoff=0.4)
                
                if closest:
                    best_match_key = closest[0] # This is the filename
                    final_sprite_name = valid_names[best_match_key] # This is GFX_filename
                    
                    changes_count += 1
                    print(f"Fixing: '{current_val}' -> '{final_sprite_name}'")
                    return f"{prefix}{final_sprite_name}"
                else:
                    # No close match found, keep original
                    return match.group(0)
    
            # Regex explanation:
            # (icon\s*=\s*)  -> Group 1: Matches 'icon =' with variable spacing
            # ([^\s#\}]+)    -> Group 2: Matches the value (chars that aren't space, #, or })
            new_text = re.sub(r'(icon\s*=\s*)([^\s#\}]+)', replacer, text_content, flags=re.IGNORECASE)
            
            # Update text widget
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", new_text)
            
            self.log_label.configure(text=f"Process complete. Fixed {changes_count} invalid icons.")
            messagebox.showinfo("Complete", f"Replaced {changes_count} invalid icons with proper GFX_ format.")
    def setup_browser_ui(self, parent):
        # Top frame with search
        top_frame = ttk.Frame(parent, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="🔍 Search:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_debounced)
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=50, font=('Segoe UI', 11))
        self.search_entry.pack(side=tk.LEFT, padx=10)
        
        # Size controls
        ttk.Label(top_frame, text="Size:").pack(side=tk.LEFT, padx=(20, 5))
        self.size_var = tk.IntVar(value=80)
        size_scale = ttk.Scale(top_frame, from_=50, to=150, variable=self.size_var, 
                               orient=tk.HORIZONTAL, length=100, command=self.on_size_change_debounced)
        size_scale.pack(side=tk.LEFT)
        
        # Cache info
        self.cache_var = tk.StringVar(value="Cache: 0")
        ttk.Label(top_frame, textvariable=self.cache_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=20)
        
        # Status label
        self.status_var = tk.StringVar(value="Scanning...")
        ttk.Label(top_frame, textvariable=self.status_var, font=('Segoe UI', 10)).pack(side=tk.RIGHT)
        
        # Path label
        path_frame = ttk.Frame(parent, padding=(10, 0))
        path_frame.pack(fill=tk.X)
        ttk.Label(path_frame, text=f"📁 {self.base_path}", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        # Visible range indicator
        self.range_var = tk.StringVar(value="")
        ttk.Label(path_frame, textvariable=self.range_var, font=('Segoe UI', 9)).pack(side=tk.RIGHT)
        
        # Main canvas area with virtual scrolling
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Container frame inside canvas (will be sized to full virtual height)
        self.inner_frame = tk.Frame(self.canvas, bg='#1e1e1e')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Bind events
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Button-4>', lambda e: self.on_scroll(-1))
        self.canvas.bind('<Button-5>', lambda e: self.on_scroll(1))
        
        # Keyboard shortcuts
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus_set())
        self.root.bind('<Escape>', lambda e: self.search_var.set(''))
        self.root.bind('<Home>', lambda e: self.canvas.yview_moveto(0))
        self.root.bind('<End>', lambda e: self.canvas.yview_moveto(1))
        
    def on_canvas_configure(self, event):
        # Update columns based on width
        new_columns = max(1, (event.width - 20) // (self.thumbnail_size[0] + 30))
        if new_columns != self.columns:
            self.columns = new_columns
            self.update_virtual_size()
            self.schedule_render()
            
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.schedule_render()
        
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.schedule_render()
        
    def on_scroll(self, direction):
        self.canvas.yview_scroll(direction, "units")
        self.schedule_render()
        
    def schedule_render(self):
        """Debounced render scheduling"""
        if self.scroll_job:
            self.root.after_cancel(self.scroll_job)
        self.scroll_job = self.root.after(16, self.render_visible)  # ~60fps
        
    def on_search_debounced(self, *args):
        """Debounced search"""
        if hasattr(self, '_search_job'):
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(200, self.do_search)
        
    def do_search(self):
        search_term = self.search_var.get().lower().strip()
        
        if search_term:
            self.filtered_images = [
                img for img in self.images 
                if search_term in img['name'].lower() or search_term in img['rel_path'].lower()
            ]
        else:
            self.filtered_images = self.images.copy()
        
        self.status_var.set(f"Showing {len(self.filtered_images)} of {len(self.images)} images")
        self.clear_visible_items()
        self.update_virtual_size()
        self.canvas.yview_moveto(0)
        self.render_visible()
        
    def on_size_change_debounced(self, value):
        if hasattr(self, '_size_job'):
            self.root.after_cancel(self._size_job)
        self._size_job = self.root.after(150, lambda: self.apply_size_change(value))
        
    def apply_size_change(self, value):
        new_size = int(float(value))
        if new_size != self.thumbnail_size[0]:
            self.thumbnail_size = (new_size, new_size)
            self.row_height = new_size + 40
            self.thumbnail_cache.clear()
            self.create_placeholders()
            self.clear_visible_items()
            self.update_virtual_size()
            self.render_visible()
            
    def scan_images(self):
        def scan():
            extensions = {'.dds', '.tga', '.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            found = []
            
            if not os.path.exists(self.base_path):
                self.root.after(0, lambda: messagebox.showerror("Error", f"Path not found:\n{self.base_path}"))
                return
                
            for root_dir, dirs, files in os.walk(self.base_path):
                for file in files:
                    if Path(file).suffix.lower() in extensions:
                        full_path = os.path.join(root_dir, file)
                        rel_path = os.path.relpath(full_path, self.base_path)
                        found.append({
                            'full_path': full_path,
                            'rel_path': rel_path,
                            'name': file,
                            'folder': os.path.dirname(rel_path) or "root"
                        })
            
            self.images = found
            self.filtered_images = found.copy()
            self.root.after(0, self.on_scan_complete)
            
        threading.Thread(target=scan, daemon=True).start()
        
    def on_scan_complete(self):
        self.status_var.set(f"Found {len(self.images)} images")
        self.update_virtual_size()
        self.render_visible()
        
    def update_virtual_size(self):
        """Update the virtual scroll region based on total items"""
        if not self.filtered_images:
            return
            
        total_rows = (len(self.filtered_images) + self.columns - 1) // self.columns
        virtual_height = total_rows * self.row_height + 20
        
        # Set the inner frame size
        self.inner_frame.configure(height=virtual_height)
        canvas_width = self.canvas.winfo_width() or 1200
        self.canvas.configure(scrollregion=(0, 0, canvas_width, virtual_height))
        
    def get_visible_range(self):
        """Calculate which rows are currently visible"""
        if not self.filtered_images:
            return 0, 0
            
        canvas_height = self.canvas.winfo_height()
        
        # Get scroll position
        try:
            top = self.canvas.yview()[0]
            bottom = self.canvas.yview()[1]
        except:
            return 0, 0
            
        total_rows = (len(self.filtered_images) + self.columns - 1) // self.columns
        virtual_height = total_rows * self.row_height
        
        if virtual_height == 0:
            return 0, 0
            
        # Calculate visible rows with buffer
        buffer_rows = 2
        first_visible_row = max(0, int(top * total_rows) - buffer_rows)
        last_visible_row = min(total_rows, int(bottom * total_rows) + buffer_rows + 1)
        
        # Convert to item indices
        first_item = first_visible_row * self.columns
        last_item = min(len(self.filtered_images), last_visible_row * self.columns)
        
        return first_item, last_item
        
    def clear_visible_items(self):
        """Remove all visible item widgets"""
        for widget in list(self.visible_items.values()):
            widget.destroy()
        self.visible_items.clear()
        
    def render_visible(self):
        """Render only visible items"""
        if not self.filtered_images:
            return
            
        first_item, last_item = self.get_visible_range()
        
        # Update range indicator
        self.range_var.set(f"Viewing: {first_item+1}-{last_item} of {len(self.filtered_images)}")
        
        # Determine which items need to be added/removed
        needed_indices = set(range(first_item, last_item))
        current_indices = set(self.visible_items.keys())
        
        # Remove items no longer visible
        for idx in current_indices - needed_indices:
            if idx in self.visible_items:
                self.visible_items[idx].destroy()
                del self.visible_items[idx]
                
        # Add new visible items
        for idx in needed_indices - current_indices:
            if idx < len(self.filtered_images):
                self.create_item_widget(idx)
                
        # Update cache info
        self.cache_var.set(f"Cache: {len(self.thumbnail_cache)}/{self.cache_max_size}")
        
    def create_item_widget(self, idx):
        """Create a widget for a single item"""
        img_data = self.filtered_images[idx]
        
        row = idx // self.columns
        col = idx % self.columns
        
        x = 10 + col * (self.thumbnail_size[0] + 30)
        y = 10 + row * self.row_height
        
        # Create frame
        frame = tk.Frame(self.inner_frame, bg='#2d2d2d', width=self.thumbnail_size[0] + 20, 
                        height=self.row_height - 10)
        frame.place(x=x, y=y)
        frame.pack_propagate(False)
        
        # Image label with placeholder
        img_label = tk.Label(frame, image=self.placeholder, bg='#3c3c3c')
        img_label.pack(pady=(5, 2))
        
        # Filename label
        display_name = img_data['name']
        if len(display_name) > 14:
            display_name = display_name[:11] + "..."
            
        name_label = tk.Label(
            frame, 
            text=display_name, 
            bg='#2d2d2d', 
            fg='#cccccc',
            font=('Segoe UI', 7),
        )
        name_label.pack()
        
        # Store reference
        self.visible_items[idx] = frame
        frame.img_label = img_label
        frame.img_data = img_data
        
        # Bind events
        for widget in [frame, img_label, name_label]:
            widget.bind("<Button-1>", lambda e, d=img_data: self.show_image_info(d))
            widget.bind("<Button-3>", lambda e, d=img_data: self.copy_path(d))
            widget.bind("<Enter>", lambda e, f=frame: self.on_item_enter(f))
            widget.bind("<Leave>", lambda e, f=frame: self.on_item_leave(f))
            
        # Queue thumbnail loading
        self.queue_thumbnail_load(idx, img_label, img_data['full_path'])
        
    def on_item_enter(self, frame):
        frame.configure(bg='#404040')
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    child.configure(bg='#404040')
                except:
                    pass
                    
    def on_item_leave(self, frame):
        frame.configure(bg='#2d2d2d')
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    # Keep image label darker
                    if hasattr(child, 'image') and child.cget('image'):
                        child.configure(bg='#3c3c3c')
                    else:
                        child.configure(bg='#2d2d2d')
                except:
                    pass
                    
    def queue_thumbnail_load(self, idx, label, path):
        """Queue a thumbnail for loading"""
        if path in self.thumbnail_cache:
            # Already cached, apply immediately
            photo = self.thumbnail_cache[path]
            if label.winfo_exists():
                label.configure(image=photo)
                label.image = photo
        elif path not in self.loading_set:
            self.loading_set.add(path)
            self.load_queue.put((idx, label, path))
            
    def start_loader_thread(self):
        """Start background loader thread"""
        def loader():
            while True:
                try:
                    idx, label, path = self.load_queue.get(timeout=0.5)
                    
                    # Check if still needed
                    if idx not in self.visible_items:
                        self.loading_set.discard(path)
                        continue
                        
                    # Load thumbnail
                    photo = self.load_thumbnail(path)
                    
                    # Schedule UI update
                    self.root.after(0, lambda l=label, p=photo, pa=path: self.apply_thumbnail(l, p, pa))
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Loader error: {e}")
                    
        for _ in range(4):  # Multiple loader threads
            t = threading.Thread(target=loader, daemon=True)
            t.start()
            
    def load_thumbnail(self, path):
        """Load and create thumbnail"""
        try:
            img = Image.open(path)
            
            # Handle different image modes
            if img.mode == 'P':
                img = img.convert('RGBA')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
            
            # Create thumbnail
            img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Create a background for transparent images
            if img.mode == 'RGBA':
                background = Image.new('RGBA', img.size, (50, 50, 50, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None
            
    def apply_thumbnail(self, label, photo, path):
        """Apply loaded thumbnail to label"""
        self.loading_set.discard(path)
        
        if photo:
            # Add to cache
            self.thumbnail_cache[path] = photo
            
            # Manage cache size
            if len(self.thumbnail_cache) > self.cache_max_size:
                # Remove oldest entries (simple approach)
                keys_to_remove = list(self.thumbnail_cache.keys())[:50]
                for key in keys_to_remove:
                    if key in self.thumbnail_cache:
                        del self.thumbnail_cache[key]
                        
            # Apply to label if still exists
            try:
                if label.winfo_exists():
                    label.configure(image=photo)
                    label.image = photo
            except tk.TclError:
                pass
        else:
            # Show error placeholder
            try:
                if label.winfo_exists():
                    label.configure(image=self.error_placeholder)
            except tk.TclError:
                pass
                
    def show_image_info(self, img_data):
        """Show detailed image info popup"""
        info_window = tk.Toplevel(self.root)
        info_window.title(img_data['name'])
        info_window.geometry("700x650")
        info_window.configure(bg='#2b2b2b')
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Info frame
        info_frame = tk.Frame(info_window, bg='#2b2b2b', padx=10, pady=10)
        info_frame.pack(fill=tk.X)
        
        # File info
        tk.Label(
            info_frame, 
            text=f"📄 {img_data['name']}", 
            bg='#2b2b2b', fg='white',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w')
        
        tk.Label(
            info_frame, 
            text=f"📁 Folder: {img_data['folder']}", 
            bg='#2b2b2b', fg='#aaaaaa',
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(5, 0))
        
        # Path frame with copy buttons
        path_frame = tk.Frame(info_frame, bg='#2b2b2b')
        path_frame.pack(fill=tk.X, pady=10)
        
        path_entry = tk.Entry(path_frame, font=('Consolas', 9), width=65)
        path_entry.insert(0, img_data['full_path'])
        path_entry.configure(state='readonly')
        path_entry.pack(side=tk.LEFT)
        
        def copy_full():
            self.root.clipboard_clear()
            self.root.clipboard_append(img_data['full_path'])
            copy_btn.configure(text="✓")
            info_window.after(1000, lambda: copy_btn.configure(text="📋"))
            
        copy_btn = ttk.Button(path_frame, text="📋", width=3, command=copy_full)
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        def copy_rel():
            self.root.clipboard_clear()
            self.root.clipboard_append(img_data['rel_path'].replace('\\', '/'))
            rel_btn.configure(text="✓")
            info_window.after(1000, lambda: rel_btn.configure(text="Rel"))
            
        rel_btn = ttk.Button(path_frame, text="Rel", width=4, command=copy_rel)
        rel_btn.pack(side=tk.LEFT, padx=2)
        
        def copy_name():
            name_no_ext = os.path.splitext(img_data['name'])[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(name_no_ext)
            name_btn.configure(text="✓")
            info_window.after(1000, lambda: name_btn.configure(text="Name"))
            
        name_btn = ttk.Button(path_frame, text="Name", width=5, command=copy_name)
        name_btn.pack(side=tk.LEFT, padx=2)
        
        # Image preview frame
        preview_frame = tk.Frame(info_window, bg='#1e1e1e')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load and show image
        def load_preview():
            try:
                img = Image.open(img_data['full_path'])
                
                # Show image info
                info_text = f"📐 {img.size[0]} x {img.size[1]} | {img.mode}"
                tk.Label(
                    info_frame, 
                    text=info_text, 
                    bg='#2b2b2b', fg='#aaaaaa',
                    font=('Segoe UI', 10)
                ).pack(anchor='w')
                
                # Create preview
                preview_size = (550, 450)
                img_copy = img.copy()
                img_copy.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
                if img_copy.mode not in ('RGB', 'RGBA'):
                    img_copy = img_copy.convert('RGBA')
                    
                if img_copy.mode == 'RGBA':
                    checker = self.create_checkerboard(img_copy.size)
                    checker.paste(img_copy, mask=img_copy.split()[3])
                    img_copy = checker
                
                photo = ImageTk.PhotoImage(img_copy)
                
                img_label = tk.Label(preview_frame, image=photo, bg='#1e1e1e')
                img_label.image = photo
                img_label.pack(expand=True)
                
            except Exception as e:
                tk.Label(
                    preview_frame, 
                    text=f"❌ Error loading image:\n{str(e)}", 
                    bg='#1e1e1e', fg='#ff6666',
                    font=('Segoe UI', 12)
                ).pack(expand=True)
                
        # Load preview in background
        threading.Thread(target=lambda: self.root.after(0, load_preview), daemon=True).start()
        
        # Button frame
        btn_frame = tk.Frame(info_window, bg='#2b2b2b', pady=10)
        btn_frame.pack(fill=tk.X)
        
        def open_explorer():
            os.system(f'explorer /select,"{img_data["full_path"]}"')
            
        ttk.Button(btn_frame, text="📂 Show in Explorer", command=open_explorer).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Close", command=info_window.destroy).pack(side=tk.RIGHT, padx=10)
        
        # Close on Escape
        info_window.bind('<Escape>', lambda e: info_window.destroy())
        
    def create_checkerboard(self, size, square_size=10):
        """Create checkerboard pattern for transparent backgrounds"""
        checker = Image.new('RGB', size, (60, 60, 60))
        for y in range(0, size[1], square_size):
            for x in range(0, size[0], square_size):
                if (x // square_size + y // square_size) % 2:
                    for py in range(min(square_size, size[1] - y)):
                        for px in range(min(square_size, size[0] - x)):
                            checker.putpixel((x + px, y + py), (80, 80, 80))
        return checker
        
    def copy_path(self, img_data):
        """Quick copy path on right-click"""
        self.root.clipboard_clear()
        self.root.clipboard_append(img_data['full_path'])
        self.status_var.set(f"✓ Copied: {img_data['name']}")
        self.root.after(2000, lambda: self.status_var.set(
            f"Showing {len(self.filtered_images)} of {len(self.images)} images"
        ))


def main():
    # Change this path if needed
    base_path = r"C:\Users\mikeg\OneDrive\Documents\Paradox Interactive\Hearts of Iron IV\Rise-of-Nations\gfx\interface\goals"
    
    root = tk.Tk()
    
    app = VirtualImageBrowser(root, base_path)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 1400) // 2
    y = (root.winfo_screenheight() - 900) // 2
    root.geometry(f"1400x900+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()