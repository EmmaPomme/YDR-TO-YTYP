import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import re
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class XMLViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("GTA5 YDR → YTYP Tool")
        # Set window size and center it
        window_width = 1350
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.configure(bg="#e6eaf3")
        
        self.settings = load_settings()

        settings = load_settings()
        self.only_bounds_var = tk.BooleanVar(value=settings.get("only_boxmax", False))
        self.edit_var = tk.BooleanVar(value=settings.get("edit_enabled", False))
        self.default_phys = settings.get("phys_dict", "")
        self.default_tex = settings.get("tex_dict", "")
        self.default_lod = settings.get("lod_dist", "9998")

        self.create_widgets()

    def create_widgets(self):
        menu_frame = tk.Frame(self.root, bg="#e6eaf3", height=24)
        menu_frame.pack(fill='x', side='top')

        import_button = tk.Button(menu_frame, text="Import", command=self.import_ydr, bg="#e6eaf3", fg="black",
                                  relief="flat", borderwidth=1, padx=10, pady=0)
        import_button.pack(side='left', padx=2, pady=0)
        import_button.bind("<Enter>", lambda e: import_button.config(bg="#ffe797"))
        import_button.bind("<Leave>", lambda e: import_button.config(bg="#e6eaf3"))

        copy_button = tk.Button(menu_frame, text="Copy", command=self.copy_to_clipboard, bg="#e6eaf3", fg="black",
                                relief="flat", borderwidth=1, padx=10, pady=0)
        copy_button.pack(side='left', padx=2, pady=0)
        copy_button.bind("<Enter>", lambda e: copy_button.config(bg="#ffe797"))
        copy_button.bind("<Leave>", lambda e: copy_button.config(bg="#e6eaf3"))
        
                # === Options Button ===
        options_button = tk.Button(menu_frame, text="Options", command=self.open_options_window,
                                   bg="#e6eaf3", fg="black", relief="flat", borderwidth=1,
                                   padx=2, pady=0)
        options_button.pack(side='left', padx=10)
        options_button.bind("<Enter>", lambda e: options_button.config(bg="#ffe797"))
        options_button.bind("<Leave>", lambda e: options_button.config(bg="#e6eaf3"))

        edit_check = tk.Checkbutton(menu_frame, text="Edit", variable=self.edit_var, command=self.toggle_edit, bg="#e6eaf3")
        edit_check.pack(side='left', padx=5)

        bounds_check = tk.Checkbutton(menu_frame, text="Only BoxMax, BoxMin, Center, Radius", variable=self.only_bounds_var,
                                      command=self.refresh_output, bg="#e6eaf3")
        bounds_check.pack(side='left', padx=10)
        
        # separator
        tk.Frame(menu_frame, height=20, width=2, bg="#999999").pack(side='left', padx=8)

        # physics dictionary edit
        tk.Label(menu_frame, text="Edit physicsDictionary:", bg="#e6eaf3").pack(side='left')
        self.phys_entry = tk.Entry(menu_frame, width=12)
        self.phys_entry.pack(side='left', padx=2)
        self.phys_entry.insert(0, self.default_phys)

        phys_btn = tk.Button(menu_frame, text="Apply", command=self.refresh_output, bg="#e6eaf3", fg="black",
                             relief="flat", borderwidth=1, padx=10, pady=2)
        phys_btn.pack(side='left', padx=3)
        phys_btn.bind("<Enter>", lambda e: phys_btn.config(bg="#ffe797"))
        phys_btn.bind("<Leave>", lambda e: phys_btn.config(bg="#e6eaf3"))

        # separator
        tk.Frame(menu_frame, height=20, width=2, bg="#999999").pack(side='left', padx=8)

        # texture dictionary edit
        tk.Label(menu_frame, text="Edit textureDictionary:", bg="#e6eaf3").pack(side='left')
        self.text_entry = tk.Entry(menu_frame, width=12)
        self.text_entry.pack(side='left', padx=2)
        self.text_entry.insert(0, self.default_tex)

        text_btn = tk.Button(menu_frame, text="Apply", command=self.refresh_output, bg="#e6eaf3", fg="black",
                             relief="flat", borderwidth=1, padx=10, pady=2)
        text_btn.pack(side='left', padx=3)
        text_btn.bind("<Enter>", lambda e: text_btn.config(bg="#ffe797"))
        text_btn.bind("<Leave>", lambda e: text_btn.config(bg="#e6eaf3"))
        
        # separator
        tk.Frame(menu_frame, height=20, width=2, bg="#999999").pack(side='left', padx=8)
        
        # lodDist edit
        tk.Label(menu_frame, text="Edit lodDist:", bg="#e6eaf3").pack(side='left')
        self.lod_entry = tk.Entry(menu_frame, width=8)
        self.lod_entry.pack(side='left', padx=2)
        self.lod_entry.insert(0, self.default_lod)

        lod_btn = tk.Button(menu_frame, text="Apply", command=self.refresh_output, bg="#e6eaf3", fg="black",
                    relief="flat", borderwidth=1, padx=10, pady=2)
        lod_btn.pack(side='left', padx=3)
        lod_btn.bind("<Enter>", lambda e: lod_btn.config(bg="#ffe797"))
        lod_btn.bind("<Leave>", lambda e: lod_btn.config(bg="#e6eaf3"))

        text_frame = tk.Frame(self.root)
        text_frame.pack(fill='both', expand=True)

        self.scrollbar = tk.Scrollbar(text_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.line_numbers = tk.Text(text_frame, width=5, bg="#f0f0f0", fg="gray", font=("Courier", 10), state='disabled')
        self.line_numbers.pack(side='left', fill='y')

        self.output_box = tk.Text(text_frame, wrap='none', bg="white", fg="black", font=("Courier", 10))
        self.output_box.pack(side='left', fill='both', expand=True)

        self.output_box.config(yscrollcommand=self.sync_scroll)
        self.line_numbers.config(yscrollcommand=self.sync_scroll)
        self.scrollbar.config(command=self.sync_scroll)

        self.output_box.bind("<KeyRelease>", self.update_line_numbers)

    def sync_scroll(self, *args):
        self.output_box.yview_moveto(args[0])
        self.line_numbers.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def import_ydr(self):
        self.last_file_paths = filedialog.askopenfilenames(filetypes=[("XML files", "*.xml")])
        if self.last_file_paths:
            self.generate_output_from_files(self.last_file_paths)

    def refresh_output(self):
        if hasattr(self, 'last_file_paths'):
            self.generate_output_from_files(self.last_file_paths)

    def toggle_edit(self):
        self.output_box.config(state='normal' if self.edit_var.get() else 'disabled')

    def copy_to_clipboard(self):
        content = self.output_box.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)
        total_lines = int(self.output_box.index('end-1c').split('.')[0])
        for i in range(1, total_lines + 1):
            self.line_numbers.insert(tk.END, f"{i:>3}\n")
        self.line_numbers.config(state='disabled')

    def generate_output_from_files(self, file_paths):
        def fmt(v): return "{:.6f}".format(float(v))
        blocks = []

        for file_path in file_paths:
            try:
                tree = ET.parse(file_path)
                root_xml = tree.getroot()

                name = root_xml.findtext('Name')
                bs_center = root_xml.find('BoundingSphereCenter')
                bs_radius = root_xml.find('BoundingSphereRadius')
                bb_min = root_xml.find('BoundingBoxMin')
                bb_max = root_xml.find('BoundingBoxMax')

                tex = self.text_entry.get() or name.split('_')[0]
                phys = self.phys_entry.get() or name

                if self.only_bounds_var.get():
                    item_block = f"""<!-- {name} -->
<bbMin x="{fmt(bb_min.get('x'))}" y="{fmt(bb_min.get('y'))}" z="{fmt(bb_min.get('z'))}" />
<bbMax x="{fmt(bb_max.get('x'))}" y="{fmt(bb_max.get('y'))}" z="{fmt(bb_max.get('z'))}" />
<bsCentre x="{fmt(bs_center.get('x'))}" y="{fmt(bs_center.get('y'))}" z="{fmt(bs_center.get('z'))}" />
<bsRadius value="{fmt(bs_radius.get('value'))}" />"""
                else:
                    item_block = f"""<Item type="CBaseArchetypeDef">
  <lodDist value="{self.lod_entry.get()}" />
  <flags value="32" />
  <specialAttribute value="0" />
  <bbMin x="{fmt(bb_min.get('x'))}" y="{fmt(bb_min.get('y'))}" z="{fmt(bb_min.get('z'))}" />
  <bbMax x="{fmt(bb_max.get('x'))}" y="{fmt(bb_max.get('y'))}" z="{fmt(bb_max.get('z'))}" />
  <bsCentre x="{fmt(bs_center.get('x'))}" y="{fmt(bs_center.get('y'))}" z="{fmt(bs_center.get('z'))}" />
  <bsRadius value="{fmt(bs_radius.get('value'))}" />
  <hdTextureDist value="60" />
  <name>{name}</name>
  <textureDictionary>{tex}</textureDictionary>
  <clipDictionary />
  <drawableDictionary />
  <physicsDictionary>{phys}</physicsDictionary>
  <assetType>ASSET_TYPE_DRAWABLE</assetType>
  <assetName>{name}</assetName>
  <extensions />
</Item>"""
                blocks.append(item_block)

            except Exception as e:
                blocks.append(f"<!-- Error parsing {file_path}: {e} -->")

        final_text = "\n".join(blocks)
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert("1.0", final_text)
        self.apply_syntax_highlighting()
        if not self.edit_var.get():
            self.output_box.config(state='disabled')
        self.update_line_numbers()

    def apply_syntax_highlighting(self):
        self.output_box.tag_config("tag", foreground="blue")
        self.output_box.tag_config("attr", foreground="red")
        self.output_box.tag_config("val", foreground="purple")
        self.output_box.tag_config("comment", foreground="green")

        content = self.output_box.get("1.0", tk.END)

        for match in re.finditer(r'(<!--.*?-->)', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.output_box.tag_add("comment", start, end)

        for match in re.finditer(r'(</?\w+)', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.output_box.tag_add("tag", start, end)

        for match in re.finditer(r'(\w+)=', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.output_box.tag_add("attr", start, end)

        for match in re.finditer(r'".*?"', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.output_box.tag_add("val", start, end)

    def open_options_window(self):
        options_win = tk.Toplevel(self.root)
        options_win.title("Default Preferences")
        # Set and center options window
        opt_width = 300
        opt_height = 300
        screen_width = options_win.winfo_screenwidth()
        screen_height = options_win.winfo_screenheight()
        x = (screen_width // 2) - (opt_width // 2)
        y = (screen_height // 2) - (opt_height // 2)
        options_win.geometry(f"{opt_width}x{opt_height}+{x}+{y}")
    
        options_win.configure(bg="#e6eaf3")

        edit_default_var = tk.BooleanVar(value=self.edit_var.get())
        tk.Checkbutton(options_win, text="Enable Edit by default", variable=edit_default_var, bg="#e6eaf3").pack(anchor='w', pady=5, padx=10)

        bounds_default_var = tk.BooleanVar(value=self.only_bounds_var.get())
        tk.Checkbutton(options_win, text="Enable 'Only BoxMax...' by default", variable=bounds_default_var, bg="#e6eaf3").pack(anchor='w', pady=5, padx=10)

        tk.Label(options_win, text="Default physicsDictionary:", bg="#e6eaf3").pack(anchor='w', pady=(10, 0), padx=10)
        default_phys_entry = tk.Entry(options_win)
        default_phys_entry.insert(0, self.phys_entry.get())
        default_phys_entry.pack(fill='x', padx=10)

        tk.Label(options_win, text="Default textureDictionary:", bg="#e6eaf3").pack(anchor='w', pady=(10, 0), padx=10)
        default_text_entry = tk.Entry(options_win)
        default_text_entry.insert(0, self.text_entry.get())
        default_text_entry.pack(fill='x', padx=10)
        
        tk.Label(options_win, text="Default lodDist:", bg="#e6eaf3").pack(anchor='w', pady=(10, 0), padx=10)
        lod_entry = tk.Entry(options_win)
        lod_entry.insert(0, str(self.settings.get("lod_dist", "9998")))
        lod_entry.pack(fill='x', padx=10)

        def apply_defaults():
            # 🟢 Get values first
            edit_value = edit_default_var.get()
            bounds_value = bounds_default_var.get()
            phys_value = default_phys_entry.get()
            text_value = default_text_entry.get()
            lod_value = lod_entry.get()

            # 🟢 Save them
            save_settings({
            "edit_enabled": edit_value,
            "only_boxmax": bounds_value,
            "phys_dict": phys_value,
            "tex_dict": text_value,
            "lod_dist": lod_value
        })

            # 🟢 Apply to main window
            self.edit_var.set(edit_value)
            self.only_bounds_var.set(bounds_value)
            self.text_entry.delete(0, tk.END)
            self.text_entry.insert(0, text_value)
            self.phys_entry.delete(0, tk.END)
            self.phys_entry.insert(0, phys_value)
            self.lod_entry.delete(0, tk.END)
            self.lod_entry.insert(0, lod_value)

            self.toggle_edit()
            self.refresh_output()
            options_win.destroy()
            

        tk.Button(options_win, text="Apply", command=apply_defaults, bg="#e6eaf3", relief="flat").pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLViewer(root)
    root.mainloop()
