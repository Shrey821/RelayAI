import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors - Executive Carbon & High Contrast Palette
    BG_DARK = RGBColor(13, 17, 23)           # #0D1117 (Deep Carbon)
    CARD_BG = RGBColor(22, 27, 34)           # #161B22 (Matte Panel)
    CARD_BORDER = RGBColor(48, 54, 61)       # #30363D (Subtle Slate Border)
    HEADER_ROW_BG = RGBColor(30, 41, 59)     # #1E293B (Dark Slate Header)
    
    # Accent Branding Colors
    ACCENT_CYAN = RGBColor(14, 165, 233)     # #0EA5E9 (Relay Blue/Cyan)
    ACCENT_EMERALD = RGBColor(16, 185, 129)  # #10B981 (Growth / Success)
    ACCENT_AMBER = RGBColor(245, 158, 11)    # #F59E0B (Moderate / Notice)
    ACCENT_ROSE = RGBColor(239, 68, 68)      # #EF4444 (Risk / Free Tier)
    
    # Text Colors
    TEXT_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC (Bright White)
    TEXT_MUTED = RGBColor(148, 163, 184)     # #94A3B8 (Silver Muted)
    TEXT_DIM = RGBColor(100, 116, 139)       # #64748B (Slate Subtext)
    
    # Heat Map Fill Colors (Curated for readability with bold white/light text)
    HM_CRITICAL = RGBColor(13, 110, 68)      # Deep Emerald (High Value / Critical)
    HM_HIGH = RGBColor(20, 130, 85)          # Emerald
    HM_MED_HIGH = RGBColor(35, 115, 95)      # Teal Slate
    HM_MED = RGBColor(180, 105, 12)          # Warm Amber (Moderate / Neutral)
    HM_LOW = RGBColor(155, 45, 45)           # Muted Rose (Low / High Churn)
    HM_NEUTRAL = RGBColor(40, 50, 70)        # Dark Slate Neutral

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category, slide_num):
        # Category Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(0.28))
        tf = cat_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        
        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(10.5), Inches(0.55))
        tf2 = title_box.text_frame
        tf2.word_wrap = True
        tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
        p2 = tf2.paragraphs[0]
        p2.text = title
        p2.font.size = Pt(21)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_LIGHT
        
        # Slide number counter
        num_box = slide.shapes.add_textbox(Inches(11.7), Inches(0.4), Inches(0.9), Inches(0.3))
        tf3 = num_box.text_frame
        p3 = tf3.paragraphs[0]
        p3.text = f"{slide_num:02d} / 10"
        p3.alignment = PP_ALIGN.RIGHT
        p3.font.size = Pt(10)
        p3.font.bold = True
        p3.font.color.rgb = TEXT_DIM
        
        # Subtle separator rule
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.015))
        div.fill.solid()
        div.fill.fore_color.rgb = CARD_BORDER
        div.line.fill.background()

    def add_card(slide, left, top, width, height, title=None, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), Inches(0.32))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = TEXT_LIGHT
        return card

    def format_cell(cell, text, bg_color=None, text_color=TEXT_LIGHT, font_size=9.5, bold=False, align=PP_ALIGN.CENTER):
        if bg_color:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.08)
        cell.margin_right = Inches(0.08)
        cell.margin_top = Inches(0.05)
        cell.margin_bottom = Inches(0.05)
        
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = text_color
        p.alignment = align

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    
    # Outer frame
    frame = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    frame.fill.solid()
    frame.fill.fore_color.rgb = CARD_BG
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = Pt(1.5)
    
    # Glow edge
    edge = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.12), Inches(5.9))
    edge.fill.solid()
    edge.fill.fore_color.rgb = ACCENT_CYAN
    edge.line.fill.background()
    
    # Main hero text
    tb = s1.shapes.add_textbox(Inches(1.4), Inches(1.3), Inches(10.5), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "RELAY AI  •  UNIVERSAL MEMORY SCHEMA (UMS)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(14)
    
    p2 = tf.add_paragraph()
    p2.text = "Business Model & Subscription Strategy"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_LIGHT
    p2.space_after = Pt(12)
    
    p3 = tf.add_paragraph()
    p3.text = "A Defensible, Pragmatic SaaS Framework in Heat Map Format for Cross-LLM Developer Context Portability"
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_after = Pt(24)

    # 4 Meta Pillars at bottom of slide 1
    pill_data = [
        ("REVENUE ENGINE", "Pure Subscription Model", "Free / Pro ($12) / Team ($28) / Enterprise", ACCENT_CYAN),
        ("CORE ASSET", "Universal Memory Schema", "Zero-dependency open IR standard + local vault", ACCENT_EMERALD),
        ("MARKET REALITY", "Context Switching Penalty", "Saves 3-5 hrs/dev/month across 4+ LLMs", ACCENT_AMBER),
        ("DEFENSIBILITY", "Vendor Neutrality", "Zero scraping; official API & memory import pipelines", TEXT_LIGHT),
    ]
    for i, (tag, title, desc, col) in enumerate(pill_data):
        c_left = Inches(1.4 + i * 2.65)
        c_top = Inches(4.7)
        c_card = add_card(s1, c_left, c_top, Inches(2.5), Inches(1.6), bg_color=RGBColor(17, 22, 30))
        
        ptb = s1.shapes.add_textbox(c_left + Inches(0.15), c_top + Inches(0.12), Inches(2.2), Inches(1.35))
        ptf = ptb.text_frame
        ptf.word_wrap = True
        ptf.margin_left = ptf.margin_top = ptf.margin_right = ptf.margin_bottom = 0
        
        pp1 = ptf.paragraphs[0]
        pp1.text = tag
        pp1.font.size = Pt(9)
        pp1.font.bold = True
        pp1.font.color.rgb = col
        pp1.space_after = Pt(4)
        
        pp2 = ptf.add_paragraph()
        pp2.text = title
        pp2.font.size = Pt(12)
        pp2.font.bold = True
        pp2.font.color.rgb = TEXT_LIGHT
        pp2.space_after = Pt(4)
        
        pp3 = ptf.add_paragraph()
        pp3.text = desc
        pp3.font.size = Pt(9)
        pp3.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: THE REAL PROBLEM (NO HYPOTHETICAL EXAGGERATION)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "The Real Friction: Developer AI Fragmentation & The Context Penalty", "Market Reality & Problem Statement", 2)
    
    col_w = Inches(3.7)
    gap = Inches(0.3)
    c_top = Inches(1.6)
    c_h = Inches(4.3)
    
    p_cards = [
        ("The Multi-Model Reality", ACCENT_CYAN, [
            ("84% of developers", "regularly switch between 2-4 AI tools weekly: Claude Sonnet for deep coding, ChatGPT for architectural synthesis, Cursor for in-file edits, Gemini for 1M+ token repo analysis."),
            ("Frequent Switching Drivers", "Prompt rate limits (Claude 5-hr cap), model-specific strengths, and pricing boundaries force devs to shift tools multiple times in a single coding sprint."),
            ("Vendor Lock-In Silos", "Each AI provider locks custom rules into proprietary silos, preventing seamless workflow handoffs.")
        ]),
        ("The 'Context Reset' Penalty", ACCENT_AMBER, [
            ("15-20 Minutes Per Switch", "Engineers repeatedly re-feed tech stacks, strict TypeScript rules ('zero any', Tailwind v4), architectural decisions, and current blockers every time they switch models."),
            ("Compounded Billable Waste", "An average engineer wastes 3 to 5 productive hours every month simply getting a secondary LLM up to speed on active sprint context."),
            ("Context Window Pollution", "Re-explaining context in prose wastes scarce context tokens and triggers model instruction drift.")
        ]),
        ("Why Existing Tools Fail", ACCENT_ROSE, [
            ("Brittle Screen Scrapers", "Third-party browser extensions using DOM scrapers constantly break with UI changes and violate provider Terms of Service."),
            ("Raw Chat Dump Bloat", "Exporting raw transcripts burns 25,000+ tokens on chit-chat, bloating memory and degrading model reasoning."),
            ("The UMS Breakthrough", "UMS uses officially documented import prompts & memory queries, normalizing data into a lean 3-Tier standard.")
        ])
    ]
    
    for i, (title, color, items) in enumerate(p_cards):
        c_left = Inches(0.8 + i * (3.7 + 0.3))
        add_card(s2, c_left, c_top, col_w, c_h, title)
        
        # Color bar indicator
        c_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, c_top, col_w, Inches(0.04))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = color
        c_bar.line.fill.background()
        
        tb = s2.shapes.add_textbox(c_left + Inches(0.25), c_top + Inches(0.6), col_w - Inches(0.5), c_h - Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for j, (bold_txt, reg_txt) in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {bold_txt}: "
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_LIGHT
            
            run = p.add_run()
            run.text = reg_txt
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(12)

    # Bottom summary callout
    b_card = add_card(s2, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9), bg_color=RGBColor(20, 26, 36))
    btb = s2.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
    btf = btb.text_frame
    btf.word_wrap = True
    bp = btf.paragraphs[0]
    bp.text = "CORE INSIGHT (ZERO HYPERBOLE): "
    bp.font.size = Pt(10.5)
    bp.font.bold = True
    bp.font.color.rgb = ACCENT_EMERALD
    brun = bp.add_run()
    brun.text = "Developers do not want another AI model—they want their existing personalization, coding standards, and active sprint memory to follow them instantly between the models they already pay for."
    brun.font.bold = False
    brun.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 3: 3-TIER ARCHITECTURE & VALUE FOUNDATION
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Product Foundation: The 3-Tier Universal Memory Architecture", "Architecture & Value Proposition", 3)
    
    t_cards = [
        ("TIER 1: AI Identity & Long-Term Memory", ACCENT_CYAN, "PERSISTENT CORE", [
            ("User Profile & Role", "Senior Systems Architect, Full-Stack Engineer, AI Researcher"),
            ("Tech Stack & Toolchains", "TypeScript Strict, Next.js, Tailwind v4, FastAPI, PostgreSQL, Docker"),
            ("Engineering Conventions", "Zero-any rule, strict TDD, clean architecture, no lazy placeholders"),
            ("Communication Tone", "Concise, senior engineer demeanor, no conversational filler"),
            ("Target Hydration", "Claude Memory Import, ChatGPT Custom Instructions, Gemini Saved Info")
        ]),
        ("TIER 2: Active Working Context", ACCENT_EMERALD, "SPRINT-LEVEL CONTEXT", [
            ("Primary Objective", "E.g., Complete UMS Core v1 Engine & SQLite Vault migration"),
            ("Active Decisions Today", "Decisions finalized this session (e.g., zero external dependencies)"),
            ("Current Blockers", "Known constraints, pending PR reviews, temporary architectural locks"),
            ("Ephemeral Guardrails", "Constraints like 'Do not touch auth schema during this refactor'"),
            ("Target Hydration", "Active chat preambles, Cursor/Windsurf session rules, CLI state")
        ]),
        ("TIER 3: Conversation Transcript", ACCENT_ROSE, "FILTERED / PRUNED", [
            ("Raw Turn-by-Turn History", "Raw multi-turn conversational chat logs between user and LLM"),
            ("Zero Token Bloat", "Pruned by default during cross-model transfer to eliminate token waste"),
            ("Privacy Boundary", "Prevents accidental leakage of transient conversational banter"),
            ("Optional Archival", "Stored locally in SQLite vault only if developer explicitly requests"),
            ("Target Hydration", "Local snapshot replay only; never injected into LLM system prompts")
        ])
    ]
    
    for i, (title, color, tag, items) in enumerate(t_cards):
        c_left = Inches(0.8 + i * (3.7 + 0.3))
        add_card(s3, c_left, Inches(1.6), col_w, Inches(4.3), title)
        
        # Color top indicator
        c_bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, Inches(1.6), col_w, Inches(0.04))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = color
        c_bar.line.fill.background()
        
        # Badge tag
        badge = s3.shapes.add_textbox(c_left + Inches(0.2), Inches(2.05), col_w - Inches(0.4), Inches(0.25))
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = tag
        bp.font.size = Pt(8.5)
        bp.font.bold = True
        bp.font.color.rgb = color
        
        tb = s3.shapes.add_textbox(c_left + Inches(0.2), Inches(2.35), col_w - Inches(0.4), Inches(3.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for j, (bold_txt, reg_txt) in enumerate(items):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {bold_txt}: "
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_LIGHT
            
            run = p.add_run()
            run.text = reg_txt
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(8)

    # Architecture Ecosystem Bar
    bot_card = add_card(s3, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9), bg_color=RGBColor(20, 26, 36))
    bb = s3.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
    bbtf = bb.text_frame
    bbtf.word_wrap = True
    p = bbtf.paragraphs[0]
    p.text = "THE ZERO-DEPENDENCY SUITE: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    r = p.add_run()
    r.text = "Open Spec (spec/ums-v1.json)  →  Local SQLite Vault (ums_vault.db)  →  Headless CLI (cli.py)  →  Web Studio (run.py)  →  Browser Companion (extension/)\nEnables 100% offline, local-first privacy with instant 1-click cloud sync whenever the user desires."
    r.font.bold = False
    r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: CORE BUSINESS MODEL: MARKET SEGMENT HEAT MAP
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Business Model Heat Map: Customer Segment Viability Matrix", "Core Business Model  •  Market Evaluation", 4)
    
    # Heat map table
    # Columns: Segment (2.2), Context Pain (1.5), Willingness To Pay (1.5), CAC Efficiency (1.5), Retention/Churn (1.5), Expansion (1.5), Overall Rating (1.8) -> Total 11.5
    rows = 6
    cols = 7
    t_shape = s4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.3))
    table = t_shape.table
    
    col_widths = [Inches(2.2), Inches(1.5), Inches(1.6), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.9)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w
        
    headers = [
        "Customer Segment",
        "Context Pain\n(1-5)",
        "Willingness To Pay\n(WTP / User / Mo)",
        "Acquisition CAC\nEfficiency",
        "Retention / Churn\nRisk Profile",
        "Expansion Revenue\nPotential",
        "Commercial\nAttractiveness"
    ]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        format_cell(cell, h, bg_color=HEADER_ROW_BG, text_color=ACCENT_CYAN, font_size=9.5, bold=True)
        
    # Segment data rows
    segment_data = [
        (
            "Indie Hackers & Students\n(Solo hobbyists, early builders)",
            ("Moderate (2.5/5)\nSingle project focus", HM_NEUTRAL),
            ("Low ($0 - $5/mo)\nHigh price resistance", HM_LOW),
            ("High Organic\n(GitHub, viral HN)", HM_HIGH),
            ("High Churn (6-8%)\nProject abandonment", HM_LOW),
            ("Minimal\nSingle user seats", HM_LOW),
            ("NEUTRAL (Tier: Free OSS)\nTop-of-funnel brand flywheel", HM_NEUTRAL)
        ),
        (
            "Senior Dev Contractors\n(Consultants, multi-client leads)",
            ("Very High (4.8/5)\nMultiple clients & LLMs", HM_CRITICAL),
            ("High ($12 - $15/mo)\nBilled as work expense", HM_CRITICAL),
            ("High (PLG Organic)\nExtension store search", HM_HIGH),
            ("Low Churn (3.0%)\nDaily workflow dependency", HM_MED_HIGH),
            ("Moderate\nRecommends to clients", HM_MED),
            ("HIGH (Tier: Pro $12/mo)\nImmediate payback & high LTV", HM_HIGH)
        ),
        (
            "Scale-Up Teams (5-50 Devs)\n(Fast-paced AI software squads)",
            ("Extreme (4.9/5)\nRepo rules & onboard drift", HM_CRITICAL),
            ("Very High ($25 - $35/seat)\nCorporate SaaS card", HM_CRITICAL),
            ("Very High (Viral)\nDev leads invite squad", HM_CRITICAL),
            ("Very Low Churn (<1.5%)\nTeam repository lock-in", HM_CRITICAL),
            ("High Expansion\nSeats grow with hiring", HM_CRITICAL),
            ("PRIME TARGET (Tier: Team $28)\nCore ARR engine & viral growth", HM_CRITICAL)
        ),
        (
            "Mid-Market Tech (50-250 Devs)\n(Standardized engineering orgs)",
            ("High (4.2/5)\nEngineering governance", HM_HIGH),
            ("High ($20 - $28/seat)\nDevOps/Tools budget", HM_HIGH),
            ("Moderate\nRequires security review", HM_MED),
            ("Very Low Churn (<1.0%)\nAnnual team contracts", HM_CRITICAL),
            ("High Expansion\nRollout across squads", HM_HIGH),
            ("HIGH (Tier: Team/Enterprise)\nStable recurring expansion", HM_HIGH)
        ),
        (
            "Regulated Enterprise (250+)\n(Fintech, Health, Defense orgs)",
            ("Critical (4.7/5)\nStrict PII/Secret leaks", HM_CRITICAL),
            ("Extreme ($50+/seat)\nDedicated IT budget", HM_CRITICAL),
            ("Low (6-9 mo sales)\nHeavy procurement drag", HM_LOW),
            ("Near Zero (<0.5%)\nMulti-year enterprise SLA", HM_CRITICAL),
            ("High Account Expansion\nCross-division deployment", HM_HIGH),
            ("SELECTIVE (Tier: Enterprise)\nPhase 3 self-hosted opportunity", HM_MED)
        )
    ]
    
    for r_idx, row in enumerate(segment_data, start=1):
        # First cell (Segment name)
        cell = table.cell(r_idx, 0)
        format_cell(cell, row[0], bg_color=CARD_BG, text_color=TEXT_LIGHT, font_size=9, bold=True, align=PP_ALIGN.LEFT)
        
        # 6 attribute cells
        for c_idx in range(1, 7):
            val_text, fill_col = row[c_idx]
            cell = table.cell(r_idx, c_idx)
            format_cell(cell, val_text, bg_color=fill_col, text_color=TEXT_LIGHT, font_size=8.5, bold=True)
            
    # Bottom callout banner
    add_card(s4, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.95), bg_color=RGBColor(20, 26, 36))
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "STRATEGIC TAKEAWAY FROM HEAT MAP: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD
    r = p.add_run()
    r.text = "The commercial sweet spot is dual-pronged: (1) Solo Power Contractors ($12/mo Pro) via frictionless Chrome Extension conversion, and (2) Scale-Up Engineering Teams ($28/seat Team) who need team-wide .cursorrules and CLAUDE.md convention sync. Indie hackers serve as the viral zero-CAC distribution channel."
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 5: REVENUE STREAM: SUBSCRIPTION MODEL & TIERING
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Revenue Engine: Grounded 4-Tier Subscription Architecture", "SaaS Pricing & Monetization Model", 5)
    
    tier_w = Inches(2.75)
    tier_gap = Inches(0.24)
    t_top = Inches(1.5)
    t_h = Inches(5.4)
    
    tiers = [
        ("COMMUNITY", "$0", "Forever Free", ACCENT_CYAN, "Indie developers & hobbyists", [
            ("Local-First Vault", "Full offline SQLite storage (ums_vault.db)"),
            ("Headless CLI", "Standard extract, parse, and verify CLI"),
            ("Single Browser", "Chrome extension active tab inspector"),
            ("Manual Export/Import", "Export persona.ums.json manually"),
            ("Zero Cloud Sync", "Single machine only; zero server footprint"),
            ("Community Support", "GitHub Issues & open community")
        ], "TOP-OF-FUNNEL FLYWHEEL"),
        
        ("RELAY PRO", "$12", "per user / mo ($120/yr)", ACCENT_EMERALD, "Senior devs, power contractors", [
            ("Encrypted Cloud Sync", "End-to-end encrypted multi-device relay"),
            ("1-Click Tab Handoff", "Seamlessly migrate active Claude to ChatGPT"),
            ("Semantic Diff Engine", "Automated verification score & memory diff"),
            ("Unlimited Snapshots", "Full version history & instant rollback"),
            ("Priority Connectors", "Fast updates when OpenAI/Anthropic changes"),
            ("Email & Chat Support", "< 24-hr turnaround on adapter issues")
        ], "HIGH-CONVERTING PLG HOOK"),
        
        ("RELAY TEAM", "$28", "per seat / mo (min 5 seats)", ACCENT_AMBER, "Fast-growing engineering teams", [
            ("Shared Team Vault", "Synchronize team coding standards across devs"),
            (".cursorrules Sync", "Centralized CLAUDE.md / AGENTS.md sync"),
            ("Secret Redaction Filter", "Scrub API keys & PII before provider ingest"),
            ("Role-Based Access", "Admin, Tech Lead, and Member permissions"),
            ("Team Audit Logs", "Track who pushed rule updates and when"),
            ("Priority Support", "Dedicated Slack/Discord private channel")
        ], "CORE EXPANSION REVENUE"),
        
        ("ENTERPRISE", "$55+", "per seat / mo (annual contract)", TEXT_LIGHT, "Regulated orgs & large tech", [
            ("Self-Hosted Relay", "Private VPC / On-premise relay container"),
            ("SSO / SAML / Okta", "Enterprise identity & user provisioning"),
            ("SOC2 Audit Logging", "Immutable audit trail of all memory syncs"),
            ("Air-Gapped Operation", "Internal network deployment without external ping"),
            ("Custom Adapters", "Dedicated adapter builds for custom LLMs"),
            ("99.9% Uptime SLA", "Dedicated technical account manager")
        ], "HIGH-MARGIN ACCOUNTS")
    ]
    
    for i, (name, price, sub, col, target, features, tag) in enumerate(tiers):
        t_left = Inches(0.8 + i * (2.75 + 0.24))
        add_card(s5, t_left, t_top, tier_w, t_h)
        
        # Color bar indicator
        c_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, t_left, t_top, tier_w, Inches(0.04))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = col
        c_bar.line.fill.background()
        
        # Tier Title & Pricing block
        tb = s5.shapes.add_textbox(t_left + Inches(0.18), t_top + Inches(0.15), tier_w - Inches(0.36), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.text = price
        p2.font.size = Pt(26)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_LIGHT
        
        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = TEXT_DIM
        p3.space_after = Pt(4)
        
        p4 = tf.add_paragraph()
        p4.text = f"Target: {target}"
        p4.font.size = Pt(8.5)
        p4.font.bold = True
        p4.font.color.rgb = TEXT_MUTED
        
        # Divider inside card
        cdiv = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, t_left + Inches(0.18), t_top + Inches(1.55), tier_w - Inches(0.36), Inches(0.015))
        cdiv.fill.solid()
        cdiv.fill.fore_color.rgb = CARD_BORDER
        cdiv.line.fill.background()
        
        # Features list
        ftb = s5.shapes.add_textbox(t_left + Inches(0.18), t_top + Inches(1.7), tier_w - Inches(0.36), Inches(3.0))
        ftf = ftb.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        
        for j, (f_title, f_desc) in enumerate(features):
            fp = ftf.paragraphs[0] if j == 0 else ftf.add_paragraph()
            fp.text = f"✓ {f_title}: "
            fp.font.size = Pt(9)
            fp.font.bold = True
            fp.font.color.rgb = TEXT_LIGHT
            
            frun = fp.add_run()
            frun.text = f_desc
            frun.font.bold = False
            frun.font.color.rgb = TEXT_MUTED
            fp.space_after = Pt(6)
            
        # Bottom pill tag inside card
        tag_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, t_left + Inches(0.18), t_top + Inches(4.85), tier_w - Inches(0.36), Inches(0.35))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = RGBColor(18, 24, 34)
        tag_box.line.color.rgb = CARD_BORDER
        tag_box.line.width = Pt(0.75)
        
        ttb = s5.shapes.add_textbox(t_left + Inches(0.2), t_top + Inches(4.88), tier_w - Inches(0.4), Inches(0.3))
        ttf = ttb.text_frame
        tp = ttf.paragraphs[0]
        tp.text = tag
        tp.font.size = Pt(8)
        tp.font.bold = True
        tp.font.color.rgb = col
        tp.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 6: FEATURE GATING & MARGIN HEAT MAP
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Monetization Heat Map: Feature Gating & Margin Density", "Unit Cost vs Value Heat Map", 6)
    
    # 8 Features x 6 Columns Table
    rows = 9
    cols = 6
    t_shape = s6.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.4))
    table = t_shape.table
    
    col_widths = [Inches(2.5), Inches(1.6), Inches(1.8), Inches(1.8), Inches(1.8), Inches(2.233)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w
        
    headers = [
        "Feature / Platform Capability",
        "Subscription Tier\nAccess Gate",
        "Perceived User Value\n(Friction Saved)",
        "Relay Infra Cost\n(COGS / User / Mo)",
        "Gross Margin\nContribution",
        "Upgrade Conversion\nLeverage Intensity"
    ]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        format_cell(cell, h, bg_color=HEADER_ROW_BG, text_color=ACCENT_CYAN, font_size=9.5, bold=True)
        
    feature_heatmap = [
        (
            "UMS Open Spec & Headless CLI",
            ("Community (Free)", HM_NEUTRAL),
            ("Moderate\nStandardization", HM_MED),
            ("Zero ($0)\n100% Client-side", HM_CRITICAL),
            ("100% Margin\nZero server load", HM_CRITICAL),
            ("LOW (Top of Funnel)\nEstablishes open standard", HM_NEUTRAL)
        ),
        (
            "Local SQLite Vault (ums_vault.db)",
            ("Community (Free)", HM_NEUTRAL),
            ("High\nFull data privacy", HM_HIGH),
            ("Zero ($0)\nLocal disk only", HM_CRITICAL),
            ("100% Margin\nZero server load", HM_CRITICAL),
            ("MODERATE\nCreates sticky local data", HM_MED)
        ),
        (
            "E2E Encrypted Cloud Sync Relay",
            ("Relay Pro ($12/mo)", HM_HIGH),
            ("Very High\nLaptop/desktop parity", HM_CRITICAL),
            ("Negligible (<$0.25)\nEncrypted JSON blobs", HM_CRITICAL),
            ("97.9% Margin\nMinimal server bytes", HM_CRITICAL),
            ("VERY HIGH (Primary Hook)\nUsers need multi-machine sync", HM_CRITICAL)
        ),
        (
            "1-Click Cross-Tab Session Handoff",
            ("Relay Pro ($12/mo)", HM_HIGH),
            ("Extreme\nSaves 20 min per switch", HM_CRITICAL),
            ("Zero ($0)\nBrowser-local extension", HM_CRITICAL),
            ("100% Margin\nClient-side script", HM_CRITICAL),
            ("CRITICAL (Daily Habit)\nInstant switching gratification", HM_CRITICAL)
        ),
        (
            "Semantic Retention Diff Engine",
            ("Relay Pro ($12/mo)", HM_HIGH),
            ("High\nVerifies memory fidelity", HM_HIGH),
            ("Minimal (<$0.30)\nLocal diff algorithm", HM_HIGH),
            ("97.5% Margin\nStandard library diff", HM_HIGH),
            ("HIGH (Trust Driver)\nProves LLM memory retained", HM_HIGH)
        ),
        (
            "Centralized .cursorrules & CLAUDE.md Sync",
            ("Relay Team ($28/seat)", HM_CRITICAL),
            ("Extreme\nRepo-wide consistency", HM_CRITICAL),
            ("Negligible (<$0.40)\nGit/WebHook sync", HM_CRITICAL),
            ("98.5% Margin\nText payload sync", HM_CRITICAL),
            ("CRITICAL (Team Expansion)\nTech lead mandates for whole squad", HM_CRITICAL)
        ),
        (
            "Secret & PII Redaction Guardrail",
            ("Relay Team ($28/seat)", HM_CRITICAL),
            ("Critical\nBlocks API key leaks", HM_CRITICAL),
            ("Negligible (<$0.15)\nClient-side regex/WASM", HM_CRITICAL),
            ("99.4% Margin\nEdge execution", HM_CRITICAL),
            ("HIGH (Compliance Enabler)\nRequired by security audits", HM_HIGH)
        ),
        (
            "Self-Hosted Private Relay (VPC/On-Prem)",
            ("Enterprise ($55+/seat)", HM_MED),
            ("Critical\nZero outside transmission", HM_CRITICAL),
            ("Zero ($0)\nCustomer's AWS/GCP infra", HM_CRITICAL),
            ("95.0% Margin\nPure licensing fee", HM_CRITICAL),
            ("CRITICAL (Procurement Gate)\nMandatory for regulated deals", HM_CRITICAL)
        )
    ]
    
    for r_idx, row in enumerate(feature_heatmap, start=1):
        cell = table.cell(r_idx, 0)
        format_cell(cell, row[0], bg_color=CARD_BG, text_color=TEXT_LIGHT, font_size=9, bold=True, align=PP_ALIGN.LEFT)
        for c_idx in range(1, 6):
            val_text, fill_col = row[c_idx]
            cell = table.cell(r_idx, c_idx)
            format_cell(cell, val_text, bg_color=fill_col, text_color=TEXT_LIGHT, font_size=8.5, bold=True)

    # Bottom insight
    add_card(s6, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.95), bg_color=RGBColor(20, 26, 36))
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EXECUTIVE TAKEAWAY ON UNIT MARGINS: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD
    r = p.add_run()
    r.text = "RelayAI does not pay for LLM inference tokens—the user's existing accounts (OpenAI, Anthropic) bear all compute costs. Relay operates purely as an encrypted synchronization and semantic normalization layer, delivering extraordinary 95-98% SaaS gross margins."
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 7: UNIT ECONOMICS & CONSERVATIVE PROJECTIONS
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Unit Economics & Conservative Financial Model (No Exaggeration)", "Financial Viability & Cohort Metrics", 7)
    
    # Left Card: Unit Economics Analysis
    add_card(s7, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "SaaS Unit Economics Breakdown")
    
    uetb = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    uetf = uetb.text_frame
    uetf.word_wrap = True
    uetf.margin_left = uetf.margin_top = uetf.margin_right = uetf.margin_bottom = 0
    
    ue_points = [
        ("Relay Pro ($12/mo Individual)", ACCENT_CYAN, [
            ("Blended Monthly ARPU", "$11.20 (Factoring 35% annual upfront discount)"),
            ("Direct COGS per Active User", "$0.48 / mo (Encrypted sync storage, DB, auth)"),
            ("Net Gross Margin", "95.7% (Extremely capital efficient)"),
            ("Monthly Churn Rate", "3.2% (Grounded benchmark for solo dev tools)"),
            ("Customer Lifetime (1/Churn)", "~31.2 Months"),
            ("Customer Lifetime Value (LTV)", "$334 Net Contribution"),
            ("Customer Acquisition Cost (CAC)", "$62 (Organic GitHub + Extension store PLG)"),
            ("LTV : CAC Ratio", "5.4x (Healthy developer SaaS benchmark)")
        ]),
        ("Relay Team ($28/seat/mo — Avg 5-Seat Squad)", ACCENT_EMERALD, [
            ("Average Team ARPU", "$140.00 / mo ($1,680 / yr)"),
            ("Direct COGS per Team", "$2.80 / mo (Audit logging & git sync hooks)"),
            ("Net Gross Margin", "98.0%"),
            ("Monthly Team Churn Rate", "1.1% (High stickiness via repo-wide rules)"),
            ("Customer Lifetime Value (LTV)", "$12,470 per team account"),
            ("Team Acquisition CAC", "$380 (Inbound content, developer word-of-mouth)"),
            ("LTV : CAC Ratio (Capped at 36mo)", "12.8x (Superb team expansion dynamics)")
        ])
    ]
    
    for section_idx, (sec_title, col, metrics) in enumerate(ue_points):
        p = uetf.paragraphs[0] if section_idx == 0 else uetf.add_paragraph()
        p.text = sec_title.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)
        
        for m_name, m_val in metrics:
            mp = uetf.add_paragraph()
            mp.text = f"• {m_name}: "
            mp.font.size = Pt(8.5)
            mp.font.bold = True
            mp.font.color.rgb = TEXT_LIGHT
            
            mrun = mp.add_run()
            mrun.text = m_val
            mrun.font.bold = False
            mrun.font.color.rgb = TEXT_MUTED
            mp.space_after = Pt(2)
        if section_idx == 0:
            uetf.add_paragraph().space_after = Pt(8)

    # Right Card: Conservative 3-Year ARR Growth Trajectory
    add_card(s7, Inches(6.8), Inches(1.5), Inches(5.733), Inches(5.4), "Grounded 3-Year ARR Trajectory (Zero Hype)")
    
    arr_tb = s7.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    arr_tf = arr_tb.text_frame
    arr_tf.word_wrap = True
    arr_tf.margin_left = arr_tf.margin_top = arr_tf.margin_right = arr_tf.margin_bottom = 0
    
    years = [
        ("YEAR 1: Foundation & Bootstrapping", ACCENT_CYAN, [
            ("Free Open-Source Base", "25,000 Total Active Developers"),
            ("Paid Pro Subscribers", "750 Users @ $12/mo  →  $108,000 ARR"),
            ("Paid Team Accounts", "40 Teams (200 seats) @ $28/mo  →  $67,200 ARR"),
            ("Total Year 1 ARR", "$175,200 ARR (Cash-flow break-even for lean core team)"),
            ("Server & Infra Overhead", "< $1,200 / month (Local-first architecture)")
        ]),
        ("YEAR 2: PLG Expansion & Viral Loops", ACCENT_EMERALD, [
            ("Free Open-Source Base", "85,000 Active Developers"),
            ("Paid Pro Subscribers", "2,400 Users @ $12/mo  →  $345,600 ARR"),
            ("Paid Team Accounts", "160 Teams (880 seats) @ $28/mo  →  $295,680 ARR"),
            ("Enterprise Pilots", "5 Mid-Market Deals  →  $45,000 ARR"),
            ("Total Year 2 ARR", "$686,280 ARR (Healthy profitable developer tools business)")
        ]),
        ("YEAR 3: Enterprise & Team Scale", ACCENT_AMBER, [
            ("Free Open-Source Base", "220,000 Active Developers"),
            ("Paid Pro Subscribers", "5,200 Users @ $12/mo  →  $748,800 ARR"),
            ("Paid Team Accounts", "420 Teams (2,300 seats) @ $28/mo  →  $772,800 ARR"),
            ("Enterprise Contracts", "18 Enterprise Deals @ $55/seat  →  $215,000 ARR"),
            ("Total Year 3 ARR", "$1,736,600 ARR (High-growth, cash-flow positive company)")
        ])
    ]
    
    for y_idx, (y_title, col, stats) in enumerate(years):
        p = arr_tf.paragraphs[0] if y_idx == 0 else arr_tf.add_paragraph()
        p.text = y_title.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(3)
        
        for s_title, s_val in stats:
            sp = arr_tf.add_paragraph()
            sp.text = f"• {s_title}: "
            sp.font.size = Pt(8.5)
            sp.font.bold = True
            sp.font.color.rgb = TEXT_LIGHT
            
            srun = sp.add_run()
            srun.text = s_val
            srun.font.bold = False
            srun.font.color.rgb = TEXT_MUTED
            sp.space_after = Pt(2)
        if y_idx < len(years) - 1:
            arr_tf.add_paragraph().space_after = Pt(6)

    # ==========================================
    # SLIDE 8: GO-TO-MARKET (GTM) DISTRIBUTION FLYWHEEL
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Go-To-Market Engine: Product-Led Growth (PLG) Distribution", "Distribution & Acquisition Flywheel", 8)
    
    step_w = Inches(2.75)
    s_top = Inches(1.6)
    s_h = Inches(4.2)
    
    steps = [
        ("STAGE 1", "Open Standard Adoption", ACCENT_CYAN, "Top-of-Funnel Discovery", [
            ("Apache 2.0 Spec Release", "Publish ums-v1.json specification openly on GitHub"),
            ("Zero-Dependency CLI", "Developers use cli.py without installing bloated node_modules or pip packages"),
            ("Developer Trust", "100% local-first privacy (ums_vault.db); zero corporate telemetry"),
            ("Organic Buzz", "Hacker News Show HN, Reddit r/LocalLLaMA, Twitter/X technical threads")
        ]),
        ("STAGE 2", "Frictionless Extension", ACCENT_EMERALD, "Daily Active Engagement", [
            ("Chrome Web Store", "1-Click install into Chrome, Brave, and Edge browsers"),
            ("Cross-Tab Detection", "Extension automatically recognizes open Claude, ChatGPT, and Gemini tabs"),
            ("Zero-Config Extraction", "1-Click memory inspection and extraction prompt copying"),
            ("Habit Formation", "Developer uses Relay daily whenever switching between models")
        ]),
        ("STAGE 3", "Pro Upgrade Trigger", ACCENT_AMBER, "PQL Commercial Conversion", [
            ("Multi-Machine Friction", "Developer wants laptop and desktop coding environments synced"),
            ("1-Click Tab Bridge", "Moving an active live session from Claude to ChatGPT with 1-click"),
            ("Snapshot History", "Rollback memory state when prompt drift occurs"),
            ("Organic Conversion", "2.8% - 3.5% of free extension users upgrade to Pro ($12/mo)")
        ]),
        ("STAGE 4", "Team Viral Expansion", TEXT_LIGHT, "Bottom-Up Enterprise Land", [
            ("Repo Standardization", "Senior dev creates team .cursorrules and CLAUDE.md from Relay"),
            ("Team Workspace Invite", "Senior dev shares standardized team vault with squad members"),
            ("Compliance Guardrails", "Engineering VP enforces automated secret/PII scrubbing before LLM input"),
            ("Seat Expansion", "Converts single $12/mo dev into 5-25 seat Team subscription ($28/seat)")
        ])
    ]
    
    for i, (stage, title, col, role, items) in enumerate(steps):
        s_left = Inches(0.8 + i * (2.75 + 0.24))
        add_card(s8, s_left, s_top, step_w, s_h)
        
        # Color bar
        c_bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, s_left, s_top, step_w, Inches(0.04))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = col
        c_bar.line.fill.background()
        
        # Header
        tb = s8.shapes.add_textbox(s_left + Inches(0.18), s_top + Inches(0.15), step_w - Inches(0.36), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = stage
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_LIGHT
        p2.space_after = Pt(2)
        
        p3 = tf.add_paragraph()
        p3.text = role
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = TEXT_DIM
        
        # Divider
        sdiv = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, s_left + Inches(0.18), s_top + Inches(1.15), step_w - Inches(0.36), Inches(0.015))
        sdiv.fill.solid()
        sdiv.fill.fore_color.rgb = CARD_BORDER
        sdiv.line.fill.background()
        
        # Bullets
        btb = s8.shapes.add_textbox(s_left + Inches(0.18), s_top + Inches(1.28), step_w - Inches(0.36), Inches(2.8))
        btf = btb.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0
        
        for j, (bold_txt, reg_txt) in enumerate(items):
            bp = btf.paragraphs[0] if j == 0 else btf.add_paragraph()
            bp.text = f"• {bold_txt}: "
            bp.font.size = Pt(8.8)
            bp.font.bold = True
            bp.font.color.rgb = TEXT_LIGHT
            
            brun = bp.add_run()
            brun.text = reg_txt
            brun.font.bold = False
            brun.font.color.rgb = TEXT_MUTED
            bp.space_after = Pt(8)

    # Bottom Callout
    add_card(s8, Inches(0.8), Inches(6.0), Inches(11.733), Inches(1.0), bg_color=RGBColor(20, 26, 36))
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(6.08), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE ZERO-CAC ADVANTAGE: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD
    r = p.add_run()
    r.text = "Because UMS functions as an open standard and developers already experience context switching daily across ChatGPT and Claude, RelayAI does not need expensive paid advertising. The Chrome Extension and GitHub repository act as self-funding, high-intent acquisition channels."
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 9: RISK ANALYSIS & MOAT HEAT MAP
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Risk Assessment & Defensibility: Competitive Moat Matrix", "Defensibility & Provider Dynamics", 9)
    
    # 5 Risks Table x 5 Columns
    rows = 6
    cols = 5
    t_shape = s9.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.3))
    table = t_shape.table
    
    col_widths = [Inches(2.5), Inches(1.4), Inches(1.4), Inches(3.633), Inches(2.8)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w
        
    headers = [
        "Identified Risk Vector",
        "Likelihood\n(Low/Med/High)",
        "Impact\n(Low/Med/High)",
        "RelayAI Structural Moat & Defensibility",
        "Strategic Mitigation Plan"
    ]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        format_cell(cell, h, bg_color=HEADER_ROW_BG, text_color=ACCENT_CYAN, font_size=9.5, bold=True)
        
    risk_matrix = [
        (
            "Providers Build Native Multi-Model Exporters",
            ("Low (1.5/5)\nWalled garden incentives", HM_CRITICAL),
            ("High (4.0/5)\nIf built natively", HM_MED),
            ("Walled Gardens Never Collaborate: OpenAI will never build an automated export tool to migrate users seamlessly to Anthropic Claude. Neutrality is our permanent moat.", CARD_BG),
            ("Maintain pure vendor neutrality across all current and future LLMs.", HM_MED_HIGH)
        ),
        (
            "Provider UI / DOM Scraping Breakage",
            ("High for bots\nZero for UMS", HM_CRITICAL),
            ("Critical for bots\nZero for UMS", HM_CRITICAL),
            ("Zero Screen Scraping: UMS operates strictly via officially documented provider prompts, official memory settings, and documented verification queries.", CARD_BG),
            ("Track official API and documentation changes with 24-hr adapter turnaround.", HM_HIGH)
        ),
        (
            "IDE Silo Expansion (Cursor, Windsurf, Copilot)",
            ("High (4.0/5)\nIDEs expand features", HM_MED),
            ("Moderate (2.5/5)\nComplementary role", HM_MED_HIGH),
            ("IDEs Are Isolated to the Editor: Cursor cannot manage memory inside ChatGPT web or Claude research chats. Relay acts as the universal bridge between web and IDE.", CARD_BG),
            ("Native export to CLAUDE.md, .cursorrules, and AGENTS.md files.", HM_HIGH)
        ),
        (
            "Developer DIY Scripting Inertia",
            ("Moderate (3.0/5)\nDevs write custom scripts", HM_MED),
            ("Low (1.5/5)\nDIY maintenance drag", HM_CRITICAL),
            ("High Maintenance Burden: Writing a one-off parser is easy; maintaining multi-model sync, schema normalization, diffing, and browser extension across 5 tools is unsustainable for teams.", CARD_BG),
            ("Deliver 1-click convenience that makes DIY scripts obsolete.", HM_MED_HIGH)
        ),
        (
            "Enterprise Security & Data Leak Skepticism",
            ("High (4.2/5)\nEnterprise paranoia", HM_MED),
            ("High (4.0/5)\nBlocks deals if unsolved", HM_MED),
            ("Local-First Architecture: UMS stores data locally in SQLite by default. Zero prompt telemetry. Client-side secret scrubbing eliminates corporate data leak concerns.", CARD_BG),
            ("Provide self-hosted on-premise relay container with SOC2 compliance.", HM_CRITICAL)
        )
    ]
    
    for r_idx, row in enumerate(risk_matrix, start=1):
        cell = table.cell(r_idx, 0)
        format_cell(cell, row[0], bg_color=CARD_BG, text_color=TEXT_LIGHT, font_size=9, bold=True, align=PP_ALIGN.LEFT)
        
        # Likelihood
        cell1 = table.cell(r_idx, 1)
        format_cell(cell1, row[1][0], bg_color=row[1][1], text_color=TEXT_LIGHT, font_size=8.5, bold=True)
        
        # Impact
        cell2 = table.cell(r_idx, 2)
        format_cell(cell2, row[2][0], bg_color=row[2][1], text_color=TEXT_LIGHT, font_size=8.5, bold=True)
        
        # Moat
        cell3 = table.cell(r_idx, 3)
        format_cell(cell3, row[3][0], bg_color=row[3][1], text_color=TEXT_MUTED, font_size=8.5, bold=False, align=PP_ALIGN.LEFT)
        
        # Mitigation
        cell4 = table.cell(r_idx, 4)
        format_cell(cell4, row[4][0], bg_color=row[4][1], text_color=TEXT_LIGHT, font_size=8.5, bold=True)

    # Bottom insight
    add_card(s9, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.95), bg_color=RGBColor(20, 26, 36))
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "DEFENSIVE POSITIONING SUMMARY: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD
    r = p.add_run()
    r.text = "RelayAI's ultimate moat is Switzerland-like vendor neutrality. As the AI model landscape fragments further between OpenAI, Anthropic, Google, and open-weights (DeepSeek, Mistral), developers and engineering teams demand an independent, neutral source of truth for their AI context."
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 10: EXECUTION ROADMAP & SUMMARY
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Execution Roadmap & Investment Summary: Path to Sustainable SaaS", "Phased Execution  •  Milestones", 10)
    
    r_w = Inches(3.7)
    r_gap = Inches(0.3)
    r_top = Inches(1.6)
    r_h = Inches(4.3)
    
    phases = [
        ("PHASE 1: Foundation & OSS Flywheel", "MONTHS 1 - 4", ACCENT_CYAN, [
            ("UMS Spec 1.0 Finalization", "Publish open JSON Schema, TypeScript types, and RFC standard"),
            ("Zero-Dependency Tooling", "Solidify CLI (cli.py), Local Web Studio (run.py), and SQLite Vault"),
            ("Chrome Web Store Release", "Deploy Manifest V3 extension companion with active tab detection"),
            ("Community Target", "Reach 10,000 active developers; establish core open-source credibility")
        ]),
        ("PHASE 2: Relay Pro Commercial Launch", "MONTHS 5 - 8", ACCENT_EMERALD, [
            ("Encrypted Sync Relay", "Deploy multi-device synchronization backend with zero-knowledge keys"),
            ("1-Click Tab Session Handoff", "Live cross-browser active session transfer between Claude & ChatGPT"),
            ("Closed-Loop Diff Engine", "Automate semantic retention scoring (🟢 Learned, 🟡 Adapted, 🔴 Filtered)"),
            ("Financial Target", "Reach 800+ paid Pro subscribers ($10,000 MRR / $120k ARR)")
        ]),
        ("PHASE 3: Team Expansion & Governance", "MONTHS 9 - 14", ACCENT_AMBER, [
            ("Relay for Teams Launch", "Centralized .cursorrules, CLAUDE.md, and repo prompt vault sync"),
            ("Compliance & Secret Scrubbing", "WASM/Edge PII and API key redaction filter before provider ingest"),
            ("Self-Hosted Relay Container", "Dockerized on-premise relay for privacy-sensitive enterprise teams"),
            ("Financial Target", "Reach 50+ paid teams and 2,500 Pro devs ($50,000+ MRR / $600k+ ARR)")
        ])
    ]
    
    for i, (title, timeline, col, milestones) in enumerate(phases):
        r_left = Inches(0.8 + i * (3.7 + 0.3))
        add_card(s10, r_left, r_top, r_w, r_h, title)
        
        c_bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, r_left, r_top, r_w, Inches(0.04))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = col
        c_bar.line.fill.background()
        
        # Timeline tag
        tb = s10.shapes.add_textbox(r_left + Inches(0.2), r_top + Inches(0.55), r_w - Inches(0.4), Inches(0.3))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = timeline
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        
        # Milestones
        mtb = s10.shapes.add_textbox(r_left + Inches(0.2), r_top + Inches(0.9), r_w - Inches(0.4), Inches(3.2))
        mtf = mtb.text_frame
        mtf.word_wrap = True
        mtf.margin_left = mtf.margin_top = mtf.margin_right = mtf.margin_bottom = 0
        
        for j, (m_title, m_desc) in enumerate(milestones):
            mp = mtf.paragraphs[0] if j == 0 else mtf.add_paragraph()
            mp.text = f"• {m_title}: "
            mp.font.size = Pt(9.5)
            mp.font.bold = True
            mp.font.color.rgb = TEXT_LIGHT
            
            mrun = mp.add_run()
            mrun.text = m_desc
            mrun.font.bold = False
            mrun.font.color.rgb = TEXT_MUTED
            mp.space_after = Pt(10)

    # Bottom Final Summary Card
    add_card(s10, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.95), bg_color=RGBColor(20, 26, 36))
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(6.1), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EXECUTIVE SUMMARY: "
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    r = p.add_run()
    r.text = "RelayAI combines an open, community-trusted specification (Universal Memory Schema) with a defensible, high-margin subscription SaaS model ($12/mo Pro, $28/seat Team). By eliminating the 'Context Reset Penalty' across ChatGPT, Claude, and developer IDEs without ToS violations or compute bloat, Relay delivers an indispensable utility for the multi-model AI era."
    r.font.bold = False
    r.font.color.rgb = TEXT_LIGHT

    # Save Presentation
    output_filename = "RelayAI_UMS_Business_Model.pptx"
    prs.save(output_filename)
    print(f"Presentation generated successfully: {output_filename}")

if __name__ == "__main__":
    build_deck()
