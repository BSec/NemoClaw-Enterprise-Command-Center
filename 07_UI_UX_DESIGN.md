# NemoClaw Gateway Dashboard - UI/UX Design Concepts

## Phase: Ideation (v0.1.0)

---

## 1. Design System Overview

### 1.1 Visual Identity

**Brand Alignment**: NVIDIA-inspired with focus on:
- Technology-forward aesthetic
- Dark mode default (reduces eye strain for monitoring)
- High information density
- Real-time data visualization

**Color Palette**:
```
Primary:
- NVIDIA Green: #76B900 (success, action, brand)
- Dark Background: #0D1117 (main background)
- Card Background: #161B22 (elevated surfaces)
- Border: #30363D (subtle dividers)

Status Colors:
- Success: #3FB950 (running, healthy, approved)
- Warning: #D29922 (caution, pending, attention)
- Error: #F85149 (error, denied, critical)
- Info: #58A6FF (information, neutral)

Text Colors:
- Primary Text: #E6EDF3 (headings, important text)
- Secondary Text: #8B949E (body text, descriptions)
- Muted Text: #6E7681 (timestamps, metadata)
```

**Typography**:
```
Font Families:
- Primary: Inter, system-ui, sans-serif
- Monospace: JetBrains Mono, Consolas, monospace

Font Sizes:
- H1: 24px / font-semibold
- H2: 20px / font-semibold  
- H3: 16px / font-medium
- Body: 14px / font-normal
- Small: 12px / font-normal
- Micro: 10px / font-normal (timestamps, badges)
```

### 1.2 Layout Grid

**Container System**:
- Max Width: 1440px (wide screens)
- Breakpoints: sm(640px), md(768px), lg(1024px), xl(1280px), 2xl(1440px)
- Gutters: 24px (desktop), 16px (tablet), 12px (mobile)

**Dashboard Grid**:
- 12-column grid system
- Widget spacing: 16px
- Sidebar width: 280px (expanded), 72px (collapsed)
- Header height: 64px

---

## 2. Screen Layouts (Wireframe Descriptions)

### 2.1 Global Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (64px)                                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │  Logo   │ │ Persona │ │ Search  │ │ Alerts  │ │  User   │    │
│  │         │ │Selector │ │   Bar   │ │  Bell   │ │  Menu   │    │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│ Sidebar  │                                                      │
│ (280px)  │              Main Content Area                       │
│          │         (adapts to persona and screen)               │
│          │                                                      │
│  ┌────┐  │  ┌──────────────────────────────────────────────┐  │
│  │Icon│  │  │                                              │  │
│  │Item│  │  │           Dashboard Widgets                  │  │
│  ├────┤  │  │         (grid or list layout)                │  │
│  │Icon│  │  │                                              │  │
│  │Item│  │  └──────────────────────────────────────────────┘  │
│  ├────┤  │                                                      │
│  │Icon│  │                                                      │
│  │Item│  │                                                      │
│  └────┘  │                                                      │
│          │                                                      │
│ Settings │                                                      │
│ (bottom) │                                                      │
└──────────┴──────────────────────────────────────────────────────┘
```

### 2.2 Engineer View - Sandbox Dashboard

**Purpose**: Main operational view for managing sandboxes and monitoring resources

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  [Sandbox Status Cards - 4 columns]                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Sandbox 1│ │ Sandbox 2│ │ Sandbox 3│ │ Sandbox 4│          │
│  │  RUNNING │ │  STOPPED │ │   ERROR  │ │  RUNNING │          │
│  │ GPU: 75% │ │          │ │ Restart  │ │ GPU: 45% │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  [GPU Telemetry - Full Width]                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ GPU Utilization %          │  Memory Usage              │  │
│  │ [████████░░░░░░░░░░] 65%   │  [███████░░░░░░░░░] 7.2GB │  │
│  │ [line chart - 1hr history] │  [gauge chart] 12GB total │  │
│  └─────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  [Recent Logs - 2/3 width]    │  [Inference Providers - 1/3]  │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐   │
│  │ Filter: [ERROR ▼]       │  │  │ NVIDIA NIM ● Active   │   │
│  │ Search: [__________]    │  │  │ Latency: 45ms         │   │
│  │ ─────────────────────   │  │  │ [Switch to Ollama]    │   │
│  │ 10:42:23 ERROR Agent-7  │  │  │                       │   │
│  │ 10:41:15 WARN  Rate lim │  │  │ Ollama ○              │   │
│  │ 10:40:01 INFO  Task com │  │  │ Latency: 120ms        │   │
│  │ ...                     │  │  │ [Test Provider ▼]     │   │
│  └─────────────────────────┘  │  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components**:
1. **Sandbox Cards**: Status badge, quick actions, resource mini-charts
2. **GPU Telemetry**: Real-time utilization and memory with sparklines
3. **Log Viewer**: Filterable list with severity indicators
4. **Inference Router**: Provider cards with latency and switch controls

**Interactions**:
- Click sandbox card → Open detail drawer
- Hover GPU chart → Tooltip with exact values
- Click log entry → Expand full message
- Select provider → Confirmation modal

### 2.3 Engineer View - Sandbox Detail

**Purpose**: Deep dive into specific sandbox for debugging and management

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  [Breadcrumb] > Sandboxes > Agent-7                        [X]│
├─────────────────────────────────────────────────────────────────┤
│  Agent-7                                    [Restart] [Stop]   │
│  Status: RUNNING ●    Created: 2 days ago    Uptime: 47h 23m    │
├─────────────────────────────────────────────────────────────────┤
│  [Tabs: Overview | Logs | Workspace | Settings]                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Resource Usage - Large Charts]                                 │
│  ┌────────────────────┐  ┌────────────────────┐               │
│  │ GPU Utilization    │  │ Memory Usage       │               │
│  │ [area chart]       │  │ [line chart]       │               │
│  │ 65% avg, 89% peak  │  │ 7.2GB / 12GB       │               │
│  └────────────────────┘  └────────────────────┘               │
│                                                                  │
│  [Live Logs - Full Width]                                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ [Real-time log stream with tail -f behavior]            │  │
│  │ 10:45:23 [Agent-7] Processing request #1294...           │  │
│  │ 10:45:24 [Agent-7] Calling tool: web_search             │  │
│  │ 10:45:25 [Agent-7] Tool response: 3 results found       │  │
│  │ ... (auto-scrolls, pause on hover)                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Workspace Files - Bottom Section]                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 📁 workspace/                                             │  │
│  │   📁 data/                                                │  │
│  │     📄 customers.csv                                      │  │
│  │   📄 config.yaml                                        │  │
│  │   📄 prompts.json                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 SecOps View - Request Queue

**Purpose**: Central hub for reviewing and acting on network requests

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Network Request Queue                              [Auto-refresh│
│  12 pending | 45 approved today | 3 denied today]              │
├─────────────────────────────────────────────────────────────────┤
│  [Filter Bar]                                                   │
│  Status: [All ▼] | Risk: [High+ ▼] | Time: [Last hour ▼]       │
│  [Refresh] [Export] [Bulk Actions ▼]                            │
├─────────────────────────────────────────────────────────────────┤
│  [Request Table]                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ☐ | Time    | Agent  | Destination         | Risk | Action ││
│  │─────────────────────────────────────────────────────────────││
│  │ ☐ | 10:45:23| Agt-7 | api.github.com       |  35  | [✓][✗]││
│  │ ☐ | 10:44:01| Agt-3 | http://192.168.1.50  |  78  | [✓][✗]││
│  │ ☐ | 10:43:15| Agt-7 | api.openai.com       |  45  | [✓][✗]││
│  │ ☐ | 10:42:58| Agt-12| internal-db:5432      |  89  | [✓][✗]││
│  │    |         |       |                      | HIGH |       ││
│  │ ☐ | 10:41:22| Agt-7 | cdn.jsdelivr.net    |  12  | [✓][✗]││
│  │ ...                                                         ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  [Selected: 3] [Approve Selected] [Deny Selected] [Escalate]    │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components**:
1. **Stats Bar**: Quick overview of queue status
2. **Filter Bar**: Multi-criteria filtering
3. **Request Table**: Sortable, selectable rows
4. **Risk Indicator**: Color-coded score with tooltip
5. **Quick Actions**: Inline approve/deny buttons
6. **Bulk Actions**: Multi-select operations

**Interactions**:
- Click row → Open request detail drawer
- Click risk score → View risk breakdown
- Right-click row → Context menu (view agent, view history)
- Hover destination → Preview domain reputation

### 2.5 SecOps View - Agent Reputation Dashboard

**Purpose**: Monitor and manage agent trust scores

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Agent Reputation Scoring                                         │
│  Average Score: 72/100  [███░░░░░░░]  Trending: ↗ +5 this week  │
├─────────────────────────────────────────────────────────────────┤
│  [Agent Cards - 3 columns]                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Agent-3     │ │  Agent-7     │ │  Agent-12    │            │
│  │              │ │              │ │  ⚠ REVIEW    │            │
│  │   ┌────┐     │ │   ┌────┐     │ │   ┌────┐     │            │
│  │   │ 85 │     │ │   │ 72 │     │ │   │ 45 │     │            │
│  │   └────┘     │ │   └────┘     │ │   └────┘     │            │
│  │   SCORE      │ │   SCORE      │ │   SCORE      │            │
│  │              │ │              │ │              │            │
│  │  ↗ Improving │ │  → Stable    │ │  ↘ Declining │            │
│  │              │ │              │ │              │            │
│  │ [View] [Log]│ │ [View] [Log] │ │[Quarantine] │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  [Signal Breakdown - Agent-12 Selected]                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Positive Signals:                    Negative Signals:        ││
│  │ ✓ Uses designated tools (+20)      ✗ Blocked requests (-15)││
│  │ ✓ Low token ratio (+15)            ✗ File access anomaly(-12)│
│  │ ✓ Task completion (+10)            ✗ High error rate (-10)  ││
│  │                                    ✗ Unusual hours (-8)     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.6 SecOps View - HITL Adjudication

**Purpose**: Interface for human review of high-risk agent actions

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Human-in-the-Loop Adjudication    SLA: 2 pending | Avg 3.2min  │
├─────────────────────────────────────────────────────────────────┤
│  [Queue - Left Sidebar]          │  [Current Case - Main]       │
│  ┌────────────────────────────┐ │ ┌───────────────────────────┐│
│  │ HIGH PRIORITY              │ │ │ Case #2847                ││
│  │ ─────────────────────────  │ │ │                           ││
│  │ ● Agent-7 Database Delete  │ │ │ Agent: Agent-7            ││
│  │   2 min ago ⚠ SLA 5min     │ │ │ Action: DELETE FROM users ││
│  │                            │ │ │ Risk Score: 89/100        ││
│  │ ○ Agent-3 File Export      │ │ │                           ││
│  │   5 min ago               │ │ │ [Context Tab] [History]   ││
│  │                            │ │ │                           ││
│  │ PENDING                    │ │ │ Current Task:             ││
│  │ ○ Agent-12 API Call        │ │ │ "Archive old user data"   ││
│  │   8 min ago               │ │ │                           ││
│  │                            │ │ │ Requested Action:         ││
│  └────────────────────────────┘ │ │ DELETE FROM users WHERE   ││
│                                 │ │ created_at < '2023-01-01' ││
│                                 │ │                           ││
│                                 │ │ Similar Past Decisions:   ││
│                                 │ │ • Approved 12 times       ││
│                                 │ │ • Denied 1 time           ││
│                                 │ │                           ││
│                                 │ │ ┌─────────────────────┐   ││
│                                 │ │ │ [  Approve  ]        │   ││
│                                 │ │ │ [  Deny     ]        │   ││
│                                 │ │ │ [Override...▼]       │   ││
│                                 │ │ └─────────────────────┘   ││
│                                 │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.7 CISO View - Compliance Dashboard

**Purpose**: Executive-level compliance and risk overview

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  AI Security Compliance Posture                                   │
│  Last Updated: March 26, 2026 | Next Audit: April 15, 2026      │
├─────────────────────────────────────────────────────────────────┤
│  [Framework Selector: NIST AI RMF ▼]                             │
├─────────────────────────────────────────────────────────────────┤
│  [Overall Score - Large Display]                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │     92% Compliant                    ┌──────────┐        │  │
│  │                                      │          │        │  │
│  │   [███████████████░]                 │  RISK    │        │  │
│  │                                      │  SCORE   │        │  │
│  │   45 / 49 Controls                   │    23    │        │  │
│  │                                      │  (Low)   │        │  │
│  │                                      └──────────┘        │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  [Category Breakdown - Donut Charts]                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │  Govern     │ │   Map       │ │  Measure    │ │   Manage   │ │
│  │             │ │             │ │             │ │            │ │
│  │ [donut]     │ │ [donut]     │ │ [donut]     │ │ [donut]    │ │
│  │   100%      │ │    87%      │ │    90%      │ │    95%     │ │
│  │  12/12      │ │  13/15      │ │   9/10      │ │   11/12   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  [Non-Compliant Items - Table]                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Control | Category | Gap | Risk | Action                    ││
│  │────────────────────────────────────────────────────────────││
│  │ M-3.1   │ Measure  │ No   │ Med │ [Add Evidence]          ││
│  │         │          │ log  │     │                           ││
│  │ Ma-2.2  │ Manage   │ Unvetted│ Low│ [Review Policy]      ││
│  │         │          │ vendor│    │                           ││
│  │ Map-1.1 │ Map      │ Partial│ Med│ [Complete Form]       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.8 CISO View - Executive Summary Report

**Purpose**: Board-ready one-page summary

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  NemoClaw Gateway Security Report                                │
│  Q1 2026 | Generated: March 26, 2026                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Key Metrics - 4 columns]                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Agents    │   Requests    │   Incidents   │  Compliance   ││
│  │             │               │               │               ││
│  │    12       │    1,247      │      3        │     92%       ││
│  │   Active    │   Processed   │    Minor      │    NIST AI   ││
│  │             │               │               │      RMF      ││
│  │  ↗ +3      │   ↗ +15%     │    ↘ -40%    │   → +5%      ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                  │
│  [Risk Trend Chart - Full Width]                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Risk Score Over Time (6 months)                             ││
│  │                                                             ││
│  │  80 ┤                           ╭─╮                         ││
│  │     │              ╭─╮         ╭╯ ╰╮  ╭──                   ││
│  │  60 ┤    ╭──╮     ╭╯ ╰╮   ╭──╯    ╰──╯                     ││
│  │     │╭──╯  ╰─────╯    ╰───╯                                ││
│  │  40 ┤╯                                                     ││
│  │     └────┬────┬────┬────┬────┬────┬────┬                   ││
│  │         Oct  Nov  Dec  Jan  Feb  Mar                        ││
│  │                                                             ││
│  │ [Export PDF] [Export PPTX] [Schedule Monthly]             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [Highlights]                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✓ Successfully blocked 45 high-risk network requests        ││
│  │ ✓ Zero data exfiltration incidents                          ││
│  │ ✓ Mean time to detect: 1.2 minutes (target: <5 min)        ││
│  │ ⚠ 2 sandboxes running outdated agent versions              ││
│  │ ⚠ Shadow AI detected: 3 unmanaged endpoints                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Status Badges

**Variants**:
```
[Running]  - Green dot, pulsing animation
[Stopped]  - Gray dot, static
[Error]    - Red dot, blinking 2x
[Pending]  - Amber dot, pulsing slowly
[Warning]  - Amber triangle icon
[Unknown]  - Gray question mark
```

**Sizes**:
- Small: 16px height (tables)
- Medium: 20px height (cards)
- Large: 24px height (headers)

### 3.2 Metric Cards

**Structure**:
```
┌─────────────────────────────┐
│ Icon  Label                    │
│                              │
│        Value                 │
│        [Large Number]        │
│                              │
│ [Sparkline]  Trend +5%      │
└─────────────────────────────┘
```

**Examples**:
- GPU Utilization: 65% with area chart
- Memory Usage: 7.2GB / 12GB with gauge
- Request Rate: 245/min with bar chart
- Agent Score: 85/100 with circular progress

### 3.3 Data Tables

**Standard Table**:
- Row height: 48px
- Header height: 40px
- Padding: 16px horizontal
- Divider: 1px border-bottom
- Hover: Background highlight
- Selection: Checkbox left-aligned

**Interactive Features**:
- Column sorting (click header)
- Column filtering (dropdown in header)
- Row actions (right-aligned buttons)
- Bulk selection (header checkbox)
- Expandable rows (chevron icon)

### 3.4 Forms & Inputs

**Text Input**:
- Height: 40px
- Border radius: 6px
- Padding: 12px 16px
- Focus: Green border (#76B900)
- Error: Red border with message below

**Select Dropdown**:
- Same dimensions as input
- Chevron icon on right
- Dropdown max-height: 300px
- Group headers for categories

**Buttons**:
- Primary: Green background, dark text
- Secondary: Dark background, green border
- Danger: Red background (destructive)
- Ghost: Transparent, hover highlight
- Heights: Small(32px), Medium(40px), Large(48px)

### 3.5 Modals & Drawers

**Modal** (for confirmations):
- Width: 400px (standard), 600px (large)
- Backdrop: Semi-transparent black
- Close: X button top-right, click backdrop, ESC key
- Actions: Right-aligned buttons

**Drawer** (for detail views):
- Width: 480px (standard), 640px (wide)
- Position: Right side
- Overlay: Pushes content or overlays
- Header: Title with close button
- Scrollable content area

### 3.6 Charts & Visualizations

**Sparklines** (mini charts in tables/cards):
- Height: 24px
- Width: 60-100px
- No axes, just trend line
- Color matches status

**Area Charts** (metrics over time):
- Height: 120px
- Gradient fill below line
- Y-axis: Auto-scaled
- X-axis: Time labels
- Tooltip on hover

**Gauge Charts** (percentage displays):
- Size: 120px diameter
- Arc: 240 degrees (like speedometer)
- Color segments: Green/Yellow/Red
- Center: Large percentage value

**Donut Charts** (distribution):
- Size: 120px diameter
- Center: Total or percentage
- Legend: Right side or below
- Interactive: Hover for details

---

## 4. Animation & Motion

### 4.1 Micro-interactions

**Button Hover**:
- Duration: 150ms
- Easing: ease-out
- Effect: Background lighten, subtle scale(1.02)

**Status Changes**:
- Duration: 300ms
- Effect: Color transition, icon morph
- Example: Stopped → Running (gray → green)

**Loading States**:
- Skeleton: Pulse opacity 0.5 → 1.0
- Spinner: Rotate 360deg infinite
- Progress: Width animation 300ms

### 4.2 Page Transitions

**Persona Switching**:
- Duration: 300ms
- Effect: Cross-fade content
- Maintain: Header and sidebar

**Detail View Open**:
- Duration: 250ms
- Effect: Slide drawer from right
- Easing: cubic-bezier(0.4, 0, 0.2, 1)

### 4.3 Real-time Indicators

**Live Badge**:
- Animation: Pulse green dot
- Frequency: 2s cycle
- Tooltip: "Real-time updates active"

**Data Refresh**:
- Animation: Spin refresh icon 360deg
- Duration: 500ms
- Success: Checkmark flash

---

## 5. Responsive Behavior

### 5.1 Breakpoints

- **Mobile** (< 640px): Single column, stacked layout
- **Tablet** (640px - 1024px): 2-column grids, collapsed sidebar
- **Desktop** (1024px - 1440px): Full layout, expanded sidebar
- **Wide** (> 1440px): Max-width container, centered

### 5.2 Layout Adaptations

**Sidebar**:
- Desktop: Expanded (280px) with text labels
- Tablet: Collapsed (72px) with icons only
- Mobile: Hidden (hamburger menu)

**Dashboard Grid**:
- Wide: 4-column widget grid
- Desktop: 3-column widget grid
- Tablet: 2-column widget grid
- Mobile: Single column stack

**Tables**:
- Desktop: Full table with all columns
- Tablet: Condensed (hide less important columns)
- Mobile: Card view (row → card conversion)

---

## 6. Accessibility Considerations

### 6.1 Color Contrast

- All text meets WCAG AA (4.5:1 ratio)
- Status colors distinguishable without color (icons)
- Focus indicators clearly visible

### 6.2 Keyboard Navigation

- Tab order follows visual flow
- Enter activates buttons and links
- Escape closes modals and drawers
- Arrow keys navigate tables and menus

### 6.3 Screen Readers

- ARIA labels on all interactive elements
- Table headers properly associated
- Status changes announced via live regions
- Icons have descriptive labels

---

*Document Version: 0.1.0*
*Phase: Ideation*
*Last Updated: March 26, 2026*
