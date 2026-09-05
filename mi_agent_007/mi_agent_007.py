import reflex as rx


# ============================================================
# MI BOND / AGENT 007
# V2 Control Plane
# ============================================================


NAV_ITEMS = [
    ("layout-dashboard", "Command Center"),
    ("messages-square", "Chats"),
    ("bot", "Agents"),
    ("list-checks", "Tasks"),
    ("workflow", "Automations"),
    ("shield-check", "Approvals"),
    ("brain", "Memory"),
    ("plug", "Connections"),
    ("cpu", "Compute"),
    ("activity", "Activity"),
    ("settings", "Settings"),
]


class State(rx.State):
    page: str = "Command Center"

    command: str = ""
    last_command: str = ""
    execution_status: str = "Ready"

    selected_agent: str = "Bond"

    selected_provider: str = "Auto"
    selected_model: str = "Auto"
    selected_runtime: str = "Auto"

    selected_compute: str = "Auto"
    routing_policy: str = "Balanced"

    max_tokens: str = "4096"
    temperature: str = "0.4"

    approval_mode: str = "Recommended"
    memory_enabled: bool = True

    # --------------------------------------------------------
    # UI state setters
    # --------------------------------------------------------

    def set_page(self, value: str):
        self.page = value

    def set_command(self, value: str):
        self.command = value

    def set_selected_agent(self, value: str):
        self.selected_agent = value

    def set_selected_provider(self, value: str):
        self.selected_provider = value

    def set_selected_model(self, value: str):
        self.selected_model = value

    def set_selected_runtime(self, value: str):
        self.selected_runtime = value

    def set_selected_compute(self, value: str):
        self.selected_compute = value

    def set_routing_policy(self, value: str):
        self.routing_policy = value

    def set_max_tokens(self, value: str):
        self.max_tokens = value

    def set_temperature(self, value: str):
        self.temperature = value

    def set_approval_mode(self, value: str):
        self.approval_mode = value

    def toggle_memory(self, value: bool):
        self.memory_enabled = value

    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------

    def execute(self):
        if self.command.strip():
            self.last_command = self.command
            self.execution_status = (
                f"Queued · {self.selected_agent} · "
                f"{self.selected_model} · {self.selected_compute}"
            )
            self.command = ""


# ============================================================
# COMMON COMPONENTS
# ============================================================


def status_dot(status: str = "online"):
    dot_color = {
        "online": rx.color("green", 9),
        "standby": rx.color("amber", 9),
        "offline": rx.color("gray", 8),
        "future": rx.color("purple", 8),
    }.get(status, rx.color("gray", 8))

    return rx.box(
        width="8px",
        height="8px",
        border_radius="999px",
        background=dot_color,
        flex_shrink="0",
    )


def section_title(kicker: str, title: str, subtitle: str):
    return rx.vstack(
        rx.text(
            kicker.upper(),
            font_size="10px",
            color=rx.color("gray", 10),
            letter_spacing="0.08em",
        ),
        rx.heading(title, size="7"),
        rx.text(
            subtitle,
            color=rx.color("gray", 10),
            max_width="850px",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def metric(title: str, value: str, detail: str, icon: str):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.text(
                    title.upper(),
                    size="1",
                    color=rx.color("gray", 10),
                ),
                width="100%",
            ),
            rx.text(value, weight="bold", size="5"),
            rx.text(
                detail,
                size="1",
                color=rx.color("gray", 10),
            ),
            spacing="2",
            align="start",
        ),
        min_width="185px",
        flex="1",
    )


def setting_select(label: str, value, options, handler, description=""):
    return rx.vstack(
        rx.text(label, weight="medium", size="2"),
        rx.select(
            options,
            value=value,
            on_change=handler,
            width="100%",
        ),
        rx.cond(
            description != "",
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def nav_button(icon: str, label: str):
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(label, size="2", weight="medium"),
            width="100%",
            spacing="3",
        ),
        on_click=lambda: State.set_page(label),
        width="100%",
        justify_content="flex-start",
        variant="ghost",
        color_scheme="gray",
        background=rx.cond(
            State.page == label,
            rx.color("gray", 4),
            "transparent",
        ),
    )


def sidebar():
    top_items = NAV_ITEMS[:-1]
    settings_item = NAV_ITEMS[-1]

    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.text("007", weight="bold", font_size="10px"),
                border="1px solid",
                border_color=rx.color("gray", 6),
                border_radius="8px",
                padding="4px 5px",
                min_width="30px",
                text_align="center",
            ),
            rx.vstack(
                rx.text("MI BOND", weight="bold", size="3"),
                rx.text(
                    "Agent 007",
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            padding="5px 7px 18px",
            align="center",
        ),

        *[
            nav_button(icon, label)
            for icon, label in top_items
        ],

        rx.spacer(),

        nav_button(*settings_item),

        rx.hstack(
            rx.color_mode.button(),
            rx.text(
                "Appearance",
                size="1",
                color=rx.color("gray", 10),
            ),
            padding="7px",
            spacing="2",
            align="center",
        ),

        width="240px",
        min_width="240px",
        height="100vh",
        padding="18px 12px",
        border_right="1px solid",
        border_color=rx.color("gray", 5),
        align="stretch",
        position="sticky",
        top="0",
    )


def page_shell(content):
    return rx.box(
        content,
        width="100%",
        min_height="100vh",
    )


# ============================================================
# COMMAND CENTER
# ============================================================


def command_center():
    return rx.vstack(
        rx.hstack(
            section_title(
                "Command Center",
                "MI BOND",
                "One command surface for agents, models, tools, workflows and compute.",
            ),
            rx.spacer(),
            rx.badge(
                rx.hstack(
                    status_dot("online"),
                    rx.text("SYSTEM READY"),
                ),
                variant="soft",
                size="2",
            ),
            width="100%",
            align="start",
        ),

        rx.hstack(
            metric(
                "Control Plane",
                "Online",
                "Reflex · Agent 007",
                "server",
            ),
            metric(
                "Compute Router",
                State.selected_compute,
                "CPU · GPU · API · Local",
                "cpu",
            ),
            metric(
                "Model Runtime",
                State.selected_runtime,
                "vLLM · MLX · Ollama · API",
                "brain",
            ),
            metric(
                "Approvals",
                "0",
                "No actions waiting",
                "shield-check",
            ),
            spacing="3",
            width="100%",
            flex_wrap="wrap",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "What should we accomplish?",
                            weight="bold",
                            size="5",
                        ),
                        rx.text(
                            "Bond can research, reason, delegate, automate and execute.",
                            size="2",
                            color=rx.color("gray", 10),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.badge(
                        State.routing_policy,
                        variant="soft",
                    ),
                    width="100%",
                ),

                rx.text_area(
                    placeholder=(
                        "Ask Bond to research, build, monitor, "
                        "schedule, analyze or execute..."
                    ),
                    value=State.command,
                    on_change=State.set_command,
                    width="100%",
                    min_height="145px",
                    size="3",
                ),

                rx.grid(
                    setting_select(
                        "Agent",
                        State.selected_agent,
                        [
                            "Bond",
                            "Research",
                            "Executive",
                            "Engineering",
                            "Communications",
                        ],
                        State.set_selected_agent,
                    ),
                    setting_select(
                        "Model",
                        State.selected_model,
                        [
                            "Auto",
                            "Qwen",
                            "Llama",
                            "GPT",
                            "Claude",
                            "Grok",
                            "Local Model",
                        ],
                        State.set_selected_model,
                    ),
                    setting_select(
                        "Runtime",
                        State.selected_runtime,
                        [
                            "Auto",
                            "vLLM",
                            "Transformers",
                            "MLX",
                            "Ollama",
                            "Provider API",
                        ],
                        State.set_selected_runtime,
                    ),
                    setting_select(
                        "Compute",
                        State.selected_compute,
                        [
                            "Auto",
                            "Reflex CPU",
                            "Mac Apple Silicon",
                            "Kaggle T4 x2",
                            "Lightning GPU",
                            "NVIDIA CUDA Lab",
                            "AMD ROCm Lab",
                        ],
                        State.set_selected_compute,
                    ),
                    columns="4",
                    spacing="3",
                    width="100%",
                ),

                rx.hstack(
                    rx.hstack(
                        rx.icon("shield-check", size=15),
                        rx.text(
                            "Sensitive actions require approval.",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("send", size=16),
                        "Execute",
                        on_click=State.execute,
                        size="3",
                    ),
                    width="100%",
                    align="center",
                ),

                spacing="4",
                width="100%",
            ),
            width="100%",
            padding="24px",
        ),

        rx.grid(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("activity", size=18),
                        rx.text("EXECUTION TRACE", weight="bold"),
                    ),
                    rx.divider(),
                    rx.hstack(
                        status_dot("online"),
                        rx.text(State.execution_status, size="2"),
                    ),
                    rx.cond(
                        State.last_command != "",
                        rx.box(
                            rx.text(
                                "LAST COMMAND",
                                size="1",
                                color=rx.color("gray", 10),
                            ),
                            rx.text(State.last_command, size="2"),
                            padding="14px",
                            width="100%",
                            border_radius="9px",
                            background=rx.color("gray", 2),
                        ),
                    ),
                    rx.text(
                        "Future: tool calls, retries, latency, tokens, cost and intermediate agent steps.",
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
            ),

            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("cpu", size=18),
                        rx.text("COMPUTE STATUS", weight="bold"),
                    ),
                    rx.divider(),

                    compute_row(
                        "Reflex Cloud",
                        "CPU · Control Plane",
                        "online",
                    ),
                    compute_row(
                        "Mac",
                        "Apple Silicon · Optional Worker",
                        "online",
                    ),
                    compute_row(
                        "Kaggle",
                        "NVIDIA T4 ×2 · GPU Worker",
                        "standby",
                    ),
                    compute_row(
                        "Lightning",
                        "Cloud GPU Worker",
                        "standby",
                    ),
                    compute_row(
                        "NVIDIA CUDA Lab",
                        "Remote CUDA Worker",
                        "standby",
                    ),

                    spacing="3",
                    align="start",
                    width="100%",
                ),
            ),

            columns="2",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# COMPUTE
# ============================================================


def compute_row(name: str, description: str, status: str):
    return rx.hstack(
        status_dot(status),
        rx.vstack(
            rx.text(name, weight="medium", size="2"),
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.badge(status.upper(), variant="soft"),
        width="100%",
        align="center",
    )


def compute_page():
    return rx.vstack(
        section_title(
            "Infrastructure",
            "Compute",
            "Choose where Bond executes CPU, GPU and model inference workloads.",
        ),

        rx.card(
            rx.vstack(
                rx.heading("Default routing", size="4"),

                rx.grid(
                    setting_select(
                        "Default Compute",
                        State.selected_compute,
                        [
                            "Auto",
                            "Reflex CPU",
                            "Mac Apple Silicon",
                            "Kaggle T4 x2",
                            "Lightning GPU",
                            "NVIDIA CUDA Lab",
                            "AMD ROCm Lab",
                        ],
                        State.set_selected_compute,
                        "The preferred execution host.",
                    ),
                    setting_select(
                        "Routing Policy",
                        State.routing_policy,
                        [
                            "Balanced",
                            "GPU First",
                            "Fastest",
                            "Lowest Cost",
                            "Local Only",
                            "Best Quality",
                        ],
                        State.set_routing_policy,
                        "Controls how Bond selects compute.",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
        ),

        rx.grid(
            compute_card(
                "Reflex Cloud",
                "Control Plane",
                "CPU",
                "Online",
                "Persistent UI, scheduler and orchestration.",
            ),
            compute_card(
                "Kaggle",
                "GPU Worker",
                "NVIDIA T4 ×2",
                "Standby",
                "Primary free GPU inference target.",
            ),
            compute_card(
                "Mac",
                "Local Worker",
                "Apple Silicon",
                "Available",
                "MLX / Ollama / CPU tools.",
            ),
            compute_card(
                "Lightning",
                "GPU Worker",
                "Cloud GPU",
                "Standby",
                "Optional cloud inference fallback.",
            ),
            compute_card(
                "NVIDIA CUDA Lab",
                "Remote Worker",
                "CUDA",
                "Standby",
                "Existing NVIDIA engineering environment.",
            ),
            compute_card(
                "AMD ROCm Lab",
                "Future Worker",
                "ROCm",
                "Planned",
                "Portable AMD accelerated inference.",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def compute_card(name, role, accelerator, status, description):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(name, weight="bold", size="4"),
                    rx.text(
                        role.upper(),
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(status, variant="soft"),
                width="100%",
            ),
            rx.divider(),
            rx.text(accelerator, weight="medium", size="2"),
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
            rx.hstack(
                rx.text("CPU", size="1"),
                rx.text("GPU", size="1"),
                rx.text("RAM", size="1"),
                rx.text("VRAM", size="1"),
                spacing="3",
                color=rx.color("gray", 10),
            ),
            spacing="3",
            align="start",
            min_height="180px",
        ),
    )


# ============================================================
# SETTINGS
# ============================================================


def settings_page():
    return rx.vstack(
        section_title(
            "Configuration",
            "Settings",
            "Configure Bond's intelligence, execution runtime, routing and safety.",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("brain", size=19),
                    rx.heading("Models & Inference", size="4"),
                ),

                rx.grid(
                    setting_select(
                        "Provider",
                        State.selected_provider,
                        [
                            "Auto",
                            "Open Source",
                            "OpenAI",
                            "Anthropic",
                            "xAI",
                            "Hugging Face",
                            "Local",
                        ],
                        State.set_selected_provider,
                        "Source of model intelligence.",
                    ),

                    setting_select(
                        "Model",
                        State.selected_model,
                        [
                            "Auto",
                            "Qwen",
                            "Llama",
                            "GPT",
                            "Claude",
                            "Grok",
                            "Local Model",
                        ],
                        State.set_selected_model,
                        "Model family used by the agent.",
                    ),

                    setting_select(
                        "Runtime / Serving",
                        State.selected_runtime,
                        [
                            "Auto",
                            "vLLM",
                            "Transformers",
                            "MLX",
                            "Ollama",
                            "Provider API",
                        ],
                        State.set_selected_runtime,
                        "How the selected model is served.",
                    ),

                    columns="3",
                    spacing="4",
                    width="100%",
                ),

                rx.grid(
                    setting_select(
                        "Max Tokens",
                        State.max_tokens,
                        [
                            "1024",
                            "2048",
                            "4096",
                            "8192",
                            "16384",
                            "32768",
                        ],
                        State.set_max_tokens,
                    ),

                    setting_select(
                        "Temperature",
                        State.temperature,
                        [
                            "0.0",
                            "0.2",
                            "0.4",
                            "0.7",
                            "1.0",
                        ],
                        State.set_temperature,
                    ),

                    setting_select(
                        "Compute",
                        State.selected_compute,
                        [
                            "Auto",
                            "Reflex CPU",
                            "Mac Apple Silicon",
                            "Kaggle T4 x2",
                            "Lightning GPU",
                            "NVIDIA CUDA Lab",
                            "AMD ROCm Lab",
                        ],
                        State.set_selected_compute,
                    ),

                    columns="3",
                    spacing="4",
                    width="100%",
                ),

                spacing="5",
                width="100%",
            ),
            padding="24px",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("route", size=19),
                    rx.heading("Routing & Failover", size="4"),
                ),

                setting_select(
                    "Routing Policy",
                    State.routing_policy,
                    [
                        "Balanced",
                        "GPU First",
                        "Fastest",
                        "Lowest Cost",
                        "Local Only",
                        "Best Quality",
                    ],
                    State.set_routing_policy,
                    "Bond can automatically fail over between available model and compute providers.",
                ),

                rx.text(
                    "Planned fallback chain",
                    weight="medium",
                    size="2",
                ),

                rx.code(
                    "Kaggle GPU → Mac Local → Lightning GPU → Provider API",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=19),
                    rx.heading("Safety & Permissions", size="4"),
                ),

                setting_select(
                    "Approval Policy",
                    State.approval_mode,
                    [
                        "Recommended",
                        "Strict",
                        "Manual Only",
                    ],
                    State.set_approval_mode,
                    "Controls which actions require your approval before execution.",
                ),

                rx.hstack(
                    rx.vstack(
                        rx.text("Long-term Memory", weight="medium"),
                        rx.text(
                            "Allow Bond to retain approved operational context.",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=State.memory_enabled,
                        on_change=State.toggle_memory,
                    ),
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# AGENTS
# ============================================================


def agent_card(name, role, description, status):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("bot", size=20),
                    padding="9px",
                    border_radius="10px",
                    background=rx.color("gray", 3),
                ),
                rx.vstack(
                    rx.text(name, weight="bold", size="3"),
                    rx.text(
                        role,
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(status, variant="soft"),
                width="100%",
            ),
            rx.text(
                description,
                size="2",
                color=rx.color("gray", 10),
            ),
            rx.divider(),
            rx.hstack(
                rx.text("Memory", size="1"),
                rx.text("Tools", size="1"),
                rx.text("Policies", size="1"),
                rx.spacer(),
                rx.button("Configure", size="1", variant="soft"),
                width="100%",
            ),
            spacing="3",
            align="start",
        ),
    )


def agents_page():
    return rx.vstack(
        section_title(
            "Agent Network",
            "Agents",
            "Specialized agents coordinated by Bond with independent permissions and tools.",
        ),

        rx.grid(
            agent_card(
                "Bond",
                "Chief Orchestrator",
                "Plans, delegates, monitors and coordinates multi-agent execution.",
                "ONLINE",
            ),
            agent_card(
                "Research",
                "Intelligence",
                "Search, synthesis, competitive analysis and source validation.",
                "STANDBY",
            ),
            agent_card(
                "Executive",
                "Strategy",
                "Executive summaries, recommendations and decision support.",
                "STANDBY",
            ),
            agent_card(
                "Engineering",
                "Code & Infrastructure",
                "Repositories, code, testing, infrastructure and technical workflows.",
                "STANDBY",
            ),
            agent_card(
                "Communications",
                "Email & Messaging",
                "Drafting, inbox triage and approved communications.",
                "STANDBY",
            ),
            agent_card(
                "Automation",
                "Background Operations",
                "Scheduled work, condition watches and workflow execution.",
                "STANDBY",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# CONNECTIONS
# ============================================================


def connection_card(name, description, status, icon):
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=20),
                padding="10px",
                border_radius="10px",
                background=rx.color("gray", 3),
            ),
            rx.vstack(
                rx.text(name, weight="bold"),
                rx.text(
                    description,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(status, variant="soft"),
                rx.button(
                    "Configure",
                    size="1",
                    variant="outline",
                ),
                align="end",
            ),
            width="100%",
            align="center",
        ),
    )


def connections_page():
    return rx.vstack(
        section_title(
            "Integrations",
            "Connections",
            "OAuth, APIs and MCP connections used by Agent 007.",
        ),

        rx.grid(
            connection_card(
                "Google",
                "Gmail · Calendar · Drive",
                "NOT CONNECTED",
                "mail",
            ),
            connection_card(
                "Microsoft",
                "Outlook · Calendar · OneDrive",
                "NOT CONNECTED",
                "mail",
            ),
            connection_card(
                "GitHub",
                "Repositories · Issues · Actions",
                "NOT CONNECTED",
                "github",
            ),
            connection_card(
                "LinkedIn",
                "Approved publishing workflows",
                "NOT CONNECTED",
                "briefcase-business",
            ),
            connection_card(
                "Slack",
                "Channels · Messaging · Alerts",
                "NOT CONNECTED",
                "message-square",
            ),
            connection_card(
                "MCP",
                "External tool servers",
                "READY",
                "plug",
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# AUTOMATIONS
# ============================================================


def automation_row(name, trigger, action, status):
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon("workflow", size=18),
                padding="9px",
                border_radius="10px",
                background=rx.color("gray", 3),
            ),
            rx.vstack(
                rx.text(name, weight="bold"),
                rx.text(
                    trigger,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.text(action, size="2"),
            rx.badge(status, variant="soft"),
            width="100%",
            align="center",
        ),
    )


def automations_page():
    return rx.vstack(
        section_title(
            "Operations",
            "Automations",
            "Scheduled and condition-driven jobs that continue without an open chat.",
        ),

        rx.hstack(
            rx.button(
                rx.icon("plus", size=16),
                "New Automation",
            ),
            rx.button(
                rx.icon("workflow", size=16),
                "Workflow Builder",
                variant="outline",
            ),
        ),

        automation_row(
            "Morning Intelligence Brief",
            "Every weekday · 06:30",
            "Research → Summarize → Deliver",
            "PLANNED",
        ),
        automation_row(
            "GPU Health Watch",
            "Every hour",
            "Check workers → Alert on failure",
            "PLANNED",
        ),
        automation_row(
            "Important Email Watch",
            "On qualifying message",
            "Classify → Summarize → Notify",
            "PLANNED",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="4",
        align="stretch",
    )


# ============================================================
# SIMPLE PLACEHOLDERS
# ============================================================


def simple_page(title: str, subtitle: str, icon: str):
    return rx.vstack(
        section_title(
            "MI BOND",
            title,
            subtitle,
        ),
        rx.card(
            rx.vstack(
                rx.icon(icon, size=32),
                rx.heading(f"{title} workspace", size="4"),
                rx.text(
                    "This module is ready for the next implementation phase.",
                    color=rx.color("gray", 10),
                ),
                spacing="3",
                padding="40px",
                align="center",
            ),
            width="100%",
        ),
        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# PAGE ROUTER
# ============================================================


def routed_page():
    return rx.match(
        State.page,
        ("Command Center", command_center()),
        ("Agents", agents_page()),
        ("Automations", automations_page()),
        ("Connections", connections_page()),
        ("Compute", compute_page()),
        ("Settings", settings_page()),
        (
            "Chats",
            simple_page(
                "Chats",
                "Persistent conversations and agent sessions.",
                "messages-square",
            ),
        ),
        (
            "Tasks",
            simple_page(
                "Tasks",
                "Track queued, running, completed and failed work.",
                "list-checks",
            ),
        ),
        (
            "Approvals",
            simple_page(
                "Approvals",
                "Review sensitive actions before Bond executes them.",
                "shield-check",
            ),
        ),
        (
            "Memory",
            simple_page(
                "Memory",
                "Control long-term operational knowledge and retrieval.",
                "brain",
            ),
        ),
        (
            "Activity",
            simple_page(
                "Activity",
                "Audit agent actions, model calls, tools and compute usage.",
                "activity",
            ),
        ),
        command_center(),
    )


def index():
    return rx.hstack(
        sidebar(),
        page_shell(routed_page()),
        width="100%",
        min_height="100vh",
        spacing="0",
        align="start",
    )


app = rx.App()

app.add_page(
    index,
    title="MI BOND · Agent 007",
    description="MI BOND Agentic AI Command Center",
    image="/mi-bond-favicon.svg",
)
