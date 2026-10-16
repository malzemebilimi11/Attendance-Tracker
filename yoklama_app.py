import datetime
import json
import os
import customtkinter as ctk

# Görünüm ayarları (Notion tarzı açık tema)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

DATA_FILE = "yoklama_verileri.json"
START_DATE = datetime.date(2026, 10, 12)  # 1. Hafta Pazartesi (12 Ekim 2026)
TOTAL_WEEKS = 14

COURSES = {
    "451": {"name": "METE 451", "color": "#0b8043"},
    "301": {"name": "METE 301", "color": "#5e35b1"},
    "401": {"name": "METE 401", "color": "#d8561b"},
    "453": {"name": "METE 453", "color": "#0d3b66"},
    "211": {"name": "ENG 211", "color": "#d81b60"},
    "470": {"name": "METE 470", "color": "#00695c"},
    "414": {"name": "METE 414", "color": "#9e9d24"},
}

WEEKLY_TEMPLATE = {
    0: [  # Pazartesi
        {"id": "451-1", "label": "451-1", "courseKey": "451", "time": "12:40"},
        {"id": "451-2", "label": "451-2", "courseKey": "451", "time": "13:40"},
    ],
    1: [  # Salı
        {"id": "301-tue", "label": "301", "courseKey": "301", "time": "08:40"},
        {"id": "401-tue", "label": "401", "courseKey": "401", "time": "09:40"},
    ],
    2: [  # Çarşamba
        {"id": "451-wed", "label": "451", "courseKey": "451", "time": "11:40"}
    ],
    3: [  # Perşembe
        {"id": "301-thu", "label": "301", "courseKey": "301", "time": "08:40"},
        {"id": "453-thu", "label": "453", "courseKey": "453", "time": "09:40"},
        {"id": "211-thu", "label": "211", "courseKey": "211", "time": "13:40"},
    ],
    4: [  # Cuma
        {"id": "470-fri", "label": "470", "courseKey": "470", "time": "09:40"},
        {"id": "414-fri", "label": "414", "courseKey": "414", "time": "13:40"},
    ],
    5: [],  # Cumartesi
    6: [],  # Pazar
}

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class AttendanceApp(ctk.CTk):

  def __init__(self):
    super().__init__()
    self.title("📅 Ders Yoklama Takip Sistemi (14 Hafta)")
    self.geometry("1220x800")
    self.configure(fg_color="#ffffff")

    self.current_week = 0
    self.is_expanded = False
    self.attendance_data = self.load_data()

    self.setup_ui()
    self.render_all()

  def load_data(self):
    if os.path.exists(DATA_FILE):
      try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
          return json.load(f)
      except:
        pass
    # İlk açılışta 2. fotoğraftaki varsayılan veriler
    default_data = {
        "w0_d0_451-1": "present",
        "w0_d0_451-2": "present",
        "w0_d1_401-tue": "present",
        "w0_d2_451-wed": "present",
        "w0_d3_301-thu": "present",
        "w0_d3_453-thu": "present",
        "w0_d3_211-thu": "present",
    }
    self.save_data(default_data)
    return default_data

  def save_data(self, data=None):
    if data is None:
      data = self.attendance_data
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

  def setup_ui(self):
    # Üst Bar
    self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.top_frame.pack(fill="x", padx=20, pady=(15, 5))

    title_lbl = ctk.CTkLabel(
        self.top_frame,
        text="📅 CALENDAR VIEW — ATTENDANCE",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#37352f",
    )
    title_lbl.pack(side="left")

    self.toggle_btn = ctk.CTkButton(
        self.top_frame,
        text="🔍 Tüm Dönemi Göster (14 Hafta)",
        command=self.toggle_view,
        fg_color="#2383e2",
        hover_color="#1b6ec2",
        height=32,
    )
    self.toggle_btn.pack(side="right", padx=5)

    # İstatistik Paneli
    self.stats_frame = ctk.CTkFrame(
        self,
        fg_color="#fbfbfa",
        corner_radius=10,
        border_width=1,
        border_color="#e9e9e7",
    )
    self.stats_frame.pack(fill="x", padx=20, pady=10)

    # Navigasyon Barı
    self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.nav_frame.pack(fill="x", padx=20, pady=5)

    self.period_label = ctk.CTkLabel(
        self.nav_frame,
        text="October 2026",
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
        fg_color="#ffffff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        hover_color="#f7f6f3",
        command=lambda: self.change_week(-1),
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        nav_btns,
        text="Bugün (1. Hafta)",
        width=110,
        height=28,
        fg_color="#ffffff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        hover_color="#f7f6f3",
        command=self.go_first_week,
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        nav_btns,
        text="Sonraki Hafta ❯",
        width=110,
        height=28,
        fg_color="#ffffff",
        text_color="#37352f",
        border_width=1,
        border_color="#e9e9e7",
        hover_color="#f7f6f3",
        command=lambda: self.change_week(1),
    ).pack(side="left", padx=3)

    # Takvim Alanı (Kaydırılabilir)
    self.cal_scroll = ctk.CTkScrollableFrame(
        self, fg_color="#ffffff", corner_radius=0
    )
    self.cal_scroll.pack(fill="both", expand=True, padx=15, pady=5)

  def set_status(self, key, status):
    if self.attendance_data.get(key) == status:
      del self.attendance_data[key]
    else:
      self.attendance_data[key] = status
    self.save_data()
    self.render_all()

  def render_stats(self):
    for widget in self.stats_frame.winfo_children():
      widget.destroy()

    stats = {
        k: {"present": 0, "absent": 0, "cancelled": 0} for k in COURSES.keys()
    }

    for w in range(TOTAL_WEEKS):
      for d in range(7):
        for cls in WEEKLY_TEMPLATE.get(d, []):
          key = f"w{w}_d{d}_{cls['id']}"
          st = self.attendance_data.get(key)
          if st == "present":
            stats[cls["courseKey"]]["present"] += 1
          elif st == "absent":
            stats[cls["courseKey"]]["absent"] += 1
          elif st == "cancelled":
            stats[cls["courseKey"]]["cancelled"] += 1

    for idx, (k, c) in enumerate(COURSES.items()):
      self.stats_frame.grid_columnconfigure(idx, weight=1)
      s = stats[k]
      active_total = s["present"] + s["absent"]
      pct = round((s["present"] / active_total) * 100) if active_total > 0 else None

      card = ctk.CTkFrame(
          self.stats_frame,
          fg_color="#ffffff",
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

      pct_text = f"%{pct}" if pct is not None else "—"
      pct_color = (
          "#eb5757" if (pct is not None and pct < 70) else "#37352f"
      )
      ctk.CTkLabel(
          card,
          text=pct_text,
          font=ctk.CTkFont(size=22, weight="bold"),
          text_color=pct_color,
      ).pack(anchor="w", padx=10, pady=2)

      sub_text = f"Katılım: {s['present']} / {active_total} işlenen"
      if s["cancelled"] > 0:
        sub_text += f" ({s['cancelled']} iptal)"
      ctk.CTkLabel(
          card,
          text=sub_text,
          font=ctk.CTkFont(size=11),
          text_color="#787774",
      ).pack(anchor="w", padx=10, pady=(0, 8))

  def render_week_grid(self, parent, w):
    week_start = START_DATE + datetime.timedelta(days=w * 7)
    week_end = week_start + datetime.timedelta(days=6)

    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="x", pady=(0, 25))

    if self.is_expanded:
      banner = ctk.CTkLabel(
          container,
          text=f"{w+1}. HAFTA ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')})",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color="#787774",
      )
      banner.pack(anchor="w", pady=(0, 5))

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
      hdr = ctk.CTkLabel(
          grid_frame,
          text=DAY_NAMES[d],
          fg_color="#fbfbfa",
          text_color="#787774",
          font=ctk.CTkFont(size=12, weight="bold"),
          height=28,
      )
      hdr.grid(row=0, column=d, padx=1, pady=1, sticky="nsew")

      cur_date = START_DATE + datetime.timedelta(days=w * 7 + d)
      bg_col = "#fcfcfb" if d >= 5 else "#ffffff"
      day_cell = ctk.CTkFrame(
          grid_frame, fg_color=bg_col, corner_radius=0, height=230
      )
      day_cell.grid(row=1, column=d, padx=1, pady=1, sticky="nsew")

      # Gün numarası
      is_today = cur_date == datetime.date.today()
      date_lbl = ctk.CTkLabel(
          day_cell,
          text=str(cur_date.day),
          font=ctk.CTkFont(size=12, weight="bold"),
          fg_color="#eb5757" if is_today else "transparent",
          text_color="#ffffff" if is_today else "#37352f",
          corner_radius=12,
          width=24,
          height=24,
      )
      date_lbl.pack(anchor="e", padx=6, pady=6)

      # Ders Kartları
      for cls in WEEKLY_TEMPLATE.get(d, []):
        key = f"w{w}_d{d}_{cls['id']}"
        st = self.attendance_data.get(key, "none")

        card_bg = "#ffffff"
        border_col = "#e9e9e7"
        if st == "present":
          card_bg = "#edf3ec"
          border_col = "#b7d5b9"
        elif st == "absent":
          card_bg = "#fdebec"
          border_col = "#f5c2c4"
        elif st == "cancelled":
          card_bg = "#f4f4f2"
          border_col = "#d3d3d0"

        c_card = ctk.CTkFrame(
            day_cell,
            fg_color=card_bg,
            corner_radius=6,
            border_width=1,
            border_color=border_col,
        )
        c_card.pack(fill="x", padx=6, pady=4)

        top_row = ctk.CTkFrame(c_card, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(6, 2))

        title_font = ctk.CTkFont(
            size=13, weight="bold", overstrike=(st == "cancelled")
        )
        ctk.CTkLabel(
            top_row, text=cls["label"], font=title_font, text_color="#37352f"
        ).pack(side="left")

        if st == "cancelled":
          ctk.CTkButton(
              c_card,
              text="Geri Al",
              width=50,
              height=20,
              font=ctk.CTkFont(size=11),
              fg_color="transparent",
              text_color="#2383e2",
              hover_color="#e9e9e7",
              command=lambda k=key: self.set_status(k, "cancelled"),
          ).pack(anchor="w", padx=6, pady=(0, 6))
        else:
          del_btn = ctk.CTkButton(
              top_row,
              text="🗑️",
              width=22,
              height=22,
              fg_color="transparent",
              text_color="#787774",
              hover_color="#e9e9e7",
              command=lambda k=key: self.set_status(k, "cancelled"),
          )
          del_btn.pack(side="right")

          bot_row = ctk.CTkFrame(c_card, fg_color="transparent")
          bot_row.pack(fill="x", padx=8, pady=(2, 6))

          ctk.CTkLabel(
              bot_row,
              text="Attendance",
              font=ctk.CTkFont(size=11),
              text_color="#787774",
          ).pack(side="left")

          # Çarpı Butonu
          x_btn = ctk.CTkButton(
              bot_row,
              text="✗",
              width=24,
              height=22,
              font=ctk.CTkFont(size=12, weight="bold"),
              fg_color="#eb5757" if st == "absent" else "#ffffff",
              text_color="#ffffff" if st == "absent" else "#787774",
              border_width=1,
              border_color="#eb5757" if st == "absent" else "#dcdcdc",
              hover_color="#fdebec",
              command=lambda k=key: self.set_status(k, "absent"),
          )
          x_btn.pack(side="right", padx=(3, 0))

          # Tik Butonu
          v_btn = ctk.CTkButton(
              bot_row,
              text="✓",
              width=24,
              height=22,
              font=ctk.CTkFont(size=12, weight="bold"),
              fg_color="#2383e2" if st == "present" else "#ffffff",
              text_color="#ffffff" if st == "present" else "#787774",
              border_width=1,
              border_color="#2383e2" if st == "present" else "#dcdcdc",
              hover_color="#edf3ec",
              command=lambda k=key: self.set_status(k, "present"),
          )
          v_btn.pack(side="right")

  def render_calendar(self):
    for widget in self.cal_scroll.winfo_children():
      widget.destroy()

    if self.is_expanded:
      self.period_label.configure(text="Tüm Dönem Görünümü (14 Hafta)")
      for w in range(TOTAL_WEEKS):
        self.render_week_grid(self.cal_scroll, w)
    else:
      w_start = START_DATE + datetime.timedelta(days=self.current_week * 7)
      self.period_label.configure(
          text=f"{w_start.strftime('%B %Y')} — ({self.current_week + 1}. Hafta / 14)"
      )
      self.render_week_grid(self.cal_scroll, self.current_week)

  def change_week(self, delta):
    if self.is_expanded:
      return
    nxt = self.current_week + delta
    if 0 <= nxt < TOTAL_WEEKS:
      self.current_week = nxt
      self.render_calendar()

  def go_first_week(self):
    self.is_expanded = False
    self.toggle_btn.configure(text="🔍 Tüm Dönemi Göster (14 Hafta)")
    self.current_week = 0
    self.render_calendar()

  def toggle_view(self):
    self.is_expanded = not self.is_expanded
    if self.is_expanded:
      self.toggle_btn.configure(text="📅 Haftalık Görünüme Dön")
    else:
      self.toggle_btn.configure(text="🔍 Tüm Dönemi Göster (14 Hafta)")
    self.render_calendar()

  def render_all(self):
    self.render_stats()
    self.render_calendar()


if __name__ == "__main__":
  app = AttendanceApp()
  app.mainloop()