from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4

APP_NAME = 'Project Spacing Board'
DEFAULT_COLUMNS = ['Road Name', 'Category', 'Arrangement', 'Spacing']
DEFAULT_ROWS = [
    {
        'id': 'sample-row',
        'values': {
            'Road Name': 'Marketing Site',
            'Category': 'Desktop',
            'Arrangement': 'Hero / Cards / Footer',
            'Spacing': '8 / 16 / 24 / 48',
        },
    }
]
SUPPORT_README_NAME = 'project-spacing-board.README.txt'

PALETTE = {
    'bg': '#060816',
    'panel': '#0f1630',
    'panel_alt': '#141d3c',
    'surface': '#1a244b',
    'surface_alt': '#101834',
    'text': '#edf2ff',
    'muted': '#9aa6d1',
    'accent': '#7aa2ff',
    'accent_alt': '#5d8dff',
    'danger': '#ff8ea1',
    'border': '#2c3869',
}


@dataclass
class BoardDocument:
    title: str = APP_NAME
    columns: list[str] = field(default_factory=lambda: DEFAULT_COLUMNS.copy())
    rows: list[dict[str, object]] = field(default_factory=lambda: normalize_rows(DEFAULT_COLUMNS, DEFAULT_ROWS))

    def to_dict(self) -> dict[str, object]:
        return {
            'title': self.title,
            'columns': self.columns,
            'rows': self.rows,
        }


@dataclass
class RowWidgets:
    text_widgets: dict[str, tk.Text]
    remove_button: ttk.Button


def normalize_rows(columns: list[str], rows: list[dict[str, object]] | None) -> list[dict[str, object]]:
    if not rows:
        return [create_row(columns)]

    normalized: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        values = row.get('values', {}) if isinstance(row, dict) else {}
        normalized_values = {column: str(values.get(column, '')) for column in columns}
        normalized.append(
            {
                'id': str(row.get('id', f'row-{index + 1}')) if isinstance(row, dict) else f'row-{index + 1}',
                'values': normalized_values,
            }
        )

    return normalized or [create_row(columns)]


def create_row(columns: list[str]) -> dict[str, object]:
    return {
        'id': uuid4().hex,
        'values': {column: '' for column in columns},
    }


def normalize_document(raw: dict[str, object] | None) -> BoardDocument:
    raw = raw or {}
    raw_columns = raw.get('columns', DEFAULT_COLUMNS)
    columns = [str(column).strip() or f'Column {index + 1}' for index, column in enumerate(raw_columns)]
    if not columns:
        columns = DEFAULT_COLUMNS.copy()

    rows = normalize_rows(columns, raw.get('rows') if isinstance(raw, dict) else DEFAULT_ROWS)
    title = str(raw.get('title', APP_NAME)).strip() or APP_NAME
    return BoardDocument(title=title, columns=columns, rows=rows)


class ProjectSpacingBoardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry('1380x900')
        self.root.minsize(1040, 700)
        self.root.configure(bg=PALETTE['bg'])

        self.current_path: Path | None = None
        self.document = normalize_document({'title': APP_NAME, 'columns': DEFAULT_COLUMNS, 'rows': DEFAULT_ROWS})
        self.column_vars: list[tk.StringVar] = []
        self.row_widgets: dict[str, RowWidgets] = {}

        self.title_var = tk.StringVar(value=self.document.title)
        self.file_status_var = tk.StringVar(value='Using an unsaved board.')
        self.pin_var = tk.BooleanVar(value=False)

        self._configure_styles()
        self._build_layout()
        self._bind_events()
        self.render_board()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('.', background=PALETTE['bg'], foreground=PALETTE['text'])
        style.configure('Shell.TFrame', background=PALETTE['bg'])
        style.configure('Panel.TFrame', background=PALETTE['panel'])
        style.configure('PanelAlt.TFrame', background=PALETTE['panel_alt'])
        style.configure('Surface.TFrame', background=PALETTE['surface'])
        style.configure(
            'HeroTitle.TLabel',
            background=PALETTE['panel'],
            foreground=PALETTE['text'],
            font=('Segoe UI', 22, 'bold'),
        )
        style.configure(
            'Eyebrow.TLabel',
            background=PALETTE['panel'],
            foreground=PALETTE['accent'],
            font=('Segoe UI', 9, 'bold'),
        )
        style.configure(
            'Body.TLabel',
            background=PALETTE['panel'],
            foreground=PALETTE['muted'],
            font=('Segoe UI', 10),
        )
        style.configure(
            'Muted.TLabel',
            background=PALETTE['panel_alt'],
            foreground=PALETTE['muted'],
            font=('Segoe UI', 9),
        )
        style.configure(
            'Toolbar.TLabel',
            background=PALETTE['panel_alt'],
            foreground=PALETTE['muted'],
            font=('Segoe UI', 9, 'bold'),
        )
        style.configure(
            'Primary.TButton',
            background=PALETTE['accent_alt'],
            foreground=PALETTE['text'],
            borderwidth=0,
            focusthickness=3,
            focuscolor=PALETTE['accent_alt'],
            padding=(14, 10),
        )
        style.map('Primary.TButton', background=[('active', PALETTE['accent'])])
        style.configure(
            'Ghost.TButton',
            background=PALETTE['surface'],
            foreground=PALETTE['text'],
            borderwidth=1,
            relief='solid',
            padding=(12, 9),
        )
        style.map('Ghost.TButton', background=[('active', PALETTE['surface_alt'])])
        style.configure(
            'Danger.TButton',
            background=PALETTE['surface_alt'],
            foreground=PALETTE['danger'],
            borderwidth=1,
            relief='solid',
            padding=(10, 8),
        )
        style.map('Danger.TButton', background=[('active', '#22192a')])
        style.configure(
            'Pin.TCheckbutton',
            background=PALETTE['surface'],
            foreground=PALETTE['text'],
            font=('Segoe UI', 10, 'bold'),
            padding=(10, 8),
        )
        style.map('Pin.TCheckbutton', background=[('active', PALETTE['surface'])])
        style.configure(
            'Board.Horizontal.TScrollbar',
            background=PALETTE['surface'],
            troughcolor=PALETTE['panel_alt'],
        )
        style.configure(
            'Board.Vertical.TScrollbar',
            background=PALETTE['surface'],
            troughcolor=PALETTE['panel_alt'],
        )

    def _build_layout(self) -> None:
        shell = ttk.Frame(self.root, style='Shell.TFrame', padding=24)
        shell.pack(fill='both', expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)

        self.hero = ttk.Frame(shell, style='Panel.TFrame', padding=24)
        self.hero.grid(row=0, column=0, sticky='ew')
        self.hero.columnconfigure(0, weight=1)
        self.hero.columnconfigure(1, weight=0)

        hero_copy = ttk.Frame(self.hero, style='Panel.TFrame')
        hero_copy.grid(row=0, column=0, sticky='nw')
        ttk.Label(hero_copy, text='LOCAL-FIRST PYTHON UTILITY', style='Eyebrow.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(hero_copy, text=APP_NAME, style='HeroTitle.TLabel').grid(row=1, column=0, sticky='w', pady=(8, 0))
        ttk.Label(
            hero_copy,
            text='Keep design-note JSON files beside each project, edit them quickly, pin the window to the front, and export starter support files right from the app.',
            style='Body.TLabel',
            wraplength=760,
            justify='left',
        ).grid(row=2, column=0, sticky='w', pady=(12, 0))

        hero_actions = ttk.Frame(self.hero, style='Panel.TFrame')
        hero_actions.grid(row=0, column=1, sticky='ne', padx=(24, 0))
        ttk.Button(hero_actions, text='New Board', style='Ghost.TButton', command=self.reset_document).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(hero_actions, text='Open JSON', style='Ghost.TButton', command=self.open_document).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(hero_actions, text='Save JSON', style='Primary.TButton', command=self.save_document).grid(row=0, column=2, padx=6, pady=6)
        ttk.Button(hero_actions, text='Generate Support Files', style='Ghost.TButton', command=self.generate_support_files).grid(row=1, column=0, columnspan=3, padx=6, pady=6, sticky='ew')

        toolbar = ttk.Frame(shell, style='PanelAlt.TFrame', padding=18)
        toolbar.grid(row=1, column=0, sticky='ew', pady=(20, 20))
        toolbar.columnconfigure(0, weight=1)
        toolbar.columnconfigure(1, weight=0)

        status_group = ttk.Frame(toolbar, style='PanelAlt.TFrame')
        status_group.grid(row=0, column=0, sticky='ew')
        status_group.columnconfigure(1, weight=1)
        ttk.Label(status_group, text='Board Title', style='Toolbar.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 12))
        self.title_entry = tk.Entry(
            status_group,
            textvariable=self.title_var,
            bg=PALETTE['surface_alt'],
            fg=PALETTE['text'],
            insertbackground=PALETTE['text'],
            relief='flat',
            highlightthickness=1,
            highlightbackground=PALETTE['border'],
            highlightcolor=PALETTE['accent'],
            font=('Segoe UI', 11),
        )
        self.title_entry.grid(row=0, column=1, sticky='ew', ipady=8)
        ttk.Label(status_group, textvariable=self.file_status_var, style='Muted.TLabel').grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))

        action_group = ttk.Frame(toolbar, style='PanelAlt.TFrame')
        action_group.grid(row=0, column=1, sticky='e', padx=(18, 0))
        ttk.Button(action_group, text='Add Column', style='Ghost.TButton', command=self.add_column).grid(row=0, column=0, padx=6)
        ttk.Button(action_group, text='Add Row', style='Ghost.TButton', command=self.add_row).grid(row=0, column=1, padx=6)
        ttk.Checkbutton(action_group, text='Pin to front', style='Pin.TCheckbutton', variable=self.pin_var, command=self.toggle_pin).grid(row=0, column=2, padx=6)

        board_panel = ttk.Frame(shell, style='Panel.TFrame', padding=16)
        board_panel.grid(row=2, column=0, sticky='nsew')
        board_panel.columnconfigure(0, weight=1)
        board_panel.rowconfigure(0, weight=1)

        self.board_canvas = tk.Canvas(
            board_panel,
            bg=PALETTE['panel'],
            highlightthickness=0,
            bd=0,
            relief='flat',
        )
        self.board_canvas.grid(row=0, column=0, sticky='nsew')

        v_scroll = ttk.Scrollbar(board_panel, orient='vertical', command=self.board_canvas.yview, style='Board.Vertical.TScrollbar')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(board_panel, orient='horizontal', command=self.board_canvas.xview, style='Board.Horizontal.TScrollbar')
        h_scroll.grid(row=1, column=0, sticky='ew')
        self.board_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.board_frame = ttk.Frame(self.board_canvas, style='Panel.TFrame')
        self.board_window = self.board_canvas.create_window((0, 0), window=self.board_frame, anchor='nw')
        self.board_frame.bind('<Configure>', self._on_board_frame_configure)
        self.board_canvas.bind('<Configure>', self._on_board_canvas_configure)

    def _bind_events(self) -> None:
        self.title_var.trace_add('write', self._on_title_changed)

    def _on_board_frame_configure(self, _event: tk.Event) -> None:
        self.board_canvas.configure(scrollregion=self.board_canvas.bbox('all'))

    def _on_board_canvas_configure(self, event: tk.Event) -> None:
        self.board_canvas.itemconfigure(self.board_window, width=max(event.width, self.board_frame.winfo_reqwidth()))

    def _on_title_changed(self, *_args: object) -> None:
        self.document.title = self.title_var.get().strip() or APP_NAME

    def reset_document(self) -> None:
        self.document = normalize_document({'title': APP_NAME, 'columns': DEFAULT_COLUMNS, 'rows': DEFAULT_ROWS})
        self.current_path = None
        self._update_file_status('Using an unsaved board.')
        self.title_var.set(self.document.title)
        self.render_board()

    def add_column(self) -> None:
        base_name = 'New Column'
        next_name = base_name
        counter = 1
        while next_name in self.document.columns:
            counter += 1
            next_name = f'{base_name} {counter}'

        self.document.columns.append(next_name)
        for row in self.document.rows:
            row['values'][next_name] = ''
        self.render_board()

    def remove_column(self, column_name: str) -> None:
        if len(self.document.columns) <= 1:
            messagebox.showinfo(APP_NAME, 'At least one column is required.')
            return

        self.document.columns = [column for column in self.document.columns if column != column_name]
        for row in self.document.rows:
            row['values'].pop(column_name, None)
        self.render_board()

    def rename_column(self, old_name: str, new_name: str) -> None:
        new_name = new_name.strip() or old_name
        if new_name == old_name:
            return
        if new_name in self.document.columns:
            messagebox.showwarning(APP_NAME, f'The column name “{new_name}” already exists.')
            self.render_board()
            return

        self.document.columns = [new_name if column == old_name else column for column in self.document.columns]
        for row in self.document.rows:
            row['values'][new_name] = row['values'].pop(old_name, '')
        self.render_board()

    def add_row(self) -> None:
        self._sync_widget_values_into_document()
        self.document.rows.append(create_row(self.document.columns))
        self.render_board()

    def remove_row(self, row_id: str) -> None:
        self._sync_widget_values_into_document()
        self.document.rows = [row for row in self.document.rows if row['id'] != row_id]
        if not self.document.rows:
            self.document.rows = [create_row(self.document.columns)]
        self.render_board()

    def open_document(self) -> None:
        path = filedialog.askopenfilename(
            title='Open board JSON',
            filetypes=[('JSON Files', '*.json')],
        )
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
            self.document = normalize_document(data)
            self.current_path = Path(path)
            self.title_var.set(self.document.title)
            self._update_file_status(f'Editing {self.current_path}')
            self.render_board()
        except Exception as error:  # noqa: BLE001
            messagebox.showerror(APP_NAME, f'Could not open JSON:\n\n{error}')

    def save_document(self) -> None:
        self._sync_widget_values_into_document()
        suggested_name = slugify(self.document.title) or 'project-spacing-board'
        path = filedialog.asksaveasfilename(
            title='Save board JSON',
            defaultextension='.json',
            initialfile=f'{suggested_name}.json',
            filetypes=[('JSON Files', '*.json')],
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as handle:
                json.dump(self.document.to_dict(), handle, indent=2)
                handle.write('\n')
            self.current_path = Path(path)
            self._update_file_status(f'Editing {self.current_path}')
        except Exception as error:  # noqa: BLE001
            messagebox.showerror(APP_NAME, f'Could not save JSON:\n\n{error}')

    def generate_support_files(self) -> None:
        self._sync_widget_values_into_document()
        directory = filedialog.askdirectory(title='Choose a folder for support files')
        if not directory:
            return

        target_dir = Path(directory)
        json_path = target_dir / f"{slugify(self.document.title) or 'project-spacing-board'}.json"
        readme_path = target_dir / SUPPORT_README_NAME

        try:
            with open(json_path, 'w', encoding='utf-8') as handle:
                json.dump(self.document.to_dict(), handle, indent=2)
                handle.write('\n')

            support_text = (
                f'{APP_NAME}\n\n'
                'These support files were generated by the packaged Python app.\n\n'
                f'- Board JSON: {json_path.name}\n'
                f'- Title: {self.document.title}\n'
                f'- Columns: {", ".join(self.document.columns)}\n\n'
                'You can keep this JSON beside your project files and reopen it in the app at any time.\n'
            )
            readme_path.write_text(support_text, encoding='utf-8')
            messagebox.showinfo(APP_NAME, f'Support files generated in:\n\n{target_dir}')
        except Exception as error:  # noqa: BLE001
            messagebox.showerror(APP_NAME, f'Could not generate support files:\n\n{error}')

    def toggle_pin(self) -> None:
        self.root.attributes('-topmost', self.pin_var.get())

    def _sync_widget_values_into_document(self) -> None:
        synced_rows: list[dict[str, object]] = []
        for row in self.document.rows:
            widgets = self.row_widgets.get(row['id'])
            values: dict[str, str] = {}
            for column in self.document.columns:
                if widgets and column in widgets.text_widgets:
                    widget = widgets.text_widgets[column]
                    values[column] = widget.get('1.0', 'end-1c')
                else:
                    values[column] = str(row['values'].get(column, ''))
            synced_rows.append({'id': row['id'], 'values': values})
        self.document.rows = synced_rows
        self.document.title = self.title_var.get().strip() or APP_NAME

    def _update_file_status(self, value: str | None = None) -> None:
        if value is not None:
            self.file_status_var.set(value)
        else:
            self.file_status_var.set(f'Editing {self.current_path}' if self.current_path else 'Using an unsaved board.')

    def render_board(self) -> None:
        self._sync_widget_values_into_document()
        self.column_vars.clear()
        self.row_widgets.clear()

        for child in self.board_frame.winfo_children():
            child.destroy()

        for column_index, column_name in enumerate(self.document.columns):
            self.board_frame.grid_columnconfigure(column_index, weight=1, uniform='board')
            header_container = tk.Frame(self.board_frame, bg=PALETTE['panel'])
            header_container.grid(row=0, column=column_index, sticky='ew', padx=8, pady=(0, 12))

            column_var = tk.StringVar(value=column_name)
            column_entry = tk.Entry(
                header_container,
                textvariable=column_var,
                bg=PALETTE['surface'],
                fg=PALETTE['text'],
                insertbackground=PALETTE['text'],
                relief='flat',
                highlightthickness=1,
                highlightbackground=PALETTE['border'],
                highlightcolor=PALETTE['accent'],
                font=('Segoe UI', 11, 'bold'),
            )
            column_entry.pack(side='left', fill='x', expand=True, ipady=8)
            column_entry.bind('<FocusOut>', lambda event, old=column_name, var=column_var: self.rename_column(old, var.get()))
            self.column_vars.append(column_var)

            remove_button = ttk.Button(
                header_container,
                text='Remove',
                style='Danger.TButton',
                command=lambda target=column_name: self.remove_column(target),
            )
            remove_button.pack(side='left', padx=(8, 0))

        actions_header = ttk.Frame(self.board_frame, style='Panel.TFrame')
        actions_header.grid(row=0, column=len(self.document.columns), sticky='w', padx=8, pady=(0, 12))

        for row_index, row in enumerate(self.document.rows, start=1):
            text_widgets: dict[str, tk.Text] = {}
            for column_index, column_name in enumerate(self.document.columns):
                card = tk.Frame(
                    self.board_frame,
                    bg=PALETTE['surface_alt'],
                    highlightthickness=1,
                    highlightbackground=PALETTE['border'],
                    padx=8,
                    pady=8,
                )
                card.grid(row=row_index, column=column_index, sticky='nsew', padx=8, pady=8)

                text = tk.Text(
                    card,
                    height=6,
                    width=26,
                    wrap='word',
                    bg=PALETTE['surface_alt'],
                    fg=PALETTE['text'],
                    insertbackground=PALETTE['text'],
                    relief='flat',
                    highlightthickness=0,
                    borderwidth=0,
                    font=('Segoe UI', 10),
                    padx=6,
                    pady=6,
                )
                text.insert('1.0', str(row['values'].get(column_name, '')))
                text.pack(fill='both', expand=True)
                text_widgets[column_name] = text

            button_wrap = ttk.Frame(self.board_frame, style='Panel.TFrame')
            button_wrap.grid(row=row_index, column=len(self.document.columns), sticky='n', padx=(8, 0), pady=8)
            remove_button = ttk.Button(
                button_wrap,
                text='Remove Row',
                style='Danger.TButton',
                command=lambda target=row['id']: self.remove_row(target),
            )
            remove_button.pack()
            self.row_widgets[row['id']] = RowWidgets(text_widgets=text_widgets, remove_button=remove_button)

        self._update_file_status()
        self.board_canvas.update_idletasks()
        self.board_canvas.configure(scrollregion=self.board_canvas.bbox('all'))


def slugify(value: str) -> str:
    slug = re.sub(r'[^A-Za-z0-9._-]+', '-', value.strip()).strip('-_.')
    return slug.lower()


def main() -> None:
    root = tk.Tk()
    app = ProjectSpacingBoardApp(root)
    root.mainloop()


if __name__ == '__main__':
    if '--build-windows' in sys.argv:
        subprocess.run([sys.executable, 'build_windows.py'], check=True)
    else:
        main()
