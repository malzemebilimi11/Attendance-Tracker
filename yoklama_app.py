import datetime
import json
import os
import time
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

DATA_FILE = "dinamik_yoklama_verileri.json"
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
COLOR_PALETTE = [
    ("#0b8043", "Yeşil"),
    ("#5e35b1", "Mor"),
    ("#d8561b", "Turuncu"),
    ("#0d3b66", "Lacivert"),
    ("#d81b60", "Pembe"),
    ("#00695c", "Turkuaz"),
    ("#9e9d24", "Zeytin"),
    ("#2383e2", "Mavi"),
]

DEFAULT_STATE = {
    "startDate": "2026-10-12",
    "totalWeeks": 14,
    "courses": {
        "451": {"name": "METE 451", "color": "#0b8043"},
        "301": {"name": "METE 301", "color": "#5e35b1"},
        "401": {"name": "METE 401", "color": "#d8561b"},
        "453": {"name": "METE 453", "color": "#0d3b66"},
        "211": {"name": "ENG 211", "color": "#d81b60"},
        "470": {"name": "METE 470", "color": "#00695c"},
        "414": {"name": "METE 414", "color": "#9e9d24"},
    },
    "weeklyTemplate": {
        "0": [
            {"id": "451-1", "label": "451-1", "courseKey": "451"},
            {"id": "451-2", "label": "451-2", "courseKey": "451"},
        ],
        "1": [
            {"id": "301-tue", "label": "301", "courseKey": "301"},
            {"id": "401-tue", "label": "401", "courseKey": "401"},
        ],
        "2": [{"id": "451-wed", "label": "451", "courseKey": "451"}],
        "3": [
            {"id": "301-thu", "label": "301", "courseKey": "301"},
            {"id": "453-thu", "label": "453", "courseKey": "453"},
            {"id": "211-thu", "label": "211", "courseKey": "211"},
        ],
        "4": [
            {"id": "470-fri", "label": "470", "courseKey": "470"},
            {"id": "414-fri", "label": "414", "courseKey": "414"},
        ],
        "5": [],
        "6": [],
    },
    "attendance": {
        "w0_d0_451-1": "present",
        "w0_d0_451-2": "present",
        "w0_d1_401-tue": "present",
        "w0_d2_451-wed": "present",
        "w0_d3_301-thu": "present",
        "w0_d3_453-thu": "present",
        "w0_d3_211-thu": "present",
    },
}


class ScheduleEditorModal(ctk.CTkToplevel):

  def __init__(self, parent):
    super().__init__(parent)
    self.parent = parent
    self.title("⚙️ Ders Programını Düzenle")
    self.geometry("860x680")
    self.configure(fg_color="#ffffff")
    self.grab_set()

    self.scroll = ctk.CTkScrollableFrame(self, fg_color="#ffffff")
    self.scroll.pack(fill="both", expand=True, padx=15, pady=15)

    self.render_editor()

  def render_editor(self):
    for w in self.scroll.winfo_children():
      w.destroy()

    # 1. Dönem Ayarları
    sec1 = ctk.CTkFrame(
        self.scroll,
        fg_color="#fbfbfa",
        corner_radius=8,
        border_width=1,
        border_color="#e9e9e7",
    )
    sec1.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(
        sec1,
        text="1. Dönem Ayarları",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 5))

    row1 = ctk.CTkFrame(sec1, fg_color="transparent")
    row1.pack(fill="x", padx=12, pady=(0, 10))

    ctk.CTkLabel(row1, text="Başlangıç (YYYY-AA-GG):").pack(
        side="left", padx=(0, 5)
    )
    self.date_entry = ctk.CTkEntry(row1, width=120)
    self.date_entry.insert(0, self.parent.state["startDate"])
    self.date_entry.pack(side="left", padx=5)

    ctk.CTkLabel(row1, text="Hafta Sayısı:").pack(side="left", padx=(15, 5))
    self.weeks_entry = ctk.CTkEntry(row1, width=60)
    self.weeks_entry.insert(0, str(self.parent.state["totalWeeks"]))
    self.weeks_entry.pack(side="left", padx=5)

    ctk.CTkButton(
        row1,
        text="Kaydet",
        width=80,
        command=self.save_semester_settings,
    ).pack(side="left", padx=10)
    ctk.CTkButton(
        row1,
        text="🗑️ Tüm Programı Sıfırla",
        fg_color="#eb5757",
        hover_color="#c94444",
        command=self.clear_all,
    ).pack(side="right")

    # 2. Ders Ekle / Çıkar
    sec2 = ctk.CTkFrame(
        self.scroll,
        fg_color="#fbfbfa",
        corner_radius=8,
        border_width=1,
        border_color="#e9e9e7",
    )
    sec2.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(
        sec2,
        text="2. Ana Dersleri Tanımla",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 5))

    row2 = ctk.CTkFrame(sec2, fg_color="transparent")
    row2.pack(fill="x", padx=12, pady=5)

    self.c_name_entry = ctk.CTkEntry(
        row2, placeholder_text="Ders Adı (Örn: METE 451)", width=200
    )
    self.c_name_entry.pack(side="left", padx=(0, 8))

    self.color_map = {name: hex_c for hex_c, name in COLOR_PALETTE}
    self.c_color_cb = ctk.CTkOptionMenu(
        row2, values=list(self.color_map.keys()), width=110
    )
    self.c_color_cb.pack(side="left", padx=5)

    ctk.CTkButton(
        row2,
        text="+ Ders Ekle",
        fg_color="#0b8043",
        command=self.add_course,
    ).pack(side="left", padx=8)

    tags_frame = ctk.CTkFrame(sec2, fg_color="transparent")
    tags_frame.pack(fill="x", padx=12, pady=(5, 12))

    for k, c in self.parent.state["courses"].items():
      tag = ctk.CTkFrame(
          tags_frame,
          fg_color="#ffffff",
          border_width=1,
          border_color="#e9e9e7",
          corner_radius=6,
      )
      tag.pack(side="left", padx=4, pady=4)
      ctk.CTkLabel(
          tag,
          text=c["name"],
          text_color=c["color"],
          font=ctk.CTkFont(size=12, weight="bold"),
      ).pack(side="left", padx=(8, 4), pady=4)
      ctk.CTkButton(
          tag,
          text="✕",
          width=20,
          height=20,
          fg_color="transparent",
          text_color="#b72b2b",
          hover_color="#fdebec",
          command=lambda ck=k: self.delete_course(ck),
      ).pack(side="left", padx=(0, 4))

    # 3. Haftalık Günlere Yoklama Ekle
    sec3 = ctk.CTkFrame(
        self.scroll,
        fg_color="#fbfbfa",
        corner_radius=8,
        border_width=1,
        border_color="#e9e9e7",
    )
    sec3.pack(fill="x", pady=8, padx=5)
    ctk.CTkLabel(
        sec3,
        text="3. Haftalık Günlere Yoklama Kartı Ekle",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=12, pady=(10, 5))

    row3 = ctk.CTkFrame(sec3, fg_color="transparent")
    row3.pack(fill="x", padx=12, pady=5)

    self.day_cb = ctk.CTkOptionMenu(row3, values=DAY_NAMES, width=100)
    self.day_cb.pack(side="left", padx=(0, 8))

    self.course_names_map = {
        c["name"]: k for k, c in self.parent.state["courses"].items()
    }
    course_vals = (
        list(self.course_names_map.keys())
        if self.course_names_map
        else ["Önce Ders Ekleyin"]
    )
    self.slot_course_cb = ctk.CTkOptionMenu(row3, values=course_vals, width=150)
    self.slot_course_cb.pack(side="left", padx=5)

    self.slot_label_entry = ctk.CTkEntry(
        row3, placeholder_text="Kart Etiketi (Örn: 451-1)", width=180
    )
    self.slot_label_entry.pack(side="left", padx=8)

    ctk.CTkButton(
        row3, text="+ Güne Ekle", command=self.add_slot
    ).pack(side="left", padx=5)

    # Günlerin Listesi
    days_grid = ctk.CTkFrame(sec3, fg_color="transparent")
    days_grid.pack(fill="x", padx=12, pady=10)

    for d in range(7):
      days_grid.grid_columnconfigure(d, weight=1, uniform="ed_col")
      d_box = ctk.CTkFrame(
          days_grid,
          fg_color="#ffffff",
          border_width=1,
          border_color="#e9e9e7",
          corner_radius=6,
      )
      d_box.grid(row=0, column=d, padx=3, pady=3, sticky="nsew")
      ctk.CTkLabel(
          d_box,
          text=DAY_NAMES[d],
          font=ctk.CTkFont(size=12, weight="bold"),
          text_color="#787774",
      ).pack(pady=4)

      slots = self.parent.state["weeklyTemplate"].get(str(d), [])
      for idx, s in enumerate(slots):
        item = ctk.CTkFrame(d_box, fg_color="#f7f6f3", corner_radius=4)
        item.pack(fill="x", padx=4, pady=2)
        ctk.CTkLabel(
            item, text=s["label"], font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            item,
            text="✕",
            width=18,
            height=18,
            fg_color="transparent",
            text_color="#b72b2b",
            command=lambda day=str(d), i=idx: self.remove_slot(day, i),
        ).pack(side="right", padx=2)

  def save_semester_settings(self):
    try:
      datetime.date.fromisoformat(self.date_entry.get().strip())
      w = int(self.weeks_entry.get().strip())
      if not (1 <= w <= 52):
        raise ValueError
      self.parent.state["startDate"] = self.date_entry.get().strip()
      self.parent.state["totalWeeks"] = w
      self.parent.save_data()
      self.parent.render_all()
      messagebox.showinfo("Başarılı", "Dönem ayarları güncellendi!")
    except:
      messagebox.showerror(
          "Hata", "Tarih YYYY-AA-GG formatında, hafta 1-52 arasında olmalı!"
      )

  def add_course(self):
    name = self.c_name_entry.get().strip()
    if not name:
      return
    color = self.color_map.get(self.c_color_cb.get(), "#2383e2")
    key = f"c_{int(time.time()*1000)}"
    self.parent.state["courses"][key] = {"name": name, "color": color}
    self.parent.save_data()
    self.render_editor()
    self.parent.render_all()

  def delete_course(self, ck):
    del self.parent.state["courses"][ck]
    for d in range(7):
      day_str = str(d)
      self.parent.state["weeklyTemplate"][day_str] = [
          s
          for s in self.parent.state["weeklyTemplate"].get(day_str, [])
          if s["courseKey"] != ck
      ]
    self.parent.save_data()
    self.render_editor()
    self.parent.render_all()

  def add_slot(self):
    if not self.course_names_map:
      return
    day_idx = str(DAY_NAMES.index(self.day_cb.get()))
    c_name = self.slot_course_cb.get()
    ck = self.course_names_map.get(c_name)
    if not ck:
      return
    label = self.slot_label_entry.get().strip() or c_name
    slot_id = f"s_{int(time.time()*1000)}"
    self.parent.state["weeklyTemplate"].setdefault(day_idx, []).append(
        {"id": slot_id, "label": label, "courseKey": ck}
    )
    self.parent.save_data()
    self.render_editor()
    self.parent.render_all()

  def remove_slot(self, day_str, idx):
    self.parent.state["weeklyTemplate"][day_str].pop(idx)
    self.parent.save_data()
    self.render_editor()
    self.parent.render_all()

  def clear_all(self):
    if messagebox.askyesno(
        "Sıfırla", "Tüm dersler ve program silinecek. Emin misin?"
    ):
      self.parent.state["courses"] = {}
      self.parent.state["weeklyTemplate"] = {str(i): [] for i in range(7)}
      self.parent.state["attendance"] = {}
      self.parent.save_data()
      self.render_editor()
      self.parent.render_all()


class AttendanceApp(ctk.CTk):

  def __init__(self):
    super().__init__()
    self.title("📅 Dinamik Ders Yoklama Takip Sistemi")
    self.geometry("1240x820")
    self.configure(fg_color="#ffffff")

    self.current_week = 0
    self.is_expanded = False
    self.state = self.load_data()

    self.setup_ui()
    self.render_all()

  def load_data(self):
    if os.path.exists(DATA_FILE):
      try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
          return json.load(f)
      except:
        pass
    self.save_data(DEFAULT_STATE)
    return json.loads(json.dumps(DEFAULT_STATE))

  def save_data(self, data=None):
    if data is None:
      data = self.state
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

  def setup_ui(self):
    self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.top_frame.pack(fill="x", padx=20, pady=(15, 5))

    ctk.CTkLabel(
        self.top_frame,
        text="📅 CALENDAR VIEW — ATTENDANCE",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#37352f",
    ).pack(side="left")

    self.toggle_btn = ctk.CTkButton(
        self.top_frame,
        text="🔍 Tüm Dönemi Göster",
        command=self.toggle_view,
        fg_color="#2383e2",
        height=32,
    )
    self.toggle_btn.pack(side="right", padx=5)

    ctk.CTkButton(
        self.top_frame,
        text="⚙️ Ders Programını Düzenle",
        command=lambda: ScheduleEditorModal(self),
        fg_color="#0b8043",
        hover_color="#096936",
        height=32,
    ).pack(side="right", padx=5)

    self.stats_frame = ctk.CTkFrame(
        self,
        fg_color="#fbfbfa",
        corner_radius=10,
        border_width=1,
        border_color="#e9e9e7",
    )
    self.stats_frame.pack(fill="x", padx=20, pady=10)

    self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.nav_frame.pack(fill="x", padx=20, pady=5)

    self.period_label = ctk.CTkLabel(
        self.nav_frame,
        text="",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#37352f",
    )
    self.period_label.pack(side="left")

    nav_btns = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
    nav_btns.pack(side="right")

    ctk.CTkButton(
        nav_btns,
        text="❮ Önceki Hafta",
        width=110,
        height=28,
        fg_color="#fff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        command=lambda: self.change_week(-1),
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        nav_btns,
        text="1. Hafta",
        width=90,
        height=28,
        fg_color="#fff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        command=self.go_first_week,
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        nav_btns,
        text="Sonraki Hafta ❯",
        width=110,
        height=28,
        fg_color="#fff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        command=lambda: self.change_week(1),
    ).pack(side="left", padx=3)

    self.cal_scroll = ctk.CTkScrollableFrame(
        self, fg_color="#ffffff", corner_radius=0
    )
    self.cal_scroll.pack(fill="both", expand=True, padx=15, pady=5)

  def set_status(self, key, status):
    if self.state["attendance"].get(key) == status:
      del self.state["attendance"][key]
    else:
      self.state["attendance"][key] = status
    self.save_data()
    self.render_all()

  def render_stats(self):
    for w in self.stats_frame.winfo_children():
      w.destroy()

    courses = self.state["courses"]
    if not courses:
      ctk.CTkLabel(
          self.stats_frame,
          text="Henüz ders yok. Sağ üstten '⚙️ Ders Programını Düzenle' butonuna tıklayın.",
          text_color="#787774",
      ).pack(pady=15)
      return

    stats = {
        k: {"present": 0, "absent": 0, "cancelled": 0} for k in courses.keys()
    }
    for w in range(self.state["totalWeeks"]):
      for d in range(7):
        for cls in self.state["weeklyTemplate"].get(str(d), []):
          ck = cls["courseKey"]
          if ck not in stats:
            continue
          st = self.state["attendance"].get(f"w{w}_d{d}_{cls['id']}")
          if st == "present":
            stats[ck]["present"] += 1
          elif st == "absent":
            stats[ck]["absent"] += 1
          elif st == "cancelled":
            stats[ck]["cancelled"] += 1

    for idx, (k, c) in enumerate(courses.items()):
      self.stats_frame.grid_columnconfigure(idx, weight=1)
      s = stats[k]
      act = s["present"] + s["absent"]
      pct = round((s["present"] / act) * 100) if act > 0 else None

      card = ctk.CTkFrame(
          self.stats_frame,
          fg_color="#fff",
          corner_radius=8,
          border_width=1,
          border_color="#e9e9e7",
      )
      card.grid(row=0, column=idx, padx=6, pady=10, sticky="nsew")

      ctk.CTkLabel(
          card,
          text=c["name"],
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=c["color"],
      ).pack(anchor="w", padx=10, pady=(8, 0))
      pct_col = "#eb5757" if (pct is not None and pct < 70) else "#37352f"
      ctk.CTkLabel(
          card,
          text=f"%{pct}" if pct is not None else "—",
          font=ctk.CTkFont(size=22, weight="bold"),
          text_color=pct_col,
      ).pack(anchor="w", padx=10, pady=2)
      ctk.CTkLabel(
          card,
          text=f"Katılım: {s['present']}/{act}",
          font=ctk.CTkFont(size=11),
          text_color="#787774",
      ).pack(anchor="w", padx=10, pady=(0, 8))

  def render_week_grid(self, parent, w):
    start_dt = datetime.date.fromisoformat(self.state["startDate"])
    week_start = start_dt + datetime.timedelta(days=w * 7)

    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="x", pady=(0, 25))

    if self.is_expanded:
      ctk.CTkLabel(
          container,
          text=f"{w+1}. HAFTA ({week_start.strftime('%d %b %Y')})",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color="#787774",
      ).pack(anchor="w", pady=(0, 5))

    grid_frame = ctk.CTkFrame(
        container,
        fg_color="#e9e9e7",
        corner_radius=6,
        border_width=1,
        border_color="#e9e9e7",
    )
    grid_frame.pack(fill="x")

    for d in range(7):
      grid_frame.grid_columnconfigure(d, weight=1, uniform="day_col")
      ctk.CTkLabel(
          grid_frame,
          text=DAY_NAMES[d],
          fg_color="#fbfbfa",
          text_color="#787774",
          font=ctk.CTkFont(size=12, weight="bold"),
          height=28,
      ).grid(row=0, column=d, padx=1, pady=1, sticky="nsew")

      cur_date = start_dt + datetime.timedelta(days=w * 7 + d)
      day_cell = ctk.CTkFrame(
          grid_frame,
          fg_color="#fcfcfb" if d >= 5 else "#ffffff",
          corner_radius=0,
          height=220,
      )
      day_cell.grid(row=1, column=d, padx=1, pady=1, sticky="nsew")

      ctk.CTkLabel(
          day_cell,
          text=str(cur_date.day),
          font=ctk.CTkFont(size=12, weight="bold"),
          text_color="#37352f",
      ).pack(anchor="e", padx=8, pady=4)

      for cls in self.state["weeklyTemplate"].get(str(d), []):
        if cls["courseKey"] not in self.state["courses"]:
          continue
        key = f"w{w}_d{d}_{cls['id']}"
        st = self.state["attendance"].get(key, "none")

        card_bg = (
            "#edf3ec"
            if st == "present"
            else (
                "#fdebec"
                if st == "absent"
                else ("#f4f4f2" if st == "cancelled" else "#ffffff")
            )
        )
        c_card = ctk.CTkFrame(
            day_cell,
            fg_color=card_bg,
            corner_radius=6,
            border_width=1,
            border_color="#e9e9e7",
        )
        c_card.pack(fill="x", padx=6, pady=4)

        top_row = ctk.CTkFrame(c_card, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(6, 2))
        ctk.CTkLabel(
            top_row,
            text=cls["label"],
            font=ctk.CTkFont(
                size=13, weight="bold", overstrike=(st == "cancelled")
            ),
        ).pack(side="left")

        if st == "cancelled":
          ctk.CTkButton(
              c_card,
              text="Geri Al",
              width=50,
              height=20,
              fg_color="transparent",
              text_color="#2383e2",
              command=lambda k=key: self.set_status(k, "cancelled"),
          ).pack(anchor="w", padx=6, pady=(0, 6))
        else:
          ctk.CTkButton(
              top_row,
              text="🗑️",
              width=22,
              height=22,
              fg_color="transparent",
              text_color="#787774",
              command=lambda k=key: self.set_status(k, "cancelled"),
          ).pack(side="right")
          bot_row = ctk.CTkFrame(c_card, fg_color="transparent")
          bot_row.pack(fill="x", padx=8, pady=(2, 6))
          ctk.CTkLabel(
              bot_row,
              text="Attendance",
              font=ctk.CTkFont(size=11),
              text_color="#787774",
          ).pack(side="left")

          ctk.CTkButton(
              bot_row,
              text="✗",
              width=24,
              height=22,
              fg_color="#eb5757" if st == "absent" else "#fff",
              text_color="#fff" if st == "absent" else "#787774",
              border_width=1,
              command=lambda k=key: self.set_status(k, "absent"),
          ).pack(side="right", padx=(3, 0))
          ctk.CTkButton(
              bot_row,
              text="✓",
              width=24,
              height=22,
              fg_color="#2383e2" if st == "present" else "#fff",
              text_color="#fff" if st == "present" else "#787774",
              border_width=1,
              command=lambda k=key: self.set_status(k, "present"),
          ).pack(side="right")

  def render_calendar(self):
    for w in self.cal_scroll.winfo_children():
      w.destroy()
    if self.is_expanded:
      self.period_label.configure(
          text=f"Tüm Dönem ({self.state['totalWeeks']} Hafta)"
      )
      for w in range(self.state["totalWeeks"]):
        self.render_week_grid(self.cal_scroll, w)
    else:
      start_dt = datetime.date.fromisoformat(self.state["startDate"])
      w_start = start_dt + datetime.timedelta(days=self.current_week * 7)
      self.period_label.configure(
          text=f"{w_start.strftime('%B %Y')} — ({self.current_week + 1}. Hafta / {self.state['totalWeeks']})"
      )
      self.render_week_grid(self.cal_scroll, self.current_week)

  def change_week(self, delta):
    if (
        not self.is_expanded
        and 0 <= self.current_week + delta < self.state["totalWeeks"]
    ):
      self.current_week += delta
      self.render_calendar()

  def go_first_week(self):
    self.is_expanded = False
    self.current_week = 0
    self.render_calendar()

  def toggle_view(self):
    self.is_expanded = not self.is_expanded
    self.toggle_btn.configure(
        text="📅 Haftalık Görünüm"
        if self.is_expanded
        else "🔍 Tüm Dönemi Göster"
    )
    self.render_calendar()

  def render_all(self):
    self.render_stats()
    self.render_calendar()


if __name__ == "__main__":
  app = AttendanceApp()
  app.mainloop()